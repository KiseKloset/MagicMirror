import numpy as np

class ViewContract(object):
    def next_sample(self):
        pass

    def previous_sample(self):
        pass

    def hsv_upper_bound(self):
        pass

    def hsv_lower_bound(self) -> np.ndarray:
        pass