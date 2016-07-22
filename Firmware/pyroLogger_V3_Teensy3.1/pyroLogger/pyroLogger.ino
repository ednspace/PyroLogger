#include <Arduino.h>
#include <MegunoLink.h>
#include "CommandParser.h"  //A local version of this library changes from the original may exist
#include <OneWire.h>
#include "DallasTemperature.h"
#include <SPI.h>
//#include <SdFat.h>

InterfacePanel Panel;
//SdFat sd;
//SdFile myFile;




// Data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 2
//#define ONE_WIRE_BUS 3

#define TEMPERATURE_PRECISION 12 //Not sure what this is doing yet, needs research seems to default to 12 always

// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature sensors(&oneWire);

// arrays to hold device addresses
DeviceAddress frontThermometer, backThermometer;
uint8_t myScratchpad;

//Some Variables to Hold the Temperatures
float tempF;
float tempC;
float front;
float back;

//Averaging Variables
float frontAverage;
float backAverage;
float frontAverageArray[25];
float backAverageArray[25];
int averageCount=0;
int dataLength = 0;

//Status Variables Control the ON off State of functionality from MeguinoLinkPro
int averageStatus=0; //0=Averaging OFF 1=Averaging ON
int tempStatus=1; //0=Celsius 1=Fahrenheit start condition - can be changed in GUI also
int filterStatus=1; //0=Filter Data is Off 1=Filter Data is on
int loggingStatus=0; //0=Logging is Off 1=Filter Logging is on
int fileCounter = 0;

//For the MeguinoLinkPro time plots
long LastSent;  // Millis value when the data was last sent. 
int SendInterval = 3000; // Interval (milliseconds) between sending analog data - can be changed in GUI also
TimePlot PyroPlot;  // Name of the Meguino Plot Window where data will be sent

//For the status LED
int LED = 6;

//Get the MLP command parser up and running
MLP::CommandParser<> Parser;


//All Thy Functions doth Lie ;) Below
float rollingAverage(float *store, int size, float entry)
{
	int l;
	float total = 0;
	float result;

	for(l=0; l<size-1; l++)
	{
		store[l] = store[l+1];
		total += store[l];
	}
	store[size-1] = entry;
	total += entry;
	result = total / (float)size;

	return result;
}

void DoSetTempC(MLP::CommandParameter &Parameter)
{
  Serial.print(F("Setting TempType to C"));
  tempStatus=0;
  
      DoStatusUpdate();
  
}

void DoSetTempF(MLP::CommandParameter &Parameter)
{
  Serial.print(F("Setting TempType to F"));
  tempStatus=1;
  
      DoStatusUpdate();
  
  
  
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
  
  DoStatusUpdate();
}

void DoAveragingON(MLP::CommandParameter &Parameter)
{
	const char *pchValue;

	pchValue = Parameter.NextParameter();
	if (pchValue == NULL)
	{
		Serial.println(F("Averaging Data Points missing parameter"));
		return;
	}

	
	Serial.println(F("Turning On Averaging"));
	dataLength = atoi(pchValue);
	averageStatus = 1; //Turn on the Averaging later in the code
	
	DoStatusUpdate();
	
	
	
}

void DoAveragingOFF(MLP::CommandParameter &Parameter)
{
	
	Serial.println(F("Turning OFF Averaging"));
	averageStatus = 0; //Turn off the Averaging later in the code
	
	DoStatusUpdate();
	
}

void DoLoggingOFF(MLP::CommandParameter &Parameter)
{
	
	Serial.println(F("Turning OFF Logging"));
	loggingStatus = 0; //Turn off logging later in the code
	
	DoStatusUpdate();
	
	
	
}

/*
void DoLogggingON(MLP::CommandParameter &Parameter)
{
	
	Serial.println(F("Turning ON Logging"));
	// initialize the SD card at SPI_HALF_SPEED to avoid bus errors with
	// breadboards.  use SPI_FULL_SPEED for better performance.
	if (!sd.begin (10, SPI_HALF_SPEED))
	  {
		  Serial.println(F("SD Communication Error"));
		  return;  // failed to start
	  }
	loggingStatus = 1; //Turn on Logging later in the code
	fileCounter = 0; //Reset the file counter
	
	DoStatusUpdate();
	
	
}
*/

