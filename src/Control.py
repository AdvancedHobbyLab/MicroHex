import Hardware as hw
import Legs
import Values

import time
import math

class EventHandler:
    def update(self, elapsed):
        pass
    
class EventGroup(EventHandler):
    def __init__(self, handlers):
        self.__handlers = handlers
        
    def update(self, elapsed):
        for handler in self.__handlers:
            handler.update(elapsed)

class Animator(EventHandler):
    def __init__(self, dest):
        self.dest_value = dest
        
        self.target_value = None
        self.start_value = None
        self.remaining_delta = 0
        self.target_delta = 0
        self.curve = "linear"
        
        self.counts = 0
        
    def animate(self, value, delta, curve="linear"):
        self.target_value = value
        self.start_value = Values.Point(self.dest_value.get_value())
        self.target_delta = delta*1000000 # in micro seconds
        self.remaining_delta = self.target_delta
        self.curve = curve
        
    def animation_done(self):
        pass
    
    def update(self, elapsed):
        if self.target_delta == 0:
            return
        
        self.remaining_delta -= elapsed
        if self.remaining_delta <= 0:
            remaining = self.remaining_delta
            
            self.remaining_delta = 0
            self.target_delta = 0
            
            self.dest_value.set_value(self.target_value)
            
            self.animation_done()
            
            if self.remaining_delta != 0:
                self.remaining_delta -= elapsed
                self.__update_animation()
        else:
            self.__update_animation()
            
    def __update_animation(self):
        ratio = (self.target_delta - self.remaining_delta)/self.target_delta
        if self.curve == "smooth":
            if ratio < .5:
                ratio = ratio*2
                ratio = (ratio*ratio)/2
            else:
                ratio = (ratio-.5)*-2+1
                ratio = (ratio*ratio)*-1
                ratio = ratio/2+1
        elif self.curve == "jerk":
            ratio = ratio*-1+1
            ratio = ratio*ratio
            ratio = ratio*-1+1
        elif self.curve == "ramp":
            ratio = ratio*ratio
            
        
        new_value = self.start_value+(self.target_value-self.start_value)*ratio
        self.dest_value.set_value(new_value)

class LegAnimator(Animator):
    def __init__(self, leg, state, cycle_order=0, plane=Values.Plane(0, 0, 0)):
        super().__init__(leg.get_point())
        
        self.leg = leg
        self.control_state = state
        self.plane = plane
        self.order = cycle_order
        
        self.center = leg.get_center()
        
        self.state = 0
        self.animate(Values.Point(self.center), .5+cycle_order*.25)
        
    def animation_done(self):
        delay = .25
        
        forward = self.control_state["direction"][0]
        left = self.control_state["direction"][1]
        rotate = self.control_state["direction"][2]
        if rotate != 0:
            forward = rotate
            if self.center[0] < 0:
                forward *= -1
        distance = math.sqrt(forward*forward + left*left)
        if distance != 0:
            forward = forward / distance * -40
            left = left / distance * 40
        
        if self.state == 0:
            lift = 0
            if distance != 0:
                lift = -40
            self.state = 1
            target = [self.center[0]+left, self.center[1]+forward, self.center[2]+lift]
            self.animate(Values.Point(target), delay/3)
        elif self.state == 1:
            lift = 0
            if distance != 0:
                lift = -40
            self.state = 2
            target = [self.center[0]+left*-1, self.center[1]+forward*-1, self.center[2]+lift]
            self.animate(Values.Point(target), delay/3)
            #print(target)
        elif self.state == 2:
            self.state = 3
            target = [self.center[0]+left*-1, self.center[1]+forward*-1, self.center[2]]
            self.animate(Values.Point(target), delay/3)
        elif self.state == 3:
            self.state = 0
            target = [self.center[0]+left, self.center[1]+forward, self.center[2]]
            self.animate(Values.Point(target), delay*5)
            
    def update(self, elapsed):
        super().update(elapsed*self.control_state["speed"])
        
        
        if self.state == 1 or self.state == 2:
            lift_height = 0
        else:
            direction = self.control_state["direction"]
            if direction[0] == 0 and direction[1] == 0:
                lift_height = 0
            else:
                lift_height = 40
        
        x_angle = self.plane.x_angle/180*math.pi
        y_angle = self.plane.y_angle/180*math.pi
        point = self.leg.get_point().get_value()
        point_x = point[0].get_value()
        point_y = point[1].get_value()
        height = self.plane.height + point_x*math.tan(x_angle) + point_y*math.tan(y_angle)
        point[2].set_value(point[2].get_value()+height)

