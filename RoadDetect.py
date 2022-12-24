import cv2
import math
import numpy as np
from line import Line
import datetime
from matplotlib import pyplot as plt

# consts
X_CROP=400
Y_CROP=775
HOUGH_LINE_TH=40
MIN_SLOPE=0.275
MAX_SWITCH_LANES_FRAMES=30

class RoadDetect:

    def __init__(self):
        self.__currentFrame = None
        self.__originalFrame = None
        self.__linesDetected = []

        self.__switchLanes=False
        self.__frameCount=MAX_SWITCH_LANES_FRAMES
        self.__switchLaneMessage=None
        
        self.__lastLeftLane = None
        self.__lastLeftLaneSlope = None

        self.__lastRightLane = None
        self.__lastRightLaneSlope = None

        self.__cropped_image = None
        

    def __crop(self):
        self.__currentFrame=self.__currentFrame[Y_CROP:-150,X_CROP:1250]
        self.__cropped_image=self.__currentFrame.copy()
        

    def __turn_gray(self):
        self.__currentFrame=cv2.cvtColor(self.__currentFrame, cv2.COLOR_BGR2GRAY)

    def __median_blur(self):
        self.__currentFrame=cv2.medianBlur(self.__currentFrame, 3)

    def __binary_image(self):
        # 220
        ret,self.__currentFrame = cv2.threshold( self.__currentFrame,220,255,cv2.THRESH_BINARY)
    def __canny(self,min_TH,high_TH):
        cv2.Canny(self.__currentFrame,min_TH,high_TH)
    def __get_new_point(self,x1,x2,y1,y2,max_x_value,slope):
        b=Line.find_b(x1,y1,slope)
        new_y1=140
        new_x1=(new_y1-b)/slope
        new_y2=0
        new_x2=(new_y2-b)/slope
        if new_x2>max_x_value:
            new_x2=max_x_value
            new_y2=new_x2*slope+b

        if new_x1>max_x_value:
            new_x1=max_x_value
            new_y1=new_x1*slope+b

        if new_x2<0:
            new_x2=0
            new_y2=new_x2*slope+b

        if new_x1<0:
            new_x1=0
            new_y1=new_x1*slope+b

        return new_x1,new_y1,new_x2,new_y2

    def __switch_lanes_text(self,res):
        if self.__switchLanes:
            cv2.putText(res, self.__switchLaneMessage,
                            (700,200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5, 2)
            self.__frameCount=self.__frameCount-1
            if self.__frameCount<=0:
                self.__frameCount=MAX_SWITCH_LANES_FRAMES
                self.__switchLanes=False


    def __switch_lanes(self,new_lane):
        """
        Switches lanes based on the slope of the new lane.
        
        This method sets the `__switchLanes` attribute to True if the slope of the new lane is less than or equal to -5 or
        greater than or equal to 5. It also sets the `__switchLaneMessage` attribute to "moving left" or "moving right"
        depending on the slope of the new lane.
        
        Parameters:
        - new_lane (Lane): The new lane to switch to.
        
        Returns:
        None
        """

        if not self.__switchLanes:
            if new_lane.slope()<=-5:
                self.__switchLanes=True
                self.__switchLaneMessage= "moving left"
            elif new_lane.slope()>=5:
                self.__switchLanes=True
                self.__switchLaneMessage= "moving right"



    def __find_lines(self,found_lines,max_x_value):
        cluster_lines=[]
        for line in found_lines:
            x1, y1, x2, y2 = line[0]
            slope=Line.find_slope(x1,y1,x2,y2)
            if slope<-MIN_SLOPE or slope>MIN_SLOPE:
                new_x1,new_y1,new_x2,new_y2=self.__get_new_point(x1,x2,y1,y2,max_x_value,slope)
                degree=Line.find_degree(new_x1,new_y1,new_x2,new_y2)
                #350,50
                if (Line.find_distance(new_x1,new_y1,new_x2,new_y2)<=350 and abs(new_x1-new_x2)<=350 and abs(new_y1-new_y2)>=70 ):
                    if not (min(new_x1,new_x2)<450 and max(new_x1,new_x2)>450):
                         if not (min(new_x1,new_x2)>800 and max(new_x1,new_x2)>800):
                            if not (min(new_x1,new_x2)<200 and max(new_x1,new_x2)<200):
                                current_line=Line(gap=100)
                                current_line.add(new_x1,new_y1,new_x2,new_y2,degree)
                                self.__add_line(cluster_lines,current_line)

        return cluster_lines


    def __best_fit_two_lane(self,res):
        found_left=False
        found_right=False
        if(len(self.__linesDetected)==2):
                for line in self.__linesDetected:
                    if line.slope()<0:
                        self.__switch_lanes(line) 
                        self.__lastLeftLane = line
                    else:
                        self.__switch_lanes(line) 
                        self.__lastRightLane = line
        elif self.__lastLeftLane and self.__lastRightLane:
             for line in self.__linesDetected:
                if found_left and found_right:
                    break
                if not found_left and Line.close_line(self.__lastLeftLane,line):
                    if line.slope()<0:
                        self.__switch_lanes(line) 
                        self.__lastLeftLane=line
                        found_left=True
                if not found_right and Line.close_line(self.__lastRightLane,line):
                    if line.slope()>0:
                        self.__switch_lanes(line) 
                        self.__lastRightLane=line
                        found_right=True


                

   



    def __remove_intersected_lines(self):
        lines_to_remove=set()
        for current_line in self.__linesDetected:
            for search_line in self.__linesDetected:
                if (current_line.slope()<0 and search_line.slope()>0) or (current_line.slope()>0 and search_line.slope()<0):
                    if min(search_line.x1(),search_line.x2())< max(current_line.x1(),current_line.x2())<max(search_line.x1(),search_line.x2()):
                        if(abs(current_line.slope())<abs(search_line.slope())):
                            lines_to_remove.add(current_line)
                        else:
                            lines_to_remove.add(search_line)

        for line in lines_to_remove:
            self.__linesDetected.remove(line)


                    


    def __write_lines(self,res):
        if self.__lastLeftLane:
            res = cv2.line(res, (self.__lastLeftLane.x1()+X_CROP, self.__lastLeftLane.y1()+Y_CROP),
                                (self.__lastLeftLane.x2()+X_CROP, self.__lastLeftLane.y2()+Y_CROP),
                                (0, 0, 255), thickness=10)


        if self.__lastRightLane:
            res = cv2.line(res, (self.__lastRightLane.x1()+X_CROP, self.__lastRightLane.y1()+Y_CROP),
                                (self.__lastRightLane.x2()+X_CROP, self.__lastRightLane.y2()+Y_CROP),
                                (0, 0, 255), thickness=10)






    def __hough_lines_P(self):
        
        lines=cv2.HoughLinesP(self.__currentFrame, 3,  np.pi / 180.0, 25, minLineLength = 50, maxLineGap = 50)
        res =self.__originalFrame.copy()        
        max_x_value=self.__currentFrame.shape[1]
        
        if len(lines)>0 :
            self.__linesDetected=self.__find_lines(lines,max_x_value)
            self.__remove_intersected_lines()
            self.__best_fit_two_lane(res)           
            self.__switch_lanes_text(res)
            self.__write_lines(res)


        return res


    def __hough_lines_P_on_crop(self):
        # 50
        lines=cv2.HoughLinesP(self.__currentFrame, 3,  np.pi / 180.0, 25, minLineLength = 50, maxLineGap = 50)
        res =self.__cropped_image.copy()        
        max_x_value=self.__currentFrame.shape[1]
        if len(lines)>0:
            self.__linesDetected=self.__find_lines(lines,max_x_value)
            self.__remove_intersected_lines()
            self.__best_fit_two_lane(res)
            if self.__lastLeftLane:
                res = cv2.line(res, (self.__lastLeftLane.x1(), self.__lastLeftLane.y1()),
                                    (self.__lastLeftLane.x2(), self.__lastLeftLane.y2()),
                                     (0, 0, 255), thickness=10)
                res=cv2.putText(res, str(self.__lastLeftLane.slope()),
                        (self.__lastLeftLane.x1(), self.__lastLeftLane.y1()), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, 2)
            
            if self.__lastRightLane:
                res = cv2.line(res, (self.__lastRightLane.x1(), self.__lastRightLane.y1()),
                                    (self.__lastRightLane.x2(), self.__lastRightLane.y2()),
                                    (0, 0, 255), thickness=10)
                res=cv2.putText(res,str(self.__lastRightLane.slope()),
                        (self.__lastRightLane.x1(), self.__lastRightLane.y1()), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3, 2)

            # for line in self.__linesDetected:
            #     res = cv2.line(res, (line.x1(), line.y1()), (line.x2(), line.y2()), (0, 0, 255), thickness=10)

        return res


                





    def __add_line(self,all_lines,current_line):
        # if all lines empty add it as new
        if len(all_lines)==0:
            all_lines.append(current_line)
            return

        # find line connected tp the current line
        for line in all_lines:
            if line.is_line_connected(current_line):
                line.add_line(current_line)
                return
            # elif line.continous_line(current_line):
            #     return
        # in case no line is connected add it as new
        all_lines.append(current_line)
        return
         



    def __getVideoWriter(self, sampleImage, outputFileName):    
        height, width, layers = sampleImage.shape
        videoWriter = cv2.VideoWriter(outputFileName, cv2.VideoWriter_fourcc(*"XVID"), 30, (width, height))
        return videoWriter

    def detect(self, videoFileName):
        videoCapture = cv2.VideoCapture(videoFileName)
        videoWriter=None
        while videoCapture.isOpened():
            ret,  self.__originalFrame = videoCapture.read()
            if not videoWriter:
                videoWriter=self.__getVideoWriter(self.__originalFrame,"Lane.avi")
            if ret == True:
                self.__currentFrame= self.__originalFrame.copy()
                self.__crop()
                self.__turn_gray()
                # self.__currentFrame = cv2.convertScaleAbs(self.__currentFrame, alpha=1.0, beta=40)
                self.__median_blur()
                self.__binary_image()
                self.__canny(100,200)
                # self.__originalFrame=self.__hough_lines_P_on_crop()
                lines_image=self.__hough_lines_P()

                self.__originalFrame = cv2.addWeighted(self.__originalFrame, 0.5, lines_image, 0.5, 0)

                
                cv2.imshow('Frame',self.__originalFrame)
                # Get the current video time in seconds



                cv2.imshow('Frame',self.__originalFrame)
                videoWriter.write(self.__originalFrame)

                key = cv2.waitKey(30) & 0xff
                if key == ord('p'):
                    # Wait until the user presses the 'p' key again
                    while True:
                        key2 = cv2.waitKey(30) & 0xff
                        if key2 == ord('p'):
                            break

                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break

        videoCapture.release()
        videoWriter.release()
        cv2.destroyAllWindows()
