#!/usr/bin/python
import serial

for i in range(256):
    try:
         print i,
         s = serial.Serial(i)
         print s.portstr
         s.close()
    except serial.SerialException:
         print
