#!/usr/bin/env python

import pypot.dynamixel
import time
import itertools
import numpy as np
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from math import pi,atan,sin,cos,degrees
#import rospy
#from std_msgs.msg import String
flag = 0
#ang=(91.38, 87.34, 6.81, -47.16, 79.87, -80.31, -94.9, 124.18, -0.31, -2.68, 11.47, -12.7, -15.78, 14.55, -8.48, 3.91, -0.13, -4.26, 46.99)
darwin = {1: 90, 2: -90, 3: 67.5, 4: -67.5, 7: 45, 8: -45, 9: 'i', 10: 'i', 13: 'i', 14: 'i', 17: 'i', 18: 'i'}
abmath = {11: 15, 12: -15, 13: -10, 14: 10, 15: -5, 16: 5}
hand = {5: 60, 6: -60}

path1 = "/home/akarsh/Python/Walk/data.xml"
path2 = "/home/akarsh/Python/Walk/newdata.xml"
abc =True
y,u,v = 0,142,56

cap = cv2.VideoCapture(1)

def get_area():

	rec=True	
	while rec:
		rec,img = cap.read()
		img_yuv = cv2.cvtColor(img,cv2.COLOR_BGR2YUV)
		#out.write(img)
	
		blur = cv2.GaussianBlur(img_yuv,(11,11),2)
		ball = cv2.inRange(blur, (np.array([0,u-30,v-30])), (np.array([255,u+30,v+30])))
		im_floodfill = ball.copy()
		h, w = ball.shape[:2]
		mask = np.zeros((h+2, w+2), np.uint8)
		cv2.floodFill(im_floodfill, mask, (0,0), 255)
		fill = cv2.bitwise_and(im_floodfill,im_floodfill,mask = ball)

		if cv2.waitKey(25)&0xff==27:
		    break

		cv2.rectangle(img, (310,230), (330,250), (255,255,255),2)
		crop_img = fill[230:250, 310:330]
	
		images,s_contour,hierarchy = cv2.findContours(crop_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

		images,contour,hierarchy = cv2.findContours(fill,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

		cv2.drawContours(img, contour, -1, (0,255,0), 2)

		cv2.imshow("",img)
		#cv2.imshow("mask",im_floodfill)
		
		t=time.time()
		if len(contour)>=1:
			cnt = contour[0]
			area = cv2.contourArea(cnt)
			return area
		else:
			return 0
		

class Dynamixel(object) :
	def __init__(self) :
		ports = pypot.dynamixel.get_available_ports()
		if not ports :
			raise IOError("port bhakchodi pel rahe hain")

		print "Is port se judna hai",ports[0]

		self.dxl = pypot.dynamixel.DxlIO(ports[0])
		self.ids = self.dxl.scan(range(25))
		print self.ids
		self.dxl.enable_torque(self.ids)
		if len(self.ids)<20 :
			raise RuntimeError("kuch motor bhakchodi pel rahe hain")
		self.dxl.set_moving_speed(dict(zip(self.ids,itertools.repeat(100))))


	def setSpeed(self,speed,ids) :
		self.dxl.set_moving_speed(dict(zip(ids,itertools.repeat(speed))))

	def setPos(self,pose) :
		pos = {ids:angle for ids,angle in pose.items()}
		self.dxl.set_goal_position(pos)
		#print pos

	def listWrite(self,list) :
		pos = dict(zip(self.ids,list))
		self.dxl.set_goal_position(pos)

	def dictWrite(self,dicti) :
		
		self.dxl.set_goal_position(dicti)

	def angleWrite(self,ids,pose) :
		self.dxl.set_goal_position({ids:pose})
		
	def returnPos(self,ids) :

		return self.dxl.get_present_position((ids,))	



class XML(object) :
	def __init__(self,file) :
		try :
			tree = ET.parse(file)
			self.root = tree.getroot()
		except :
			raise RuntimeError("File nahi mil rahi")

	def parse(self,motion) :
		find = "PageRoot/Page[@name='" +motion+ "']/steps/step"
		steps = [x for x in self.root.findall(find)]
		p_frame = str()
		p_pose = str()
		for step in steps :
			Walk(step.attrib['frame'],step.attrib['pose'],p_frame,p_pose)
			p_frame = step.attrib['frame']
			p_pose = step.attrib['pose']
			
	
xml1 = XML(path1)
xml2 = XML(path2)
x=Dynamixel()

class Walk(object) :
	def __init__(self,frame,pose,p_frame,p_pose) :
		self.frame = int(frame)
		self.begin = {}
		self.end = {}
		if not(p_pose) :
			self.frame_diff = 1
			p_pose = pose
		else :
			self.frame_diff = self.frame-int(p_frame) 

		for ids,pos in enumerate(map(float,p_pose.split())) :
			self.end[ids+1]=pos	

		for ids,pos in enumerate(map(float,pose.split())) :
			self.begin[ids+1]=pos
		
		self.set(offsets=[darwin,hand])

	def Offset(self,offset) :
		
		for key in offset.keys() :
			if offset[key] == 'i' :
				self.begin[key] = -self.begin[key]
				self.end[key] = -self.end[key]
			else :
				self.begin[key] += offset[key]
				self.end[key] += offset[key]
		
		

	def set(self,offsets=[]) :
		for offset in offsets :
			self.Offset(offset)
		self.motion() 

	def motion(self) :
		#print self.begin
		#print self.end
		write=[]
		ids=[]
		for key in self.end.keys() :
			linp=np.linspace(self.end[key],self.begin[key],self.frame_diff)
			write.append(linp)
			ids.append(key)	

		#print "out"
		for pose in zip(*write) :
			#print "in"
			x.setPos(dict(zip(ids,pose)))
			time.sleep(0.0017)

						

def walk() :
	xml=xml1
	w1 = xml.parse("32 F_S_L")
	time.sleep(0.01)
	w2 = xml.parse("33 ")
	time.sleep(0.01)
	t0=time.time()
	while True:
		if get_area()>25000:
			xml=xml2
		w3 = xml.parse("38 F_M_R")
		time.sleep(0.01)	
		w4 = xml.parse("39 ")
		time.sleep(0.01)
		w5 = xml.parse("36 F_M_L")
		time.sleep(0.01)
		w6 = xml.parse("37 ")
		time.sleep(0.01)
	

if __name__=="__main__" :
	m_20 = 90
	x.angleWrite(19,0)
	x.angleWrite(20,m_20)
	balance = xml1.parse("152 Balance")
	raw_input("Proceed?")

	walk()
