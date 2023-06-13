import numpy as np

from presenter.ViewContract import ViewContract
from model.ObjectTracking import ObjectTracking, DIRECTION_LEFT, DIRECTION_RIGHT


class Presenter:
    def __init__(self, view: ViewContract):
        self.view: ViewContract = view
        self.tracker = ObjectTracking()


    def check_gesture(self, frame: np.ndarray):
        self.tracker.update(frame, self.view.hsv_lower_bound(), self.view.hsv_upper_bound())

        direction = self.tracker.predict_direction()
        if direction != 0:
            print(direction)
        
        if direction == DIRECTION_LEFT:
            self.view.previous_sample()

        elif direction == DIRECTION_RIGHT:
            self.view.next_sample()


    def get_tracking_pts(self):
        return self.tracker.pts

