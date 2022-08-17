import math
from re import X

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

class Pt:
    def __init__(self, x,y):
        self.x = x
        self.y = y

point = Pt(0.5,0.5)

polygon1 = [Pt(0,0), Pt(1,0), Pt(1,1), Pt(0,1)] # clockwise
polygon2 = [Pt(0,0), Pt(0,1), Pt(1,1), Pt(1,0)] # counterclosewise
polygon3 = [Pt(0,0), Pt(3,0), Pt(1,1), Pt(0,3)] # concave

print(polygonInsideJudge(point, polygon1))
print(polygonInsideJudge(point, polygon2))
print(polygonInsideJudge(point, polygon3))