class ScriptAnimator(Animator):
    def __init__(self, dest):
        super().__init__(dest)
        
        self.__index = -1
        self.__script = []
        
    def push_animation(self, value, delta, curve="linear"):
        self.__script.append((value, delta, curve))
    
    def start_animation(self):
        if len(self.__script) == 0: return
        
        self.__index = 0
        self.animation_done()
    
    def clear_animation(self):
        self.__index = -1
        self.__script = []
        
    def animation_done(self):
        value, delta, curve = self.__script[self.__index]
        self.animate(value, delta, curve)
        
        self.__index += 1
        if self.__index >= len(self.__script):
            self.__index = 0
        

class ScriptHandler(EventHandler):
    def __init__(self, legs):
        self.centers = []
        self.legs = []
        for leg in legs:
            self.centers.append(leg.get_center())
            self.legs.append(ScriptAnimator(leg.get_point()))
        
    def start(self):
        for leg in self.legs:
            leg.clear_animation()
        
        center = self.centers[0]
        leg = self.legs[0]
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0]-80, center[1], center[2]-80]), .25)
        leg.push_animation(Values.Point([center[0]-80, center[1], center[2]-80]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]+40]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        center = self.centers[1]
        leg = self.legs[1]
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]+40]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0]-80, center[1], center[2]-80]), .25)
        leg.push_animation(Values.Point([center[0]-80, center[1], center[2]-80]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        center = self.centers[2]
        leg = self.legs[2]
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0]-80, center[1], center[2]-80]), .25)
        leg.push_animation(Values.Point([center[0]-80, center[1], center[2]-80]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]+40]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        center = self.centers[3]
        leg = self.legs[3]
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]+40]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0]+80, center[1], center[2]-80]), .25)
        leg.push_animation(Values.Point([center[0]+80, center[1], center[2]-80]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        center = self.centers[4]
        leg = self.legs[4]
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0]+80, center[1], center[2]-80]), .25)
        leg.push_animation(Values.Point([center[0]+80, center[1], center[2]-80]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]+40]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        center = self.centers[5]
        leg = self.legs[5]
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]+40]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        leg.push_animation(Values.Point([center[0]+80, center[1], center[2]-80]), .25)
        leg.push_animation(Values.Point([center[0]+80, center[1], center[2]-80]), .5)
        leg.push_animation(Values.Point([center[0], center[1], center[2]]), .25)
        
        for leg in self.legs:
            leg.start_animation()
        
    def update(self, elapsed):
        for leg in self.legs:
            leg.update(elapsed)

