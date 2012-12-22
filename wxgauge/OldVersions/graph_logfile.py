#!/usr/bin/python
"""
Script to Process a log file collected with the Pyro Logger
Grabs reads in the data and produces a Graph against time
allows interactive zooming panning and saving of the graph image
via matplotlib 
"""
from pylab import *

count = 0
thermo_front = []
thermo_back = []
date = []
high_front = 0
high_back = 0


print "Slurping Raw Data... ummmmmm!!!"
f = open('log.txt', 'r')
for line in f.readlines():
    #Split line up into its individual fields
    fields = line.rsplit('\', \'')
    
    #Read in the Front and Back Thermocouple Values and do stats
    thermo_front.append(fields[1])
    if float(fields[1]) > high_front:
        high_front = float(fields[1])

    thermo_back.append(fields[3])  
    if float(fields[3]) > high_back:
        high_back = float(fields[3])
        

    #Further Split up the last field and read in the Date Code
    paren = line.rfind(')')
    date.append(line[paren-19:paren-1])

#Change all the Data to Floats
date_float = map(float, date)
thermo_front_float = map(float, thermo_front)
thermo_back_float = map(float, thermo_back)

#Print some Stats
print "High Temperature for Front Thermocouple ==>",high_front
print "High Temperature for Back Thermocouple ==>",high_back
print "Number of Data Points Collected ==========>",len(date_float)

#Make Pretty PLOT ;)
figure(figsize=(12.5,5.5))
plot_date(date_float,thermo_front_float, 'r-')
plot_date(date_float,thermo_back_float, 'b-')
title('Kiln Temperature Graph')
xlabel('Friday - Tuesday')
ylabel('temp (F)')
legend(["Front", "Back"],loc='upper left')
show()
