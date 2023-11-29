import tkinter as tk
import typing
from tkinter import ttk, filedialog
from PIL import Image, ImageTk 
import subprocess
from Show_TifffileStack import TifStackViewer
from Show_Tiff_matplotlib import TifStackViewer_matplot
from automization import CameraFilterSynronizer
import os

class CFsyncApp:

    def __init__(self, root):
        self.root = root
        root.title("Camera Filter Synchronizer")

        self.error_message_min_wavelength = tk.Label(root, text="", foreground="red")
        self.error_message_max_wavelength = tk.Label(root, text="", foreground="red")
        self.error_message_bitdepth = tk.Label(root, text="", foreground="red")
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

        label3 = tk.Label(root, text="Bit depth:")
        bitdepth_entry = tk.Entry(root)
        bitdepth_entry.insert(0, 32768)
        self.bitdepth_entry = bitdepth_entry

        label4 = tk.Label(root, text="Exposure Time [µs]:")
        exposure_time_entry = tk.Entry(root)
        exposure_time_entry.insert(0, 5000000)
        self.exposure_time_entry = exposure_time_entry

        label5 = tk.Label(root, text="Filename:")
        filename_entry = tk.Entry(root)
        self.filename_entry = filename_entry
        
        # Button zum Öffnen des Ordners
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

        label3.grid(row=2, column=0)
        bitdepth_entry.grid(row=2, column=1)
        self.error_message_bitdepth.grid(row=2, column=2)

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
        min_wavelength = self.min_wavelength_spinbox.get()
        max_wavelength = self.max_wavelength_spinbox.get()
        bitdepth = self.bitdepth_entry.get()
        exposure_time = self.exposure_time_entry.get()
        filename = self.filename_entry.get()
        calibfile = self.selected_file.get()
        calibfolder = self.selected_folder.get()
        is_min_valid = self.validate_entry(self.min_wavelength_spinbox, self.error_message_min_wavelength, self.validate_integer, "Please enter a valid integer for Min. Wavelength!")
        is_max_valid = self.validate_entry(self.max_wavelength_spinbox, self.error_message_max_wavelength, self.validate_integer, "Please enter a valid integer for Max. Wavelength")
        is_bitdepth_valid = self.validate_entry(self.bitdepth_entry, self.error_message_bitdepth, self.validate_float, "Please enter a valid float for Bit Depth")
        is_exposure_time_valid = self.validate_entry(self.exposure_time_entry, self.error_message_exposure_time, self.validate_float, "Please enter a valid float for Exposure time")

        if is_min_valid and is_max_valid and is_bitdepth_valid and is_exposure_time_valid:
            is_min_smaller_max = self.min_smaller_max((self.min_wavelength_spinbox, self.max_wavelength_spinbox), self.error_message_max_wavelength,  "Max. Wavelength must be bigger than Min. Wavelength!")
            if is_min_smaller_max:
                output = f"Min. Wavelength [nm]: {min_wavelength}\nMax. Wavelength [nm]: {max_wavelength}\nBit depth: {bitdepth}\nExposure Time [µs]: {exposure_time}"
                self.output_text.config(state=tk.NORMAL)
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, output)
                self.output_text.config(state=tk.DISABLED)
                syncroniser = CameraFilterSynronizer(wavelengths=[ int(min_wavelength) + i for i in range(int(max_wavelength)-int(min_wavelength)+1)],
                                            tag_bitdepth = int(bitdepth),
                                            tag_exposure= int(exposure_time)
                                            )
                syncroniser.gatherImages(
                    output_dir = os.path.abspath(r'.'),
                    filename = f"{filename}.tif",
                    calib_filepath= os.join(calibfolder,calibfile)
                    )
                syncroniser.cleanup()
    #display error messages
    def display_error_message(label, message):
        label.config(text=message)

    #validation output: Error messages
    def validate_entry(self, entry, error_message_label, validation_function, error_message):
        value = entry.get()
        if validation_function(value):
            self.display_error_message(error_message_label, "")
            return True
        else:
            self.display_error_message(error_message_label, error_message)
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

    def min_smaller_max(self,min_and_max: typing.Tuple, error_message_label, error_message):
        minimum = min_and_max[0].get()
        maximum = min_and_max[1].get()
        
        if int(minimum)< int(maximum):
            self.display_error_message(error_message_label, "")
            return True
        else:
            self.display_error_message(error_message_label, error_message)
            return False

    def open_window_tif_view():
        window_tifView = tk.Toplevel(root)
        window_tifView.title("Display_tiffiles")

        test = TifStackViewer(window_tifView)

        window_tifView.mainloop()


    def open_folder(self):
        folder_path = filedialog.askdirectory()  
        if folder_path:
            self.selected_folder.set(folder_path) 
            self.update_calib_file_dropdown(folder_path) 

    def update_calib_file_dropdown(self, folder_path):
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        self.calib_file_dropdown.destroy() 
        self.calib_file_dropdown = tk.OptionMenu(self.root, self.selected_file, *files)
        self.calib_file_dropdown.grid(row= 6, column= 1)



if __name__ == "__main__":
    root = tk.Tk()
    app = CFsyncApp(root)
    root.mainloop()