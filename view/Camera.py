import cv2

class Camera:
	def __init__(self):
		self.frame = None
		self.cap = cv2.VideoCapture(0)
		if not self.cap.isOpened():
			raise ValueError("Unable to open video source")
		self.width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
		self.height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	

	def update(self):
		ret, frame = self.cap.read()    
		if ret:
			self.frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)

	
	def release(self):
		self.cap.release()
	