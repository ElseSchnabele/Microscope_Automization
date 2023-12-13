# Microscope_Automization
A Microscope Automatization Project by Jan-Niklas Topf and Frederick Krafft 

Documentation: [Documentation](./html/index.html)
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
Note that the Power Calibrator is not implemented yet and would be necessary to establish a relation between the intensity captured by the camera and the total incident/reflected power distribution.
## GUI Usage 

The main graphical user interface offers the initialization of a new measurement series using the Synchronizer and displaying existing data in a Viewer subroutine. The user flow is visualized in the following:
```mermaid
flowchart TD
    B["Main Window<br>- set Wavelength min and max<br>- set exposure time<br>- set filename<br>- select calibration file"]
    B -->|collect image| C["Collects images for the set wavelengths in a tif file.<br>The values for the wavelength interval are stored in the filename."]
    B -->|Show images| D("Opens the window where the gathered images can be displayed")
    D -->|Load Tif| E("Opens the plot to show the image. The slider can be used to change the visible page of the tif file")
    E -->|one click| F("Shows the spectrum for the clicked location")
    E -->|drag mouse| G("Shows the mean spectrum for the highlighted area")

```
## Image Processing
The synchronizer useses reference intensity data to normalize the images, which was captured using a reference white scattering sample as the target. Thus the data is displayed in a relative scale to the corresponding incident flux density. After the normalization one could implement a power calibrator, which would put the captured intensity on the camera in relation to the total incident power. The flow can be visualized as following (Power calibrator not implemented!):
```mermaid
flowchart LR
    A[Raw Image]
    A -->|Normalize| B[Normalized Image]
    B -->|Get Power Values| C[Power Values]
    style C stroke-dasharray: 5, 5
    C -->|Output| D[Output Image]

```