void DoStatusUpdate(){
	//Update Status Table
	
	//Clear the Table
	Serial.print("{TABLE");
		Serial.print("|CLEAR|");
	Serial.println("}");
	
	
	//Update Table Temperature Status
	if (tempStatus == 1){
		Serial.print("{TABLE");
			Serial.print("|SET|");
			Serial.print("Temperature");
			Serial.print("|");
			Serial.print("Fahrenheit");
		Serial.println("}");
	}
	if (tempStatus == 0){
		Serial.print("{TABLE");
			Serial.print("|SET|");
			Serial.print("Temperature");
			Serial.print("|");
			Serial.print("Celcius");
		Serial.println("}");
	}
	
	//Update Table Sample Rate
	Serial.print("{TABLE");
		Serial.print("|SET|");
		Serial.print("Sample Rate");
		Serial.print("|");
		Serial.print(SendInterval / 1000);
		Serial.print("|");
		Serial.print("Seconds");
		
		
	Serial.println("}");
	
	
	//Update Table Average Status
	if (averageStatus == 1){
		Serial.print("{TABLE");
			Serial.print("|SET|");
			Serial.print("Averaging");
			Serial.print("|");
			Serial.print("ON");
			Serial.print("|");
			Serial.print("Points ");
			Serial.print(dataLength);
		Serial.println("}");
	}
	
	if (averageStatus == 0) {
		Serial.print("{TABLE");
			Serial.print("|CLEAR|");
			Serial.print("Averaging");
		Serial.println("}");
		
		Serial.print("{TABLE");
			Serial.print("|SET|");
			Serial.print("Averaging");
			Serial.print("|");
			Serial.print("OFF");
		Serial.println("}");
	}
	
	//Update Table Logging Status
	if (loggingStatus == 1) {
		Serial.print("{TABLE");
			Serial.print("|SET|");
			Serial.print("SD Logging");
			Serial.print("|");
			Serial.print("ON");
		Serial.println("}");
	}
	
	if (loggingStatus == 0) {
		Serial.print("{TABLE");
			Serial.print("|SET|");
			Serial.print("SD Logging");
			Serial.print("|");
			Serial.print("OFF");
		Serial.println("}");
	}
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

// function to read the scratchpad for a device
void printScratchpad(DeviceAddress deviceAddress,uint8_t* myScratchpad)
{
	sensors.readScratchPad(deviceAddress,myScratchpad);
	//Serial.print("Temp C: ");
	
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
  
  pinMode(LED, OUTPUT);

  // Start up the library
  sensors.begin();
delay(5000);
  // locate devices on the bus
  Serial.print("Locating devices...");
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount(), DEC);
  Serial.println(" devices.");

  // report parasite power requirements
  Serial.print("Parasite power is: "); 
  if (sensors.isParasitePowerMode()) Serial.println("ON");
  else Serial.println("OFF");

  // assign address manually.  the addresses below will need to be changed
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
  if (!sensors.getAddress(frontThermometer, 0)) Serial.println("Unable to find address for Device 0"); 
  if (!sensors.getAddress(backThermometer, 1)) Serial.println("Unable to find address for Device 1"); 

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
  printAddress(frontThermometer);
  Serial.println();

  Serial.print("Device 1 Address: ");
  printAddress(backThermometer);
  Serial.println();

  // set the resolution to 12 bit
  sensors.setResolution(frontThermometer, TEMPERATURE_PRECISION);
  sensors.setResolution(backThermometer, TEMPERATURE_PRECISION);

  Serial.print("Device 0 Resolution: ");
  Serial.print(sensors.getResolution(frontThermometer), DEC); 
  Serial.println();

  Serial.print("Device 1 Resolution: ");
  Serial.print(sensors.getResolution(backThermometer), DEC); 
  Serial.println();


  //Interface Control Panel 
  Parser.AddCommand(F("SetTempC"), DoSetTempC);
  Parser.AddCommand(F("SetTempF"), DoSetTempF);
  Parser.AddCommand(F("SampleRate"),DoSampleRate);
  Parser.AddCommand(F("AveragingON"),DoAveragingON);
  Parser.AddCommand(F("AveragingOFF"),DoAveragingOFF);
 // Parser.AddCommand(F("LoggingOFF"),DoLoggingOFF);
 // Parser.AddCommand(F("LoggingON"),DoLogggingON);
  
 
	  
  }




