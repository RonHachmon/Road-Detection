import math
import numpy as np
class Line:
    def __init__(self,gap=20):
        self.__x1 = 0
        self.__y1 = 0
        self.__x2 = 0
        self.__y2 = 0
        self.__slope = 0
        self.__degree = 0
        self.__gap = gap
        self.__counter = 0

    def is_connected(self,x1,y1,x2,y2): 
        # print("in line 1")
        return self.__distance_from_point_one(x1,y1) and self.__distance_from_point_two(x2,y2)
        
    def is_line_connected(self,line): 
        return self.is_connected(line.x1(),line.y1(),line.x2(),line.y2())

    def __distance_from_point_one(self,x1,y1):
        value=(((x1 - self.x1())**2 + (y1 - self.y1())**2)**0.5)
        if value<self.__gap:
            return True
        False


    def __distance_from_point_two(self,x2,y2):
        value=((x2 - self.x2())**2 + (y2 - self.y2())**2)**0.5
        if value<self.__gap:
            return True
        return False


    def add(self,x1,y1,x2,y2,degree):
        self.__x1 += x1
        self.__y1 += y1
        self.__x2 += x2
        self.__y2 += y2
        self.__degree +=degree
        self.__counter +=1
        self.__slope=Line.find_slope(self.x1(),self.y1(),self.x2(),self.y2())

    def continous_line(self,line):
        is_continous_line=False
        if abs(line.degree()-self.__degree)<=10:
            if   self.__distance_from_point_one(line.x2(),line.y2()):
                self.__x1 = line.x1()
                self.__y1 = line.y1()
                is_continous_line = True

            if self.__distance_from_point_two(line.x1(),line.y1()):
                self.__x2 = line.x2()
                self.__y2 = line.y2()
                is_continous_line = True
        return is_continous_line



    def add_line(self,line):
        self.add(line.x1(),line.y1(),line.x2(),line.y2(),line.degree())


    def x1(self):
        return int(self.__x1/self.__counter)

    def slope(self):
        return self.__slope

    def x2(self):
        return int(self.__x2/self.__counter)

    def y1(self):
        return int(self.__y1/self.__counter)

    def y2(self):
        return int(self.__y2/self.__counter)

    def degree(self):
        return int(self.__degree/self.__counter)

    @staticmethod
    def find_slope(x1,y1,x2,y2):
        if x2 - x1==0:
            return 0.0000001
        return (y2 - y1)/(x2 - x1)

    @staticmethod
    def find_b(x1,y1,slope):
        return y1-(x1*slope)

    @staticmethod
    def find_degree(x1,y1,x2,y2):
        if y2 - y1==0:
            return 90
        if x2 - x1==0:
            return 180
        m=(y2 - y1)/(x2 - x1)
        return math.atan(m)*180/np.pi

    @staticmethod
    def find_distance(x1,y1,x2,y2):
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    @staticmethod
    def close_line(line1,line2):
        if abs(line1.x1()-line2.x1()<=10) and abs(line1.y1()-line2.y1()<=10):
             if abs(line1.x2()-line2.x2()<=10) and abs(line1.y2()-line2.y2()<=10):
                    return True
        return False