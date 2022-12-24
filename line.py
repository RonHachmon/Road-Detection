import math
import numpy as np
class Line:
    
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