"""
   DWF Python Example
"""
from ctypes import *
import math
import time
import sys


if sys.platform.startswith("win"):
    dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
    dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
    dwf = cdll.LoadLibrary("libdwf.so")

version = create_string_buffer(16)
dwf.FDwfGetVersion(version)
print("DWF Version: "+str(version.value))

hdwf = c_int(0)
print("Opening first device")
dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

if hdwf.value == 0:
    print("failed to open device")
    szerr = create_string_buffer(512)
    dwf.FDwfGetLastErrorMsg(szerr)
    print(str(szerr.value))
    quit()

print('Connected with Analog Discovey 2')

hzSys = c_double()
dwf.FDwfDigitalOutInternalClockInfo(hdwf, byref(hzSys))#fetches the internal clock frequency and stores it in hzSys
print(hzSys)
# SPI parameters
CPOL = 1 # Clock Polarity
CPHA = 1 # Clock Phase
hzFreq = 1e6 
cBits = 16
rgdData = (2*c_byte)(*[0x99,0x99])#Data sent for write is stored in rgdData by c byte array which is of length 2
print(rgdData)
print(*rgdData)
def hold_first(): #function to set Select Signal high
	print('Hold Start After 0.5s')
	# serialization time length
	dwf.FDwfDigitalOutRunSet(hdwf, c_double(0.1))#Sets the Select signal Low for 0.1 sec
	# DIO 2 Select 
	dwf.FDwfDigitalOutEnableSet(hdwf, c_int(2), c_int(1))
	# output high while DigitalOut not running
	dwf.FDwfDigitalOutIdleSet(hdwf, c_int(2), c_int(2)) # 2=DwfDigitalOutIdleHigh
	# output constant low while running
	dwf.FDwfDigitalOutCounterInitSet(hdwf, c_int(2), c_int(0), c_int(0))
	dwf.FDwfDigitalOutCounterSet(hdwf, c_int(2), c_int(0), c_int(0))

	dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))
	time.sleep(1)#Sets the Select high initially for 1 second

def run_ad2(): #Function to generate SPI signal
  print('In 2nd Part')
  dwf.FDwfDigitalOutRunSet(hdwf, c_double(17e-6))
  # DIO 2 Select
  dwf.FDwfDigitalOutEnableSet(hdwf, c_int(2), c_int(1))
  # set prescaler twice of SPI frequency
  dwf.FDwfDigitalOutDividerSet(hdwf, c_int(2), c_int(int(hzSys.value/hzFreq/0.5)))
  # 14 tick low, 2 tick high
  dwf.FDwfDigitalOutCounterSet(hdwf, c_int(2), c_int(14), c_int(2))

  # DIO 1 Clock
  dwf.FDwfDigitalOutEnableSet(hdwf, c_int(1), c_int(1))
  # set prescaler twice of SPI frequency
  dwf.FDwfDigitalOutDividerSet(hdwf, c_int(1), c_int(int(hzSys.value/hzFreq/2)))
  # 1 tick low, 1 tick high
  dwf.FDwfDigitalOutCounterSet(hdwf, c_int(1), c_int(1), c_int(1))
  # start with low or high based on clock polarity
  dwf.FDwfDigitalOutCounterInitSet(hdwf, c_int(1), c_int(CPOL), c_int(1))
  dwf.FDwfDigitalOutIdleSet(hdwf, c_int(1), c_int(1+CPOL)) # 1=DwfDigitalOutIdleLow 2=DwfDigitalOutIdleHigh
  # DIO 0 Data
  dwf.FDwfDigitalOutEnableSet(hdwf, c_int(0), 1)
  dwf.FDwfDigitalOutTypeSet(hdwf, c_int(0), c_int(1)) # 1=DwfDigitalOutTypeCustom
  # for high active clock, hold the first bit for 1.5 periods 
  dwf.FDwfDigitalOutDividerInitSet(hdwf, c_int(0), c_int(int((1+0.5*CPHA)*hzSys.value/hzFreq))) # SPI frequency, bit frequency 
  dwf.FDwfDigitalOutDividerSet(hdwf, c_int(0), c_int(int(hzSys.value/hzFreq)))
  # data sent out LSB first
  dwf.FDwfDigitalOutDataSet(hdwf, c_int(0), byref(rgdData), c_int(cBits))
  dwf.FDwfDigitalOutConfigure(hdwf, c_int(1))
  print("Generating SPI signal")
  time.sleep(17e-6)#Running the function for 17 micro secs

hold_first()
run_ad2()
