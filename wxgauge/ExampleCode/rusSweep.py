#! /usr/bin/env python

# This python code uses two queries all available ports searching
#   for two devices, an SRS DS345 function generator and a SRS SR850
#   lock-in amplifier.  Once found, a frequency sweep is made
#   over the user-specified range.  Data is piped real-time to
#   Grace for graphical viewing.
#
# Two non-standard Python modules are used:
#
#  ->Pyserial module from which we get the serial stuff.
#    This is available on the Parnassus web site.
#
#  ->GracePlot module for viewing data realtime (sort of)
#
#
# authors: John Scales, 11/20/02
#          Brian Zadler 05/07/04
#
# Last update: 01/24/06
#####################################################################
#####################################################################
#
# About serial connections: All devices in /dev should have the
#   proper permissions at this point (for PAL machines)
#   If not, this can be changes in
#     /etc/udev/permissions.d/50-udev.permissions
#
#   Find the lines specifying 'ttyS' and 'ttyUSB' and change
#     the permissions to 0666.
#
# The device name depends upon how you connect the device.
#   Use: '/dev/ttyUSBx' (x is a value, 0->whatever) for USB
#     connection
#
#   KNOWN ISSUE:
#     "serial.serialutil.SerialException: Could not open port:"
#   FIX:
#     change permissions on /dev/ttyUSBx to read/write for all via
#     chmod ugoa+rw /dev/ttyUSBx
#     Must be done each time (sadly) or get help from administrator
#
# Use: '/dev/ttySx' (x is the serial port number, which can
#   be found using queryserial.py)
#
# Type 'python queryserial' at the prompt for available ports
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#####################################################################



#####################################################################
# Dependencies
#####################################################################
import serial
from time import gmtime
from time import sleep
from time import localtime
from time import mktime
from string import atof
from string import atoi
from re import split
from posix import system
from GracePlot import *

from serial import Serial
from serial.serialutil import SerialException
import os
import sys
from posix import system
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#####################################################################




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
      sp = Serial(file) 
      validPortCount += 1
      validPorts.append(sp.getPort()) 
    except SerialException:
      pass

# Find the files that start with ttyS, 9 pin serial connection
for file in fileList:
  if file.startswith("ttyS"):
    try:
      sp = Serial(file) 
      validPortCount += 1
      validPorts.append(sp.getPort()) 
    except SerialException:
      pass

# Write to the shell the available ports
print "\n"
print "[HAL] I have found ", validPortCount, "valid ports"
print validPorts


# Find the SR850 by trying all valid ports in the list validPorts
#   Ask each port for ID information via *IDN?
#   The Stanford SR850 returns a list of strings which
#     includes the model number, SR850, so we search for it.
for name in validPorts:
  lockinPortTest  = '/dev/' + name
  lockin = serial.Serial(lockinPortTest,timeout=1, baudrate=19200)
  lockin.write('outx 0 \n')  #write to lockin first
  lockin.write('*IDN? \n')   #gets ID info of the device
  a = lockin.readline()
  lockin.sendBreak()
  lockin.close()
  if a.find('SR850') is not -1: #returns -1 for wrong ports, else N
    lockinPort = lockinPortTest #lockinPort holds the found port
    print 'SR850 Port is: ' + lockinPort
    break
  else:
    print "SR850 Port not found"


# Find the DS345 by trying all valid ports in the list validPorts
#   Ask each port for ID information via *IDN?
#   The Stanford DS345 returns a list of strings which
#     includes the model number, DS345, so we search for it.
for name in validPorts:
  fgenPortTest  = '/dev/' + name
  fgen = serial.Serial(fgenPortTest,timeout=1, baudrate=9600)
  fgen.write('*STB?\n')   #gets status byte, needed?
  fgen.write('*IDN? \n')  #gets the ID information for the device
  a = fgen.readline()
  fgen.sendBreak()
  fgen.close()
  if a.find('DS345') is not -1: #returns -1 for wrong ports, else N
    fgenPort = fgenPortTest     #fgenPort holds the found port
    print 'DS345 Port is: ' + fgenPort
    break
  else:
    print "DS345 Port not found" #better luck next time




# Go back to original directory
os.chdir(cd)
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#####################################################################




#####################################################################
# Important changable parameters
#####################################################################

# Use these if the port querying fails.
#fgenPort  = '/dev/ttyUSB0'
#lockinPort= '/dev/ttyS0'

filenameS = 'testingMg'  # obvious
startFreq   = 20000.      # starting frequency in hertz
stopFreq   = 100001.      # ending frequency in hertz

sweeptime = 60          # sweep time in seconds
vpp       = 10          # peak to peak voltage of fgen
SR        = 8           # sample rate, see table below
TC        = 9           # 300 ms time constant
sens      = 20          # 50 mV sensitivity
trace1    = 1           # Trace 1
trace2    = 2           # Trace 2
trace3    = 3           # Trace 3
trace4    = 12          # Trace 4

nPieces   = 8           # number of pieces to chop the measurement
                        #  into (for higher density data)
