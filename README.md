# Microscope_Automization
A Microscope Automatization Project of Jan Niklas Topf and Frederick Krafft 
## Class Diagram 
The project structure is visualized in the following class diagram:
```mermaid
classDiagram

CFsyncApp o-- CameraFilterSyncronizer: Create Images
CameraFilterSyncronizer --> ImageNormalizer: Normalize Images
CameraFilterSyncronizer --> PowerCalibrator: Pull power values
CFsyncApp o-- TifStackViewer_matplot: Show images
TifStackViewer_matplot o-- ShowSpectra: clickevent
TifStackViewer_matplot o-- ShowSpectra_Area: markevent
    class CFsyncApp {
        +root: TkinterWidget
        -error_message_min_wavelength: Label
        -error_message_max_wavelength: Label
        -error_message_exposure_time: Label
        -min_wavelength_spinbox: Spinbox
        -max_wavelength_spinbox: Spinbox
        -exposure_time_entry: Entry
        -filename_entry: Entry
        -open_folder_button: Button
        -selected_folder: StringVar
        -selected_file: StringVar
        -calib_file_dropdown: OptionMenu
        -output_text: Text

        +__init__(root: TkinterWidget)
        +run_script()
        +display_error_message(label: Label, message: str)
        +validate_entry(entry: Entry, error_message_label: Label, validation_function: function, error_message: str): bool
        +validate_integer(P: str): bool
        +validate_float(P: str): bool
        +min_smaller_max(min_and_max: Tuple, error_message_label: Label, error_message: str): bool
        +open_window_tif_view()
        +open_folder()
        +update_calib_file_dropdown(folder_path: str)
    }
    class CameraFilterSyncronizer {
        -_wavelengths: list
        -_hdl: KuriosHandle
        -_exposure: int
        -_image_width: int
        -_image_height: int
        -_is_color_camera: bool
        -_mono_to_color_sdk: MonoToColorProcessorSDK
        -_mono_to_color_processor: MonoToColorProcessor

        +__init__(wavelengths: list, exposure: int)
        +gatherImages(output_dir: str, filename: str, calib_filepath: str, is_calib: bool)
        +cleanup()
    }
    class PowerCalibrator{
        //TODO: Not Implemented yet!
        -calib
        +calibrate_imagedata(wavelength_interval)
    }
    class ImageNormalizer {
        -_calib: dict

        +__init__(calibration_file_path: str)
        +normalize_image(wavelength: int, input_image: np.ndarray): np.ndarray
    }
    class ShowSpectra {
        -root: tk.Tk
        -x: int
        -y: int
        -filepath: str
        -wavelength_min: int
        -wavelength_max: int
        -figure: plt.Figure
        -ax: plt.Axes
        -canvas: FigureCanvasTkAgg

        +__init__(root: tk.Tk, x: int, y: int, file_path: str, wavelength_min: int, wavelength_max: int)
        +get_pixel_value(slide: int): int
        +build_array_pixel(): np.ndarray
        +show_image(): void
    }
        class ShowSpectra_Area {
        -root: tk.Tk
        -top_left: typing.Tuple
        -bottom_right: typing.Tuple
        -filepath: str
        -wavelength_min: int
        -wavelength_max: int
        -figure: plt.Figure
        -ax: plt.Axes
        -canvas: FigureCanvasTkAgg

        +__init__(root: tk.Tk, topleft: typing.Tuple, bottomright: typing.Tuple, file_path: str, wavelength_min: int, wavelength_max: int)
        +get_pixel_value(slide: int): int
        +build_array_pixel(): np.ndarray
        +show_image(): void
        +crop_matrix_with_corners(matrix: np.ndarray): np.ndarray
    }
    class TifStackViewer_matplot {
        -root: tk.Tk
        -wavelength_intervall: list
        -frame: tk.Frame
        -current_index: int
        -filepath: str
        -load_button: tk.Button
        -slider: tk.Scale
        -fig: plt.Figure
        -ax: plt.Axes
        -canvas: FigureCanvasTkAgg
        -toolbar: NavigationToolbar2Tk
        -last_click_time: dt.datetime
        -x1: int
        -x2: int
        -y1: int
        -y2: int
        -inner_plot: plt.Axes

        +__init__(root: tk.Tk)
        +load_tif_stack(): void



        +load_images_from_tif(file_path: str): list
        +show_image(): void
        +slider_control(value: float): void

        +on_canvas_click(event: Event): void
        +on_canvas_release(event: Event): void
    }
```
## GUI Usage 

The main graphical user interface offers the initialization of a new measurement series using the Synchronizer and displaying existing data in a Viewer subroutine. The user flow is visualized in the following:
``` mermaid
flowchart TD
    B("Main Window
       - set Wavelength min and max
       - set exposure time
       - set filename
       - select calibration file
                        ")
    B -->|collect image|C(Collects images for the set wavelengths in a tif file.
                          The values for the wavelength intervall are stored in the filename.)
    B -->|Show images|D(Opens the window where the gathered images can be displayed)
    D -->|Load Tif|E(Opens the plot to show the image. The slider can be used to change the 
                     visible page of the tif file)
    E -->|one click|F(shows the spectrum for the clicked location)
    E -->|drag mouse|G(shows the mean specrum for the highlighted area)
```
