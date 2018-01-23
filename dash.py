import cv2
import time
import numpy as np
import walk
flag = 0

abc =True
y,u,v = 138,101,80

cap = cv2.VideoCapture(3)
width,height = cap.get(3),cap.get(4)
cap.set(3,width/5)
cap.set(4,height/5)

def get_area():
	flag1=False
	t=time.time()
	rec=True	
	while rec:
		rec,img = cap.read()
		img_yuv = cv2.cvtColor(img,cv2.COLOR_BGR2YUV)
	
		blur = cv2.GaussianBlur(img_yuv,(11,11),2)
		ball = cv2.inRange(blur, (np.array([0,u-30,v-30])), (np.array([255,u+30,v+30])))
		im_floodfill = ball.copy()
		h, w = ball.shape[:2]
		mask = np.zeros((h+2, w+2), np.uint8)
		cv2.floodFill(im_floodfill, mask, (0,0), 255)
		fill = cv2.bitwise_and(im_floodfill,im_floodfill,mask = ball)

		
	
		#images,s_contour,hierarchy = cv2.findContours(crop_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

		images,contour,hierarchy = cv2.findContours(fill,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

		cv2.drawContours(img, contour, -1, (0,255,0), 2)

		
		
		
		if len(contour)>0:
			cnt = contour[0]
			area = cv2.contourArea(cnt)
			if area>1000:#(time.time()-t)>3:#
				flag1=True
			if flag1:
				walk.bk_walk()
			else:
				walk.ft_walk()
			
		else:
			pass
		#cv2.imshow("",img)
		#if cv2.waitKey(1)&0xff==27:
		#    break
		

walk.stand()
walk.st_pos()
get_area()
