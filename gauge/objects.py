#!/usr/bin/python
import pygame,sys,os,math,matplotlib,time
from datetime import datetime
from pygame.locals import *
from matplotlib.dates import date2num
from matplotlib.dates import num2date
from matplotlib.dates import DateFormatter
 
from time import gmtime, strftime
matplotlib.use('Agg')
import pylab

class Thermometer:
    def __init__ (self,scale,x,y,filename) :
        self.scale=scale
        self.filename=filename
        self.x=x
        self.y=y
        self.gauge = os.path.join("images",self.filename)
        self.background = pygame.image.load(self.gauge).convert()
        self.composite = pygame.Surface(self.background.get_size())
    def update_gauge(self,temp):
        if(self.scale == 'amb_F'):  #Ambient Farenheit Scale
            self.length = 338 - ((temp * 3.2) - 48)
        if(self.scale == 'kiln_F_H'): #Kiln Farenheit High Scale
            self.length = 338 - ((temp * .16) - 64)
        if(self.scale == 'kiln_F_L'): #Kiln Farenheit Low Scale
            self.length = 100 + temp
        self.composite.blit(self.background, (0,0))
        self.lastrect = pygame.draw.line(self.composite,(255,0,0), (57,330), (57, self.length),4)
        screen.blit(self.composite, (self.x,self.y)) #relitave position of composite on screen
	    #blank = font.render('         F',True,(255,255,255),(0,0,255))
	    #screen.blit(blank, (45,380))
	    #temp = round(temp,2)
	    #degree_symbol = unichr(176).encode("latin-1")
	
	    #return 


#Initialize the Screen
pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('Object Tester')

#Fill the Background
background = pygame.Surface(screen.get_size())
background.fill((0, 0, 255))
screen.blit( background, background.get_rect( ) )

def input(events): 
    for event in events: 
        if event.type == QUIT: 
            sys.exit(0)

ambient0=Thermometer('amb_F',0,20,'thermo1.png')
ambient1=Thermometer('amb_F',100,20,'thermo1.png')
ambient2=Thermometer('amb_F',200,20,'thermo1.png')
ambient3=Thermometer('amb_F',300,20,'thermo1.png')
ambient4=Thermometer('amb_F',400,20,'thermo1.png')
ambient5=Thermometer('amb_F',500,20,'thermo1.png')
ambient6=Thermometer('amb_F',600,20,'thermo1.png')

kiln0=Thermometer('kiln_F_H',0,20,'thermo2.png')
kiln1=Thermometer('kiln_F_H',100,20,'thermo2.png')
kiln2=Thermometer('kiln_F_H',200,20,'thermo2.png')
kiln3=Thermometer('kiln_F_H',300,20,'thermo2.png')
kiln4=Thermometer('kiln_F_H',400,20,'thermo2.png')
kiln5=Thermometer('kiln_F_H',500,20,'thermo2.png')
kiln6=Thermometer('kiln_F_H',600,20,'thermo2.png')

while 1:
    for i in range(20,110):
        print i
        ambient0.update_gauge(i)
        ambient1.update_gauge(i+1)
        ambient2.update_gauge(i+2)
        ambient3.update_gauge(i+3)
        ambient4.update_gauge(i+4)
        ambient5.update_gauge(i+5)
        ambient6.update_gauge(i+6)
        pygame.display.update()
        input(pygame.event.get())
        pygame.time.delay(100)
        
    for i in range(450,2400,25):
        kiln0.update_gauge(i)
        kiln1.update_gauge(i+10)
        kiln2.update_gauge(i+20)
        kiln3.update_gauge(i+30)
        kiln4.update_gauge(i+40)
        kiln5.update_gauge(i+50)
        kiln6.update_gauge(i+60)
        pygame.display.update()
        input(pygame.event.get())
        pygame.time.delay(100)
       

"""
blank = font.render('         F',True,(255,255,255),(0,0,255))
screen.blit(blank, (45,380))
temp = round(temp,2)
degree_symbol = unichr(176).encode("latin-1")
text = font.render(str(temp),True,(255,255,255),(0,0,255))
screen.blit(text, (45,380))
"""
