import tkinter as tk
import glob

from pathlib import Path
from PIL import Image, ImageTk
from view.Camera import Camera
from presenter.ViewContract import ViewContract
from presenter.Presenter import Presenter
from model.tryon.TryOn import CLOTHES_PATH


SAMPLE_SPACE = 5
SAMPLE_WIDTH = 72
SAMPLE_HEIGHT = 96
SAMPLE_HORIZONTAL_PADDING = 5


class CameraView(tk.Frame, ViewContract):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.init_camera()
		self.presenter: Presenter = Presenter(self)
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


	def get_camera_size(self):
		return self.camera.width, self.camera.height


	def update(self):
		self.camera.update()
		if self.camera.frame is None:
			self.destroy()

		self.presenter.process_frame(self.camera.frame, self.sample_names[self.selected_sample])


	def on_processed(self, frame):
		self.draw_background(frame)
		self.draw_samples()
		self.after(1, self.update)


	def draw_background(self, background):
		self.canvas_image = ImageTk.PhotoImage(image = Image.fromarray(background))
		self.canvas.create_image(self.camera_offset_x, self.camera_offset_y, image = self.canvas_image, anchor = tk.NW)

	
	def draw_samples(self):
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


	def next_sample(self):
		self.selected_sample = (self.selected_sample + 1) % len(self.samples)

	
	def previous_sample(self):
		self.selected_sample = (self.selected_sample - 1) % len(self.samples)


	def release(self):
		self.camera.release()