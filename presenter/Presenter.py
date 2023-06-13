import numpy as np
import torch

from presenter.ViewContract import ViewContract
from model.ObjectTracking import ObjectTracking, DIRECTION_LEFT, DIRECTION_RIGHT
from model.TryOn import TryOn


class Presenter:
    def __init__(self, view: ViewContract):
        self.view: ViewContract = view
        self.tracker = ObjectTracking()
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.tryon = TryOn(device)


    def check_gesture(self, frame: np.ndarray):
        self.tracker.update(frame, self.view.hsv_lower_bound(), self.view.hsv_upper_bound())

        direction = self.tracker.predict_direction()
        
        if direction == DIRECTION_LEFT:
            self.view.previous_sample()

        elif direction == DIRECTION_RIGHT:
            self.view.next_sample()


    def perform_tryon(self, frame: np.ndarray, clothes_name):
        return self.tryon(frame, clothes_name)


    def get_tracking_pts(self):
        return self.tracker.pts

