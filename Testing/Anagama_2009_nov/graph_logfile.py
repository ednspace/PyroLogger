#!/usr/bin/python
"""
Script to Process a log file collected with the Pyro Logger
Grabs reads in the data and produces a Graph against time
allows interactive zooming panning and saving of the graph image
via matplotlib 

This script modified to handle the new USB pyrologger and the wxgauge program.
5-30-2008

Modified to support two thermocouples
5-07-2009
"""
from pylab import *
from matplotlib.dates import HourLocator, MinuteLocator
from matplotlib.ticker import Locator, FormatStrFormatter

filename = 'log.txt'
count = 0
thermofront = []
thermoback = []
date = []
highfront = 0
highback = 0

skip = 0



print "Slurping Raw Data... ummmmmm!!!"






f = open(filename , 'r')
for line in f.readlines():
    if (skip >= 3):
        """Split line up into its individual fields
        and skip over the first 3 lines which is just a comment"""
        fields = line.rsplit('\', \'')
        #Read in the Front and Back Thermocouple Values and do stats
    
        if float(fields[1]) > 150 and float(fields[2]) > 150:
            thermofront.append(fields[1])
            thermoback.append(fields[2])
            #Further Split up the last field and read in the Date Code
            paren = line.rfind(')')
            date.append(line[paren-19:paren-1])
    
            if float(fields[1]) > highfront:
                highfront = float(fields[1])
            
            if float(fields[2]) > highback:
                highback = float(fields[2])
        
    skip = skip + 1
    
    

#Change all the Data to Floats
date_float = map(float, date)
thermo_float_front = map(float, thermofront)
thermo_float_back = map(float, thermoback)


print "High Temperature for Front Thermocouple ==> ", highfront
print "High Temperature for Back Thermocouple ==> " , highback
print "Number of Data Points Collected ==========>",len(date_float)



#Make Pretty PLOT ;)
figure(figsize=(12.5,5.5))
ax = subplot(111)

plot_date(date_float,thermo_float_front, 'r-')
plot_date(date_float,thermo_float_back, 'b-')

# Configure axis info formatters and locators
hourLocator = HourLocator(arange(0,24,1))
minuteLocator = MinuteLocator(arange(0,60,15))
dateFormatter = DateFormatter("%D")
dateFormatter = DateFormatter("%H:%M")
temperatureFormatter = FormatStrFormatter('%.1f F')

ax.xaxis.set_major_locator(hourLocator)
ax.xaxis.set_major_formatter(dateFormatter)
ax.xaxis.set_minor_locator(minuteLocator)

ax.yaxis.set_major_formatter(temperatureFormatter)

# Rotate x labels
xlabels = ax.get_xticklabels()
setp(xlabels,'rotation', 45, fontsize=8)
# Set y labels font 8
ylabels = ax.get_yticklabels()
setp(ylabels,fontsize=8)


title('Woodfire Kiln Temperature')
xlabel('time')
ylabel('temp (F)')



show()

