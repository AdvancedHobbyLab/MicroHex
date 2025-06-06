import Values
from Logger import Logger

import math

class Leg:
    __s = 30  # length of sholder
    __l = 50  # length of leg
    __f = 82  # length of foot
    
    def __init__(self, shoulder, leg, foot, angle, offset, name=""):
        self.__angle = angle
        self.__offset = offset
        self.__servos = [shoulder, leg, foot]
        self.__point = Values.Point(self.get_center())
        self.__name = name
        
        
    def get_center(self):
        length = self.__s+self.__l
        angle_rad = self.__angle/180*math.pi
        center = [self.__offset[0]+math.cos(angle_rad)*length,
                  self.__offset[1]+math.sin(angle_rad)*length,
                  self.__f]
        return center
    
    def get_point(self):
        return self.__point
        
    def update(self, elapsed):
        x = self.__point.get_value()[0].get_value()
        y = self.__point.get_value()[1].get_value()
        z = self.__point.get_value()[2].get_value()
        
        x -= self.__offset[0]
        y -= self.__offset[1]
        z -= self.__offset[2]
        
        s = 30  # length of sholder
        l = 50  # length of leg
        f = 82  # length of foot
        
        try:
            a = math.sqrt(x*x + y*y) - s
            
            b = math.sqrt(z*z + a*a)
            
            F = math.acos((l*l + f*f - b*b)/(2*l*f))
            F = F * (180/math.pi)
            
            if z == 0:
                height_angle = math.pi/2
            else:
                height_angle = math.atan(a/z)
            L = math.acos((l*l + b*b - f*f)/(2*l*b)) + height_angle
            L = L * (180/math.pi)
            
            if x == 0:
                S = math.pi/2
            else:
                S = math.atan(y/x)
            S = S * (180/math.pi) 
            
            if x < 0:
                S = S-(self.__angle-180)
                S *= -1
            else:
                S = S-self.__angle
            S += 90
            
            self.__servos[0].set_angle(S)
            self.__servos[1].set_angle(L)
            self.__servos[2].set_angle(F)
        except Exception as e:
            Logger.err(f"IK error (Leg: {self.__name}): {str(e)}")
        #print()
        #print(f"S: {S}")
        #print(f"L: {L}")
        #print(f"F: {F}")