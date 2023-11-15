import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image

class TifStackViewer:
    def __init__(self, root):
        # Fenster
        self.root = root
        self.root.title("TIF Stack Viewer")

        # Bildzähler
        self.current_index = 0

        # Button
        self.load_button = tk.Button(root, text="Load TIF Stack", command=self.load_tif_stack)
        self.load_button.pack(side=tk.BOTTOM)

        # Canvas für Matplotlib-Figur
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(expand=tk.YES, fill=tk.BOTH)

        # Slider
        self.slider = tk.Scale(root, from_=0, to=1, orient=tk.HORIZONTAL, resolution=1, command=self.slider_control)
        self.slider.pack(expand=tk.YES, fill=tk.BOTH)

    def load_tif_stack(self):
        file_path = filedialog.askopenfilename(filetypes=[("TIF files", "*.tif")])
        if file_path:
            self.image_stack = self.load_images_from_tif(file_path)
            self.slider.config(to=len(self.image_stack) - 1)
            self.show_image()

    def load_images_from_tif(self, file_path):
        image_stack = []
        with Image.open(file_path) as img:
            for i in range(img.n_frames):
                img.seek(i)
                image_stack.append(img.copy())
        return image_stack

    def show_image(self):
        if self.image_stack:
            img = self.image_stack[self.current_index]
            self.ax.imshow(img, cmap='gray')  # Hier kannst du die colormap anpassen
            self.root.title(f"TIF Stack Viewer - Image {self.current_index + 1}/{len(self.image_stack)}")
            self.canvas.draw()

    def slider_control(self, value):
        self.current_index = int(value)
        self.show_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = TifStackViewer(root)
    root.mainloop()
