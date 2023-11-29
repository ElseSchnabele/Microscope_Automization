import re
import time
import numpy as np
import os
import tifffile
import typing
import scipy
from image_normalizer import ImageNormalizer
try:
    from Sensor_lib.KURIOS_COMMAND_LIB import *
except OSError as ex:
    print("Warning:",ex)



from thorlabs_tsi_sdk.tl_camera import TLCameraSDK
from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE





class CameraFilterSynronizer:
    
    def __init__(self, wavelengths: list, tag_bitdepth: int, tag_exposure: int) -> None:
        self._wavelengths = wavelengths
        
        #try to access Kurios
        devs = KuriosListDevices()
        print(devs)
        if(len(devs) <= 0):
            print('There is no devices connected')
            exit()
        Kurios = devs[0] #get serial number
        hdl = KuriosOpen(Kurios[0],115200,3)
        self._hdl = hdl
                        #try to access camera
        with TLCameraSDK() as sdk:
            cameras = sdk.discover_available_cameras()
            if len(cameras) == 0:
                print("Error: no cameras detected!")

            with sdk.open_camera(cameras[0]) as camera:
                #  setup the camera for continuous acquisition
                camera.frames_per_trigger_zero_for_unlimited = 0
                camera.image_poll_timeout_ms = 2000  # 2 second timeout

                # save these values to set for camera later
                self._bit_depth = tag_bitdepth
                self._exposure = tag_exposure

                # need to save the image width and height for color processing
                self._image_width= camera.image_width_pixels
                self._image_height = camera.image_height_pixels

                # initialize a mono to color processor if this is a color camera
                is_color_camera = (camera.camera_sensor_type == SENSOR_TYPE.BAYER)
                self._is_color_camera = is_color_camera
                mono_to_color_sdk = None
                mono_to_color_processor = None
                if is_color_camera:
                    mono_to_color_sdk = MonoToColorProcessorSDK()
                    mono_to_color_processor = mono_to_color_sdk.create_mono_to_color_processor(
                        camera.camera_sensor_type,
                        camera.color_filter_array_phase,
                        camera.get_color_correction_matrix(),
                        camera.get_default_white_balance_matrix(),
                        camera.bit_depth
                    )
                self._mono_to_color_sdk = mono_to_color_sdk
                self._mono_to_color_processor = mono_to_color_processor

                
        
    def gatherImages(self, output_dir: str, filename: str, calib_filepath:str):
        
        # delete image if it exists
        if os.path.exists(output_dir + os.sep + filename):
            os.remove(output_dir + os.sep + filename)
            
                #try to access camera
        with TLCameraSDK() as sdk:
            cameras = sdk.discover_available_cameras()
            if len(cameras) == 0:
                print("Error: no cameras detected!")

            with sdk.open_camera(cameras[0]) as camera:
                #  setup the camera for continuous acquisition
                camera.frames_per_trigger_zero_for_unlimited = 0
                camera.image_poll_timeout_ms = 20000  # 20 second timeout
                camera.arm(2)
                camera.issue_software_trigger()
                time.sleep(1)
                camera.exposure_time_us = self._exposure
                
                #set range of wavelength and iterate

                for wl in self._wavelengths:
                    time.sleep(self._exposure*(10e-7)+0.3)
                    KuriosSetWavelength(self._hdl, wl)
                    frame = camera.get_pending_frame_or_null()
                    if frame is None:
                        raise TimeoutError("Timeout was reached while polling for a frame, program will now exit")
                    image_data = frame.image_buffer
                    if self._is_color_camera:
                        # transform the raw image data into RGB color data
                        image_data= self._mono_to_color_processor.transform_to_48(image_data, self._image_width, self._image_height).reshape(self._image_height, self._image_width, 3)
                    data_dict = {
                        'images': image_data,
                        'wavelengths': self._wavelengths
                    }
                    img_normalizer = ImageNormalizer(data_dict= data_dict, calibration_file_path= calib_filepath)
                    scaled_image_data = ((image_data - image_data.min()) / (image_data.max() - image_data.min()) * 256).astype(np.uint8)
                    
                    with tifffile.TiffWriter(output_dir + os.sep + filename, append=True) as tiff:
                        tiff.save(data=scaled_image_data,  # np.ushort image data array from the camera
                                #compression = 'deflate'# amount of compression (0-9), by default it is uncompressed (0)
                                )
                    
  
                    
    def cleanup(self):
        """
        The function `cleanup` disposes of resources related to a color camera and closes the camera
        connection.
        """
        if self._is_color_camera:
            try:
                self._mono_to_color_processor.dispose()
            except Exception as exception:
                print("Unable to dispose mono to color processor: " + str(exception))
            try:
                self._mono_to_color_sdk.dispose()
            except Exception as exception:
                print("Unable to dispose mono to color sdk: " + str(exception))
        with TLCameraSDK() as sdk:
            cameras = sdk.discover_available_cameras()
            if len(cameras) == 0:
                print("Error: no cameras detected!")

            with sdk.open_camera(cameras[0]) as camera:
                if camera:
                    camera.disarm()  
                if self._hdl:
                    KuriosClose(self._hdl) 

                



if __name__ == "__main__":

    syncroniser = CameraFilterSynronizer(wavelengths=[ x + 550 for x in range(10)],
                                        tag_bitdepth = 32768,
                                        tag_exposure= int(5e6)
                                        )
    syncroniser.gatherImages(
        output_dir = os.path.abspath(r'.'),
        filename = 'test_series1.tif',
        )
    syncroniser.cleanup()


