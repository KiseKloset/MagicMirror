import cv2
import numpy as np
import torch

from presenter.ViewContract import ViewContract
from model.gesture.GestureDetector import *
from model.pose.MediapipePoseEstimator import MediapipePoseEstimator
from model.pose.PoseEstimator import *
from model.tryon.TryOn import TryOn


class Presenter:
	def __init__(self, view: ViewContract):
		self.view: ViewContract = view
		self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

		self.counter = 0

		self.pose_estimator: PoseEstimator = MediapipePoseEstimator()
		self.pose_keypoints = None
		self.pose_mask = None

		self.gesture_detector: GestureDetector = GestureDetector()

		self.person_bbox = None
		self.person = None

		self.background_mask = None
		self.segmentation_model = None # TODO

		self.try_on_result = None
		self.try_on_model: TryOn = TryOn(self.device)

		camera_width, camera_height = self.view.get_camera_size()
		self.__init_regison(camera_width, camera_height)
		self.current_frame = None

		# Background
		self.rgb_background = cv2.cvtColor(cv2.imread("background/night-street.jpg"), cv2.COLOR_BGR2RGB)
		self.rgb_background = cv2.resize(self.rgb_background, (int(camera_width), int(camera_height)))

	def process_frame(self, bgr_frame: np.ndarray, clothes_id: str):
		# self.counter += 1

		if True:
			rgb_frame = self.__pre_process(bgr_frame)

			# CPU
			self.pose_keypoints, self.pose_mask = self.__detect_pose_keypoints_and_segmentation(rgb_frame)
			if self.pose_keypoints is not None:
				self.__check_gesture(rgb_frame)

				self.person = self.__crop_person(rgb_frame)

				# # GPU optimized here
				self.try_on = self.__try_on(clothes_id)

			rgb_frame = self.__add_background(rgb_frame)

			out = self.__post_process(rgb_frame, try_on=self.try_on if self.pose_keypoints is not None else None)

			# out = self.__draw_region(out)

			self.current_frame = out

		self.view.on_processed(self.current_frame)

	def __pre_process(self, bgr_frame):
		# Histogram equalization
		# ycrcb_img = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2YCrCb)
		# # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
		# # ycrcb_img[:, :, 0] = clahe.apply(ycrcb_img[:, :, 0])
		# ycrcb_img[:, :, 0] = cv2.equalizeHist(ycrcb_img[:, :, 0])
		# equalized_img = cv2.cvtColor(ycrcb_img, cv2.COLOR_YCrCb2RGB)
		# return equalized_img
		return bgr_frame

	def __detect_pose_keypoints_and_segmentation(self, frame):
		return self.pose_estimator.predict(frame)

	def __check_gesture(self, frame):
		direction = self.gesture_detector.predict(self.pose_keypoints, frame)
		if direction == DIRECTION_LEFT:
			self.view.next_sample()

		elif direction == DIRECTION_RIGHT:
			self.view.previous_sample()


	def __crop_person(self, frame):
		# TODO
		person = frame.copy()
		person[~self.pose_mask] = 255
		person = person[self.rect_y : self.rect_y + self.rect_height, self.rect_x : self.rect_x + self.rect_width]
		return person
	

	def __try_on(self, clothes_id: str):
		person = cv2.resize(self.person, (192, 256))
		return self.try_on_model(person, clothes_id)


	def __post_process(self, frame, try_on=None):
		# TODO
		# Remapping, re histogram equalization
		if try_on is not None:
			result = cv2.resize(try_on, (self.rect_width, self.rect_height))
			ori = frame.copy()
			frame[self.rect_y : self.rect_y + self.rect_height, self.rect_x : self.rect_x + self.rect_width] = result
			frame = frame*self.pose_mask + ori*(~self.pose_mask)

		return frame

	def __add_background(self, frame):
		if self.pose_mask is not None:
			frame = (frame*self.pose_mask + self.rgb_background*(1 - self.pose_mask)).astype(np.uint8)

		return frame
	
	def __init_regison(self, frame_width, frame_height):
		# Calculate the rectangle coordinates
		w, h = int(frame_width), int(frame_height)
		self.rect_width = int(h * (192 / 256))
		self.rect_height = h
		self.rect_x = (w - self.rect_width) // 2
		self.rect_y = 0

	def __draw_region(self, frame):
		cv2.rectangle(
			frame, 
			(self.rect_x, self.rect_y), 
			(self.rect_x + self.rect_width, self.rect_y + self.rect_height), 
			(255, 0, 0), 
			2,
		)

		return frame
