import cv2
import time


from .ObjectTracking import *


MAX_TRACKING_PTS = 2
MOVEMENT_PX_THRESHOLD = 10
DIRECTION_HORIZONTAL_PX_THRESHOLD = 30
DIRECTION_VERTICAL_PX_THRESHOLD = 100
FORGET_STEP_THRESHOLD = 3
PREDICT_DELAY_MS = 1000


class HSVColorTracking(ObjectTracking):
	def __init__(self):
		self.pts = []
		self.forget_counter = 0
		self.delay_start = 0

	
	def update(self, frame):
		if (time.time() - self.delay_start) * 1000 < PREDICT_DELAY_MS:
			return

		cnts = []
		if frame is not None:
			cnts = self.find_contours(frame)
		
		if len(cnts) > 0:
			self.on_new_tracking(cnts)
		else:
			self.on_lost_tracking()


	def find_contours(self, frame):
		hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

		mask = cv2.inRange(hsv, (30, 100, 100), (85, 255, 255))
		# mask = cv2.erode(mask, None, iterations=2)
		# mask = cv2.dilate(mask, None, iterations=2)

		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		if len(cnts) == 2:
			return cnts[0]

		elif len(cnts) == 3:
			return cnts[1]

		raise Exception("Contours tuple must have length 2 or 3")
	

	def on_new_tracking(self, cnts):
		c = max(cnts, key=cv2.contourArea)
		M = cv2.moments(c)

		if M["m00"] <= 0:
			return
		
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

		if len(self.pts) > 0:
			last = self.pts[-1]
			dx, dy = self.distance_pts(center, last)
			if abs(dx) < MOVEMENT_PX_THRESHOLD and abs(dy) < MOVEMENT_PX_THRESHOLD:
				self.pts.clear()

		if len(self.pts) == MAX_TRACKING_PTS:
			self.pts.pop(0)
			
		self.pts.append(center)


	def on_lost_tracking(self):
		self.forget_counter += 1
		if self.forget_counter == FORGET_STEP_THRESHOLD:
			self.forget_counter = 0
			self.pts.clear()

	
	def predict_direction(self):
		direction = DIRECTION_NONE
		
		if len(self.pts) < MAX_TRACKING_PTS:
			return direction
		
		dx, dy = self.distance_pts(self.pts[0], self.pts[-1])

		if dx > DIRECTION_HORIZONTAL_PX_THRESHOLD:
			direction = direction | DIRECTION_RIGHT
		elif dx < -DIRECTION_HORIZONTAL_PX_THRESHOLD:
			direction = direction | DIRECTION_LEFT

		if dy > DIRECTION_VERTICAL_PX_THRESHOLD:
			direction = direction | DIRECTION_DOWN
		elif dy < -DIRECTION_VERTICAL_PX_THRESHOLD:
			direction = direction | DIRECTION_UP

		if direction != DIRECTION_NONE:
			self.delay_start = time.time()
			self.pts.clear()

		return direction
	

	def distance_pts(self, p0, p1):
		dx = p1[0] - p0[0]
		dy = p1[1] - p0[1]
		return (dx, dy)


	def tracking_pts(self):
		return self.pts