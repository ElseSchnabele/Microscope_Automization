import pandas as pd
import numpy as np
import tifffile as tif


class ImageNormalizer:
    def __init__(self, calibration_file_path):
        try:
            calib = tif.imread(calibration_file_path)
            #assume calib file always contains whole spectrum covered by Kurios
            calib = dict([(x+430, calib[x]) for x in range(301)])
            self._calib = calib
        except Exception:
            print('Calibration File not found does not match expected wavelengths (430nm-730nm)!')
    
    def normalize_image(self, wavelength, input_image):
        calib_image = self._calib[wavelength]
        try:
            return input_image/calib_image
        except Exception as e:
            print(f'cannot normalize image, maybe wrong format: {e}')
            
    

    