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


	def process_frame(self, bgr_frame: np.ndarray, clothes_id: str):
		self.counter += 1

		rgb_frame = self.__pre_process(bgr_frame)

		# CPU
		self.pose_keypoints, self.pose_mask = self.__detect_pose_keypoints_and_segmentation(rgb_frame)
		self.__check_gesture()

		self.person_bbox, self.person = self.__crop_person(rgb_frame)

		# GPU optimized here
		self.try_on = self.__try_on(clothes_id)

		out = self.__post_process(rgb_frame)

		self.view.on_processed(out)


	def __pre_process(self, bgr_frame):
		# Histogram equalization
		ycrcb_img = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2YCrCb)
		ycrcb_img[:, :, 0] = cv2.equalizeHist(ycrcb_img[:, :, 0])
		equalized_img = cv2.cvtColor(ycrcb_img, cv2.COLOR_YCrCb2RGB)
		return equalized_img
	

	def __detect_pose_keypoints_and_segmentation(self, frame):
		return self.pose_estimator.predict(frame)


	def __check_gesture(self):
		direction = self.gesture_detector.predict(self.pose)
		
		if direction == DIRECTION_LEFT:
			self.view.previous_sample()

		elif direction == DIRECTION_RIGHT:
			self.view.next_sample()


	def __crop_person(self, frame):
		# TODO
		return [0, 0, frame.shape[1], frame.shape[0]], frame
	

	def __try_on(self, clothes_id: str):
		return self.try_on_model(self.person, clothes_id)


	def __post_process(self, frame):
		# TODO
		# Remapping, re histogram equalization
		return frame