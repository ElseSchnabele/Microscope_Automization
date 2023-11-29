import time
import pandas as pd
import numpy as np
import os
try:
    from KURIOS_COMMAND_LIB import *
except OSError as ex:
    print("Warning:",ex)
from datetime import datetime
from ctypes import cdll,c_long, c_ulong, c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int,c_int16,c_double, sizeof, c_voidp
from TLPM import TLPM
import time
from ThorlabsPM100 import ThorlabsPM100, USBTMC

import pyvisa
from ThorlabsPM100 import ThorlabsPM100


class PowerCalibrator():
    def __init__(self) -> None:
        #try to access Kurios
        devs = KuriosListDevices()
        print(devs)
        if(len(devs) <= 0):
            print('There is no devices connected')
            exit()
        Kurios = devs[0] #get serial number
        hdl = KuriosOpen(Kurios[0],115200,3)
        self._hdl = hdl
        #try to access powermeter
        tlPM = TLPM()
        deviceCount = c_uint32()
        tlPM.findRsrc(byref(deviceCount))
        print("devices found: " + str(deviceCount.value))
        #get device name
        resourceName = create_string_buffer(1024)
        for i in range(0, deviceCount.value):
            tlPM.getRsrcName(c_int(i), resourceName)
            print(c_char_p(resourceName.raw).value)
            break
        resourceName = c_char_p(resourceName.raw).value.decode('utf-8')
        self._tlPM = tlPM
        rm = pyvisa.ResourceManager()
        inst = rm.open_resource(resourceName, timeout=1)
        power_meter = ThorlabsPM100(inst=inst)
        power_meter.system.beeper.immediate() 
        #set power range to auto to provide maximum accuracy
        power_meter.sense.power.dc.range.auto = "ON"
        time.sleep(.5)
        print("PM Measurement type :", power_meter.getconfigure)
        print("PM Wavelength       :", power_meter.sense.correction.wavelength)
        self._power_meter = power_meter
                
    def calibrate(self, min_wavelength, max_wavelength, csv_name):
        
        wavelength_interval =[min_wavelength+i for i in range(max_wavelength-min_wavelength+1)]
        measurements = {
            "wavelengths": np.array([]),
            "power_meas": np.array([]),
            "std_power_meas": np.array([])
        }
        for wl in wavelength_interval:
            KuriosSetWavelength(self._hdl, wl)
            time.sleep(0.1)
            #take mean of 100 measurements
            mes = np.array([self._power_meter.read for _ in range(100)])
            measurements["power_meas"] =np.append(measurements["power_meas"], mes.mean())
            measurements["std_power_meas"]= np.append(measurements["std_power_meas"], mes.std())
            measurements["wavelengths"]= np.append(measurements["wavelengths"], wl)
            print(mes.mean())
        
        df = pd.DataFrame(measurements)
        output_folder = 'PowerCalibrationFiles' 
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        df.to_csv(os.path.join(output_folder, csv_name), index=False)

    def cleanup(self):
        KuriosClose(self._hdl)
        self._tlPM.close()
        
    def load_calib(self):
        #TODO load and process raw CSV data
        pass
    
if __name__ == "__main__":
    calib = PowerCalibrator()
    calib.calibrate(420, 730, 'Calib_x40.csv')
    calib.cleanup()
    