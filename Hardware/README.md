Hardware Lives Here
---------

The folder Pyrologger_V3_KiCad contains the latest board files. Its a daughter board for 
the teensy 3.1 that has connections for the thermocouple sensors and an SD card.

The folder ds2760-pcb contains the orginal board files for the pyrometer 
sensor. The chip is a ds2760 lithium ion battery monitor from Maxim now 
Dallas Semiconductor.  It uses the one wire bus to get the mv drop over 
the shunt resistor which in this case is actually a type K 
thermocouple. The files where generated with Linux-PCB and the 
schematics are in gschem.  The LMD file is for driving an LPKF circuit 
board plotter to cut out the board.

The folder 16F88_FT232RL contains the board files and schematic for the 
microcontroller interface to the computer.  It uses a microchip 
technology 16F88 and an FTDI chip to make a serial connection through 
USB.  The microcontroller board is accessed with by the wxPython GUI 
software which collects the data and displays it on screen.  The board 
files where done with Eagle.


