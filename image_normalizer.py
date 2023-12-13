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
            with tif.TiffFile(calibration_file_path) as file:
                # Lesen aller Seiten (Bilder) des TIFFs
                calib_raw = [page.asarray() for page in file.pages]
            #calib_raw = tif.imread(calibration_file_path)
            #assume calib file always contains whole spectrum covered by Kurios
            calib = dict([(x+430, calib_raw[x]) for x in range(301)])
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
        for the given wavelength and then multiplying it by the maximum 8bit value. To allow relative intensity greater than 100%, each pixel is saved as 16bit integer.
        """
        calib_image = self._calib[wavelength]
        try:
            output_image = (input_image/calib_image*2**8).astype(np.uint16)
            
            if output_image.max() > 2**16:
                raise OverflowError('Image Input per pixel channel is larger than 16 bit! Check normalization Files!')
            else:
                return output_image
        except Exception as e:
            print(f'cannot normalize image, maybe wrong format: {e}')
            
    

    