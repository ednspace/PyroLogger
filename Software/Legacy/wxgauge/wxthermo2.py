#!/usr/bin/python2.7

#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.


"""
Updated October 2011
fixed print to print()
changed coeffecients for reverse polynomial equation.  Converts deg C in uV 


Updated April 2009
Program edited to allow for two thermocouples, one in the front, one in the back
Pretty Major ReWrite, Bug Fixing, Feature Enhancement Etc...

If you want to just graph one Thermocouple comment out graph line around line number 430
"""

import wx,os,sys,math,time,matplotlib,serial
matplotlib.interactive(False)
#Use the WxAgg back end. The Wx one takes too long to render
matplotlib.use('WXAgg')
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

class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title,(0,0),(975,500))
        
        
        
        self.TopPanel = wx.Panel(self, -1)
        gauge1 = wx.Panel(self.TopPanel,-1)
        gauge2 = wx.Panel(self.TopPanel,-1)
        graph1 = wx.Panel(self.TopPanel,-1)
        
        #Set Panel Background Colors
        graph1.SetBackgroundColour("black")
        gauge1.SetBackgroundColour("black")
        gauge2.SetBackgroundColour("black")
        self.TopPanel.SetBackgroundColour("black")
        
        
        
        
        #Instantiate the Two Thermometers One for the Kiln One for ambient
        #self.ambient=Thermometer(gauge1,-1,'amb_F',0,0,os.path.join("images",'ambient_F.png'))
        



        
        
        self.thermo_front=Thermometer(gauge1,-1,'kiln_F_H',0,0,os.path.join("images",'kiln_FH.png'))
        self.thermo_back=Thermometer(gauge2,-1,'kiln_F_H',0,0,os.path.join("images",'kiln_FH.png'))
        
        #self.ambient.update_gauge(17)
        self.thermo_front.update_gauge(450)
        self.thermo_back.update_gauge(450)
        
        #Set up the Graph Panel
        self.fig = Figure((10,5),75)
        self.canvas = FigureCanvasWx(graph1,-1,self.fig)
       
        
        
        #Create the sizer
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(gauge1,0,wx.ALIGN_CENTER_HORIZONTAL | wx.TOP , 30)
        hbox.Add(graph1,0,wx.ALIGN_CENTER_HORIZONTAL | wx.TOP , 20)
        hbox.Add(gauge2,0,wx.ALIGN_CENTER_HORIZONTAL | wx.TOP , 30)
        self.TopPanel.SetSizer(hbox)
        
        
        self.OutputBoxes()   

        


        #Set Some Environment Variables
        self.Centre()
        self.Show(True)
        
        self.AutoSave = 'FALSE'
        self.debug = 'FALSE'
        
        self.FrontHigh = 0
        self.BackHigh= 0
        
        #Unique Sensor IDs
        self.id1 = '30ED284B1000008F'
        self.id2 = '3063294B100000BB'
        
        
        
        
        self.front_sensor = self.id1
        self.back_sensor = self.id2
        
        #Starting Temperatures for the gauges
        self.ambient = 70
        self.kiln_front = 1000
        self.kiln_back = 1000
        
        #Initialize the plot data arrays
        self.ambient_array= []
        self.kiln_front_array = []
        self.kiln_back_array = []
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

        
        
        #Setup the Clock
        self.SensorTimer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.OnTick,self.SensorTimer)
        
        

        #Menu Items
        ################################################
        self.menubar = wx.MenuBar()
        self.FileMenu = wx.Menu()
        self.ConfigMenu = wx.Menu()
        self.SerialMenu = wx.Menu()
        self.HelpMenu = wx.Menu()
        
        self.FileMenu.Append(100, '&Load', 'Load a saved Graph')
        self.FileMenu.Append(101, '&Save', 'Save the current Graph')
        self.FileMenu.Append(108, '&Save As...', 'Save the current Graph')
        self.FileMenu.Append(105, '&Start Logging', 'Start logging process')
        self.FileMenu.Append(106, '&Stop Logging', 'Stop logging process')
        self.FileMenu.Append(107, '&Clear Graph', 'Reset the Graph Panel')
        self.FileMenu.AppendSeparator()
        self.FileMenu.Append(102, '&Quit', 'Quit')
        
    
        #Build the Configuration Menu
        # Build the Serial SubMenu
        # Get list of files in /dev
        cd = os.getcwd()
        os.chdir("/dev")
        dirdev = os.getcwd()
        fileList = os.listdir(dirdev)

        self.validPorts = list() 
        validPortCount = 0

        # Find the files that start with ttyUSB, USB connection
        for file in fileList:
          if file.startswith("ttyUSB"):
            try:
              sp = serial.Serial(file) 
              validPortCount += 1
              self.validPorts.append(sp.getPort()) 
            except serial.SerialException:
              pass

        # Find the files that start with ttyS, 9 pin serial connection
        for file in fileList:
          if file.startswith("ttyS"):
            try:
              sp = serial.Serial(file) 
              validPortCount += 1
              self.validPorts.append(sp.getPort()) 
            except serial.SerialException:
              pass

        
        IdNumber=500
        for port in self.validPorts:
            self.SerialMenu.AppendRadioItem(IdNumber,port)
            self.Bind(wx.EVT_MENU, self.OnSerial, id=IdNumber)
            IdNumber = IdNumber + 1
        
        self.ConfigMenu.AppendMenu(104, "&Serial", self.SerialMenu)
        self.ConfigMenu.AppendCheckItem(110,'&AutoSave','Toggle AutoSave')
        self.ConfigMenu.AppendSeparator()
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
        self.Bind(wx.EVT_MENU, self.OnQuit, id=102)
        self.Bind(wx.EVT_MENU, self.OnSaveAs, id=108)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=103)
        self.Bind(wx.EVT_MENU, self.OnSerial, id=104)
        self.Bind(wx.EVT_MENU, self.OnLog, id=105)
        self.Bind(wx.EVT_MENU, self.OnStop, id=106)
        self.Bind(wx.EVT_MENU, self.OnClear, id=107)
        self.Bind(wx.EVT_MENU, self.OnAutoSave, id=110)
        self.Bind(wx.EVT_MENU, self.OnDebug, id=120)
        ################################################### 
        
        """Commented Out Buttons
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
        #self.ambient.OnPaint(self)
        self.thermo_front.OnPaint(self)
        self.thermo_back.OnPaint(self)
       
        
        #Get Celcius From Front Thermo
        self.celsius = self.get_celsius(self.front_sensor)
        self.celsius_reverse = self.reverse_poly(self.celsius)
        self.ambient =(((self.celsius*9.0)/5.0)+32)
        #print ("Front Ambient ==> ", self.ambient)
        time.sleep(1)
        
        
        #Get uV from Front Thermo
        self.uv = self.get_uv(self.front_sensor)
        self.uv = self.uv + self.celsius_reverse
        self.uv = self.uv * 1000
        
        if (self.uv > 20.644):
            self.temp_uv = self.convert_uv_high(self.uv)
        else:
			self.temp_uv = self.convert_uv_low(self.uv)
		      
        self.kiln_front = (((self.temp_uv*9.0)/5.0)+32)
        
        #Make sure thermo measurement is not less then ambient
        #If it is less set the thermo to the ambient
        if (self.kiln_front < self.ambient):
            self.kiln_front = self.ambient
            
        time.sleep(1)
        
        #Get Celcius From Back Thermo
        self.celsius = self.get_celsius(self.back_sensor)
        self.celsius_reverse = self.reverse_poly(self.celsius)
        self.ambient =(((self.celsius*9.0)/5.0)+32)
        #print ("Back Ambient ==> ", self.ambient)
        time.sleep(1)
        
        
        #Get uV from back Thermo
        self.uv = self.get_uv(self.back_sensor)
        self.uv = self.uv + self.celsius_reverse
        self.uv = self.uv * 1000
        
        if (self.uv > 20.644):
            self.temp_uv = self.convert_uv_high(self.uv)
            
        else:
			self.temp_uv = self.convert_uv_low(self.uv)
			
        
        
        self.kiln_back = (((self.temp_uv*9.0)/5.0)+32)
        
        #Make sure thermo measurement is not less then ambient
        #If it is less set the thermo to the ambient
        if (self.kiln_back < self.ambient):
            self.kiln_back = self.ambient
        time.sleep(1)
        
        
        #Update the Front High Value Holder
        if self.kiln_front > self.FrontHigh:
            self.FrontHigh = self.kiln_front
        self.FrontHigh = round(self.FrontHigh,1)
        self.FrontHighReading.Clear()
        self.FrontHighReading.AppendText(str(self.FrontHigh))
        
        #Update the Back High Value Holder
        if self.kiln_back > self.BackHigh:
            self.BackHigh = self.kiln_back
        self.BackHigh = round(self.BackHigh,1)
        self.BackHighReading.Clear()
        self.BackHighReading.AppendText(str(self.BackHigh))
        
        self.BackReading.Clear()
        self.BackReading.AppendText(str(round(self.kiln_back,1)))
        
        self.FrontReading.Clear()
        self.FrontReading.AppendText(str(round(self.kiln_front,1)))
        
        self.elapsed = time.time()-self.t1
        self.ElapsedReading.Clear()
        self.ElapsedReading.AppendText(time.strftime("day %j - %H hrs. %M mins. %S secs.", time.gmtime(self.elapsed)))
        
        
    
        
        
        
        """Rolling Average Filter Commented Out
        if len(kiln_temp) > 20:
            sensor_average = 0
            #print kiln_temp[len(kiln_temp)-10:]
            #moving_part = [len(kiln_temp)-10:]
            for sample in kiln_temp[len(kiln_temp)-20:]:    
                sensor_average = sensor_average + sample
            sensor_average = sensor_average / 20
            sensor_average = round(sensor_average,2)
            print ("Ambient===>",self.ambient,"kiln Temp===>",self.kiln_F,"average is ==>", sensor_average)
            self.kiln_F = sensor_average
        """
        
        
        
        #Update the thermometer displays
        
        if (self.kiln_front > 500):
            self.thermo_front.update_gauge(self.kiln_front)
            
        if (self.kiln_back > 500):
            self.thermo_back.update_gauge(self.kiln_back)
        
    
        #Update the Lists and Graph
        self.kiln_front_array.append(self.kiln_front)
        self.kiln_back_array.append(self.kiln_back)
        self.ambient_array.append(self.ambient)
    
        self.date_human.append(strftime("%a, %d %b %Y %H:%M:%S"))
        self.date.append(date2num(datetime.now()))
  
        self.x.append(self.count)
        self.count = self.count + 1
        self.SampleNum.Clear()
        self.SampleNum.AppendText(str(self.count))
        
        
        """Attempts to just plot part of the line
        Turn This code on if you want to only plot to a certain depth
        self.depth is a variable that represents the number of readings to 
        show on the graph at one time.  After this number is exceeded the graph scrolls"""
        
        self.depth = 720
        if self.count > self.depth:
            self.graph_front=self.kiln_front_array[(len(self.kiln_front_array)-self.depth):len(self.kiln_front_array)]
            self.graph_back=self.kiln_back_array[(len(self.kiln_back_array)-self.depth):len(self.kiln_back_array)]
            self.graph_date=self.date[(len(self.date)-self.depth):len(self.date)]
        else:
            self.graph_front=self.kiln_front_array
            self.graph_back=self.kiln_back_array
            self.graph_date=self.date
            
            
        print ("front=>", round(self.kiln_front,1), "     back=>", round(self.kiln_back,1), "     ambient=>", round(self.ambient,1), "     Samples==>",self.count)
        
        #print "Ambient===>",self.ambient,"kiln front===>",self.kiln_front, "kiln back===>",self.kiln_back,"Samples==>",self.count
        
        self.sample_count = self.sample_count + 1
        if (self.sample_count >= self.sample_max):
            self.draw_graph()
            self.sample_count = 0
        if (self.count%100 == 0) & (self.AutoSave == 'True'):
            if (self.debug == 'True'):
                print ("I gots 100 samples, now ehm gonna save em")
            self.OnSave(None)
        
        
    
    def load_graph(self):
        #Set some plot attributes
        #add_subplot makes an Axes instance and puts it in the Figure instance
        #self.subplot is this Axes instance, as I had guessed.  
        #So, you can apply any Axes method to it.
        
        
        self.subplot = self.fig.add_subplot(111)
        self.subplot.set_title(r"Kiln Temperature")
        
        
    def draw_graph(self):
        if (self.debug == 'True'):
            print ("updating the graph ;")
        
        self.subplot.clear()
        self.subplot = self.fig.add_subplot(111)
        self.subplot.xaxis.set_minor_locator( HourLocator(12))
        
        """
        self.subplot.set_title(r"Kiln Temperature")
        self.subplot.xaxis.set_major_locator( DayLocator() )
        self.subplot.xaxis.set_major_locator( HourLocator(1))
        self.subplot.xaxis.set_major_locator( MinuteLocator(30))
        self.subplot.xaxis.set_major_locator( HourLocator(1))
        """
        
        #Turn off Scientific Notation on Y Axis
        self.subplot.yaxis.set_major_formatter(ScalarFormatter(False))
        self.subplot.xaxis.set_major_formatter(DateFormatter('%H:%M'))
        self.fig.autofmt_xdate()
        self.subplot.grid(True)
        
        self.subplot.plot(self.graph_date, self.graph_front, 'r-', linewidth = 1)
        self.subplot.plot(self.graph_date, self.graph_back, 'b-', linewidth = 1)
        
        #self.subplot.plot(self.date, self.kiln_front_array, 'r-', linewidth = 1)
        #self.subplot.plot(self.date, self.kiln_back_array, 'b-', linewidth = 1)
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
            print ("Somebody clicked on Autosave")
            print (self.ConfigMenu.IsChecked(110))
        if (self.ConfigMenu.IsChecked(110)):
            self.AutoSave = 'True'
            self.SetStatusText("Auto Save is on... Saving every 100 samples")
        else:
            self.AutoSave = 'False'
            self.SetStatusText("Auto Save is now off")
    
    def OnSerial(self, event): 
        if (self.debug == 'True'):
            print ("You are trying to change a port")
        IdNumber = 500
        for port in self.validPorts:
            if self.ConfigMenu.IsChecked(IdNumber):
                self.SerialSelect = port
                self.SetStatusText("Serial Port Now Set to " + self.SerialSelect)
                if (self.debug == 'True'):
                    print (port,"Is Checked")
            IdNumber = IdNumber + 1
                
    def OnClear(self,event):
        """clear the lists"""
        
        self.SetStatusText("Clearing the current graph...")
        self.date = []
        self.kiln_front_array = []
        self.kiln_back_array = []
        
        self.graph_front = self.kiln_front_array
        self.graph_back = self.kiln_back_array
        self.graph_date = self.date
        
        
       
        """clear the boxes"""
        self.SampleNum.Clear()
        self.FrontReading.Clear()
        self.BackReading.Clear()
        self.FrontHighReading.Clear()
        self.BackHighReading.Clear()
        self.ElapsedReading.Clear()
        
        """Clear the graph Window"""
        self.draw_graph()
    
    def OnStop(self,event):
        self.SetStatusText("Now stops the logging...")
        self.SensorTimer.Stop()
    
    def OnQuit(self,event):
        self.SetStatusText("Now we quit buh bye...")
        self.Close()

    def OnLog(self, event):
        #Open the serial port connection
        try: 
            self.ser = serial.Serial(self.SerialSelect, 9600, timeout=5)
            self.SetStatusText("Now starts the logging...")
            self.t1 = time.time()
            self.SensorTimer.Start(30000)
        except:
            self.SetStatusText("Invalid Serial Port Selected")

    def OnAbout(self, event):
        self.SetStatusText("All about ...PyroLogger...")
        dlg = wx.MessageDialog(self, 'When you as the Pyro want to Log!  Last updated October 2012', 'About Pyrologger', wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()
                   
    
    
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
            file.write ("Fields:Ambient KilnFront KilnBack Date Date2Num")
            file.write ("\n")
            file.write ("\n")
            for reading in self.date:
                value_1 = "%.1f" % self.ambient_array[list_count]
                value_2 = "%.1f" % self.kiln_front_array[list_count]
                value_3 = "%.1f" % self.kiln_back_array[list_count]
                value_4 = self.date_human[list_count]
                value_5 = "%.11f" % self.date[list_count]
                value = (list_count,value_1,value_2,value_3,value_4,value_5)
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
            file.write ("Fields:Ambient KilnFront KilnBack Date Date2Num")
            file.write ("\n")
            file.write ("\n")
            for reading in self.date:
                value_1 = "%.1f" % self.ambient_array[list_count]
                value_2 = "%.1f" % self.kiln_front_array[list_count]
                value_3 = "%.1f" % self.kiln_back_array[list_count]
                value_4 = self.date_human[list_count]
                value_5 = "%.11f" % self.date[list_count]
                value = (list_count,value_1,value_2,value_3,value_4,value_5)
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
        print ("You Pressed Load")
        print ("Slurping Raw Data... ummmmmm!!!")
        file = open(self.filename, 'r')
        skip = 0
        self.date = []
        self.kiln_front_array = []
        self.kiln_back_array = []
        
        for line in file.readlines():
            if (skip >= 3):
                #Split line up into its individual fields
                fields = line.split ('\', \'')
                self.kiln_front_array.append(fields[1])
                self.kiln_back_array.append(fields[2])
                paren = line.rfind(')')
                self.date.append(line[paren-19:paren-1])
            skip = skip + 1
        
        self.date = map(float, self.date)
        self.kiln_front_array = map(float, self.kiln_front_array)
        self.kiln_back_array = map(float, self.kiln_back_array)
        
        self.graph_front = self.kiln_front_array
        self.graph_back = self.kiln_back_array
        self.graph_date = self.date

        self.draw_graph()

    def get_celsius(self,address):
        self.ser.flushInput()
        self.ser.write("\r")
        self.ser.write("C")
        self.ser.write(address)
        self.ser.write("\r")
        #line = ser.read(5)
        line = self.ser.readline()
        self.ser.flushInput()
        return float(line)

    def get_uv(self,address):
        self.ser.flushInput()
        self.ser.write("\r")
        self.ser.write("K")
        self.ser.write(address)
        self.ser.write("\r")
        #line = ser.read(9)
        line = self.ser.readline()
        self.ser.flushInput()
        return float(line)
    """
    #This is older code and didn't give good values for ambient at higher temps use new code below
    def reverse_poly(self,x):
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
    """
    def reverse_poly(self,x):
        #Takes in Temp in deg C and gives back Uv's, used to adjust for ambiant temperature supposed to be good from 0-1372 deg C
        coeffecients = [-1.7600413686E-2, 3.8921204975E-2, 1.8558770032E-5, -9.9457592874E-8, 3.1840945719E-10, -5.6072844889E-13, 5.6075059059E-16, -3.2020720003E-19, 9.7151147152E-23, -1.2104721275E-26]
        
        result2 = 0.0
        #added = 0.0
        power = 0


        for c in coeffecients:
            result2 = (result2 + c * pow(x,power))
            power = power + 1
        #result2 = result2 + added
        #result2 = result2 / 1000000
        result2 = result2 / 1000
        return (result2)
 
 

    def convert_uv_low(self,uv):
        """The coefficients for Temperature range 0 deg C to 500 deg C
        Voltage range 0 mV to 20.644 mV
        Error range .04 deg C to -.05 deg C are:
			C0 = 0
			C1 = 2.508355 * 10^1
			C2 = 7.860106 * 10^-2
			C3 = -2.503131 *10^-1
			C4 = 8.315270 * 10^-2
			C5 = -1.228034 * 10^-2
			C6 = 9.804036 * 10^-4
			C7 = -4.413030 * 10^-5
			C8 = 1.057734 * 10^-6
			C9 = -1.052755 * 10^-8
		"""
		
        #coefficients = [0.226584602, 24152.10900, 67233.4248, 2210340.682, -860963914.9, 4.83506e10, -1.18452e12, 1.38690e13, -6.33708e13]
        coefficients = [0, 2.508355E1, 7.860106E-2, -2.503131E-1, 8.315270E-2, -1.228034E-2, 9.804036E-4, -4.413030E-5, 1.057734E-6, -1.052755E-8]
       
        result1 = 0.0
        power = 0
        
        for c in coefficients:
            result1 = result1 + c * pow(uv,power)
            power = power + 1
        result1 = round(result1,2)
        return result1
        
        
    def convert_uv_high(self,uv):
        """The coefficients for Temperature range 500 deg C to 1372 deg C
        Voltage range 20.644 mV to 54.886 mV
        Error range .06 deg C to -.05 deg C are:
            C0 = -1.318058 * 10^2
            C1 = 4.830222 * 10^1
            C2 = -1.646031
            C3 = 5.464731 * 10^-2
            C4 = -9.650715 * 10^-4
            C5 = 8.802193 * 10^-6
            C6 = -3.110810 * 10^-8
            C7 = 0
            C8 = 0
            C9 = 0
		"""
        
        coefficients = [-1.318058E2, 4.830222E1, -1.646031, 5.464731E-2, -9.650715E-4, 8.802193E-6, -3.110810E-8, 0, 0, 0]
       
        result1 = 0.0
        power = 0
        for c in coefficients:
            result1 = result1 + c * pow(uv,power)
            power = power + 1
        result1 = round(result1,2)
        return result1

    def OutputBoxes(self):
        """Create Output Boxes"""
        
        self.SampleNumLabel = wx.StaticText(self.TopPanel, -1,'Reading',(25,400))
        self.SampleNumLabel.SetForegroundColour('white')
        self.SampleNum = wx.TextCtrl(self.TopPanel, -1,"",(25,415),style=wx.TE_READONLY|wx.TE_CENTER)
        
        self.FrontReadingLabel = wx.StaticText(self.TopPanel, -1,'Front Temp',(125,400))
        self.FrontReadingLabel.SetForegroundColour('white')
        self.FrontReading = wx.TextCtrl(self.TopPanel, -1,"",(125,415),style=wx.TE_READONLY|wx.TE_CENTER)
        
        self.BackReadingLabel = wx.StaticText(self.TopPanel, -1,'Back Temp',(225,400))
        self.BackReadingLabel.SetForegroundColour('white')
        self.BackReading = wx.TextCtrl(self.TopPanel, -1,"",(225,415),style=wx.TE_READONLY|wx.TE_CENTER)
        
        self.FrontHighReadingLabel = wx.StaticText(self.TopPanel, -1,'Front High',(325,400))
        self.FrontHighReadingLabel.SetForegroundColour('white')
        self.FrontHighReading = wx.TextCtrl(self.TopPanel, -1,"",(325,415),style=wx.TE_READONLY|wx.TE_CENTER)
        
        self.BackHighReadingLabel = wx.StaticText(self.TopPanel, -1,'Back High',(425,400))
        self.BackHighReadingLabel.SetForegroundColour('white')
        self.BackHighReading = wx.TextCtrl(self.TopPanel, -1,"",(425,415),style=wx.TE_READONLY|wx.TE_CENTER)
        
        self.ElapsedReadingLabel = wx.StaticText(self.TopPanel, -1,'Elapsed Time',(525,400))
        self.ElapsedReadingLabel.SetForegroundColour('white')
        self.ElapsedReading = wx.TextCtrl(self.TopPanel, -1,"",(525,415),size=(300, 26),style=wx.TE_READONLY|wx.TE_CENTER)
        
        
class Thermometer(wx.Panel):
    
    def __init__ (self,parent,id,scale,x,y,filename):
        wx.Panel.__init__(self, parent, id,size=(104,362) )    
        self.scale=scale
        self.filename=filename
        self.x=x
        self.y=y
        self.gauge=wx.Bitmap(self.filename)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.dc = wx.PaintDC(self)
        self.SaveTemp = 0
        
    def OnPaint(self,event):
        self.dc = wx.PaintDC(self)
        self.dc.DrawBitmap(self.gauge,0,0)
        self.update_gauge(self.SaveTemp)
        #self.dc.DrawBitmap(self.gauge, self.x, self.y)
        
    def update_gauge(self,temp):
        temp = round(temp,2)
        if (temp != self.SaveTemp):
            self.SaveTemp = temp
            
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
        frame = MainFrame(None,-1,'PyroLogger')
        frame.Show(True)
        self.SetTopWindow(frame)
        return True
        
app = MyApp(0)
app.MainLoop()
