/* 
	Editor: http://www.visualmicro.com
	        visual micro and the arduino ide ignore this code during compilation. this code is automatically maintained by visualmicro, manual changes to this file will be overwritten
	        the contents of the Visual Micro sketch sub folder can be deleted prior to publishing a project
	        all non-arduino files created by visual micro and all visual studio project or solution files can be freely deleted and are not required to compile a sketch (do not delete your own code!).
	        note: debugger breakpoints are stored in '.sln' or '.asln' files, knowledge of last uploaded breakpoints is stored in the upload.vmps.xml file. Both files are required to continue a previous debug session without needing to compile and upload again
	
	Hardware: Teensy 3.1, Platform=avr, Package=teensy
*/

#define __ARM_MK20dx256__
#define __ARM_MK20DX256__
#define ARDUINO 106
#define ARDUINO_MAIN
#define __AVR__
#define F_CPU 96000000
#define USB_SERIAL
#define LAYOUT_US_ENGLISH
#define __MK20DX256__
#define TEENSYDUINO 123
extern "C" void __cxa_pure_virtual() {;}

float rollingAverage(float *store, int size, float entry);
void DoStatusUpdate();
void printAddress(DeviceAddress deviceAddress);
void printScratchpad(DeviceAddress deviceAddress,uint8_t* myScratchpad);
void printTemperature(DeviceAddress deviceAddress);
void printResolution(DeviceAddress deviceAddress);
void printData(DeviceAddress deviceAddress);
void setup(void);
void loop(void);

#include "C:\Users\Customer\Desktop\arduino-1.0.6\hardware\teensy\cores\teensy3\arduino.h"
#include <pyroLogger.ino>
#include <CommandParser.cpp>
#include <CommandParser.h>
#include <SdFatConfig.h>
