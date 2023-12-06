import tifffile as tif
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

class ShowSpectra_Area:
    def __init__(self, root, topleft, bottomright, file_path, wavelength_min, wavelength_max):
        self.root = root
        self.root.title("Show spectrum")

        self.top_left = topleft
        self.bottom_right = bottomright
        self.filepath = file_path

        self.wavelength_max = wavelength_max
        self.wavelength_min = wavelength_min

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(expand=tk.YES, fill=tk.BOTH)

        self.show_image()

    def get_pixel_value(self, slide):

        image = tif.imread(self.filepath)
        image_pixel_value = np.mean(self.crop_matrix_with_corners(image[slide, : , :]))

        return image_pixel_value

    def build_array_pixel(self):
        image = tif.imread(self.filepath)
        slide_number = image.shape[0]
        final_array = []

        for i in range(slide_number):
            final_array.append(self.get_pixel_value(i))

        return final_array

    def show_image(self):
        x_values = list(range(self.wavelength_min, self.wavelength_max + 1))
        y_values = self.build_array_pixel()

        self.ax.plot(x_values, y_values, label = "Spectra")

        self.ax.minorticks_on()
        self.ax.grid()
        self.ax.legend()
        self.ax.set_xlabel("Wavelength")
        self.ax.set_ylabel("Intsity")

        self.canvas.draw()

    def crop_matrix_with_corners(self, matrix):
        top_left_row, top_left_col = self.top_left
        bottom_right_row, bottom_right_col = self.bottom_right

        top_right = (top_left_row, bottom_right_col)
        bottom_left = (bottom_right_row, top_left_col)

        cropped_matrix = matrix[top_left_row:bottom_right_row + 1, top_left_col:bottom_right_col + 1]

        return cropped_matrix

if __name__ == "__main__":
    file_path = "/Users/jan-niklastopf/Downloads/EmbryoCE/focal551-755.tif"
    x_coord = 300
    y_coord = 200
    min_wavelength = 400
    max_wavelength = 604 
    root = tk.Tk()
    app = ShowSpectra_Area(root, x_coord, y_coord, file_path, min_wavelength, max_wavelength)
    root.mainloop()


