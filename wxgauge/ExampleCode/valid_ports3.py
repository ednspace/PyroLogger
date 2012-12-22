
#!/usr/bin/python
import serial, os, sys
#####################################################################
# Find our devices
#####################################################################
#
# This section will query the available ports, find the serial
#   ports and scan them for devices.  Currently, these devices
#   are set to be a Stanford DS345 function generator and
#   a Stanford SR850 Lockin amplifier.
#
# If the search fails and/or you know where your devices are,
#   comment out this section and define the device ports in the
#   changeable parameter section below.
#####################################################################

# Get list of files in /dev
cd = os.getcwd()
os.chdir("/dev")
dirdev = os.getcwd()
fileList = os.listdir(dirdev)

validPorts = list() 
validPortCount = 0

# Find the files that start with ttyUSB, USB connection
for file in fileList:
  if file.startswith("ttyUSB"):
    try:
      sp = serial.Serial(file) 
      validPortCount += 1
      validPorts.append(sp.getPort()) 
    except serial.SerialException:
      pass

# Find the files that start with ttyS, 9 pin serial connection
for file in fileList:
  if file.startswith("ttyS"):
    try:
      sp = serial.Serial(file) 
      validPortCount += 1
      validPorts.append(sp.getPort()) 
    except serial.SerialException:
      pass

# Write to the shell the available ports
print "\n"
print "[HAL] I have found ", validPortCount, "valid ports"
print validPorts
