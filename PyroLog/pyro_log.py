#!/usr/bin/python
#Revision History

#Adjusted logger program to log data at Rogers Big Wood Fired Kiln
#March 1 2007
#Updated to monitor two thermo couples instead of one
#September 2007
#Changed the logger so that you could address individual 
#Thermocouple Sensors  from the PC without them being
#hard coded in the Pic Firmware
#Added Graphing Capability
#Eric Daine

import serial
import time
from datetime import datetime
from matplotlib.dates import date2num
from matplotlib.dates import num2date
from time import gmtime, strftime
import os
import sys
from pylab import *
from datetime import datetime
from numpy import *



#System Variables
#loop takes 4 sec
#sec_multiple = 26
#sec_multiple = 26
sec_multiple = 5

#Set to 1 to turn on graph
#Set to 0 to turn graph off
graphing = 1


#Turn On Interactive Mode
if graphing == 1:
    print "Turning on Graphing"
    ion()


#Thermocouple address list
#Front
thermo_1 = "30ED284B1000008F"
#Back
thermo_2 = "3063294B100000BB"


#For Linux Serial
#ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)

#For Widows Serial
#ser = serial.Serial(0)

#Function Definitions
def get_faren(address):
	ser.flushInput()
	ser.write("\r")
	ser.write("F")
	ser.write(address)
	ser.write("\r")
	line = ser.read(5)
	ser.flushInput()
	return line

def get_celsius(address):
	ser.flushInput()
	ser.write("\r")
	ser.write("C")
	ser.write(address)
	ser.write("\r")
	line = ser.read(5)
	ser.flushInput()
	return line

def get_uv(address):
	ser.flushInput()
	ser.write("\r")
	ser.write("K")
	ser.write(address)
	ser.write("\r")
	line = ser.read(9)
	ser.flushInput()
	return line

def reverse_poly(x):
    #Takes in Temp in deg C and gives back Uv's, used to adjust for ambiant temperature
    coeffecients = [-1.76E1, 3.8921E1, 1.8559E-2, -9.9458E-5, 3.18409E-7, -5.607284E-10, 5.607506E-13, -3.20207E-16, 9.71511E-20, -1.21047E-23]

    a0 = 1.18597600000E2
    a1 = -0.118343200000E-3
    a2 = 0.126968600000E3

    e = 2.71828182

    result2 = 0.0
    added = 0.0
    power = 0

    exponent_value = x - a2
    exponent_value = exponent_value * exponent_value
    exponent_value = a1 * exponent_value
    added = pow(e,exponent_value)
    added = added * a0

    for c in coeffecients:
        result2 = (result2 + c * pow(x,power))
        power = power + 1
    result2 = result2 + added
    result2 = result2 / 1000000
    return (result2)

def convert_uv(uv):
    coefficients = [0.226584602, 24152.10900, 67233.4248, 2210340.682, -860963914.9, 4.83506e10, -1.18452e12, 1.38690e13, -6.33708e13]
    result1 = 0.0
    power = 0
    for c in coefficients:
        result1 = result1 + c * pow(uv,power)
        power = power + 1
    result1 = round(result1,2)
    return result1

def save_data(reading_num,a1,k1,a2,k2,time):
    file = open('log.txt', 'a')
    #file2 = open('graph.txt' , 'a')
    value_1 = "%.2f" % a1
    value_2 = "%.2f" % k1
    value_3 = "%.2f" % a2
    value_4 = "%.2f" % k2
    value_5 = strftime("%a, %d %b %Y %H:%M:%S")
    value_6 = "%.11f" % date2num(datetime.now())
 
	#value = (reading_num,value_1,value_2,value_3,value_4,strftime("%a, %d %b %Y %H:%M:%S"))
    value = (reading_num,value_1,value_2,value_3,value_4,value_5,value_6)
    #value2 = (value_2,value_4)
    file_line = str(value)
    #file_line2 = str(value2)
    file.write (file_line)
    #file2.write (file_line2)
    file.write ("\n")
    #file2.write ("\n")
    file.close
    #file2.close


#Main Program Loop
#Logs Data to file and time stamps it...
#Also Displays output to screen...


if (graphing == 1):
    date_float = []
    thermo_front_float = []
    thermo_back_float= []

loop = 1

if (os.path.exists('log.txt') & (graphing ==0)):
    print "Found Log text"
    print "Slurping Raw Data... ummmmmm!!!"
    current_sample = 1
    f = open('log.txt', 'r')
    for line in f.readlines():
        current_sample = current_sample + 1

