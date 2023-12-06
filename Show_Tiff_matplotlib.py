import tkinter as tk
from tkinter import filedialog
#import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.patches import Rectangle
from PIL import Image
from show_spectra import ShowSpectra
from show_spectra_area import ShowSpectra_Area
import re
import os
import datetime as dt

class TifStackViewer_matplot:
    def __init__(self, root):
        # window
        self.root = root
        self.root.title("TIF Stack Viewer")
        self.root.state('zoomed')

        #for wavelength from file-name
        self.wavelength_intervall = [0,0]

        #frame for canfas and slider
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand = tk.YES, fill = tk.BOTH)

        # counter
        self.current_index = 0

        self.filepath = ""

        # Button
        self.load_button = tk.Button(self.frame, text="Load TIF Stack", command=self.load_tif_stack)
        self.load_button.pack(side=tk.BOTTOM)

        # Slider
        self.slider = tk.Scale(self.frame, from_=0, to=1, orient=tk.HORIZONTAL, resolution=1, command=self.slider_control)
        self.slider.pack(expand = tk.YES, side = tk.BOTTOM, fill=tk.X)

        # Canvas for Matplotlib-Figur
        self.fig, self.ax = plt.subplots(figsize = (5,4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(expand=tk.YES, fill=tk.BOTH)

        #interactive part
        self.canvas.get_tk_widget().pack(expand = tk.YES, side = tk.BOTTOM, fill = tk.X)
        self.toolbar = NavigationToolbar2Tk(self.canvas,self.frame)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(expand = tk.YES, side = tk.BOTTOM, fill = tk.X)

        # Binding for click event on the canvas
        self.canvas.mpl_connect("button_press_event", self.on_canvas_click)
        self.canvas.mpl_connect("button_release_event", self.on_canvas_release)

        self.last_click_time = dt.datetime.now()

        self.x1 = 0
        self.x2 = 0

        self.y1 = 0
        self.y2 = 0

        self.inner_plot = plt.subplot()

    def load_tif_stack(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("TIF files", "*.tif")])
        if self.file_path:
            self.image_stack = self.load_images_from_tif(self.file_path)
            self.slider.config(from_ = 0, to=len(self.image_stack) - 1)
            self.show_image()

            filename = os.path.basename(self.file_path)
            pattern = re.compile(r'wl_(\d+)-(\d+)\.tif')
            solution = pattern.search(filename)

            if solution:
                self.wavelength_intervall[0] = int(solution.group(1))
                self.wavelength_intervall[1] = int(solution.group(2))

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

    def on_canvas_click(self, event):
        # Function to be called when the left mouse button is clicked on the canvas
        #if event.button == 1:  # Check if the left mouse button was clicked
            current_time = dt.datetime.now()
            time_diff = current_time - self.last_click_time

            if time_diff.total_seconds() < 0.5:
                x, y = int(event.xdata), int(event.ydata)
                print(f"Cursor Position on Click: x={x}, y={y}")

                window_spectra = tk.Toplevel(self.root)
                window_spectra.title("Spectra")

                ShowSpectra(window_spectra, x, y, self.file_path, self.wavelength_intervall[0], self.wavelength_intervall[1])

            else:
                self.x1, self.y1 = int(event.xdata), int(event.ydata)

            self.last_click_time = current_time
                
    def on_canvas_release(self, event):
        current_time = dt.datetime.now()
        time_diff = current_time - self.last_click_time

        if time_diff.total_seconds() > 0.5 and time_diff.total_seconds() <3.5:
            x1 = self.x1
            y1 = self.y1

            x2 = int(event.xdata)
            y2 = int(event.ydata)

            topleft = (x1, y1)
            bottomright = (x2, y2)

            window_spectraArea = tk.Toplevel(self.root)
            window_spectraArea.title("Spectra of Area")

            ShowSpectra_Area(window_spectraArea, topleft, bottomright, self.file_path, self.wavelength_intervall[0], self.wavelength_intervall[1])

            width = x1 - x2
            height = y1 - y2

            rectangle = Rectangle(bottomright, width, height, edgecolor = "red", facecolor = 'none')

            self.inner_plot.add_patch(rectangle)
            self.inner_plot.plot()
            self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = TifStackViewer_matplot(root)
    root.mainloop()

    
