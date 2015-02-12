#include <Arduino.h>
#include <MegunoLink.h>
#include "CommandParser.h"

#include <OneWire.h>
#include <DallasTemperature.h>

InterfacePanel Panel;

// Data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 2
#define TEMPERATURE_PRECISION 9

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

// arrays to hold device addresses
DeviceAddress insideThermometer, outsideThermometer;

//Setup the temparature holding variables
float tempF;
float tempC;
float front;
float back;
int TempType=1; //0=Cel 1=F Default is F

//For the Megunolink time plots
long LastSent;  // Millis value when the data was last sent. 
int SendInterval = 3000; // Interval (milliseconds) between sending analog data
TimePlot PyroPlot;  // The plot we are sending data to.

//Get the MLP command parser up and running
MLP::CommandParser<> Parser;


//All Thy Functions Lie ;) Below
void DoSetTempC(MLP::CommandParameter &Parameter)
{
  Serial.print(F("Setting TempType to C"));
  TempType=0;
  
}

void DoSetTempF(MLP::CommandParameter &Parameter)
{
  Serial.print(F("Setting TempType to F"));
  TempType=1;
  
}

void DoSampleRate(MLP::CommandParameter &Parameter)
{
  const char *pchValue;

  pchValue = Parameter.NextParameter();
  if (pchValue == NULL)
  {
    Serial.println(F("Set interval missing parameter"));
    return;
  }

  SendInterval = atoi(pchValue);
}


// function to print a device address
void printAddress(DeviceAddress deviceAddress)
{
  for (uint8_t i = 0; i < 8; i++)
  {
    // zero pad the address if necessary
    if (deviceAddress[i] < 16) Serial.print("0");
    Serial.print(deviceAddress[i], HEX);
  }
}

// function to print the temperature for a device
void printTemperature(DeviceAddress deviceAddress)
{
  float tempC = sensors.getTempC(deviceAddress);
  Serial.print("Temp C: ");
  Serial.print(tempC);
  Serial.print(" Temp F: ");
  Serial.print(DallasTemperature::toFahrenheit(tempC));
}

// function to print a device's resolution
void printResolution(DeviceAddress deviceAddress)
{
  Serial.print("Resolution: ");
  Serial.print(sensors.getResolution(deviceAddress));
  Serial.println();    
}

// main function to print information about a device
void printData(DeviceAddress deviceAddress)
{
  Serial.print("Device Address: ");
  printAddress(deviceAddress);
  Serial.print(" ");
  printTemperature(deviceAddress);
  Serial.println();
}


void setup(void)
{
  // start serial port
  Serial.begin(57600);
  Serial.println("Dallas Temperature IC Control Library Demo");

  // Start up the library
  sensors.begin();

  // locate devices on the bus
  Serial.print("Locating devices...");
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount(), DEC);
  Serial.println(" devices.");

  // report parasite power requirements
  Serial.print("Parasite power is: "); 
  if (sensors.isParasitePowerMode()) Serial.println("ON");
  else Serial.println("OFF");

  // assign address manually.  the addresses below will beed to be changed
  // to valid device addresses on your bus.  device address can be retrieved
  // by using either oneWire.search(deviceAddress) or individually via
  // sensors.getAddress(deviceAddress, index)
  //insideThermometer = { 0x28, 0x1D, 0x39, 0x31, 0x2, 0x0, 0x0, 0xF0 };
  //outsideThermometer   = { 0x28, 0x3F, 0x1C, 0x31, 0x2, 0x0, 0x0, 0x2 };

  // search for devices on the bus and assign based on an index.  ideally,
  // you would do this to initially discover addresses on the bus and then 
  // use those addresses and manually assign them (see above) once you know 
  // the devices on your bus (and assuming they don't change).
  // 
  // method 1: by index
  if (!sensors.getAddress(insideThermometer, 0)) Serial.println("Unable to find address for Device 0"); 
  if (!sensors.getAddress(outsideThermometer, 1)) Serial.println("Unable to find address for Device 1"); 

  // method 2: search()
  // search() looks for the next device. Returns 1 if a new address has been
  // returned. A zero might mean that the bus is shorted, there are no devices, 
  // or you have already retrieved all of them.  It might be a good idea to 
  // check the CRC to make sure you didn't get garbage.  The order is 
  // deterministic. You will always get the same devices in the same order
  //
  // Must be called before search()
  //oneWire.reset_search();
  // assigns the first address found to insideThermometer
  //if (!oneWire.search(insideThermometer)) Serial.println("Unable to find address for insideThermometer");
  // assigns the seconds address found to outsideThermometer
  //if (!oneWire.search(outsideThermometer)) Serial.println("Unable to find address for outsideThermometer");

  // show the addresses we found on the bus
  Serial.print("Device 0 Address: ");
  printAddress(insideThermometer);
  Serial.println();

  Serial.print("Device 1 Address: ");
  printAddress(outsideThermometer);
  Serial.println();

  // set the resolution to 9 bit
  sensors.setResolution(insideThermometer, TEMPERATURE_PRECISION);
  sensors.setResolution(outsideThermometer, TEMPERATURE_PRECISION);

  Serial.print("Device 0 Resolution: ");
  Serial.print(sensors.getResolution(insideThermometer), DEC); 
  Serial.println();

  Serial.print("Device 1 Resolution: ");
  Serial.print(sensors.getResolution(outsideThermometer), DEC); 
  Serial.println();


  //Interface Control Panel 
  Parser.AddCommand(F("SetTempC"), DoSetTempC);
  Parser.AddCommand(F("SetTempF"), DoSetTempF);
  Parser.AddCommand(F("SampleRate"),DoSampleRate);
}



void loop(void)
{ 
  //Process any commands from MLP
  Parser.Process();


  // call sensors.requestTemperatures() to issue a global temperature 
  // request to all devices on the bus
  //Serial.print("Requesting temperatures...");
  //sensors.requestTemperatures(); //Might want to move this into the interval loop instead of main loop


 



  if ((millis() - LastSent) > SendInterval)
  {
    LastSent = millis();
    sensors.requestTemperatures(); //Lets try doing this call here to see if glitching goes away...

    //Update MeguinoLinkPro Plot Window
    tempC = sensors.getTempC(insideThermometer);
    tempF = DallasTemperature::toFahrenheit(tempC);

    if (TempType == 0)
    	{
    		front = tempC;
    	}
    if (TempType == 1)
    	{
    		front = tempF;
    	}


    PyroPlot.SendData("Front", front, TimePlot::Blue, TimePlot::Solid, 1 , TimePlot::NoMarker);
    //front = tempF;
    
    //Update MeguinoLinkPro Plot Window
    tempC = sensors.getTempC(outsideThermometer);
    tempF = DallasTemperature::toFahrenheit(tempC);

    if (TempType == 0)
    	{
    		back = tempC;
    	}
    if (TempType == 1)
    	{
    		back = tempF;
    	}

    PyroPlot.SendData("Back", back, TimePlot::Red, TimePlot::Solid, 1 , TimePlot::NoMarker);
    //back = tempF;

    //Print to the Message Monitor Window in MeguinoLinkPro
    Serial.print("{MESSAGE:");
	Serial.print("TemperatureFeed");
	Serial.print("|data|");
	Serial.print("Front ");
	Serial.print(front);
    Serial.print("\tBack ");
	Serial.print(back);
	Serial.println("}");


  }

  
}

