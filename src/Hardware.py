from machine import Pin, PWM, I2C
import rp2
import time
import ustruct
import json

import config
from Logger import Logger

# Interface class for servos
class ServoInterface:
    
    def set_angle(self, angle):
        pass
    
    def get_angle(self):
        pass
    
# Servo wrapper that flips the orientation
class FlippedServo(ServoInterface):
    def __init__(self, servo):
        self.__servo = servo
        
    def set_angle(self, angle):
        self.__servo.set_angle(180-angle)
        
    def get_angle(self):
        return 180-self.__servo.get_angle()

# Base servo class
# All servo types should extend this class
class Servo(ServoInterface):
    def __init__(self, resolution=1024):
        period = 1000000 / 50
        self._min_duty = int(resolution * 1000 / period)
        self._max_duty = int(resolution * 2000 / period)
        self._angle = 180
        self._current_angle = 90
        self._offset = 0
        self._offset_duty = 0
        self._min_angle = 0
        self._max_angle = 180
        pass
    
    def _get_duty(self, angle):
        angle_ratio = (self._current_angle-self._min_angle) / (self._max_angle-self._min_angle)
        return int(self._min_duty + (self._max_duty-self._min_duty)*angle_ratio)+self._offset_duty
    
    def _update_servo(self, angle):
        pass
    
    def set_angle(self, angle):
        self._current_angle = max(self._min_angle, min(angle, self._max_angle))
        
        self._update_servo(self._current_angle)
        
    def get_angle(self):
        return self._current_angle
    
    def set_offset(self, offset):
        self._offset = offset
        self._offset_duty = int((self._max_duty-self._min_duty)*(offset/self._angle))
        
        self._update_servo(self._current_angle)
        
    def get_offset(self):
        return self._offset
    
    def set_min_angle(self, angle):
        self._min_angle = angle
        
    def get_min_angle(self):
        return self._min_angle
    
    def set_max_angle(self, angle):
        self._max_angle = angle
    
    def get_max_angle(self):
        return self._max_angle
    
    def release(self):
        pass
    
# Servo using the PWM signal from a GPIO pin
class GPIOServo(Servo):
    def __init__(self, pin_num):
        super(GPIOServo, self).__init__(65535)
        self.pwm = PWM(Pin(pin_num))
        self.pwm.freq(50)
        
    def _update_servo(self, angle):
        self.pwm.duty_u16(self._get_duty(angle))
    
    def release(self):
        self.pwm.duty_u16(0)
    
# Servo using the I2C interface through a PCA9685 servo controller
class I2CServo(Servo):
    def __init__(self, bus, addr, port):
        super(I2CServo, self).__init__(4095)
        self.bus = bus
        self.addr = addr
        self._start = 0x6+4*port
        
        # Set the start pulse to 0us
        self._write(self._start, 0)
        
        pass
    
    def _update_servo(self, angle):
        pulse = self._get_duty(angle)
        data = ustruct.pack('<HH', 0, pulse)
        self.bus.writeto_mem(self.addr, self._start,  data)
    
    def release(self):
        data = ustruct.pack('<HH', 0, 4096)
        self.bus.writeto_mem(self.addr, self._start,  data)
    
    def _write(self, reg, data):
        """
        Write bytes to the specified register.
        """
        
        # Construct message
        msg = bytearray()
        msg.append(data)
        
        # Write out message to register
        self.bus.writeto_mem(self.addr, reg, msg)
        
    def _read(self, addr, reg, nbytes=1):
        """
        Read byte(s) from specified register. If nbytes > 1, read from consecutive
        registers.
        """
        
        # Check to make sure caller is asking for 1 or more bytes
        if nbytes < 1:
            return bytearray()
        
        # Request data from specified register(s) over I2C
        data = self.bus.readfrom_mem(self.addr, reg, nbytes)
        
        return data

