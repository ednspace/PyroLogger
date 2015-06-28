For when you the Pyro, needs to log!!!
======================================
Copyright Eric Daine 2015<br/>

Summary
----

A long standing project (since early 2005) to log and provide real time graphing of wood, electric, or gas kiln firings.
This project by necessity requires a hardware and software combination and through the years many have been tried with 
varying degrees of success. Most attempts are preserved here for posterity sake.

The Current Version
-----------
The most recent version of the hardware uses the Teensy 3.1 for the microcontroller, a custom made daughter board that has an SD card and phone jack
 to connect the sensors. The sensors are [MAX31855 from Adafruit](http://www.adafruit.com/product/269). The GUI is now handled with a customized interface
 for the amazing [MegunoLink](http://www.megunolink.com/).
 While buying modular hardware and using software that requires a modest licensing fee adds to the overall build cost it makes the 
 hardware and software a bit more accessible to the novice experimenter. 
 Hopefully this will enable more people to get at there kiln data and improve there future firings and learn from the ones they have done in the past.

![Image of populated board](/Images/2015-05-17 10.10.42.jpg)
![Image of 3D enclosure split open](/Images/2015-05-30 19.18.52.jpg)
![Image of 3D enclosure closed up](/Images/2015-05-30 19.26.21.jpg)
![Image of the sensor board in the phone box](/Images/2015-05-30 19.07.14.jpg)
![Image of the GUI](/Images/Screenshot 2015-06-28 18.45.21.png)
![Image of zoomed in Tempeh graph](/Images/tempeh JUNE-1-2015-Zoom.png)

History
-----
If you dig around in the archives you will find early versions of the code that relied on Python, WxPython for a GUI, and provided a front end for a custom piece of hardware. The hardware at that time was based on a microchip PIC microcontroller and addressed a one wire bus and a DS2760A to ultimately digitize two analog type K thermocouples. The combination of hardware and software was used to collect, display and log the temperature. Many variations of the code are here and all of hardware versions of the electronics also. Many early graphs generated with that hardware software combination are in the testing folder. Most of the work was done on the WxGauge and GUI versions. Its not very organized, but feel free to poke around and use what you need.

Enjoy... ED