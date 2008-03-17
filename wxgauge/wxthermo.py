#!/usr/bin/python

import wx,os,sys,math,time,matplotlib
matplotlib.interactive(False)
#Use the WxAgg back end. The Wx one takes too long to render
matplotlib.use('WX')
from matplotlib.backends.backend_wxagg import Toolbar,FigureCanvasWx,FigureManager
from matplotlib.figure import Figure
from matplotlib.ticker import ScalarFormatter 
from matplotlib.dates import date2num
from matplotlib.dates import num2date
from matplotlib.dates import DateFormatter
from matplotlib.dates import DayLocator,HourLocator, MinuteLocator
from matplotlib.ticker import Locator, FormatStrFormatter

from datetime import datetime
from time import gmtime, strftime
from thermo_functions import *



class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size = (800,425))
        self.SetBackgroundColour('BLACK')
        self.Center()
        
        #Unique Sensor IDs
        self.id1 = '30ED284B1000008F'
        self.id2 = '3063294B100000BB'
        #Starting Temperatures for the gauges
        self.ambient_F = 70
        self.kiln_F = 1000
        #Initialize the plot data arrays
        self.kiln_temp = []
        self.date = []
        self.count = 0
        self.x = []
        #Setup the Plotting Figure and Canvas Load Blank Graph
        self.load_graph()

        #Instantiate the Two Thermometers One for the Kiln One for ambient
        self.ambient=Thermometer('amb_F',0,5,os.path.join("images",'ambient_F.png'),self)
        self.kiln=Thermometer('kiln_F_H',675,5,os.path.join("images",'kiln_FH.png'),self)
        #Startup the Event timer set it for 3 second roll over
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTick,self.timer)
        self.timer.Start(3000)
        #Bind the screen redraws to the PaintAll method in the Thermometer Class
        self.Bind(wx.EVT_PAINT, self.PaintAll)
        
        self.GraphTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.draw_graph, self.GraphTimer)
        self.GraphTimer.Start(20000)
        #self.Bind(wx.EVT_IDLE, self.draw_graph)
        
    
        
        #Menu Items
        ################################################
        menubar = wx.MenuBar()
        file = wx.Menu()
        edit = wx.Menu()
        help = wx.Menu()
        file.Append(100, '&Open', 'Open a new document')
        file.Append(101, '&Save', 'Save the document')
        file.AppendSeparator()
        file.Append(102, '&Quit', 'Quit')
        
        help.Append(103,'&About', 'About')
        
        menubar.Append(file, '&File')
        menubar.Append(help, '&Help')
        self.SetMenuBar(menubar)
        self.CreateStatusBar()
        
        #Menu Bindings Go here
        self.Bind(wx.EVT_MENU, self.openfile, id=100)
        self.Bind(wx.EVT_MENU, self.about_message, id=103)
        ################################################### 

        #Button Items
        ###############################################
     

        self.save_bitmap = wx.Image(os.path.join("images",'save.png'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.save_button = wx.BitmapButton(self, 200, bitmap=self.save_bitmap,pos=(250, 10), size = (self.save_bitmap.GetWidth(), self.save_bitmap.GetHeight()))
        
        self.load_bitmap = wx.Image(os.path.join("images",'load.png'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.load_button = wx.BitmapButton(self, 201, bitmap=self.load_bitmap,pos=(350, 10), size = (self.load_bitmap.GetWidth()+5, self.load_bitmap.GetHeight()+5))
        
        self.log_bitmap = wx.Image(os.path.join("images",'log.png'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.log_button = wx.BitmapButton(self, 202, bitmap=self.log_bitmap,pos=(450, 10), size = (self.log_bitmap.GetWidth()+5, self.log_bitmap.GetHeight()+5))

        
        wx.EVT_BUTTON(self, 200, self.OnSave)
        wx.EVT_BUTTON(self, 201, self.OnLoad)
        wx.EVT_BUTTON(self, 202, self.OnLog)      
        ###############################################
        
      
    def onTick(self, event):
        #Redraw the the thermometer backgrounds
        self.ambient.OnPaint()
        self.kiln.OnPaint()
        
        #Get Celcius From First Thermo
        self.celsius = get_celsius(self.id1)
        self.celsius_reverse = reverse_poly(self.celsius)
        self.ambient_F=(((self.celsius*9.0)/5.0)+32)
        time.sleep(1)
        
        #Get uV from first Thermo
        self.uv = get_uv(self.id1)
        self.uv = self.uv + self.celsius_reverse
        self.temp_uv = convert_uv(self.uv)
        self.kiln_F = (((self.temp_uv*9.0)/5.0)+32)
        
        #Make sure thermo measurement is not less then ambient
        if (self.kiln_F < self.ambient_F):
            self.kiln_F = self.ambient_F
        
        
        
        """
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
            print "Ambient===>",self.ambient_F,"kiln Temp===>",self.kiln_F,"average is ==>", sensor_average
            self.kiln_F = sensor_average
        """
        
        #Update the thermometer displays
        self.ambient.update_gauge(self.ambient_F)
        #self.kiln.update_gauge(self.kiln_F)
        self.kiln.update_gauge(1700)         
    
        #Update the Graph
        self.kiln_temp.append(self.kiln_F)
        self.date.append(date2num(datetime.now()))
  
        self.x.append(self.count)
        self.count = self.count + 1
        #self.draw_graph()
        print "Ambient===>",self.ambient_F,"kiln Temp===>",self.kiln_F,"Samples==>",self.count   
    
    def load_graph(self):
        #Set some plot attributes
        #add_subplot makes an Axes instance and puts it in the Figure instance
        #self.subplot is this Axes instance, as I had guessed.  
        #So, you can apply any Axes method to it.
        
        """
        fig = P.figure()
        ax = fig.add_subplot(111)
        ax.plot_date(dates, y)
        ax.xaxis.set_major_locator( P.DayLocator() )
        ax.xaxis.set_minor_locator( P.HourLocator(12))
        ax.xaxis.set_major_formatter( P.DateFormatter('%Y-%m-%d') )
        ax.xaxis.set_minor_formatter( P.DateFormatter('%Y-%m-%d %H:%M:%S'))
        ax.grid(True)
        fig.autofmt_xdate() 
        """

        self.figure = Figure((8,4) , 75)
        #pnl = wx.Panel(self, -1)
        #self.canvas = FigureCanvasWx(pnl, -1, self.figure)
        self.canvas = FigureCanvasWx(self, -1, self.figure)
        self.canvas.CenterOnParent()
        
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()

        self.subplot = self.figure.add_subplot(111)
        
        
        
        
    def draw_graph(self,event):
        print "updating the graph ;)"
        
        self.subplot.clear()
        self.subplot = self.figure.add_subplot(111)
        self.subplot.set_title(r"Kiln Temperature")

        #self.subplot.xaxis.set_major_locator( DayLocator() )
        #self.subplot.xaxis.set_minor_locator( HourLocator(12))
        #self.subplot.xaxis.set_major_locator( HourLocator(1))
        #self.subplot.xaxis.set_major_locator( MinuteLocator(10))
        
        self.subplot.yaxis.set_major_formatter(ScalarFormatter(False)) 
        self.subplot.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        
        
        self.subplot.grid(True)
        self.figure.autofmt_xdate()
        self.subplot.plot_date(self.date, self.kiln_temp, 'r-', linewidth = 1)
        self.canvas.draw()
   
    def openfile(self, event):
        dlg = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            mypath = os.path.basename(path)
            self.SetStatusText("You selected: %s" % mypath)
        dlg.Destroy()
    
    def about_message(self, event):
        dlg = wx.MessageDialog(self, 'When you as the Pyro want to Log!  Revision .0000001 March 12, 2008', 'About Pyrologger', wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
                   
    def PaintAll(self, event):
        self.ambient.OnPaint()
        self.kiln.OnPaint()
        self.ambient.update_gauge(self.ambient_F)
        #self.kiln.update_gauge(self.kiln_F) 
        self.kiln.update_gauge(1200)
    
    def OnSave(self,EVENT):
        print "You Pressed Save"

    def OnLoad(self,EVENT):
        print "You Pressed Load"

    def OnLog(self,EVENT):
        print "You Pressed Log" 
  
        
class Thermometer:
    def __init__ (self,scale,x,y,filename,frame):      
        self.scale=scale
        self.filename=filename
        self.x=x
        self.y=y
        self.gauge=wx.Bitmap(self.filename)
        self.frame = frame
        
    def OnPaint(self):
        self.dc = wx.PaintDC(self.frame)
        self.dc.DrawBitmap(self.gauge, self.x, self.y)
        
    def update_gauge(self,temp):
        temp = round(temp,2)
        if(self.scale == 'amb_F'):  #Ambient Farenheit Scale            
            self.length = (338 + self.y) - ((temp * 3.2) - 48)
            self.dc.SetPen(wx.Pen('red', 4))
            self.dc.DrawLine(self.x+58, (330+self.y), self.x+58, self.length)
            
        if(self.scale == 'kiln_F_H'): #Kiln Farenheit High Scale
            self.length = (338 + self.y) - ((temp * .16) - 64)
            self.dc.SetPen(wx.Pen('red', 4))
            self.dc.DrawLine(self.x+58, (330+self.y), self.x+58, self.length)
        return
        
class MyApp(wx.App):
    def OnInit(self):
        frame = MainFrame(None, -1, 'PyroLogger')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True

app = MyApp(0)
app.MainLoop()
