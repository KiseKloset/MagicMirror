DIRECTION_NONE = 0
DIRECTION_UP = 1 << 0
DIRECTION_LEFT = 1 << 1
DIRECTION_DOWN = 1 << 2
DIRECTION_RIGHT = 1 << 3


class ObjectTracking:

	def update(self, frame):
		pass

	def predict_direction(self):
		pass

	def tracking_pts(self):
		pass