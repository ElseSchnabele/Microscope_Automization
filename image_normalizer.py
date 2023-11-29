import pandas as pd
import numpy as np


class ImageNormalizer:
    def __init__(self, input_dict, calibration_file_path):
        self._input_dict = input_dict
        self._calibration_file_path = calibration_file_path
        
    def normalize(self)-> dict:
        try:
            calib = pd.read_csv(self._calibration_file_path, sep= ",", )
        except Exception:
            print('Calibration File not found/ Folder CalibrationFiles cannot be created!')
        #overwrite a copy of input dict
        output_dict = self._input_dict
        max_output = 0
        for j, wl in range(self._input_dict['wavelengths']):
            max_intensity_calib = calib['power_meas'][ np.where(calib['wavelengths'] is wl)]
            #devide trough maximum measured intensity
            output_dict['images'][j] = (output_dict['images'][j]/max_intensity_calib)
            if max(output_dict['images'][j]) > max_output:
                max_output = max(output_dict['images'][j])
                
        #normalize with max 
        #TODO normalize with CameraCalibrator
        for j, image in enumerate(output_dict['images']):
            output_dict['images '][j] = image/max_output*256
        
        return output_dict

    