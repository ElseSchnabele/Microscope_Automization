import tifffile as tif
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

class ShowSpectra:
    def __init__(self, root, x: int, y: int, file_path: str, wavelength_min: int, wavelength_max: int):
        """
        The above function initializes a GUI window to display a spectrum image.
        
        @param root The `root` parameter is the root window of the Tkinter application. It is the main
        window where all the widgets and graphical elements will be displayed.
        @param x The x parameter represents the x-coordinate of the spectrum plot.
        @param y The parameter `y` represents the y-coordinate of a point in a coordinate system.
        @param file_path The `file_path` parameter is a string that represents the path to the file
        containing the spectrum data.
        @param wavelength_min The parameter `wavelength_min` represents the minimum wavelength value for the
        spectrum.
        @param wavelength_max The parameter `wavelength_max` represents the maximum wavelength value for the
        spectrum. It is of type `int`.
        """
        self.root = root
        self.root.title("Show spectrum")

        self.x = x
        self.y = y
        self.filepath = file_path

        self.wavelength_max = wavelength_max
        self.wavelength_min = wavelength_min

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(expand=tk.YES, fill=tk.BOTH)

        self.show_image()

    def get_pixel_value(self, slide:int)-> int:
        """
        The function `get_pixel_value` takes in a slide number and returns the pixel value at the specified
        coordinates (x, y) in the image.
        
        @param slide The `slide` parameter represents the index of the slide in the image. It is used to
        access a specific slide in the image array.
        
        @return the pixel value of the specified slide at the given coordinates (x, y).
        """
        with tif.TiffFile(self.filepath) as file:
            file = [page.asarray() for page in file.pages]
        image_pixel_value = file[slide][ self.x, self.y]

        return image_pixel_value

    def build_array_pixel(self)-> np.ndarray:
        """
        The function `build_array_pixel` reads a TIFF image file, determines the number of slides in the
        image, and then calls the `get_pixel_value` method for each slide to obtain the pixel values, which
        are then stored in a list and returned.
        
        @return a final array, which is a list of pixel values extracted from an image.
        """
        image = tif.imread(self.filepath)
        slide_number = image.shape[0]
        final_array = []

        for i in range(slide_number):
            final_array.append(self.get_pixel_value(i))

        return final_array

    def show_image(self):
        """
        The function `show_image` plots a spectra graph of the wavelength over the intensity using the `x_values` and `y_values` lists
        sand draws the graph on a canvas.
        """
        x_values = list(range(self.wavelength_min, self.wavelength_max + 1))
        y_values = self.build_array_pixel()

        self.ax.plot(x_values, y_values, label = ("Spectra of", self.x," and", self.y))

        self.ax.minorticks_on()
        self.ax.grid()
        self.ax.legend()
        self.ax.set_xlabel("Wavelength")
        self.ax.set_ylabel("Intsity")

        self.canvas.draw()

if __name__ == "__main__":
    file_path = "/Users/jan-niklastopf/Downloads/EmbryoCE/focal551-755.tif"
    x_coord = 300
    y_coord = 200
    min_wavelength = 400
    max_wavelength = 604 
    root = tk.Tk()
    app = ShowSpectra(root, x_coord, y_coord, file_path, min_wavelength, max_wavelength)
    root.mainloop()


