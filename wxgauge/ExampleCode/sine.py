# load WxMpl's Python module
import wxmpl

# Create the PlotApp instance.
# The title string is one of several optional arguments.
app = wxmpl.PlotApp('WxMpl Example 1')

### Create the data to plot ###

from matplotlib.numerix import arange, pi, sin
x = arange(0.0, 2, 0.01)
y = sin(pi*x)

### Plot it ###

# All of WxMpl's plotting classes have a get_figure(),
# which returns the associated matplotlib Figure.
fig = app.get_figure()

# Create an Axes on the Figure to plot in.
axes = fig.gca()

# Plot the function
axes.plot(x, y)

# Let wxPython do its thing.
app.MainLoop()