class Control:
    def __init__(self):
        self.last_time = time.ticks_us()
        self.start_time = time.time()
        
        self.hexapod = hw.Hexapod(config="config.json")
        
        self.stance = 0
        
        self.state = {"action": 1, "direction":[0,0,0], "speed":1.0}
        
        self.handlers = []
        
        for i in range(18):
            self.hexapod.get_servo(i).set_angle(90)
            
        #self.handlers.append(TestSequence(self.hexapod.get_servo(15)))
        
        self.legs = [
            Legs.Leg(self.hexapod.get_servo(2), hw.FlippedServo(self.hexapod.get_servo(1)), self.hexapod.get_servo(0), 135, [-31, 60, 0]),  # Front Left
            Legs.Leg(self.hexapod.get_servo(5), hw.FlippedServo(self.hexapod.get_servo(4)), self.hexapod.get_servo(3), 180, [-40, 0, 0]),  # Mid Left
            Legs.Leg(self.hexapod.get_servo(8), hw.FlippedServo(self.hexapod.get_servo(7)), self.hexapod.get_servo(6), 225, [-31, -60, 0]),  # Back Left
            
            Legs.Leg(hw.FlippedServo(self.hexapod.get_servo(11)), self.hexapod.get_servo(10), hw.FlippedServo(self.hexapod.get_servo(9)), -45, [31, -60, 0]),  # Back Right
            Legs.Leg(hw.FlippedServo(self.hexapod.get_servo(14)), self.hexapod.get_servo(13), hw.FlippedServo(self.hexapod.get_servo(12)), 0, [40, 0, 0]), # Mid Right
            Legs.Leg(hw.FlippedServo(self.hexapod.get_servo(17)), self.hexapod.get_servo(16), hw.FlippedServo(self.hexapod.get_servo(15)), 45, [31, 60, 0])  # Front Right
        ]
        self.ik_handler = EventGroup(self.legs)
        self.handlers.append(self.ik_handler)
        
        self.plane = Values.Plane(0, 0, 0)
        events = [
            LegAnimator(self.legs[0], self.state, 0, self.plane),
            LegAnimator(self.legs[1], self.state, 3, self.plane),
            LegAnimator(self.legs[2], self.state, 4, self.plane),
            
            LegAnimator(self.legs[3], self.state, 1, self.plane),
            LegAnimator(self.legs[4], self.state, 2, self.plane),
            LegAnimator(self.legs[5], self.state, 5, self.plane)
        ]
        self.walking_gait = EventGroup(events)
        self.handlers.append(self.walking_gait)
        
        self.script_handler = ScriptHandler(self.legs)
    
    def get_state(self):
        return self.state
    
    def get_servo(self, index):
        return self.hexapod.get_servo(index)
    
    def save_config(self):
        self.hexapod.save_config("config.json")
    
    def get_uptime(self):
        return time.time()-self.start_time
    
    def set_plane(self, height, x_angle, y_angle):
        self.plane.height = height
        self.plane.x_angle = x_angle
        self.plane.y_angle = y_angle
    
    ## Increment servo positions
    def step(self):
        new_time = time.ticks_us()
        diff = time.ticks_diff(new_time, self.last_time)
        self.last_time = new_time
        
        for handler in self.handlers:
            handler.update(diff)
    
    def manual(self):
        if self.state["action"] == 0:
            return
        
        print("Switching to manual")
        
        if self.state["action"] == 1:
            self.handlers.remove(self.walking_gait)
        if self.state["action"] == 2:
            self.handlers.remove(self.script_handler)
        
        self.state["action"] = 0
        
        self.handlers.remove(self.ik_handler)
        
    
    def script(self):
        if self.state["action"] == 2:
            return
            
        print("Switching to Scripted Movement")
        if self.state["action"] == 0:
            self.handlers.append(self.ik_handler)
        elif self.state["action"] == 1:
            self.handlers.remove(self.walking_gait)
        
        self.state["action"] = 2
        
        self.handlers.append(self.script_handler)
        self.script_handler.start()
                
    def auto(self):
        if self.state["action"] == 1:
            return;
        
        print("Switching to Auto")
        if self.state["action"] == 0:
            self.handlers.append(self.ik_handler)
        if self.state["action"] == 2:
            self.handlers.remove(self.script_handler)
        
        self.state["action"] = 1
        
        self.handlers.append(self.walking_gait)
        
    def move(self, fwd, left, rotate=0):
        if self.state["direction"][0] == fwd and self.state["direction"][1] == left and self.state["direction"][2] == rotate:
            return
        
        self.state["direction"][0] = fwd
        self.state["direction"][1] = left
        self.state["direction"][2] = rotate
        
    def set_speed(self, speed):
        if self.state["speed"] == speed: return;
        
        self.state["speed"] = speed
        
