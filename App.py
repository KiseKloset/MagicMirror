
import tkinter as tk
from view.CameraView import CameraView


if __name__ == "__main__":
    app = tk.Tk()
    app.title("Camera")

    camera_view = CameraView(app)
    camera_view.pack()

    app.bind('<Escape>', lambda _: app.quit())
    app.protocol("WM_DELETE_WINDOW", app.quit())
    app.mainloop()

    camera_view.release()