import re
import time
try:
    from KURIOS_COMMAND_LIB import *
except OSError as ex:
    print("Warning:",ex)

def CommonFunc(serialNumber):
   hdl = KuriosOpen(serialNumber,115200,3)
   #or check by "KuriosIsOpen(devs[0])"
   if(hdl < 0):
       print("Connect ",serialNumber, "fail" )
       return -1
   else:
       print("Connect ",serialNumber, "successful")
      
   result = KuriosIsOpen(serialNumber)
   print("KuriosIsOpen ",result)

   id = []
   result = KuriosGetId(hdl, id)
   if(result<0):
       print("KuriosGetId fail ",result)
   else:
       print(id)
       IDString = id
       for s in IDString:
           SN, CN = GetDeviceSNCN(s)
           print("SN: ", SN, "CN: ", CN)
       if(int(SN) >= 212254) and (int(SN)!= int(CN)):
           print("KURIOS optical head SN# and controller CN# do not match. It is recommended to use matched optical head and controller for optimum factory calibrated performance.")
  
   DeviceStatus = [0]
   DeviceStatusList = {0: 'initialization', 1: 'warm up', 2: 'ready'}
   result = KuriosGetStatus(hdl, DeviceStatus)
   if(result<0):
       print("Get device status fail", result)
   else:
       print("Get device status:", DeviceStatusList.get(DeviceStatus[0]))         
   
   DeviceTem = [0]
   result = KuriosGetTemperature(hdl, DeviceTem)
   if(result<0):
       print("Get device Temperature fail", result)
   else:
       print("Get device Temperature:", DeviceTem)   

   MaxWavelength = [0]
   MinWavelength = [0]
   result = KuriosGetSpecification(hdl, MaxWavelength, MinWavelength)
   if(result<0):
      print("KuriosGetSpecification fail ",result)
   else:
      print("MaxWavelength: ", MaxWavelength, "MinWavelength: ", MinWavelength)

   SpectrumRange = [0]
   SpectrumRangeList = {0: 'Visible', 1: 'NIR'}
   BandwidthMode = [0]
   BandwidthModeList = {0: 'BLACK', 1: 'WIDE', 2: 'MEDIUM', 3: 'NARROW'}
   result = KuriosGetOpticalHeadType(hdl, SpectrumRange, BandwidthMode)
   if(result<0):
      print("KuriosGetOpticalHeadType fail ",result)
   else:
      print("filterSpectrumRange: ", GetDeviceOpticalHeadTypeNumber(SpectrumRange[1], SpectrumRangeList), "availableBandwidthMode: ", GetDeviceOpticalHeadTypeNumber(BandwidthMode[1], BandwidthModeList))
   
   return hdl

def GetDeviceSNCN(IDStr):
    import re
    SNpartern = re.compile('SN(\d{1,10})')
    SNum = re.findall(SNpartern, IDStr)
    CNpartern = re.compile('CN(\d{1,10})')
    CNum = re.findall(CNpartern, IDStr)
    return SNum[0], CNum[0]


def GetDeviceOpticalHeadTypeNumber(hex_string, targe_dict, max_length=4):

    try:
        bin_str = bin(ord(hex_string))

    except Exception as e:
        raise Exception('transert hex {0} to bin error! {1}'.format(hex_string, e))

    parrten = re.compile('0b(\d*)')
    bin_val = parrten.findall(bin_str)[0]
    bin_val_reverse = bin_val[::-1]
    
    target_ls = []    
    for t in range(len(bin_val_reverse)):
        if t < max_length and t in targe_dict.keys():
            if bin_val_reverse[t] == '1':
                target_ls.append(targe_dict[t])
    return target_ls

