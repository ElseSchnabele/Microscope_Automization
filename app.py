"""! @brief Syncronization of THORLAB Kiralux and Kurios-WB1"""
##
# @mainpage Camera-Filter Syncronization
#
# @section description_main Description
# Automization build to synchronize capturing Camera images (THORLABS kiralux CS505MU), 
# whilst regulating the transmission wavelength of a Polarization-filter (Kurios-WB1).
#
#
# @section notes_main Notes
# Contains:
#-GUI to obtain and view images for an interval of wavelengths
#-Power Calibrator which obtains the power measurements of a  
#THORLABS S170C - Microscope Slide Power Sensor and loads the intensity data into an calibration file
#-Test and example files provided by THORLABS and by Pierre CladÃ© for the powermeter
#-Calibration files for the Camera and the powermeter for a selection of objectives, exposure times and wavelengths
#
#Download on GitHub: https://github.com/ElseSchnabele/Microscope_Automization
#
##
# @file app.py
#
# @brief GUI to start and view captured images
#
# @section description_app Description
#The GUI allows to set an interval of wavelengths, for which the camera captures photos for each wavelength
#It also let the user choose a bitdepth and calibration file, which normalizes the obtained intensity
# with the maximum intensity distribution that the camera captures, if the reflected light enters the camera 
#
# @section libraries_main Libraries/Modules
# - time standard library (https://docs.python.org/3/library/time.html)
#   - Access to sleep function.
# - sensors module (local)
#   - Access to Sensor and TempSensor classes.
#
# @section notes_doxygen_example Notes
# - Comments are Doxygen compatible.
#
# @section todo_doxygen_example TODO
# - Connect PM-Calibrator to Normalizer
#
# @section author_doxygen_example Author(s)
# - Created by Jan Niklas Topf (jntopf@gmail.com)
#and Frederick Krafft (frederick.krafft@gmail.com) in 2023







# The CFsyncApp class represents a camera filter synchronizer application with various GUI elements.
import tkinter as tk
import typing
from tkinter import ttk, filedialog
from PIL import Image, ImageTk 
import subprocess
from show_tiff_matplotlib import TifStackViewer_matplot
from automization import CameraFilterSyncronizer
import os
from datetime import datetime


