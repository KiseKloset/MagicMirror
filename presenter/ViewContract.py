import numpy as np

class ViewContract(object):
    def next_sample(self):
        pass

    def previous_sample(self):
        pass

    def next_bg(self):
        pass

    def previous_bg(self):
        pass

    def on_processed(self, frame: np.ndarray):
        pass