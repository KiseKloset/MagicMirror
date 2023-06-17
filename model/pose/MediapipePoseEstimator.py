from .PoseEstimator import *

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class MediapipePoseEstimator(PoseEstimator):
    def __init__(self):
        base_options = python.BaseOptions(model_asset_path='.pose_landmarker_lite.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)
        self.detector = vision.PoseLandmarker.create_from_options(options)


    def predict(self, frame: np.ndarray):
        h, w, _ = frame.shape
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = self.detector(image)

        keypoints = [[pt.x / 255 * w, pt.y / 255 * h] for pt in detection_result.pose_landmarks[0]]
        mask = detection_result.segmentation_masks[0].numpy_view()
        return keypoints, mask