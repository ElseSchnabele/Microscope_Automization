import tkinter as tk
import typing
from tkinter import ttk
from PIL import Image, ImageTk 
import subprocess
from Show_TifffileStack import TifStackViewer
from automization import CameraFilterSynronizer
import os
#display error messages
def display_error_message(label, message):
    label.config(text=message)

#validation output: Error messages
def validate_entry(entry, error_message_label, validation_function, error_message):
    value = entry.get()
    if validation_function(value):
        display_error_message(error_message_label, "")
        return True
    else:
        display_error_message(error_message_label, error_message)
        return False

#Validate integer inputs
def validate_integer(P):
    if P == "":
        return True  
    try:
        float(P)%1 == 0
        return True
    except ValueError:
        return False

#Validate Float Inputs
def validate_float(P):
    if P == "":
        return True  
    try:
        float(P)
        return True
    except ValueError:
        return False

def min_smaller_max(min_and_max: typing.Tuple, error_message_label, error_message):
    minimum = min_and_max[0].get()
    maximum = min_and_max[1].get()
    
    if int(minimum)< int(maximum):
        display_error_message(error_message_label, "")
        return True
    else:
        display_error_message(error_message_label, error_message)
        return False

def open_window_tif_view():
    window_tifView = tk.Toplevel(root)
    window_tifView.title("Display_tiffiles")

    test = TifStackViewer(window_tifView)

    window_tifView.mainloop()

#run automatization.py button
def run_script():
    min_wavelength = min_wavelength_spinbox.get()
    max_wavelength = max_wavelength_spinbox.get()
    bitdepth = bitdepth_entry.get()
    exposure_time = exposure_time_entry.get()
    
    is_min_valid = validate_entry(min_wavelength_spinbox, error_message_min_wavelength, validate_integer, "Please enter a valid integer for Min. Wavelength!")
    is_max_valid = validate_entry(max_wavelength_spinbox, error_message_max_wavelength, validate_integer, "Please enter a valid integer for Max. Wavelength")
    is_bitdepth_valid = validate_entry(bitdepth_entry, error_message_bitdepth, validate_float, "Please enter a valid float for Bit Depth")
    is_exposure_time_valid = validate_entry(exposure_time_entry, error_message_exposure_time, validate_float, "Please enter a valid float for Exposure time")

    if is_min_valid and is_max_valid and is_bitdepth_valid and is_exposure_time_valid:
        is_min_smaller_max = min_smaller_max((min_wavelength_spinbox, max_wavelength_spinbox), error_message_max_wavelength,  "Max. Wavelength must be bigger than Min. Wavelength!")
        if is_min_smaller_max:
            output = f"Min. Wavelength [nm]: {min_wavelength}\nMax. Wavelength [nm]: {max_wavelength}\nBit depth: {bitdepth}\nExposure Time [µs]: {exposure_time}"
            output_text.config(state=tk.NORMAL)
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, output)
            output_text.config(state=tk.DISABLED)
            #TODO: initialize CameraFilterSynronizer here and display tif file (in another window)
            syncroniser = CameraFilterSynronizer(wavelengths=[ int(min_wavelength) + i for i in range(int(max_wavelength)-int(min_wavelength)+1)],
                                        tag_bitdepth = int(bitdepth),
                                        tag_exposure= int(exposure_time)
                                        )
            syncroniser.gatherImages(
                output_dir = os.path.abspath(r'.'),
                filename = 'test_gui.tif',
                )
            syncroniser.cleanup()

#main window
root = tk.Tk()
root.title("Camera Filter Synchronizer")

error_message_min_wavelength = tk.Label(root, text="", foreground="red")
error_message_max_wavelength = tk.Label(root, text="", foreground="red")
error_message_bitdepth = tk.Label(root, text="", foreground="red")
error_message_exposure_time = tk.Label(root, text="", foreground="red")

#Spinbox for Min. Wavelength (Integer)
label1 = tk.Label(root, text="Min. Wavelength [nm]:")
min_wavelength_spinbox = tk.Spinbox(root, from_=0, to=10000, increment=1)
min_wavelength_spinbox.delete(0, "end")
min_wavelength_spinbox.insert(0, 550)


#Spinbox for Max. Wavelength (Float)
label2 = tk.Label(root, text="Max. Wavelength [nm]:")
max_wavelength_spinbox = tk.Spinbox(root, from_=0, to=10000, increment=1)
max_wavelength_spinbox.delete(0, "end")
max_wavelength_spinbox.insert(0, 570)

label3 = tk.Label(root, text="Bit depth:")
bitdepth_entry = tk.Entry(root)
bitdepth_entry.insert(0, 32768)

label4 = tk.Label(root, text="Exposure Time [µs]:")
exposure_time_entry = tk.Entry(root)
exposure_time_entry.insert(0, 5000000)

tif_view_Button = tk.Button(root, text = "show Images", command=open_window_tif_view)
run_button = tk.Button(root, text="Collect Images", command=run_script)


output_text = tk.Text(root, state=tk.DISABLED, wrap=tk.WORD, width=40, height=10)


label1.grid(row=0, column=0)
min_wavelength_spinbox.grid(row=0, column=1)
error_message_min_wavelength.grid(row=0, column=2)

label2.grid(row=1, column=0)
max_wavelength_spinbox.grid(row=1, column=1)
error_message_max_wavelength.grid(row=1, column=2)

label3.grid(row=2, column=0)
bitdepth_entry.grid(row=2, column=1)
label4.grid(row=3, column=0)
error_message_bitdepth.grid(row=2, column=2)

exposure_time_entry.grid(row=3, column=1)
run_button.grid(row=4, column=0, columnspan=2)
tif_view_Button.grid(row=5, column=0, columnspan=2)
output_text.grid(row=6, column=0, columnspan=2)
error_message_exposure_time.grid(row=3, column=2)


root.mainloop()