ASF       = 1           # scale factor for amplitudes
FSF       = 1000        # scaling for frequency: /1000 outputs in Khz
                        #   /1000000 outputs in MHz (KHz needed for scilab)


# fgen and lockin parameter strings
sweepperiod = '%s' %(1./sweeptime)
vppS        = '%s' % vpp

SRS         = '%s' % SR
TCS         = '%s' % TC
sensS       = '%s' % sens
trace1S     = '%s' % trace1
trace2S     = '%s' % trace2
trace3S     = '%s' % trace3
trace4S     = '%s' % trace4


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#####################################################################




#####################################################################
# Lock-in amplifier parameter reference
#####################################################################
#
#    First, a quick reference to the most changed parameters
# [not a complete list, but the continuations should be obvious]
#
# Sensitivity(0-26)    Time Constant(0-19)   Sample Rate(0-14)
# #################    ###################   #################
#    13  50 muV            4     1 mS            4   1 Hz
#    14 100 muV            5     3 mS            5   2 Hz
#    15 200 muV            6    10 mS            6   4 Hz
#    16 500 muV            7    30 mS            7   8 Hz
#    17   1 mV             8   100 mS            8  16 Hz
#    18   2 mV             9   300 mS            9  32 Hz
#    19   5 mV             10     1 S           10  64 Hz
#    20  10 mV             11     3 S
#
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#####################################################################




#####################################################################
# Function generator
#####################################################################
# Establish serial link
fgen = serial.Serial(fgenPort,timeout=1, baudrate=9600)
print "DS345 serial connection is OPEN:",fgen.isOpen()

# Send parameters for frequency sweep
fgen.write('func 0 \n')                  # sinusoid
fgen.write('mtyp 0 \n')                  # linear sweep
fgen.write('rate ' + sweepperiod + '\n') # sweep rate
fgen.write('mena 1 \n')                  # enable modulation
fgen.write('mdwf 0 \n')                  # single sweep
fgen.write('ampl ' + vppS + 'VP' + '\n')  # set volts peak to peak
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#####################################################################




#####################################################################
# Lock-in amplifier
#####################################################################
# Establish serial link
lockin = serial.Serial(lockinPort,timeout=1, baudrate=19200)

# Send parameters for frequency sweep
lockin.write('outx 0 \n')      # output to rs232.must be done first.
print "SR850 serial connection is OPEN:", lockin.isOpen()

lockin.write('srat ' + SRS + ' \n')
lockin.write('oflt ' + TCS + ' \n')
lockin.write('sens ' + sensS + '\n')

lockin.write('trcd 1,' + trace1S + ',0,0,1 \n')
lockin.write('trcd 2,' + trace2S + ',0,0,1 \n')
lockin.write('trcd 3,' + trace3S + ',0,0,1 \n')
lockin.write('trcd 4,' + trace4S + ',0,0,1 \n')

sweeptime = sweeptime-2                  # synch issue
ssweeptime = '%s' % sweeptime            ## prevents extra points
lockin.write('slen ' + ssweeptime + '\n')
lockin.write('send 0 \n')                # perform a single shot


#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
#####################################################################



#####################################################################
# Acquisition
#####################################################################
# Open a Grace session (leave open)
p = GracePlot()

# Labels, axes properties, line/symbol properties for Grace plot
p.title('All your resonance are belong to us')
p.xaxis(label=Label('Frequency (Hz)',font=5,charsize=1.5),
        tick=Tick(majorgrid=on,majorlinestyle=dashed,majorcolor=blue,
                  minorgrid=off,minorlinestyle=dotted,minorcolor=blue))
p.yaxis(label=Label('Power',font=5,charsize=1.5),
        tick=Tick(majorgrid=on,majorlinestyle=dashed,majorcolor=blue,
                  minorgrid=off,minorlinestyle=dotted,minorcolor=blue))
s1=Symbol(symbol=diamond,size=0.3,fillcolor=red)
l1=Line(type=solid)


# Remember, the total frequency sweep range is being divided
#   into nPieces subranges, we need to calculate the subrange size:
freqSubrangeSize = (stopFreq - startFreq)/nPieces

