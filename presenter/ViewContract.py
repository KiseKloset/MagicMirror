import numpy as np

class ViewContract(object):
    def next_sample(self):
        pass

    def previous_sample(self):
        pass

    def on_processed(self, frame: np.ndarray):
        pass

    def get_camera_size(self):
        pass

    def get_next_button_rect(self):
        pass

    def get_prev_button_rect(self):
        pass