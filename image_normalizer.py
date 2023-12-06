import pandas as pd
import numpy as np
import tifffile as tif


class ImageNormalizer:
    def __init__(self, calibration_file_path):
        """
        The function initializes an Image Normalizer using a calibration file path, which is then stored as
        a dictionary.
        
        @param calibration_file_path The `calibration_file_path` parameter is a string that represents the
        file path of the calibration file. This file is expected to contain data for the whole spectrum
        covered by Kurios, which ranges from 430nm to 730nm.
        """
        try:
            calib = tif.imread(calibration_file_path)
            #assume calib file always contains whole spectrum covered by Kurios
            calib = dict([(x+430, calib[x]) for x in range(301)])
            self._calib = calib
        except Exception:
            print('Calibration File not found does not match expected wavelengths (430nm-730nm)!')
    
    def normalize_image(self, wavelength, input_image):
        """
        The `normalize_image` function takes a wavelength and an input image, and returns the normalized
        image by dividing the input image by the calibration image for that wavelength.
        
        @param wavelength The wavelength parameter represents the wavelength of the image being normalized.
        @param input_image The input image is the image that you want to normalize. It is the image that you
        want to divide by the calibration image.
        
        @return the normalized image, which is obtained by dividing the input image by the calibration image
        for the given wavelength.
        """
        calib_image = self._calib[wavelength]
        try:
            return input_image/calib_image
        except Exception as e:
            print(f'cannot normalize image, maybe wrong format: {e}')
            
    

    