from .PoseEstimator import *

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class MediapipePoseEstimator(PoseEstimator):
    def __init__(self):
        base_options = python.BaseOptions(model_asset_path='model/pose/pose_landmarker_lite.task')
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True)
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def predict(self, frame: np.ndarray):
        h, w, _ = frame.shape
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        detection_result = self.detector.detect(image)  
        if len(detection_result.pose_landmarks) <= 0:
            return None, None

        keypoints = [[pt.x * w, pt.y * h] for pt in detection_result.pose_landmarks[0]]
        mask = detection_result.segmentation_masks[0].numpy_view()
        mask = mask > 0.5
        mask = np.repeat(mask[:, :, np.newaxis], 3, axis=2)
        return keypoints, mask