void loop(void)
{ 
  //Process any commands from MLP
  Parser.Process();



  if ((millis() - LastSent) > SendInterval) //Enough Time Has passed so take the readings now
  {
     
	
	digitalWrite(LED, HIGH); //Turn on the status LED
    sensors.requestTemperatures(); //Ask for the temperatures
	
	
    
    tempC = sensors.getTempC(frontThermometer);
    tempF = DallasTemperature::toFahrenheit(tempC);
	
	if (averageStatus == 1 && tempStatus == 1){
		frontAverage=rollingAverage(frontAverageArray,dataLength,tempF);
		front = frontAverage;
	}
	
	if (averageStatus == 1 && tempStatus == 0){
		frontAverage=rollingAverage(frontAverageArray,dataLength,tempC);
		front = frontAverage;
	}
	
	if (averageStatus == 0 && tempStatus == 1){
		front = tempF;
	}
	
	if (averageStatus == 0 && tempStatus == 0){
		front = tempC;
	}
	PyroPlot.SendData("Front", front, TimePlot::Blue, TimePlot::Solid, 1 , TimePlot::NoMarker);
    
    //Update MeguinoLinkPro Plot Window
    tempC = sensors.getTempC(backThermometer);
    tempF = DallasTemperature::toFahrenheit(tempC);

    if (averageStatus == 1 && tempStatus == 1){
	    backAverage=rollingAverage(backAverageArray,dataLength,tempF);
	    back = backAverage;
    }
    
    if (averageStatus == 1 && tempStatus == 0){
	    backAverage=rollingAverage(backAverageArray,dataLength,tempC);
	    back = backAverage;
    }
    
    if (averageStatus == 0 && tempStatus == 1){
	    back = tempF;
    }
    
    if (averageStatus == 0 && tempStatus == 0){
	    back = tempC;
    }
	PyroPlot.SendData("Back", back, TimePlot::Red, TimePlot::Solid, 1 , TimePlot::NoMarker);
/*
	if (loggingStatus == 1){
		// open the file for write at end like the Native SD library
		if (!myFile.open ("pyro.txt",  O_CREAT | O_WRITE | O_APPEND))
		{
			Serial.println(F("File Error"));
			return;  // failed to start
		}
	        myFile.print(fileCounter);
		myFile.print (",     ");
  	myFile.print(front);
		myFile.print (",     ");
		myFile.print (back);
		myFile.println();
		myFile.close();
		fileCounter = fileCounter + 1;
	}
 */
    
	

    //Print to the Message Monitor Window in MeguinoLinkPro
    Serial.print("{MESSAGE:");
	Serial.print("TemperatureFeed");
	Serial.print("|data|");
	Serial.print("Front ");
	Serial.print(front);
    Serial.print("\tBack ");
	Serial.print(back);
	Serial.println("}");
	
	
     DoStatusUpdate();
	 
	 //Turn off the Status LED
	 digitalWrite(LED, LOW); //Turn off the status LED
	 
	 //Reset Millis here at the end for more accurate timing
	 LastSent = millis();
     

	//Some Debug Poop
	
	//Serial.print("Device 0 Resolution: ");
	//Serial.print(sensors.getResolution(frontThermometer), DEC);
	//Serial.println();
	

  }

  
}

