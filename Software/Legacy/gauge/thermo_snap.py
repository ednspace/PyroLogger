#!/usr/bin/python
import pygame,sys,os,math,matplotlib
from pygame.locals import *
matplotlib.use('Agg')
import pylab


def GetTemp():
    digi = os.popen("digitemp -t 1 -q -c /etc/digitemp.conf -o \%F")
    f = digi.readlines()
    digi.close()
    #return float(f[0].split()[1])
    return float(f[0])

def input(events): 
    for event in events: 
        if event.type == QUIT: 
            sys.exit(0)
        if event.type == MOUSEBUTTONDOWN:
            if button1_rect.collidepoint(event.pos) == 1 and event.button == 1:
                print "Your Pressed Button 1" 
            if button2_rect.collidepoint(event.pos) == 1 and event.button == 1:
                print "You Pressed Button 2 Wow"        
        #else: 
        #    print event
         
def update_gauge1(temp):
    length = 338 - ((temp * 3.2) - 48)
    gauge1_composite.blit(gauge1_background, (0,0))
    lastrect = pygame.draw.line(gauge1_composite, (255,0,0), (57,338), (57, length),width)
    screen.blit(gauge1_composite, (0,20)) #relitave position of composite on screen
    blank = font.render('         F',True,(255,255,255),(0,0,255))
    screen.blit(blank, (45,380))
    temp = round(temp,2)
    text = font.render(str(temp),True,(255,255,255),(0,0,255))
    screen.blit(text, (45,380))
  

def update_gauge2(temp):
    length = 338 - ((temp * .16) - 64)
    gauge2_composite.blit(gauge2_background, (0,0))
    lastrect = pygame.draw.line(gauge2_composite, (255,0,0), (57,338), (57, length),width)
    screen.blit(gauge2_composite, (675,20)) #relitave position of composite on screen
    blank = font.render('       F',True,(255,255,255),(0,0,255))
    screen.blit(blank, (720,380))
    text = font.render(str(temp),True,(255,255,255),(0,0,255))
    screen.blit(text, (720,380))
    
    
def load_graph():
    pylab.figure(num = 1, figsize=(6, 3))      
    pylab.plot( sensor, 'r-', linewidth = 1)
    pylab.savefig('graph.png')
    pylab.close(1)
    graph = os.path.join("","graph.png")
    graph_surface = pygame.image.load(graph).convert()
    screen.blit(graph_surface, (100,30))
  

#Initialize the Screen
pygame.init()
screen = pygame.display.set_mode((800,400))
pygame.display.set_caption('PyroLogger')

#Fill the Background
background = pygame.Surface(screen.get_size())
background.fill((0, 0, 255))
screen.blit( background, background.get_rect( ) )

#Load the gauges
gauge1 = os.path.join("images","thermo1.png")
gauge1_background = pygame.image.load(gauge1).convert()
gauge1_composite = pygame.Surface(gauge1_background.get_size())

gauge2 = os.path.join("images","thermo2.png")
gauge2_background = pygame.image.load(gauge2).convert()
gauge2_composite = pygame.Surface(gauge2_background.get_size())

#Load the buttons
button1 = os.path.join("images","greenpwr.png")
button1_surface = pygame.image.load(button1)
screen.blit(button1_surface, (300,350))
button1_rect = pygame.Rect(300,350,40,46)

button2 = os.path.join("images","redpwr.png")
button2_surface=pygame.image.load(button2)
screen.blit(button2_surface, (400,350))
button2_rect = pygame.Rect(400,350,40,46)

#Setup some text
font = pygame.font.Font(None, 20)

#Constants
#Thermometer Variables


width=4 #width of Hg
length=338 #starts Hg in bulb
kiln_temp=400
ambient_temp=15
sensor = []

while(1):
    input(pygame.event.get())
    
    ambient_temp = GetTemp()
    update_gauge1(ambient_temp)
    update_gauge2(kiln_temp)
    sensor.append(GetTemp())
    
    load_graph()
    
    pygame.display.update()
    
    
    
	

		
	
   
	
   
   

   
