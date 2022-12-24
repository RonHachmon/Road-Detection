# %% [markdown]
# ## Find lane



# %%

import Line
from ClusterLine import ClusterLine
import math 
from matplotlib import pyplot as plt
import cv2
import numpy as np
figsize = (10, 10)
MIN_LINE_LENGTH=50
FRAME="frame2"

def radians_to_degree(theta):
    return  theta*180/np.pi

def find_slope(x1,y1,x2,y2):
    if x2 - x1==0:
        return 0.0000001
    return (y2 - y1)/(x2 - x1)

def find_b(x1,y1,slope):
    return y1-(x1*slope)


def find_degree(x1,y1,x2,y2):
    if y2 - y1==0:
        return 90
    if x2 - x1==0:
        return 180
    m=(y2 - y1)/(x2 - x1)
    return math.atan(m)*180/np.pi





def hough_lines_P(im, canny_im, x_offset=0, y_offset=0):

    cluster_lines=[]
    lines=cv2.HoughLinesP(canny_im, 3,  np.pi / 180.0, 25, minLineLength = MIN_LINE_LENGTH, maxLineGap = 50)
    res = im.copy()
    max_x_value=canny_im.shape[1]


    for line in lines:
         x1, y1, x2, y2 = line[0]
        #  print("x1 ,y1 ",x1,y1)
        #  print("x2 ,y2 ",x2,y2)
      
         slope=find_slope(x1,y1,x2,y2)
        #  print("slope ",slope)
        #  print("_____")
         if slope<-0.3 or slope>0.3:
            b=find_b(x1,y1,slope)
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


            degree=find_degree(new_x1,new_y1,new_x2,new_y2)
            if degree<90 or degree>95:
                current_line=ClusterLine(gap=100)
                # current_line.add(x1,y1,x2,y2,degree)
                current_line.add(new_x1,new_y1,new_x2,new_y2,degree)
                add_line(cluster_lines,current_line)
         







    for line in cluster_lines:
        print("slope",line.slope())
        print("x1 ,y1 ",line.x1(),line.y1())
        print("x2 ,y2 ",line.x2(),line.y2())
        print("_____")
        res = cv2.line(res, (line.x1()+x_offset, line.y1()+y_offset), (line.x2()+x_offset, line.y2()+y_offset), (0, 0, 255), thickness=10)

     
    return res


def add_line(all_lines,current_line):
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


def diplay_image(im,title):
    plt.figure(figsize=figsize)
    plt.imshow(im)
    plt.title(title)
    plt.show()






# LaneDetection().detect("lane detection/Road.mp4") 
# %% [markdown]
# ## open frame


im3 = cv2.imread("C:\\Users\\97254\\Desktop\\Computer Vision\\project_env\\lane detection\\frames\\"+FRAME+".jpg")
im3 = cv2.cvtColor(im3, cv2.COLOR_BGR2RGB)



plt.figure(figsize=figsize)
plt.imshow(im3, cmap='gray', vmin=0, vmax=255)
plt.title("original image")
plt.show()

# %% [markdown]
# ## cropped image

cropped_im = im3[775:-165,400:1400]
cropped_im=cropped_im
diplay_image(cropped_im,"cropped image")

# %% [markdown]
# ## gray image

im_gray = cv2.cvtColor(cropped_im, cv2.COLOR_BGR2GRAY)

plt.figure(figsize=figsize)
plt.imshow(im_gray, cmap="gray", vmin=0, vmax=255)
plt.title("gray")
plt.show()

# %% [markdown]
# ## contrast image

equalized = cv2.convertScaleAbs(im_gray, alpha=1.0, beta=40)

plt.figure(figsize=figsize)
plt.imshow(equalized, cmap="gray", vmin=0, vmax=255)
plt.title("gray")
plt.show()
# %% [markdown]
# ## binary image 
ret,im_th = cv2.threshold(equalized,200,255,cv2.THRESH_BINARY)
plt.figure(figsize=(20,20))
plt.imshow(im_th,cmap="gray")
plt.show()

# %% [markdown]
# ## median image
# blur_im = cv2.GaussianBlur(im_th, (7, 7),sigmaX=10,sigmaY=10)
blur_im = cv2.medianBlur(im_th, 3)
plt.figure(figsize=(20,20))
plt.imshow(blur_im,cmap="gray")
plt.show()



# %% [markdown]
# ##Canny
mag_im = cv2.Canny(blur_im,100,200)

diplay_image(mag_im,"edge image")



# %% [markdown]
# ## hough lines P cropped image
hough_image=hough_lines_P(cropped_im,mag_im)
plt.figure(figsize=figsize)
plt.imshow(hough_image)
plt.title("hough lines")
plt.show()

# %% [markdown]
# ## hough lines P 
hough_image=hough_lines_P(im3,mag_im,400,775)
plt.figure(figsize=figsize)
plt.imshow(hough_image)
plt.title("hough lines")
plt.show()

# %%