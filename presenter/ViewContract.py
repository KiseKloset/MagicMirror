import numpy as np

class ViewContract(object):
    def next_sample(self):
        pass

    def previous_sample(self):
        pass

    def on_processed(self, frame: np.ndarray):
        pass