import tkinter as tk
import glob
import cv2
import time

from pathlib import Path
from PIL import Image, ImageTk


PADDING_HORIZONTAL = 10
PADDING_VERTICAL = 10
NORMAL_HEIGHT = 54
NORMAL_ALPHA = 255
BIG_HEIGHT = 72
NONE_IDX = -1
DISPLAY_DURATION = 5


class BackgroundSelectView:
    def __init__(self, camera_width, camera_height):
        self.init_size(camera_width, camera_height)
        self.init_bg(camera_width, camera_height)
        self.end_display_time = 0


    def init_bg(self, camera_width, camera_height):
        self.bg_paths = [Path(i) for i in glob.glob("background/*")]
        self.bg_cv = [cv2.cvtColor(cv2.imread(str(i)), cv2.COLOR_BGR2RGB) for i in self.bg_paths]
        self.bg_cv = [self.resize_crop(img, (int(camera_width), int(camera_height))) for img in self.bg_cv]
        
        self.bg_tk_big = [self.cv_to_big_tkinter(img) for img in self.bg_cv]
        self.bg_tk_normal = [self.cv_to_normal_tkinter(img) for img in self.bg_cv]
        self.none_tk_big = ImageTk.PhotoImage(Image.new('RGBA', (self.big_width, self.big_height), (170, 170, 170, 255)))
        self.none_tk_normal = ImageTk.PhotoImage(Image.new('RGBA', (self.normal_width, self.normal_height), (170, 170, 170, NORMAL_ALPHA)))
        
        self.n = len(self.bg_cv)
        self.selected_idx = NONE_IDX


    def resize_crop(self, frame, img_size):
        if frame.shape[0] * img_size[0] < frame.shape[1] * img_size[1]:
            height = frame.shape[0]
            width = int(img_size[0] * height / img_size[1])
        else:
            width = frame.shape[1]
            height = int(img_size[1] * width / img_size[0])
            
        center = (frame.shape[0] // 2, frame.shape[1] // 2)
        x = center[1] - width // 2
        y = center[0] - height // 2
        out_frame = frame[y : y + height, x : x + width]
        return cv2.resize(out_frame, (img_size[0], img_size[1]))


    def cv_to_big_tkinter(self, rgb):
        pil = Image.fromarray(rgb)
        pil = pil.resize((self.big_width, self.big_height))
        return ImageTk.PhotoImage(image = pil)
    

    def cv_to_normal_tkinter(self, rgb):
        rgba = cv2.cvtColor(rgb, cv2.COLOR_RGB2RGBA)
        rgba[:, :, 3] = NORMAL_ALPHA
        pil = Image.fromarray(rgba)
        pil = pil.resize((self.normal_width, self.normal_height))
        return ImageTk.PhotoImage(image = pil)


    def init_size(self, camera_width, camera_height):
        self.normal_height = int(NORMAL_HEIGHT)
        self.normal_width = int(NORMAL_HEIGHT * camera_width // camera_height)
        self.big_height = int(BIG_HEIGHT)
        self.big_width = int(BIG_HEIGHT * camera_width // camera_height)

        self.width = self.big_width + 2 * self.normal_width + 4 * PADDING_HORIZONTAL
        self.height = self.big_height + 2 * PADDING_VERTICAL

        self.prev_coords = [PADDING_HORIZONTAL, self.height // 2 - self.normal_height // 2]
        self.current_coords = [self.normal_width + 2 * PADDING_HORIZONTAL, PADDING_VERTICAL]
        self.next_coords = [self.big_width + self.normal_width + 3 * PADDING_HORIZONTAL, self.height // 2 - self.normal_height // 2]


    def set_display_time(self):
        self.end_display_time = time.time() + DISPLAY_DURATION


    def draw(self, canvas, l, t, r, b):
        if self.end_display_time == 0:
            self.set_display_time()

        # if time.time() > self.end_display_time:
        #     return

        x = r - self.width
        y = b - self.height

        canvas.create_rectangle(x, y, r, b, fill="white")

        current = self.selected_idx
        self.draw_bg(
            current, 
            canvas, 
            x + self.current_coords[0], 
            y + self.current_coords[1],
        )
        prev = self.decrease(current)
        self.draw_bg(
            prev, 
            canvas, 
            x + self.prev_coords[0], 
            y + self.prev_coords[1],
        )
        next = self.increase(current)
        self.draw_bg(
            next, 
            canvas, 
            x + self.next_coords[0], 
            y + self.next_coords[1],
        )


    def draw_bg(self, idx, canvas, l, t):
        if idx == NONE_IDX:
            self.draw_none(canvas, l, t)
            return
        
        if idx == self.selected_idx:
            img = self.bg_tk_big[idx]
        else:
            img = self.bg_tk_normal[idx]
            
        canvas.create_image(l, t, image = img, anchor = tk.NW)


    def draw_none(self, canvas, l, t):
        if self.selected_idx == NONE_IDX:
            img = self.none_tk_big
        else:
            img = self.none_tk_normal

        canvas.create_image(l, t, image = img, anchor = tk.NW)


    def next_bg(self):
        self.selected_idx = self.increase(self.selected_idx)
        self.set_display_time()


    def increase(self, x):
        current = x + 1
        current += 1
        current = current % (self.n + 1)
        return current - 1


    def prev_bg(self):
        self.selected_idx = self.decrease(self.selected_idx)
        self.set_display_time()

    
    def decrease(self, x):
        current = x + 1
        current -= 1
        current = current % (self.n + 1)
        return current - 1


    def get_select_bg(self):
        if self.selected_idx == NONE_IDX:
            return None
        
        return self.bg_cv[self.selected_idx]