@rp2.asm_pio(
    set_init=rp2.PIO.OUT_LOW,
    out_shiftdir=rp2.PIO.SHIFT_RIGHT
)
def servo_pio():

    # The FIFO contains:
    #
    # Bits  0-15 = HIGH pulse loop count
    # Bits 16-31 = LOW pulse loop count

    wrap_target()

    # Get a new pulse value if one is available.
    # If the FIFO is empty, keep the previous value.
    pull(noblock)
    mov(isr, osr)

    # Extract HIGH count
    out(x, 16)

    # Extract LOW count
    out(y, 16)

    # Start servo pulse
    set(pins, 1)

    # Wait for HIGH pulse
    label("high")
    jmp(x_dec, "high")

    # End servo pulse
    set(pins, 0)

    # Wait for LOW portion of frame
    label("low")
    jmp(y_dec, "low")
    
    mov(x, isr)

    wrap()

# Servo using a PWM signal generated from a PIO pin from a Raspberry Pi Pico MCU
class PIOServo(Servo):
    def __init__(self, sm_id, pin, freq=50):
        f = 1_000_000
        self._period_us = f // freq
        
        super(PIOServo, self).__init__(self._period_us)
        
        self._sm = rp2.StateMachine(
            sm_id,
            servo_pio,
            freq=1_000_000,
            set_base=Pin(pin)
        )
        
        self._sm.active(1)
        
    def _update_servo(self, angle):
        
        # Reasonable safety limits
        pulse_us = max(500, min(2500, self._get_duty(angle)))
        
        low_us = self._period_us - pulse_us
        
        # Correct for clock cycles used by servo_pio operations
        high_count = pulse_us - 1
        low_count = low_us - 4
        
        # Pack values into single 32 bit value
        value = high_count | (low_count << 16)
        
        # Push value
        self._sm.put(value)
    
# Main class for initializing and accessing the hardware of the hexapod
class Hexapod:
    def __init__(self, config_file=None):
        
        # Initialize hardware
        if config.HARDWARE == 'V1':
            gpios = [2,3,4, 6,7,8, 10,11,12]
            i2cs = [0,1,2, 4,5,6, 8,9,10]
            
            i2c = I2C(0,scl=Pin(21),sda=Pin(20))
            address = 0x40
            devices = i2c.scan()
            
            ## Setup PCA9685
            self._i2c_write(i2c, address, 0, 0x20)
            self._i2c_write(i2c, address, 0, 0x10)
            self._i2c_write(i2c, address, 0xfe, 0x79)
            self._i2c_write(i2c, address, 0, 0x20)
            time.sleep_us(5)
            
            self.servos = []
            for i in gpios:
                servo = GPIOServo(i)
                self.servos.append(servo)
            
        elif config.HARDWARE == 'V2':
            self.servo_enable = Pin(22, Pin.OUT)
            self.servo_enable.on()
            
            gpios = [0,1,2, 3,4,5, 6,7,8, 9,10,11, 12,13,14, 15]
        
            self.servos = []
            for i in gpios:
                servo = GPIOServo(i)
                self.servos.append(servo)
            
            self.servos.append(PIOServo(0, 27))
            self.servos.append(PIOServo(1, 26))
        
        else:
            err = f"Unknown hardware configuration: {config.HARDWARE}"
            Logger.err(err)
            raise RuntimeError(err)
        
        # Load configuration file if available
        if config_file is not None:
            try:
                with open(config_file, "r") as f:
                    c = json.loads(f.read())
                    for i, servo in enumerate(self.servos):
                        servo.set_min_angle(c["servos"]["min"][i])
                        servo.set_max_angle(c["servos"]["max"][i])
                        servo.set_offset(c["servos"]["offset"][i])
                    
            except:
                info = f"Unable to read config file: {config_file}"
                Logger.info(info)
                print(info)
                
        
    def get_servo(self, index):
        return self.servos[index]
        
    def _i2c_write(self, i2c, addr, reg, data):
        """
        Write bytes to the specified register.
        """
        
        # Construct message
        msg = bytearray()
        msg.append(data)
        
        # Write out message to register
        i2c.writeto_mem(addr, reg, msg)
        
    def save_config(self, filepath):
        out = {"servos":{"min":[], "max":[], "offset":[]}}
        
        for servo in self.servos:
            out["servos"]["min"].append(servo.get_min_angle())
            out["servos"]["max"].append(servo.get_max_angle())
            out["servos"]["offset"].append(servo.get_offset())
        
        with open(filepath, "w") as f:
            f.write(json.dumps(out))
        
