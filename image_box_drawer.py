import tkinter as tk
from PIL import Image, ImageTk
import os
from config import *
import argparse


class ImageBoxDrawer:
    def __init__(self, folder_path):
        self.root = tk.Toplevel()
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack()

        # get the first image
        self.image_path = next((os.path.join(folder_path, f) for f in os.listdir(
            folder_path) if os.path.isfile(os.path.join(folder_path, f))), None)
        self.image = Image.open(self.image_path)
        self.image_width, self.image_height = self.image.size
        self.photo = ImageTk.PhotoImage(self.image)

        # create canvas
        self.canvas.config(width=self.image_width, height=self.image_height)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.start_x, self.start_y = None, None
        self.rectangle = None
        self.coordinates_label = tk.Label(
            self.root, text="Coordinates in [x1, y1, x2, y2] format: ")
        self.coordinates_label.pack()

        # bind actions
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_button_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # title
        self.root.title(self.image_path.split("/")[-1])

        self.root.mainloop()

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def on_button_motion(self, event):
        if self.rectangle:
            self.canvas.delete(self.rectangle)

        self.rectangle = self.canvas.create_rectangle(
            self.start_x, self.start_y, event.x, event.y, outline="red"
        )

    def on_button_release(self, event):
        self.canvas.delete(self.rectangle)
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        # Normalize the coordinates if needed
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
        # Display the coordinates
        self.coordinates_label.config(
            text=f"Coordinates: '[{x1}, {y1}, {x2}, {y2}]'")


'''
Command line args
'''
parser = argparse.ArgumentParser("Preview Textbox Coordinate Command")
parser.add_argument(
    "dir", help="A string to specify the directory containing images", type=str)

if __name__ == '__main__':
    # ImageBoxDrawer(PREPROCESSED_TEMPLATES_DIR).run()
    args = parser.parse_args()
    ImageBoxDrawer(args.dir + "/")
