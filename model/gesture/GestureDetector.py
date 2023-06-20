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
		self.predict_delay = 5

		self.pts = []
		self.delay_start = 0

	def predict(self, pose, right_rect, left_rect):
		direction = DIRECTION_NONE

		right_x = (pose[RIGHT_THUMB][0] + pose[RIGHT_INDEX][0] + pose[RIGHT_PINKY][0]) / 3
		right_y = (pose[RIGHT_THUMB][1] + pose[RIGHT_INDEX][1] + pose[RIGHT_PINKY][1]) / 3
		right_pt = [right_x, right_y]	

		left_x = (pose[LEFT_THUMB][0] + pose[LEFT_INDEX][0] + pose[LEFT_PINKY][0]) / 3
		left_y = (pose[LEFT_THUMB][1] + pose[LEFT_INDEX][1] + pose[LEFT_PINKY][1]) / 3
		left_pt = [left_x, left_y]	

		if time.time() - self.delay_start < self.predict_delay:
			return direction

		if self.__in_rect(right_pt, right_rect) or self.__in_rect(left_pt, right_rect):
			direction = DIRECTION_RIGHT

		elif self.__in_rect(right_pt, left_rect) or self.__in_rect(left_pt, left_rect):
			direction  = DIRECTION_LEFT

		if direction != DIRECTION_NONE:
			self.delay_start = time.time()

		return direction
	

	def __in_rect(self, pt, rect):
		return pt[0] >= rect[0] and pt[0] <= rect[2] and pt[1] >= rect[1] and pt[1] <= rect[3]