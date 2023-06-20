from model.pose.PoseEstimator import *
import time


DIRECTION_NONE = 0
DIRECTION_UP = 1 << 0
DIRECTION_LEFT = 1 << 1
DIRECTION_DOWN = 1 << 2
DIRECTION_RIGHT = 1 << 3


class GestureDetector:
	def __init__(self):
		self.max_tracking_pts = 3
		self.x_threshold = 30
		self.y_threshold = 100
		self.predict_delay = 1

		self.pts = []
		self.delay_start = 0

	def predict(self, pose):
		direction = DIRECTION_NONE

		# if time.time() - self.delay_start < self.predict_delay:
		# 	return direction

		if not self.__append_pose(pose):
			return direction
		
		if len(self.pts) < self.max_tracking_pts:
			return direction
		
		dx, dy = self.__distance_pts(self.pts[0], self.pts[-1])

		if dx > self.x_threshold:
			direction = direction | DIRECTION_RIGHT
		elif dx < -self.x_threshold:
			direction = direction | DIRECTION_LEFT

		if dy > self.y_threshold:
			direction = direction | DIRECTION_DOWN
		elif dy < -self.y_threshold:
			direction = direction | DIRECTION_UP

		if direction != DIRECTION_NONE:
			self.delay_start = time.time()
			self.pts.clear()

		return direction
	

	def __append_pose(self, pose):
		if pose[RIGHT_THUMB] is None or pose[RIGHT_INDEX] is None or pose[RIGHT_PINKY] is None:
			return False

		x = (pose[RIGHT_THUMB][0] + pose[RIGHT_INDEX][0] + pose[RIGHT_PINKY][0]) / 3
		y = (pose[RIGHT_THUMB][1] + pose[RIGHT_INDEX][1] + pose[RIGHT_PINKY][1]) / 3
		pt = [x, y]

		if pt[0] <= 0 or pt[1] <= 0:
			return False

		self.pts.append(pt)

		if len(self.pts) > self.max_tracking_pts:
			self.pts.pop(0)

		return True


	def __distance_pts(self, p0, p1):
		dx = p1[0] - p0[0]
		dy = p1[1] - p0[1]
		return (dx, dy)