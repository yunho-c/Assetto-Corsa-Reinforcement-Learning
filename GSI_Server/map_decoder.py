import struct
import math
from matplotlib import pyplot as plt
import numpy as np

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

def slideVec2(point, angle=0, offset=0):
	x = point.x + math.cos(angle * math.pi / 180) * offset
	y = point.y - math.sin(angle * math.pi / 180) * offset
	return vec2(x, y)

class trackDetailNode:
	def __init__(self, rawIdeal, prevRawIdeal, rawDetail):
		self.id = rawIdeal[4]
		self.position = vec2(rawIdeal[0], rawIdeal[2])
		# self.node = rawIdeal[3] / TRACK_LENGTH // TRACK_LENGTH likely int
		self.distance = rawIdeal[3]
		# self.direction = rawDetail[4]
		self.direction = -math.degrees(
			math.atan2(prevRawIdeal[2] - self.position.y,
			           self.position.x - prevRawIdeal[0]))
		
		_wallLeft = rawDetail[5]
		_wallRight = rawDetail[6]
		
		self.wallLeft = slideVec2(self.position, -self.direction + 90, _wallLeft)
		self.wallRight = slideVec2(self.position, -self.direction - 90, _wallRight)


f = "./fast_lane.ai"

rawIdeal = []
detail = []

with open(f, "rb") as buffer:
    header, length, lapTime, sampleCount = struct.unpack("4i", buffer.read(4 * 4))

    for i in range(length):
        rawIdeal.append(struct.unpack("4f i", buffer.read(4 * 5)))

    extraCount = struct.unpack("i", buffer.read(4))[0]
    for i in range(extraCount):
        prevRawIdeal = rawIdeal[i - 1] if i > 0 else rawIdeal[length - 1]
        detail.append(
        trackDetailNode(rawIdeal[i], prevRawIdeal, struct.unpack("18f", buffer.read(4 * 18))))

A = np.zeros(shape=[2, length*2])
for i in range(length):
    i_prev = i-1 if i > 0 else length-1
    P1 = detail[i].wallRight.clone()
    P2 = detail[i].wallLeft.clone()
    # P3 = detail[i-1].wallLeft.clone()
    # P4 = detail[i-1].wallRight.clone()

    A[0, 2*i], A[1, 2*i] = P1.x, P1.y
    A[0, 2*i+1], A[1, 2*i+1] = P2.x, P2.y

x = A[0]
y = A[1]
colors = np.random.rand(length*2)
# area = (30 * np.random.rand(N))**2  # 0 to 15 point radii

plt.scatter(x, y, s=1, c=colors, alpha=0.5)
plt.gca().invert_yaxis() # invert y-axis
plt.show()

# 이얏호.