# The CFsyncApp class is a Python class that represents a camera filter synchronizer application with
# various GUI elements
class CFsyncApp:

    def __init__(self, root):
        """
        The above code is a Python script that creates a GUI for a camera filter synchronizer application.
        
        @param root The "root" parameter is the main window or the root window of the application. It is the
        parent widget for all other widgets in the application.
        """
        self.root = root
        root.title("Camera Filter Synchronizer")

        self.error_message_min_wavelength = tk.Label(root, text="", foreground="red")
        self.error_message_max_wavelength = tk.Label(root, text="", foreground="red")
        
        self.error_message_exposure_time = tk.Label(root, text="", foreground="red")

        #Spinbox for Min. Wavelength (Integer)
        label1 = tk.Label(root, text="Min. Wavelength [nm]:")
        min_wavelength_spinbox = tk.Spinbox(root, from_=0, to=10000, increment=1)
        min_wavelength_spinbox.delete(0, "end")
        min_wavelength_spinbox.insert(0, 550)
        self.min_wavelength_spinbox = min_wavelength_spinbox

        #Spinbox for Max. Wavelength (Float)
        label2 = tk.Label(root, text="Max. Wavelength [nm]:")
        max_wavelength_spinbox = tk.Spinbox(root, from_=0, to=10000, increment=1)
        max_wavelength_spinbox.delete(0, "end")
        max_wavelength_spinbox.insert(0, 570)
        self.max_wavelength_spinbox = max_wavelength_spinbox


        label4 = tk.Label(root, text="Exposure Time [s]:")
        exposure_time_entry = tk.Entry(root)
        exposure_time_entry.insert(0, 5)
        self.exposure_time_entry = exposure_time_entry

        label5 = tk.Label(root, text="Filename:")
        filename_entry = tk.Entry(root)
        self.filename_entry = filename_entry
        
        # Button to open folder
        open_folder_button = tk.Button(root, text="Open Calib Folder", command=self.open_folder)
        
        self.selected_folder = tk.StringVar()

        # Dropdown-list to select calib
        self.selected_file = tk.StringVar(value = 'Select Calibration')
        self.calib_file_dropdown = tk.OptionMenu(root, self.selected_folder, "")
        


        label6 = tk.Label(root, text = "Warning! If file already exists it will be overwritten!")
        label6.config(fg= 'red')

        header_label = tk.Label(root, text="Load existing Image Files:", font=("Helvetica", 10))

        tif_view_Button = tk.Button(root, text = "Show Images", command= self.open_window_tif_view)
        run_button = tk.Button(root, text="Collect Images", command=self.run_script)


        self.output_text = tk.Text(root, state=tk.DISABLED, wrap=tk.WORD, width=40, height=10)


        label1.grid(row=0, column=0)
        min_wavelength_spinbox.grid(row=0, column=1)
        self.error_message_min_wavelength.grid(row=0, column=2)

        label2.grid(row=1, column=0)
        max_wavelength_spinbox.grid(row=1, column=1)
        self.error_message_max_wavelength.grid(row=1, column=2)


        label4.grid(row=3, column=0)
        exposure_time_entry.grid(row=3, column=1)
        self.error_message_exposure_time.grid(row=3, column=2)

        label5.grid(row = 5, column= 0)
        filename_entry.grid(row = 5, column= 1)
        open_folder_button.grid(row = 6, column= 0)
        
        label6.grid(row = 7, column= 0, columnspan= 2)

        run_button.grid(row=8, column=0, columnspan=2)


        header_label.grid(row=9, column=0, pady=20)  
        tif_view_Button.grid(row=10, column=0, columnspan= 2)

        self.output_text.grid(row=11, column=0, columnspan=2)

    #run automatization.py button
    def run_script(self):
        """
        The `run_script` function takes user inputs for minimum wavelength, maximum wavelength, exposure
        time, filename, calibration file, and calibration folder, validates the inputs, and then runs a
        camera filter synchronization process using the provided inputs.
        """
        min_wavelength = self.min_wavelength_spinbox.get()
        max_wavelength = self.max_wavelength_spinbox.get()
        
        exposure_time = float(self.exposure_time_entry.get())*1e6#to microseconds
        filename = self.filename_entry.get()
        calibfile = self.selected_file.get()
        calibfolder = self.selected_folder.get()
        is_min_valid = self.validate_entry(self.min_wavelength_spinbox, self.error_message_min_wavelength, self.validate_integer, "Please enter a valid integer for Min. Wavelength!")
        is_max_valid = self.validate_entry(self.max_wavelength_spinbox, self.error_message_max_wavelength, self.validate_integer, "Please enter a valid integer for Max. Wavelength")
        
        is_exposure_time_valid = self.validate_entry(self.exposure_time_entry, self.error_message_exposure_time, self.validate_float, "Please enter a valid float for Exposure time")

        if is_min_valid and is_max_valid  and is_exposure_time_valid:
            is_min_smaller_max = self.min_smaller_max((self.min_wavelength_spinbox, self.max_wavelength_spinbox), self.error_message_max_wavelength,  "Max. Wavelength must be bigger than Min. Wavelength!")
            if is_min_smaller_max:
                output = f"Min. Wavelength [nm]: {min_wavelength}\n Max. Wavelength [nm]: {max_wavelength}\n Exposure Time [µs]: {exposure_time}"
                self.output_text.config(state=tk.NORMAL)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, output)
                self.output_text.config(state=tk.DISABLED)
                syncroniser = CameraFilterSyncronizer(wavelengths=[ int(min_wavelength) + i for i in range(int(max_wavelength)-int(min_wavelength)+1)],
                                            exposure= int(exposure_time)
                                            )
                current_datetime = datetime.now()
                date_format = "%Y-%m-%d_%H-%M-%S"
                syncroniser.gatherImages(
                    output_dir = os.path.abspath(r'.'),
                    filename = f"{filename}_wl_{min_wavelength}-{max_wavelength}nm_{current_datetime.strftime(date_format)}.tif",
                    calib_filepath= os.path.join(calibfolder,calibfile),
                    is_calib= False
                    )
                syncroniser.cleanup()
    #display error messages
    def display_error_message(self, label, message):
        """
        The function `display_error_message` updates the text of a label widget with an error message.
        
        @param label The label parameter is a reference to a tkinter Label widget.
        @param message The error message that you want to display.
        """
        label.config(text=message)

    #validation output: Error messages
    def validate_entry(self, entry, error_message_label, validation_function, error_message):
        """
        The `validate_entry` function checks if a given entry is valid based on a validation function, and
        displays an error message if it is not.
        
        @param entry The `entry` parameter is a reference to a tkinter Entry widget. It represents the input
        field where the user enters a value that needs to be validated.
        @param error_message_label The error_message_label parameter is the label widget where the error
        message will be displayed.
        @param validation_function The `validation_function` parameter is a function that takes a value as
        input and returns a boolean value indicating whether the value is valid or not.
        @param error_message The `error_message` parameter is a string that represents the error message to
        be displayed if the validation fails.
        
        @return a boolean value. If the validation function returns True, indicating that the entry is
        valid, the function returns True. Otherwise, if the validation function returns False, indicating
        that the entry is invalid, the function returns False.
        """
        value = entry.get()
        if validation_function(value):
            self.display_error_message(error_message_label, "")
            return True
        else:
            self.display_error_message(error_message_label, error_message)
            return False

    #Validate integer inputs

    def validate_integer(self, P):
        """
        The function "validate_integer" checks if a given input is a valid integer.
        
        @param P The parameter P is the input value that needs to be validated as an integer.
        
        @return a boolean value. If the input P is an empty string, it will return True. If the input P can
        be converted to a float and the float value is an integer (i.e., has no decimal places), it will
        return True. Otherwise, it will return False.
        """
        if P == "":
            return True  
        try:
            float(P)%1 == 0
            return True
        except ValueError:
            return False

    #Validate Float Inputs
    def validate_float(self, P):
        """
        The function "validate_float" checks if a given input is a valid float number.
        
        @param P The parameter "P" in the "validate_float" function is a value that needs to be validated as
        a float.
        
        @return a boolean value. If the input P is an empty string, it will return True. If the input P can
        be converted to a float without raising a ValueError, it will also return True. Otherwise, it will
        return False.
        """
        if P == "":
            return True  
        try:
            float(P)
            return True
        except ValueError:
            return False

    def min_smaller_max(self,min_and_max: typing.Tuple, error_message_label, error_message):
        """
        The function `min_smaller_max` checks if the minimum value is smaller than the maximum value and
        displays an error message if not.
        
        @param min_and_max The `min_and_max` parameter is a tuple containing two values. The first value is
        the minimum value, and the second value is the maximum value.
        @param error_message_label The `error_message_label` parameter is the label or widget where you want
        to display the error message.
        @param error_message The `error_message` parameter is a string that represents the error message to
        be displayed if the minimum value is not smaller than the maximum value.
        
        @return a boolean value. If the condition `int(minimum) < int(maximum)` is true, it returns `True`.
        Otherwise, it returns `False`.
        """
        minimum = min_and_max[0].get()
        maximum = min_and_max[1].get()
        
        if int(minimum)< int(maximum):
            self.display_error_message(error_message_label, "")
            return True
        else:
            self.display_error_message(error_message_label, error_message)
            return False

    def open_window_tif_view(self):
        """
        The function `open_window_tif_view` creates a new window and displays a TifStackViewer_matplot
        object in it.
        """
        window_tifView = tk.Toplevel(self.root)
        window_tifView.title("Display_tiffiles")

        TifStackViewer_matplot(window_tifView)

        window_tifView.mainloop()


    def open_folder(self):
        """
        The `open_folder` function allows the user to select a folder and updates the calibration file
        dropdown menu based on the selected folder.
        """
        folder_path = filedialog.askdirectory()  
        if folder_path:
            self.selected_folder.set(folder_path) 
            self.update_calib_file_dropdown(folder_path) 

    def update_calib_file_dropdown(self, folder_path):
        """
        The function updates a dropdown menu with a list of files in a given folder path.
        
        @param folder_path The folder path is the path to the directory where the calibration files are
        located.
        """
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        self.calib_file_dropdown.destroy() 
        self.calib_file_dropdown = tk.OptionMenu(self.root, self.selected_file, *files)
        self.calib_file_dropdown.grid(row= 6, column= 1)



if __name__ == "__main__":
    root = tk.Tk()
    app = CFsyncApp(root)
    root.mainloop()