def SetMainParameters(hdl):

    result = KuriosSetOutputMode(hdl, 1) #1 = manual; 2 = sequenced(internal clock triggered) ; 3 = sequenced(external triggered); 4 = analog signal controlled(  internal clock triggered); 5 = analog signal controlled(external triggered)
    if(result<0):
       print("Set output mode fail", result)
    else:
       print("Set output mode :", "manual")

    OutputMode = [0]
    OutputModeList = {1: 'manual', 2: 'sequenced(internal)', 3: 'sequenced(external)', 4: 'analog signal controlled(  internal)', 5: 'analog signal controlled(external)'}
    result = KuriosGetOutputMode(hdl, OutputMode) 
    if(result<0):
       print("Get output mode fail", result)
    else:
       print("Get output mode:", OutputModeList.get(OutputMode[0])) 


    result = KuriosSetBandwidthMode(hdl, 2) #1 = BLACK; 2 = WIDE; 4 = MEDIUM; 8 = NARROW
    if(result<0):
       print("Set Bandwidth mode fail", result)
    else:
       print("Set Bandwidth mode :", "WIDE")

    BandwidthMode = [0]
    BandwidthModeList = {1: 'BLACK', 2: 'WIDE', 4: 'MEDIUM', 8: 'NARROW'}
    result = KuriosGetBandwidthMode(hdl, BandwidthMode) 
    if(result<0):
       print("Get Bandwidth mode fail", result)
    else:
       print("Get Bandwidth mode:", BandwidthModeList.get(BandwidthMode[0])) 


    result = KuriosSetWavelength(hdl, 550) # the range of wavelength is between MinWavelength and MaxWavelength got in the KuriosGetSpecification function
    if(result<0):
       print("Set Wavelength fail", result)
    else:
       print("Set Wavelength :", "550")

    Wavelength = [0]    
    result = KuriosGetWavelength(hdl, Wavelength) 
    if(result<0):
       print("Get Wavelength fail", result)
    else:
       print("Get Wavelength:", Wavelength) 


    result = KuriosSetTriggerOutSignalMode(hdl, 0) #0 = normal; 1 = flipped
    if(result<0):
       print("Set Trigger Out Signal mode fail", result)
    else:
       print("Set Trigger Out Signal mode :", "normal")

    SignalMode = [0]
    SignalModeList = {0: 'normal', 1: 'flipped'}
    result = KuriosGetTriggerOutSignalMode(hdl, SignalMode) 
    if(result<0):
       print("Get Trigger Out Signal mode fail", result)
    else:
       print("Get Trigger Out Signal mode:", SignalModeList.get(SignalMode[0])) 

