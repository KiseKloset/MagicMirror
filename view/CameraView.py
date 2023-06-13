import tkinter as tk
import glob

from pathlib import Path
from PIL import Image, ImageTk
from view.Camera import Camera
from view.SettingsView import SettingsView
from presenter.ViewContract import ViewContract
from presenter.Presenter import Presenter
from model.TryOn import CLOTHES_PATH


SAMPLE_SPACE = 5
SAMPLE_WIDTH = 72
SAMPLE_HEIGHT = 96
SAMPLE_HORIZONTAL_PADDING = 5

DEBUG_TRACKING = True


class CameraView(tk.Frame, ViewContract):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.presenter: Presenter = Presenter(self)
		self.settings = SettingsView()
		self.init_camera()
		self.init_samples()
		self.init_ui()
		self.update()


	def init_camera(self):
		self.camera = Camera()
		self.camera_offset_x = 0
		self.camera_offset_y = SAMPLE_HEIGHT + 2 * SAMPLE_HORIZONTAL_PADDING


	def init_samples(self):
		sample_paths = list(glob.glob(str(CLOTHES_PATH / "*.jpg")))
		self.sample_names = [Path(path).name for path in sample_paths]

		samples = [Image.open(path).resize((SAMPLE_WIDTH, SAMPLE_HEIGHT)) for path in sample_paths]
		self.samples = [ImageTk.PhotoImage(sample) for sample in samples]
		self.selected_sample = 0

		self.sample_offset_x = (self.camera.width - (SAMPLE_WIDTH + SAMPLE_SPACE) * len(self.samples)) / 2
		self.sample_offset_y = SAMPLE_HORIZONTAL_PADDING


	def init_ui(self):
		self.canvas_image = None
		self.canvas = tk.Canvas(self, width = self.camera.width, height = self.camera.height + SAMPLE_HEIGHT)
		self.canvas.pack()


	def update(self):
		self.camera.update()
		if self.camera.frame is None:
			self.destroy()

		self.presenter.check_gesture(self.camera.frame)
		bbox, tryon = self.presenter.perform_tryon(self.camera.frame, self.sample_names[self.selected_sample])

		self.update_background(tryon)
		self.update_samples()

		if DEBUG_TRACKING:
			self.draw_tryon_bbox(bbox)
			self.update_trackings()

		self.after(10, self.update)


	def update_background(self, frame: None):
		background = frame
		if background is None:
			background = self.camera.frame

		self.canvas_image = ImageTk.PhotoImage(image = Image.fromarray(background))
		self.canvas.create_image(self.camera_offset_x, self.camera_offset_y, image = self.canvas_image, anchor = tk.NW)

	
	def update_samples(self):
		self.canvas.create_rectangle(0, 0, self.camera.width, self.camera_offset_y, fill="white")

		for i, sample in enumerate(self.samples):
			offset_x = self.sample_offset_x + i * (SAMPLE_WIDTH + SAMPLE_SPACE)
			offset_y = self.sample_offset_y
			self.canvas.create_image(offset_x, offset_y, image = sample, anchor = tk.NW)
			
			if i == self.selected_sample:
				self.canvas.create_rectangle(
					offset_x, 
					offset_y, 
					offset_x + SAMPLE_WIDTH, 
					offset_y + SAMPLE_HEIGHT, 
					outline="#00ff00",
					width=SAMPLE_HORIZONTAL_PADDING
				)

	
	def update_trackings(self):
		r = 2
		pts = self.presenter.get_tracking_pts()
		for pt in pts:
			self.canvas.create_oval(
				self.camera_offset_x + pt[0] - r, 
				self.camera_offset_y + pt[1] - r, 
				self.camera_offset_x + pt[0] + r, 
				self.camera_offset_y + pt[1] + r, 
				fill='red'
			)

	
	def draw_tryon_bbox(self, bbox):
		if bbox is None:
			return
		
		self.canvas.create_rectangle(
			self.camera_offset_x + bbox['l'], 
			self.camera_offset_y + bbox['t'], 
			self.camera_offset_x + bbox['r'], 
			self.camera_offset_y + bbox['b'], 
			outline="blue",
			width=2
		)


	def next_sample(self):
		self.selected_sample = (self.selected_sample + 1) % len(self.samples)

	
	def previous_sample(self):
		self.selected_sample = (self.selected_sample - 1) % len(self.samples)

	
	def hsv_upper_bound(self):
		return self.settings.hsv_upper_bound()
	

	def hsv_lower_bound(self):
		return self.settings.hsv_lower_bound()


	def release(self):
		self.camera.release()