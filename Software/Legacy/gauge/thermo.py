#!/usr/bin/python

import pygame,sys,os,math,matplotlib
from datetime import datetime
from pygame.locals import *
from matplotlib.dates import date2num
from matplotlib.dates import num2date
from matplotlib.dates import DateFormatter
from matplotlib.dates import HourLocator, MinuteLocator
from matplotlib.ticker import Locator, FormatStrFormatter
 
from time import gmtime, strftime
matplotlib.use('Agg')
import pylab
#from pylab import *


import thermo_functions
from thermo_functions import *

class Thermometer:
    def __init__ (self,scale,x,y,filename) :
        self.scale=scale
        self.filename=filename
        self.x=x
        self.y=y
        self.gauge = os.path.join("images",self.filename)
        self.background = pygame.image.load(self.gauge).convert()
        self.composite = pygame.Surface(self.background.get_size())
        self.font = pygame.font.Font(None, 20)
    def update_gauge(self,temp):
        temp = round(temp,2)
        if(self.scale == 'amb_F'):  #Ambient Farenheit Scale
            self.length = 338 - ((temp * 3.2) - 48)
        if(self.scale == 'kiln_F_H'): #Kiln Farenheit High Scale
            self.length = 338 - ((temp * .16) - 64)
        if(self.scale == 'kiln_F_L'): #Kiln Farenheit Low Scale
            self.length = 100 + temp
        if self.length > 330:
            self.length = 330

        self.composite.blit(self.background, (0,0))
        self.lastrect = pygame.draw.line(self.composite,(255,0,0), (57,330), (57, self.length),4)
        screen.blit(self.composite, (self.x,self.y)) #relitave position of composite on screen
        
        degree_symbol = unichr(176).encode("latin-1")
        blank = self.font.render('         '+degree_symbol+'F',True,(255,255,255),(0,0,255))
        screen.blit(blank, (self.x+40,self.y+360))
        
        text = self.font.render(str(temp),True,(255,255,255),(0,0,255))
        screen.blit(text, (self.x+40,self.y+360))
	    
        return

class Button:
    def __init__ (self,x,y,width,height,filename) :
        self.filename = filename
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.button = os.path.join("images",self.filename)
        self.surface = pygame.image.load(self.button)
        screen.blit(self.surface,(self.x,self.y))
        self.rect = pygame.Rect(self.x,self.y,self.width,self.height)
       
class Sensor:
    def __init__ (self,id_num) :
        self.id_num = id_num
        

def GetTemp():
    digi = os.popen("digitemp -t 1 -q -c /etc/digitemp.conf -o \%F")
    f = digi.readlines()
    digi.close()
    #return float(f[0].split()[1])
    return float(f[0])

def input(events):
    global zoom
    global kiln_temp
    global date 
    for event in events: 
        if event.type == QUIT: 
            sys.exit(0)
        if event.type == MOUSEBUTTONDOWN:
            if button0.rect.collidepoint(event.pos) == 1 and event.button == 1:
                print "Your Pressed the load Button" 
            if button1.rect.collidepoint(event.pos) == 1 and event.button == 1:
                print "You Pressed the save Button"
                save_data(kiln_temp,date)                
            if button2.rect.collidepoint(event.pos) == 1 and event.button == 1:
                print "Your Pressed the Zoom Button"
                zoom = not zoom
            if button3.rect.collidepoint(event.pos) == 1 and event.button == 1:
                print "You Pressed the clear Button"
                kiln_temp = []
                date = []
            if button4.rect.collidepoint(event.pos) == 1 and event.button == 1:
                print "You Pressed the start Button"  
            if button5.rect.collidepoint(event.pos) == 1 and event.button == 1:
                print "You Pressed the stop Button"    
                 
        #else: 
        #    print event
         

    
def load_graph():
    pylab.figure(num = 1, figsize=(6, 3))
    ax = pylab.gca() #get the current graphics region 
    #Set the axes position with pos = [left, bottom, width, height]
    ax.set_position([.1,.15,.8,.75])
    if zoom == False:
        print "zoom = False"
        pylab.plot_date(date, kiln_temp, 'r-', linewidth = 1)
    if zoom == True:
        print "zoom = True"
        zoom_date = date[(len(date)-zoom_level):]
        zoom_kiln_temp = kiln_temp[(len(kiln_temp)-zoom_level):]
        pylab.plot(zoom_date, zoom_kiln_temp, 'r-', linewidth = 1)
    
    pylab.title(r"Kiln Temperature")
    ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
    xlabels = ax.get_xticklabels()
    #pylab.setp(xlabels,'rotation', 45, fontsize=10)

    ylabels = ax.get_yticklabels()
    #pylab.setp(ylabels,fontsize=10)
    
    pylab.savefig('graph.png')
    pylab.close(1)
    graph = os.path.join("","graph.png")
    graph_surface = pygame.image.load(graph).convert()
    screen.blit(graph_surface, (100,30))
    
    

    """
    #Borrowed Code to Pull info from...
    # Configure axis info formatters and locators
    hourLocator = HourLocator()
    minuteLocator = MinuteLocator(range(0,60,15))
    dateFormatter = DateFormatter("%H:%M")
    temperatureFormatter = FormatStrFormatter('%.1f C')

    ax.xaxis.set_major_locator(hourLocator)
    ax.xaxis.set_major_formatter(dateFormatter)
    ax.xaxis.set_minor_locator(minuteLocator)
    ax.yaxis.set_major_formatter(temperatureFormatter)

    # Enable grid just for Y-axis
    ax.yaxis.grid(True, linewidth=0.3)

    # Define plot ranges. 
    pylab.axis([min(timeValues),max(timeValues),20,30])

    # Set title
    pylab.title(r"Kiln Temperature")
    pylab.title("Temperatures %s" % (datetime.fromtimestamp(init).strftime('%d/%m/%y')))    
    """



    
    