def SetSequence(hdl):

    result = KuriosSetOutputMode(hdl, 2) #1 = manual; 2 = sequenced(internal clock triggered) ; 3 = sequenced(external triggered); 4 = analog signal controlled(  internal clock triggered); 5 = analog signal controlled(external triggered)
    if(result<0):
       print("Set output mode fail", result)
    else:
       print("Set output mode :", "sequenced(internal clock triggered)")

    OutputMode = [0]
    OutputModeList = {1: 'manual', 2: 'sequenced(internal)', 3: 'sequenced(external)', 4: 'analog signal controlled(  internal)', 5: 'analog signal controlled(external)'}
    result = KuriosGetOutputMode(hdl, OutputMode) 
    if(result<0):
       print("Get output mode fail", result)
    else:
       print("Get output mode:", OutputModeList.get(OutputMode[0]))

    result = KuriosSetSequenceStepData(hdl, 1, 550, 1000, 4)
    if(result<0):
       print("Set Sequence Step Data fail", result)
    else:
       print("Set Sequence Step Data :", "Index:1, Wavelength: 550nm, Interval: 1000ms, BandwidthMode: MEDIUM")
       
    Wavelength = [0]
    Interval = [0]
    BandwidthMode = [0]
    BandwidthModeList = {2: 'WIDE', 4: 'MEDIUM', 8: 'NARROW'}
    result = KuriosGetSequenceStepData(hdl, 1, Wavelength, Interval, BandwidthMode)
    if(result<0):
       print("Get Sequence Step 1 Data fail", result)
    else:
       print("Get  Sequence Step 1 Data: Wavelength: ", Wavelength[0], "Interval: ", Interval[0], "BandwidthMode: ", BandwidthModeList.get(BandwidthMode[0])) 
       
    
    result = KuriosSetInsertSequenceStep(hdl, 2, 600, 2000, 2)
    if(result<0):
       print("Set Insert Sequence Step Data fail", result)
    else:
       print("Set Insert Sequence Step Data :", "Index: 2, Wavelength: 600nm, Interval: 2000ms, BandwidthMode: WIDE")
       
    AllSequenceData = []
    result = KuriosGetAllSequenceData(hdl, AllSequenceData)
    if(result<0):
       print("Get All Sequence Data fail", result)
    else:
       print("Get All Sequence Data: ", AllSequenceData) 


    SequenceLength = [0]
    result = KuriosGetSequenceLength(hdl, SequenceLength)
    if(result<0):
       print("Get Sequence Length fail", result)
    else:
       print("Get Sequence Length: ", SequenceLength[0])


    result = KuriosSetDefaultWavelengthForSequence(hdl, 650)
    if(result<0):
       print("Set Default Wavelength For Sequence fail", result)
    else:
       print("Set Default Wavelength For Sequence: ", "650nm")

    DefaultWavelength = [0]
    result = KuriosGetDefaultWavelengthForSequence(hdl, DefaultWavelength)
    if(result<0):
       print("Get Default Wavelength For Sequence fail", result)
    else:
       print("Get Default Wavelength For Sequence: ", DefaultWavelength[0])


    result = KuriosSetDefaultBandwidthForSequence(hdl, 2)
    if(result<0):
       print("Set Default Bandwidth For Sequence fail", result)
    else:
       print("Set Default Bandwidth For Sequence: ", "WIDE")

    DefaultBandwidth = [0]
    DefaultBandwidthList = {2: 'WIDE', 4: 'MEDIUM', 8: 'NARROW'}
    result = KuriosGetDefaultBandwidthForSequence(hdl, DefaultBandwidth)
    if(result<0):
       print("Get Default Bandwidth For Sequence fail", result)
    else:
       print("Get Default Bandwidth For Sequence: ", DefaultBandwidthList.get(DefaultBandwidth[0]))


    result = KuriosSetDefaultTimeIntervalForSequence(hdl,3000)
    if(result<0):
       print("Set Default Interval For Sequence fail", result)
    else:
       print("Set Default Interval For Sequence: ", "3000ms")

    DefaultInterval = [0]
    result = KuriosGetDefaultTimeIntervalForSequence(hdl, DefaultInterval)
    if(result<0):
       print("Get Default Interval For Sequence fail", result)
    else:
       print("Get Default Interval For Sequence: ", DefaultInterval[0])


    AllSequenceData = []
    result = KuriosGetAllSequenceData(hdl, AllSequenceData)
    if(result<0):
       print("Get All Sequence Data fail", result)
    else:
       print("Get All Sequence Data: ", AllSequenceData) 
       
       
    result = KuriosSetDeleteSequenceStep(hdl, 2)
    if(result<0):
       print("Set Delete Sequence Step fail", result)
    else:
       print("Set Delete Sequence Step: ", "2")

    result = KuriosSetDeleteSequenceStep(hdl, 1)
    if(result<0):
       print("Set Delete Sequence Step fail", result)
    else:
       print("Set Delete Sequence Step: ", "1")
       
       
    AllSequenceData = []
    result = KuriosGetAllSequenceData(hdl, AllSequenceData)
    if(result<0):
       print("Get All Sequence Data fail", result)
    else:
       print("Get All Sequence Data: ", AllSequenceData)  



def main():
    print("*** Kurios device python example ***")
    try:
        devs = KuriosListDevices()
        print(devs)
        if(len(devs)<=0):
           print('There is no devices connected')
           exit()

        Kurios = devs[0] #get serial number

        hdl = CommonFunc(Kurios[0]) #open device and get parameters
        print("---------------------------Device initialize finished-------------------------")
        SetMainParameters(hdl) #set main parameters

        print("---------------------------Set main parameters finnished-------------------------")
        SetSequence(hdl) 
        wavelengths = [x+550 for x in range(100)]
        for wl in wavelengths:
           KuriosSetWavelength(hdl, wl)
           time.sleep(1)
        print("---------------------------Set sequence finnished-------------------------")

        result = KuriosClose(hdl)
        if(result == 0):
            print("Kurios Close successfully!")
        else:
            print("Kurios Close fail", result)
        
    except Exception as ex:
        print("Warning:", ex)
    print("*** End ***")
    input()
main()


