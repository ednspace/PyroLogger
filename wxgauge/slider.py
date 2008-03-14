from numpy import arange, sin, cos, pi

import matplotlib

matplotlib.use('WXAgg')

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

from matplotlib.figure import Figure

import wx

app=None

t = arange(0.0,3.0,0.01)
s = sin(2*pi*t)
c = cos(2*pi*t)

class PlotFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self,None,-1,'PlotFrame',size=(550,350))

        self.figure = Figure()
       
        self.subplot = self.figure.add_subplot(111)
        self.subplot.plot(t,s)
        self.subplot.hold(False)

        pnl = wx.Panel(self, -1)
        self.canvas = FigureCanvas(pnl, -1, self.figure)
        self.canvas.draw()

        self.flag = 1
        self.timer = wx.Timer(self, 1)
       
        wx.Button(pnl, 2, 'Start', (250, 500))
        wx.Button(pnl, 3, 'Stop', (350, 500))
        self.sld = wx.Slider(pnl, 4, 1000, 10, 2000, (300, 600), (200, -1),
                wx.SL_AUTOTICKS | wx.SL_HORIZONTAL | wx.SL_LABELS)

        wx.EVT_TIMER(self, 1, self.OnTimer)
        wx.EVT_BUTTON(self, 2, self.OnStart)
        wx.EVT_BUTTON(self, 3, self.OnStop)
        wx.EVT_SLIDER(self, 4, self.OnSlider)

        self.Show(True)
        self.Centre()

    def OnTimer(self, event):
        if self.flag == 1:
            self.subplot.plot(t,c)
            self.flag = 0
        else:
            self.subplot.plot(t,s)
            self.flag = 1
        self.canvas.draw()

    def OnStart(self, event):
        self.timer.Start(1000)

    def OnStop(self, event):
        self.timer.Stop()

    def OnSlider(self, event):
        val = self.sld.GetValue()
        self.timer.Stop()
        self.timer.Start(val)

app = wx.App()
PlotFrame()
app.MainLoop() 