def save_data(kiln_temp,date):
    today = datetime.now()
    filename = 'logs/fire_'
    filename += today.strftime("%m-%d-%Y")
    filename += '.txt'
    file = open(filename, 'w')
    
    for i in range(len(kiln_temp)):
        value_1 = "%.2f" % kiln_temp[i]
        value = (value_1,date[i])
        file_line = str(value)
        file.write (file_line)
        file.write ("\n")
    file.close
    
  

#Initialize the Screen
pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Pyro-Logger')

#Fill the Background
background = pygame.Surface(screen.get_size())
background.fill((0, 0, 255))
screen.blit( background, background.get_rect( ) )

#Instantiate the Thermometers
thermo1=Thermometer('amb_F',0,20,'thermo1.png')
thermo2=Thermometer('kiln_F_H',675,20,'thermo2.png')

#Instantiate the Buttons
button0 = Button(150,350,69,46,'load.png')
button1 = Button(219,350,69,46,'save.png')
button2 = Button(288,350,69,46,'zoom.png')
button3 = Button(357,350,69,46,'clear.png')
button4 = Button(538,350,40,46,'start.png')
button5 = Button(588,350,40,46,'stop.png')

#Instantiate the Sensors
sensor1 = Sensor('30ED284B1000008F')
sensor2 = Sensor('3063294B100000BB')

#Constants
#Sensor Variables
zoom = False
zoom_level = 100
zoom_kiln_temp = []
zoom_date = []
kiln_temp = []
date = []

#Averaging Variables
index = 0
average = 0
graph_display = 'false'
#sensor_average=0

#------------------------------------------------
#Main Program Loop
#------------------------------------------------
while(1):
    input(pygame.event.get())
    pygame.display.update()
    
#Get Celcius From First Thermo
    celsius = get_celsius(sensor1.id_num)
    celsius_reverse = reverse_poly(celsius)
    ambient_F=(((celsius*9.0)/5.0)+32)
    for i in range(20):
        input(pygame.event.get())
        pygame.time.wait(50)
        

#Get uV from first Thermo
    uv = get_uv(sensor1.id_num)
    uv = uv + celsius_reverse
    temp_uv = convert_uv(uv)
    kiln_F = (((temp_uv*9.0)/5.0)+32)
    for i in range(20):
        input(pygame.event.get())
        pygame.time.wait(50)
    
    print "kiln Temp===>",kiln_F

    #------------------------------------------------
    #Rolling Average Filter
    #------------------------------------------------
    if len(kiln_temp) > 20:
        sensor_average = 0
        #print kiln_temp[len(kiln_temp)-10:]
        #moving_part = [len(kiln_temp)-10:]
        for sample in kiln_temp[len(kiln_temp)-20:]:    
            sensor_average = sensor_average + sample
        sensor_average = sensor_average / 20
        sensor_average = round(sensor_average,2)
        print "average is ==>", sensor_average
        kiln_F = sensor_average
        
    #Make sure thermo measurement is not less then ambient
    if (kiln_F < ambient_F):
        kiln_F = ambient_F
    #Update the thermometer displays        
    thermo1.update_gauge(ambient_F)
    thermo2.update_gauge(kiln_F)
    
    #Update the Graph
    kiln_temp.append(kiln_F)
    date.append(date2num(datetime.now()))
    load_graph()
    
    
      
       
    
    
    
    
"""
#Old Code from Pyro Logger to incorporate...
#------------------------------------------------
#Print to Screen
#------------------------------------------------   
    print current_sample,"\t",'%.2f'%farenheit_kiln_1,"\t",'%.2f'%farenheit_ambiant_1,"\t",'%.2f'%farenheit_kiln_2,"\t",'%.2f'%farenheit_ambiant_2,"\t",strftime("%a, %d %b %Y %I:%M:%S")
 
#-----------------------------------------------
#Log To File   
#-----------------------------------------------
    save_data(current_sample,farenheit_ambiant_1,farenheit_kiln_1,farenheit_ambiant_2,farenheit_kiln_2,time)

    
#-----------------------------------------------
#Update Graph Variables
#-----------------------------------------------
    date_float=append(date_float,date2num(datetime.now()))
    thermo_front_float=append(thermo_front_float,farenheit_kiln_1)
    thermo_back_float=append(thermo_back_float,farenheit_kiln_2)
    
#Code snippet that list creates a list with all files in a directory
#Use for load graph section of code
import os
path="C:\\somedirectory"  # insert the path to the directory of interest
here
dirList=os.listdir(path)
for fname in dirList:
    print fname

"""

   
