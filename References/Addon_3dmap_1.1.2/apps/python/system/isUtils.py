##############################################################
# APPS Utilities Module
# ver. 1.2.6 / 7.Oct.2020
# Innovare Studio Inc. / D.Tsukamoto
#############################################################

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
os.environ['PATH'] = os.environ['PATH'] + ";."

import configparser
import math
from ctypes import *
from ctypes.wintypes import MAX_PATH


class vec2:
	def __init__(self, x=0, y=False):
		if isinstance(y, bool): y = x
		self.x = float(x)
		self.y = float(y)
	
	def add(self, val):
		if not isinstance(val, vec2): val = vec2(val, val)
		self.x += val.x
		self.y += val.y
	
	def mult(self, val):
		if not isinstance(val, vec2): val = vec2(val, val)
		self.x *= val.x
		self.y *= val.y
	
	def rotate(self, angle):
		base = vec2(self.x, self.y)
		self.x = base.x * math.cos(angle * math.pi / 180) - base.y * math.sin(angle * math.pi / 180)
		self.y = base.x * math.sin(angle * math.pi / 180) + base.y * math.cos(angle * math.pi / 180)
	
	def clone(self):
		return vec2(self.x, self.y)


class vecLine:
	def __init__(self, p1=vec2(), p2=vec2()):
		self.points = [p1, p2]
	
	def add(self, val):
		for point in self.points:
			point.add(val)
	
	def mult(self, val):
		for point in self.points:
			point.mult(val)
	
	def rotate(self, angle):
		for point in self.points:
			point.rotate(angle)
	
	def clone(self):
		return vecLine(self.points[0].clone(), self.points[1].clone())


class vecTriangle:
	def __init__(self, p1=vec2(), p2=vec2(), p3=vec2()):
		self.points = [p1, p2, p3]
	
	def add(self, val):
		for point in self.points:
			point.add(val)
	
	def mult(self, val):
		for point in self.points:
			point.mult(val)
	
	def rotate(self, angle):
		for point in self.points:
			point.rotate(angle)
	
	def scale(self, val):
		x = (self.points[0].x + self.points[1].x + self.points[2].x) / 3
		y = (self.points[0].y + self.points[1].y + self.points[2].y) / 3
		for point in self.points:
			point.x -= x
			point.y -= y
			point.mult(val)
			point.x += x
			point.y += y
	
	def clone(self):
		return vecQuad(self.points[0].clone(), self.points[1].clone(), self.points[2].clone())


class vecQuad:
	def __init__(self, p1=vec2(), p2=vec2(), p3=vec2(), p4=vec2()):
		self.points = [p1, p2, p3, p4]
	
	def add(self, val):
		for point in self.points:
			point.add(val)
	
	def mult(self, val):
		for point in self.points:
			point.mult(val)
	
	def rotate(self, angle):
		for point in self.points:
			point.rotate(angle)
	
	def scale(self, val):
		x = (self.points[0].x + self.points[1].x + self.points[2].x + self.points[3].x) / 4
		y = (self.points[0].y + self.points[1].y + self.points[2].y + self.points[3].y) / 4
		for point in self.points:
			point.x -= x
			point.y -= y
			point.mult(val)
			point.x += x
			point.y += y
	
	def clone(self):
		return vecQuad(self.points[0].clone(), self.points[1].clone(), self.points[2].clone(), self.points[3].clone())


def distanceVertex(p1, p2):
	return math.pow((p2.x - p1.x) * (p2.x - p1.x) + (p2.y - p1.y) * (p2.y - p1.y), 0.5)


def crossVector(vl, vr):
	return vl.x * vr.y - vl.y * vr.x


def distancePointByLineLegacy(point, line):
	AB = vec2()
	AP = vec2()
	AB.x = line.points[1].x - line.points[0].x
	AB.y = line.points[1].y - line.points[0].y
	AP.x = point.x - line.points[0].x
	AP.y = point.y - line.points[0].y
	D = abs(crossVector(AB, AP))
	L = distanceVertex(line.points[0], line.points[1])
	H = D / L
	return H


def distancePointByLine(point, line):
	AB = vec2()
	AB.x = line.points[1].x - line.points[0].x
	AB.y = line.points[1].y - line.points[0].y
	AP = vec2()
	AP.x = AB.x * AB.x
	AP.y = AB.y * AB.y
	R = AP.x + AP.y
	T = -(AB.x * (line.points[0].x - point.x) + AB.y * (line.points[0].y - point.y))
	if T < 0:
		return (line.points[0].x - point.x) * (line.points[0].x - point.x) + (line.points[0].y - point.y) * (line.points[0].y - point.y)
	if T > R:
		return (line.points[1].x - point.x) * (line.points[1].x - point.x) + (line.points[1].y - point.y) * (line.points[1].y - point.y)
	
	F = AB.x * (line.points[0].y - point.y) - AB.y * (line.points[0].x - point.x)
	return F * F / R


def slideVec2(point, angle=0, offset=0):
	x = point.x + math.cos(angle * math.pi / 180) * offset
	y = point.y - math.sin(angle * math.pi / 180) * offset
	return vec2(x, y)


def polygonInsideJudge(point, polygon):
	angle = 0
	for i in range(0, len(polygon) - 1):
		Ax = polygon[i].x - point.x
		Ay = polygon[i].y - point.y
		Bx = polygon[i + 1].x - point.x
		By = polygon[i + 1].y - point.y
		AvB = Ax * Bx + Ay * By
		AxB = Ax * By - Ay * Bx
		angle += math.atan2(AxB, AvB)
	return math.degrees(math.fabs(angle)) - 180 > 0


def triangleCenter(triangle):
	x = (triangle.points[0].x + triangle.points[1].x + triangle.points[2].x) / 3
	y = (triangle.points[0].y + triangle.points[1].y + triangle.points[2].y) / 3
	return vec2(x, y)


def triangleArea(triangle):
	return abs((triangle.points[1].x - triangle.points[0].x) * (triangle.points[2].y - triangle.points[0].y) -
	           (triangle.points[1].y - triangle.points[0].y) * (triangle.points[2].x - triangle.points[0].x))


def polygonCenter(polygon):
	s = gx = gy = 0
	for i in range(2, len(polygon)):
		t = vecTriangle(polygon[0], polygon[i - 1], polygon[i])
		sp = triangleArea(t)
		pt = triangleCenter(t)
		gx += sp * pt.x
		gy += sp * pt.y
		s += sp
	return vec2(gx / s, gy / s)


def getACConfig(filename):
	buf = create_unicode_buffer(MAX_PATH + 1)
	
	if windll.shell32.SHGetSpecialFolderPathW(None, buf, 0x0005, False):
		docPath = buf.value
	else:
		docPath = os.path.expanduser("~/Documents")
	
	config_sys = configparser.ConfigParser()
	config_sys.read("system/cfg/inireaderdocuments.ini")
	bypass = config_sys.getint("FOLDER", "BYPASS_DOCUMENT_FOLDER")
	program_name = config_sys.get("FOLDER", "PROGRAM_NAME")
	if bypass == 1:
		docPath = config_sys.get("FOLDER", "CUSTOM_PATH")
	
	config = configparser.ConfigParser()
	config.read(docPath + "/" + program_name + "/" + filename)
	return config
