
class Value:
    def get_value(self):
        pass
    
    def set_value(self, value):
        pass
    
class Angle(Value):
    def __init__(self, angle = 0.0):
        if isinstance(angle, Angle):
            self.__angle = angle.get_value()
        else:
            self.__angle = angle
        
    def get_value(self):
        return self.__angle
    
    def set_value(self, value):
        if isinstance(value, Angle): value = value.get_value()
        self.__angle = value
        
    def __add__(self, other):
        return Angle(self.__angle+other.get_value())
    
    def __sub__(self, other):
        return Angle(self.__angle-other.get_value())
    
    def __mul__(self, other):
        return Angle(self.__angle*other.get_value())
        
        
class Point(Value):
    def __init__(self, value=[0, 0, 0]):
        x = value[0]
        y = value[1]
        z = value[2]
        if isinstance(value[0], Angle): x = value[0].get_value()
        if isinstance(value[1], Angle): y = value[1].get_value()
        if isinstance(value[2], Angle): z = value[2].get_value()
        
        self.__point = [Angle(x), Angle(y), Angle(z)]
        
    def get_value(self):
        return self.__point
    
    def set_value(self, value):
        if isinstance(value, Point):
            value = value.get_value()
        
        self.__point[0].set_value(value[0])
        self.__point[1].set_value(value[1])
        self.__point[2].set_value(value[2])
        
    def __add__(self, other):
        o = other.get_value()
        value = [self.__point[0]+o[0], self.__point[1]+o[1], self.__point[2]+o[2]]
        return Point(value)
    
    def __sub__(self, other):
        o = other.get_value()
        value = [self.__point[0]-o[0], self.__point[1]-o[1], self.__point[2]-o[2]]
        return Point(value)
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            value = [self.__point[0]*Angle(other), self.__point[1]*Angle(other), self.__point[2]*Angle(other)]
        else:
            o = other.get_value()
            value = [self.__point[0]*o[0], self.__point[1]*o[1], self.__point[2]*o[2]]
        
        return Point(value)
    
class Plane():
    def __init__(self, height, x_angle, y_angle):
        self.height = height
        self.x_angle = x_angle
        self.y_angle = y_angle