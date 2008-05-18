#!/usr/bin/python

import wx,os,sys,math,time,matplotlib
matplotlib.interactive(False)
#Use the WxAgg back end. The Wx one takes too long to render
matplotlib.use('WXAGG')
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
        wx.Frame.__init__(self, parent, id, title, size = (1000,425))
        self.SetBackgroundColour('BLACK')
        self.Center()
        self.debug = 'FALSE'
        
        #Unique Sensor IDs
        self.id1 = '30ED284B1000008F'
        self.id2 = '3063294B100000BB'
        self.current_sensor = self.id2
        #Starting Temperatures for the gauges
        self.ambient_F = 70
        self.kiln_F = 1000
        #Initialize the plot data arrays
        self.ambient_temp = []
        self.kiln_temp = []
        self.date_human = []
        self.date = []
        self.count = 0
        self.sample_count = 0
        self.x = []
        
        #Make Sure Filename is cleared
        self.filename = None
        
        #number of samples before updating graph
        self.sample_max = 5
        
        #Setup the Plotting Figure and Canvas Load Blank Graph
        self.load_graph()

        #Instantiate the Two Thermometers One for the Kiln One for ambient
        self.ambient=Thermometer('amb_F',0,5,os.path.join("images",'ambient_F.png'),self)
        self.kiln=Thermometer('kiln_F_H',880,5,os.path.join("images",'kiln_FH.png'),self)
        
        #Bind the screen redraws to the PaintAll method in the Thermometer Class
        self.Bind(wx.EVT_PAINT, self.PaintAll)
        
        #Setup the Clock
        self.SensorTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.OnTick,self.SensorTimer)
        
        

        #Menu Items
        ################################################
        self.menubar = wx.MenuBar()
        self.FileMenu = wx.Menu()
        self.ConfigMenu = wx.Menu()
        self.HelpMenu = wx.Menu()
        
        self.FileMenu.Append(100, '&Load', 'Load a saved Graph')
        self.FileMenu.Append(101, '&Save', 'Save the current Graph')
        self.FileMenu.Append(108, '&Save As...', 'Save the current Graph')
        self.FileMenu.Append(105, '&Start Logging', 'Start logging process')
        self.FileMenu.Append(106, '&Stop Logging', 'Stop logging process')
        self.FileMenu.Append(107, '&Clear Graph', 'Reset the Graph Panel')
        self.FileMenu.AppendSeparator()
        self.FileMenu.Append(102, '&Quit', 'Quit')
        
        self.ConfigMenu.Append(104, '&Serial Port', 'Serial Port')
        self.ConfigMenu.AppendSeparator()
        self.ConfigMenu.AppendCheckItem(110,'&AutoSave','Toggle AutoSave')
        self.ConfigMenu.AppendCheckItem(120,'&Debug','Toggle Debug')
        
        
        self.HelpMenu.Append(103,'&About', 'About')
        
        self.menubar.Append(self.FileMenu, '&File')
        self.menubar.Append(self.ConfigMenu, '&Config')
        self.menubar.Append(self.HelpMenu, '&Help')
        self.SetMenuBar(self.menubar)
        self.CreateStatusBar()
        
        #Menu Bindings Go here
        self.Bind(wx.EVT_MENU, self.OnLoad, id=100)
        self.Bind(wx.EVT_MENU, self.OnSave, id=101)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=108)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=103)
        self.Bind(wx.EVT_MENU, self.OnSerial, id=104)
        self.Bind(wx.EVT_MENU, self.OnLog, id=105)
        self.Bind(wx.EVT_MENU, self.OnStop, id=106)
        self.Bind(wx.EVT_MENU, self.OnClear, id=107)
        self.Bind(wx.EVT_MENU, self.OnAutoSave, id=110)
        self.Bind(wx.EVT_MENU, self.OnDebug, id=120)
        ################################################### 
        
        """
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
        """
    
    
     
    def OnTick(self,event):
        #Redraw the the thermometer backgrounds
        self.ambient.OnPaint()
        self.kiln.OnPaint()
        
        #Get Celcius From First Thermo
        self.celsius = get_celsius(self.current_sensor)
        self.celsius_reverse = reverse_poly(self.celsius)
        self.ambient_F=(((self.celsius*9.0)/5.0)+32)
        time.sleep(1)
        #for i in range(1, 10):
        #    time.sleep(.1)
        
        #Get uV from first Thermo
        self.uv = get_uv(self.current_sensor)
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
        if (self.kiln_F > 500):
            self.kiln.update_gauge(self.kiln_F)
            #self.kiln.update_gauge(1700)         
    
        #Update the Lists and Graph
        self.kiln_temp.append(self.kiln_F)
        self.ambient_temp.append(self.ambient_F)
    
        self.date_human.append(strftime("%a, %d %b %Y %H:%M:%S"))
        self.date.append(date2num(datetime.now()))
  
        self.x.append(self.count)
        self.count = self.count + 1
        print "Ambient===>",self.ambient_F,"kiln Temp===>",self.kiln_F,"Samples==>",self.count
        
        self.sample_count = self.sample_count + 1
        if (self.sample_count >= self.sample_max):
            self.draw_graph()
            self.sample_count = 0
        if (self.count%100 == 0) & (self.AutoSave == 'True'):
            if (self.debug == 'True'):
                print "I gots 100 samples, now ehm gonna save em"
            self.OnSave(None)
        
        
    
    def load_graph(self):
        #Set some plot attributes
        #add_subplot makes an Axes instance and puts it in the Figure instance
        #self.subplot is this Axes instance, as I had guessed.  
        #So, you can apply any Axes method to it.
        
        self.figure = Figure((11,4) , 75)
        #pnl = wx.Panel(self, -1)
        self.canvas = FigureCanvasWx(self, -1, self.figure)
        self.canvas.CenterOnParent()
        self.toolbar = Toolbar(self.canvas)
        self.toolbar.Realize()
        
        self.subplot = self.figure.add_subplot(111)
        self.subplot.set_title(r"Kiln Temperature")
        
        
    def draw_graph(self):
        if (self.debug == 'True'):
            print "updating the graph ;)"
        
        self.subplot.clear()
        self.subplot = self.figure.add_subplot(111)
        #self.subplot.set_title(r"Kiln Temperature")
        #self.subplot.xaxis.set_major_locator( DayLocator() )
        #self.subplot.xaxis.set_minor_locator( HourLocator(12))
        #self.subplot.xaxis.set_major_locator( HourLocator(1))
        #self.subplot.xaxis.set_major_locator( MinuteLocator(30))
        #self.subplot.xaxis.set_major_locator( HourLocator(1))
        
        #Turn off Scientific Notation on Y Axis
        self.subplot.yaxis.set_major_formatter(ScalarFormatter(False))
        self.subplot.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        self.figure.autofmt_xdate()
        self.subplot.grid(True)
        self.subplot.plot_date(self.date, self.kiln_temp, 'r-', linewidth = 1)
        self.canvas.draw()
    
    ##########################################################################
    ####################MENU Function Start Here##############################
    ##########################################################################
    def OnDebug(self, event):
        if (self.ConfigMenu.IsChecked(120)):
            self.debug = 'True'
            self.SetStatusText("Turning on Debug")
        else:
            self.debug = 'False'
            self.SetStatusText("Turning Off Debug")
                
    def OnAutoSave(self, event):
        if (self.debug == 'True'):
            print "Somebody clicked on Autosave"
            print self.ConfigMenu.IsChecked(110);
        if (self.ConfigMenu.IsChecked(110)):
            self.AutoSave = 'True'
            self.SetStatusText("Auto Save is on... Saving every 100 samples")
        else:
            self.AutoSave = 'False'
            self.SetStatusText("Auto Save is now off")
    
    def OnSerial(self, event):    
        for i in range(256):
            try:
                s = serial.Serial(i)
                print s.portstr
                s.close()
            except serial.SerialException:
                self.SetStatusText("Problem with the serial ports")
                
    def OnClear(self,event):
        self.SetStatusText("Clearing the current graph...")
        self.date = []
        self.kiln_temp = []
        self.draw_graph()
    
    def OnStop(self,event):
        self.SetStatusText("Now stops the logging...")
        self.SensorTimer.Stop()

    def OnLog(self, event):
        self.SetStatusText("Now starts the logging...")
        #Startup the Timer for Sensor Readings
        self.SensorTimer.Start(3000)
   
 
    def OnAbout(self, event):
        self.SetStatusText("All about ...PyroLogger...")
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
        if (self.filename == None):
            dialog = wx.FileDialog(self,"Save Graph Data...","","","Graph File (*.txt)|*.txt",wx.SAVE)
            if (dialog.ShowModal() == wx.ID_CANCEL):
                return  # canceled, bail
            # ok they saved
            self.filename = dialog.GetPath();
            self.SetTitle("PyroLogger        "+self.filename)

        try:
            file = open(self.filename, 'w')
            list_count = 0
            file.write ("Log Date and Time ")
            file.write (strftime("%a, %d %b %Y %H:%M:%S"))
            file.write ("\n")
            file.write ("Ambient Kiln Date Date2Num")
            file.write ("\n")
            file.write ("\n")
            for reading in self.date:
                value_1 = "%.2f" % self.ambient_temp[list_count]
                value_2 = "%.2f" % self.kiln_temp[list_count]
                value_3 = self.date_human[list_count]
                value_4 = "%.11f" % self.date[list_count]
                value = (list_count,value_1,value_2,value_3,value_4)
                file_line = str(value)
                file.write (file_line)
                file.write ("\n")
                list_count = list_count + 1
            file.close
            self.SetStatusText("Saved current Graph...")
        except IOError:
            self.SetStatusText("Error writing to file!")
            
    def OnSaveAs(self,EVENT):
        
        dialog = wx.FileDialog(self,"Save Graph Data...","","","Graph File (*.txt)|*.txt",wx.SAVE)
        if (dialog.ShowModal() == wx.ID_CANCEL):
            return  # canceled, bail
        # ok they saved
        self.filename = dialog.GetPath();
        self.SetTitle("PyroLogger        "+self.filename)

        try:
            file = open(self.filename, 'w')
            list_count = 0
            file.write ("Log Date and Time ")
            file.write (strftime("%a, %d %b %Y %H:%M:%S"))
            file.write ("\n")
            file.write ("Ambient Kiln Date Date2Num")
            file.write ("\n")
            file.write ("\n")
            for reading in self.date:
                value_1 = "%.2f" % self.ambient_temp[list_count]
                value_2 = "%.2f" % self.kiln_temp[list_count]
                value_3 = self.date_human[list_count]
                value_4 = "%.11f" % self.date[list_count]
                value = (list_count,value_1,value_2,value_3,value_4)
                file_line = str(value)
                file.write (file_line)
                file.write ("\n")
                list_count = list_count + 1
            file.close
            self.SetStatusText("Saved current Graph...")
        except IOError:
            self.SetStatusText("Error writing to file!")
    
    
    def OnLoad(self,EVENT):
        self.SetStatusText("Loading Graph...")
        self.SensorTimer.Stop()
        self.filename = None
            
        dialog = wx.FileDialog(self, "Choose a file", os.getcwd(), "", "*.*", wx.OPEN)
        if (dialog.ShowModal() == wx.ID_CANCEL):
            return  # canceled, bail
        # ok they loaded
        self.filename = dialog.GetPath()
        self.SetTitle("PyroLogger        "+self.filename)
        print "You Pressed Load"
        print "Slurping Raw Data... ummmmmm!!!"
        file = open(self.filename, 'r')
        skip = 0
        self.date = []
        self.kiln_temp = []
        
        for line in file.readlines():
            if (skip >= 3):
                #Split line up into its individual fields
                #fields = line.rsplit('\', \'')
                fields = line.split ('\', \'')
                self.kiln_temp.append(fields[1])
                paren = line.rfind(')')
                self.date.append(line[paren-19:paren-1])
            skip = skip + 1
        
        self.date = map(float, self.date)
        self.kiln_temp = map(float, self.kiln_temp)
        self.draw_graph()
        
        """
        #Print some Stats
        print "High Temperature for Front Thermocouple ==>",high_front
        print "High Temperature for Back Thermocouple ==>",high_back
        print "Number of Data Points Collected ==========>",len(date_float)
        """
   
  
        
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