elif (os.path.exists('log.txt') & (graphing ==1)):
    print "Found Log text"
    print "Slurping Raw Data... ummmmmm!!!"
    current_sample = 1
    thermo_front = []
    thermo_back = []
    date = []
    
    
    f = open('log.txt', 'r')
    for line in f.readlines():
        fields = line.rsplit('\', \'')
        thermo_front.append(fields[1])
        thermo_back.append(fields[3])

        paren = line.rfind(')')
        date.append(line[paren-19:paren-1])
        current_sample = current_sample + 1
#Variables for the Graph
    date_float = map(float, date)
    thermo_front_float = map(float, thermo_front)
    thermo_back_float = map(float, thermo_back)
    
else:
    print "No log file found"
    current_sample=1
    

print "Setting current sample to ==>",current_sample



while(1):
#while(current_sample <= num_samples):
#Get Celcius From First Thermo
    celsius_1 = get_celsius(thermo_1)
    celsius_float_1 = float(celsius_1)
    celsius_reverse_1 = reverse_poly(celsius_float_1)
    farenheit_ambiant_1=(((celsius_float_1*9.0)/5.0)+32)
    time.sleep(1)
#Get Celcius From Second Thermo
    celsius_2 = get_celsius(thermo_2)
    celsius_float_2 = float(celsius_2)
    celsius_reverse_2 = reverse_poly(celsius_float_2)
    farenheit_ambiant_2=(((celsius_float_2*9.0)/5.0)+32)
    time.sleep(1)
#Get uV from first Thermo
    uv_1 = get_uv(thermo_1)
    uv_float_1 = float(uv_1)
    uv_float_1 = uv_float_1 + celsius_reverse_1
    temp_uv_1 = convert_uv(uv_float_1)
    farenheit_kiln_1 = (((temp_uv_1*9.0)/5.0)+32)
    if (farenheit_kiln_1 < farenheit_ambiant_1):
        temp_uv_1 = celsius_float_1
        farenheit_kiln_1 = farenheit_ambiant_1
    time.sleep(1)
#Get uV from second Thermo
    uv_2 = get_uv(thermo_2)
    uv_float_2 = float(uv_2)
    uv_float_2 = uv_float_2 + celsius_reverse_2
    temp_uv_2 = convert_uv(uv_float_2)
    farenheit_kiln_2 = (((temp_uv_2*9.0)/5.0)+32)
    if (farenheit_kiln_2 < farenheit_ambiant_2):
        temp_uv_2 = celsius_float_2
        farenheit_kiln_2 = farenheit_ambiant_2
    time.sleep(1)

#------------------------------------------------
#Print to Screen
#------------------------------------------------   
    #print current_sample,"\t",'%.2f'%farenheit_kiln_1,"\t",'%.2f'%farenheit_ambiant_1,"\t",'%.2f'%farenheit_kiln_2,"\t",'%.2f'%farenheit_ambiant_2,"\t",strftime("%a, %d %b %Y %I:%M:%S")
    print current_sample,"\tTemp Front==>",'%.2f'%farenheit_kiln_1,"\tTemp Back==>",'%.2f'%farenheit_kiln_2,"\t",strftime("%a-%I:%M:%S")
    
#-----------------------------------------------
#Log To File   
#-----------------------------------------------
    save_data(current_sample,farenheit_ambiant_1,farenheit_kiln_1,farenheit_ambiant_2,farenheit_kiln_2,time)
    
#-----------------------------------------------
#Update Graph Variables
#-----------------------------------------------
    if (graphing == 1):          
        date_float=append(date_float,date2num(datetime.now()))
        thermo_front_float=append(thermo_front_float,farenheit_kiln_1)
        thermo_back_float=append(thermo_back_float,farenheit_kiln_2)
#-------------------------------------------------
#Update the Graph
#-------------------------------------------------   
    if ((loop == 10) & (graphing == 1)):
        loop = 1
        clf()
        close()        
        #print "Setting up the Graph"
        #set_minor_locator(HourLocator(12))
        figure(figsize=(13,5.5))
        title('Kiln Temperature Graph')
        xlabel('time')
        ylabel('temp (F)')
        
        #line_front, = plot_date(date_float,thermo_back_float,'r-')
        #line_back, = plot_date(date_float,thermo_front_float, 'b-')
        
       
        line_front, = plot_date(date_float,thermo_front_float,'r-')
        line_back, = plot_date(date_float,thermo_back_float, 'b-')
        legend(["Front", "Back"])
        
        draw()
    if (graphing == 1):    
        loop = loop + 1
        
    current_sample = current_sample + 1
    time.sleep(sec_multiple)
ser.close