# Loop over number of subranges (nPieces) in frequency range ()
for thisStepNumber in range(nPieces):  # thisStepNumber ranges from 0 -> nPieces-1

    # Frequency range for THIS subrange
    subStartFreq = startFreq + thisStepNumber * freqSubrangeSize
    subStopFreq = startFreq + (thisStepNumber+1) * freqSubrangeSize
    # Convert the start and stop frequencies to strings
    subStartFreqS = '%s' % subStartFreq
    subStopFreqS = '%s' % subStopFreq
    print '\n \n'
    print 'Frequency subRange: '+subStartFreqS+'-'+subStopFreqS
    fgen.write('spfr' + subStopFreqS + '\n')         # stop frequency
    fgen.write('stfr' + subStartFreqS + '\n')        # start frequency
    

    # Start lockin recording
    lockin.write('rest \n')                  # reset the amplfier
    fgen.write('tsrc 0 \n')                  # enable single trigger
    print 'We set you up the bomb'
    sleep(4)                                 # pause for rs232 lags
    print '(bomb set)'
    fgen.write('*trg \n')                    # trigger the sweep
    sleep(0)                                 # more synch issues
    lockin.write('strt \n')                  # start data acquisition
    print "Doing sweep #" + '%s' % (thisStepNumber+1)
    startTime = mktime(localtime())
    

    runTime = 0   # Keeps track of freqSubrange sweep time
    i = 0         # Dummy variable for logic test for grace plotting
    
    while  runTime < (sweeptime-2): #stop plotting before sweep stops, else error
        
        runTime = mktime(localtime())-startTime #update runTime variable
        print 'Run time: '+ '%s' % runTime + ' of ' + '%s' % sweeptime + ' seconds'


        # Graceplot won't plot a single point at a time, must have >=2 points
        # Get a data point: (f, X^2 + Y^2)
        lockin.write('snap? 1,2,9,3 \n')
        snapData1 = lockin.readline()
        snapData1 = split(',',snapData1)
        #print snapData1
        fTest1=eval(snapData1[2])
        pTest1=ASF*eval(snapData1[0])*eval(snapData1[0])+eval(snapData1[1])*eval(snapData1[1])

        # Get another data point: (f, X^2 + Y^2)
        lockin.write('snap? 1,2,9,3 \n')
        snapData2 = lockin.readline()
        snapData2 = split(',',snapData2)
        fTest2=eval(snapData2[2])
        pTest2=ASF*eval(snapData2[0])*eval(snapData2[0])+eval(snapData2[1])*eval(snapData2[1])
        
        # Make our 2 data points into a list for Graceplot and plot
        d1=Data(x=[fTest1,fTest2],y=[pTest1,pTest2],symbol=s1,line=l1,legend='realpart')
        #print d1
        p.plot(d1)
          
        # Ugly kludge to autoscale after every plotted pair
        if thisStepNumber == 0 and i == 0:
          pTestMin = pTest1
          pTestMax = pTest2
          subStartFreqBase = subStartFreq
          
        if pTest1 > pTest2:
            
          if pTest1 > pTestMax:
            pTestMax = pTest1
          else:
            pass
          
          if pTest2 < pTestMin:
            pTestMin = pTest2
          else:
            pass
              
        else:
                
          if pTest2 > pTestMax:
            pTestMax = pTest2
          else:
            pass
          
          if pTest1 < pTestMin:
            pTestMin = pTest1
          else:
            pass
            
            
        p.xaxis(xmin=subStartFreqBase,xmax=fTest2)
        p.yaxis(ymin=pTestMin,ymax=pTestMax)
        i=i+1
               

    sleep(2)  # wait for sweep to finish

    # Transfer data
    print 'transferring data'
    lockin.write('spts? 1 \n')
    numpts = atoi(lockin.readline())
    numpts = numpts -1
    snumpts = '%s' % numpts
    
    lockin.write('trca? 1,1,' + snumpts + '\n')
    trace1 = lockin.readline()
    tmp1 = split(',',trace1)
    X = tmp1[:-1]
           
    lockin.write('trca? 2,1,' + snumpts + '\n')
    trace2 = lockin.readline()
    tmp2 = split(',',trace2)
    Y = tmp2[:-1]
    
    lockin.write('trca? 4,1,' + snumpts + '\n')
    trace4 = lockin.readline()
    tmp4 = split(',',trace4)
    frequency = tmp4[:-1]

    if thisStepNumber < 10:
        thisStepNumberS = '0' + '%s' %thisStepNumber
    else:
        thisStepNumberS = '%s' %thisStepNumber


    # Save Frequency, X, Y to junkXYN file
    #   {N iterates starting at 00}
    ampfile = './junkXY'+thisStepNumberS
    n = len(frequency)
    fd = open(ampfile,'w')
    for i in range(n-1):
        print >>fd, frequency[i]/FSF, X[i], Y[i]
    fd.close()


    # Convert string data to float data
    dataX=[]
    for dataItem in X:
        dataX.append(float(dataItem))

    dataY=[]
    for dataItem in Y:
        dataY.append(float(dataItem))

    dataF=[]
    for dataItem in frequency:
        dataF.append(float(dataItem))


    # Calculate power X^2 + Y^2
    j=0
    power=[]
    for item in dataX:
        power.append(ASF*ASF*item*item+dataY[j]*dataY[j])
        j = j + 1


    #save [frequency power] for xmgr plotting/fitting
    powerfile = './junkPower_'+ thisStepNumberS
    n = len(frequency)
    fd = open(powerfile,'w')
    for i in range(n-1):
        print >>fd, frequency[i]/FSF, power[i]
    fd.close()


# Write to files, cleaup
system('cat junkXY* > '+filenameS+'_'+str(startFreq)+'-'+str(stopFreq)+'Hz')
system('cat junkPower* > power'+filenameS+'_'+str(startFreq)+'-'+str(stopFreq)+'Hz')
system('rm junk*')



            
