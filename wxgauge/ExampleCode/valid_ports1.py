#!/usr/bin/python
import serial
ports = []

for i in range(256):
    try:
        s = serial.Serial(i)
        if s.portstr != "":
            ports.append(s.portstr)
            
            
        s.close()
    except serial.SerialException:
        pass
for port in ports:
    print port
