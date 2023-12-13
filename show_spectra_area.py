import tifffile as tif
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import typing
class ShowSpectra_Area:
    def __init__(self, root, topleft: typing.Tuple, bottomright: typing.Tuple, file_path: str, wavelength_min: int, wavelength_max: int):
        """
        The above function initializes a GUI window to display a spectrum image.
        
        @param root The `root` parameter is the Tkinter root window object. It is the main window of the
        application.
        @param topleft The `topleft` parameter is a tuple that represents the coordinates of the top left
        corner of the image or spectrum. It typically consists of two values: the x-coordinate and the
        y-coordinate.
        @param bottomright The `bottomright` parameter is a tuple that represents the coordinates of the
        bottom right corner of a rectangle. It is used to define the region of interest in an image or plot.
        @param file_path The `file_path` parameter is a string that represents the path to the file
        containing the spectrum data.
        @param wavelength_min The `wavelength_min` parameter represents the minimum wavelength value for the
        spectrum. It is an integer value.
        @param wavelength_max The `wavelength_max` parameter represents the maximum wavelength value for the
        spectrum. It is an integer value.
        """

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

    def get_pixel_value(self, slide: int):
        """
        The function `get_pixel_value` takes in a slide number, reads an image file, crops the image using
        specified corners, and returns the mean pixel value of the cropped image.
        
        @param slide The parameter `slide` is an integer that represents the index of the slide in the
        image. It is used to access a specific slide in the image array.
        
        @return the average pixel value of a specific slide in an image.
        """

        with tif.TiffFile(self.filepath) as file:
            file = [page.asarray() for page in file.pages]
        

        image_pixel_value = np.mean(self.crop_matrix_with_corners(file[slide]))

        return image_pixel_value

    def build_array_pixel(self)-> np.ndarray:
        """
        The function `build_array_pixel` reads an image file, determines the number of slides in the the tif file,
        and then calls the `get_pixel_value` method for each slide to obtain the pixel values, which are
        then stored in a final array and returned.
        
        @return the final_array, which is a list containing the pixel values for each slide in the image.
        """
        image = tif.imread(self.filepath)
        slide_number = image.shape[0]
        final_array = []

        for i in range(slide_number):
            final_array.append(self.get_pixel_value(i))

        return final_array

    def show_image(self):
        """
        The function `show_image` plots a graph of wavelength values against intensity values and displays
        it.
        """
        x_values = list(range(self.wavelength_min, self.wavelength_max + 1))
        y_values = self.build_array_pixel()

        self.ax.plot(x_values, y_values, label = "Spectra")

        self.ax.minorticks_on()
        self.ax.grid()
        self.ax.legend()
        self.ax.set_xlabel("Wavelength")
        self.ax.set_ylabel("Intsity")

        self.canvas.draw()

    def crop_matrix_with_corners(self, matrix: np.ndarray)-> np.ndarray:
        """
        The function `crop_matrix_with_corners` takes a matrix and returns a cropped version of the matrix
        based on the top left and bottom right corners.
        
        @param matrix The input matrix is a numpy array that represents a 2D matrix.
        
        @return the cropped matrix, which is a subset of the original matrix.
        """
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


