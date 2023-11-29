import tkinter as tk
from PIL import Image, ImageTk
from tkinter import filedialog

class TifStackViewer:
    def __init__(self, root):
        #window
        self.root = root
        self.root.title("TIF Stack Viewer")

        #numeration of the file
        self.image_list = []
        self.current_index = 0

        self.filepath = ""

        #button
        self.load_button = tk.Button(root, text="Load TIF Stack", command=self.load_tif_stack)
        self.load_button.pack(side=tk.BOTTOM)

        self.canvas = tk.Canvas(root)
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        #slider
        self.slider = tk.Scale(root, from_=0, to=1, orient=tk.HORIZONTAL, resolution=1, command=self.slider_control)
        self.slider.pack(expand=tk.YES, fill=tk.BOTH)

    def load_tif_stack(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("TIF files", "*.tif")])
        if self.file_path:
            self.image_list = self.load_images_from_tif(self.file_path)
            self.slider.config(to = len(self.image_list) - 1)
            self.show_image()

    def load_images_from_tif(self, file_path):
        image_list = []
        with Image.open(file_path) as img:
            for i in range(img.n_frames):
                img.seek(i)
                img_copy = ImageTk.PhotoImage(img.copy())
                image_list.append(img_copy)
        return image_list

    def show_image(self):
        if self.image_list:
            img = self.image_list[self.current_index]
            self.canvas.config(width=img.width(), height=img.height())
            self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
            self.root.title(f"TIF Stack Viewer - Image {self.current_index + 1}/{len(self.image_list)}")
            self.root.update()

    def slider_control(self, value):
        self.current_index = int(value)
        self.show_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = TifStackViewer(root) 
    root.mainloop()
