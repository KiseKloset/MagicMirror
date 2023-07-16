import tkinter as tk
import glob

from pathlib import Path
from PIL import Image, ImageTk
from view.Camera import Camera
from view.BackgroundSelectView import BackgroundSelectView
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
		self.num_sub = 2
		self.init_camera()
		self.bg_view = BackgroundSelectView(self.camera.width, self.camera.height)
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

		self.sample_offset_x = (self.camera.width - (SAMPLE_WIDTH + SAMPLE_SPACE) * (self.num_sub*2 + 1)) / 2
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
		
		bg = self.bg_view.get_select_bg()
		self.presenter.process_frame(self.camera.frame, self.sample_names[self.selected_sample], bg)


	def on_processed(self, frame):
		self.draw_background(frame)
		self.draw_samples()
		self.bg_view.draw(
			self.canvas, 
			self.camera_offset_x, 
			self.camera_offset_y,
			self.camera_offset_x + frame.shape[1],
			self.camera_offset_y + frame.shape[0] 
		)
		self.after(1, self.update)


	def draw_background(self, background):
		self.canvas_image = ImageTk.PhotoImage(image = Image.fromarray(background))
		self.canvas.create_image(self.camera_offset_x, self.camera_offset_y, image = self.canvas_image, anchor = tk.NW)

	
	def draw_samples(self):
		self.canvas.create_rectangle(0, 0, self.camera.width, self.camera_offset_y, fill="white")
		
		start, end = (self.selected_sample - self.num_sub) % len(self.samples), (self.selected_sample + self.num_sub + 1) % len(self.samples)
		sub_samples = self.samples[start: end] if end > start else self.samples[start:] + self.samples[:end]

		for i, sample in enumerate(sub_samples):
			offset_x = self.sample_offset_x + i * (SAMPLE_WIDTH + SAMPLE_SPACE)
			offset_y = self.sample_offset_y
			self.canvas.create_image(offset_x, offset_y, image = sample, anchor = tk.NW)
			
			if i == self.num_sub:
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


	def next_bg(self):
		self.bg_view.next_bg()


	def previous_bg(self):
		self.bg_view.prev_bg()


	def release(self):
		self.camera.release()