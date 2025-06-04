from machine import Pin, PWM, I2C
import time
import ustruct
import json

gpios = [2,3,4, 6,7,8, 10,11,12]
i2cs = [0,1,2, 4,5,6, 8,9,10]

class ServoInterface:
    
    def set_angle(self, angle):
        pass
    
    def get_angle(self):
        pass
    
class FlippedServo(ServoInterface):
    def __init__(self, servo):
        self.__servo = servo
        
    def set_angle(self, angle):
        self.__servo.set_angle(180-angle)
        
    def get_angle(self):
        return 180-self.__servo.get_angle()

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
    
class GPIOServo(Servo):
    def __init__(self, pin_num):
        super(GPIOServo, self).__init__(65535)
        self.pwm = PWM(Pin(pin_num))
        self.pwm.freq(50)
        
    def _update_servo(self, angle):
        self.pwm.duty_u16(self._get_duty(angle))
        pass
    
    def release(self):
        self.pwm.duty_u16(0)
    
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
        pass
    
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
    
class Hexapod:
    def __init__(self, config=None):
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
            
        for i in i2cs:
            servo = I2CServo(i2c, address, i)
            self.servos.append(servo)
        
        if config is not None:
            try:
                with open(config, "r") as f:
                    c = json.loads(f.read())
                    for i, servo in enumerate(self.servos):
                        servo.set_min_angle(c["servos"]["min"][i])
                        servo.set_max_angle(c["servos"]["max"][i])
                        servo.set_offset(c["servos"]["offset"][i])
                    
            except:
                print(f"Unable to read config file: {config}")
                
        
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
        
