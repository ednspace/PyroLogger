//Capture Code
//Last Update ====> Feb 2012
#include <16F1827.h>
#use delay(clock=8000000)
#fuses NOWDT,INTRC_IO, NOPROTECT, NOBROWNOUT, NOMCLR, NOCPD, PUT, NOIESO, NOFCMEN, PLL_SW
#use rs232(baud=19200,parity=N,xmit=PIN_B5,rcv=PIN_B2,bits=8)

//Setup I2C
#use i2c(master, sda=PIN_B1, scl=PIN_B4)
#define Device_SDA PIN_B1
#define Device_SLC PIN_B4

//Include Driver File
#include<ds2482-V2.c>

//Variable Declaration
int1 interactive=0;
int8 result;
int8 i,status;
char command;
int8 dataArray[6];
int32 CapValue;
float32 pF;

//********************************************************************************
//Functions
//********************************************************************************

//Blinker Code for the indicator LED
void blink(){
output_high(PIN_A2);
delay_ms(250);
output_low(PIN_A2);
delay_ms(250);
}

void main(){
setup_oscillator (OSC_8MHZ);
setup_timer_1(T1_DISABLED);
setup_adc_ports(NO_ANALOGS|VSS_VDD);
setup_adc(ADC_OFF);
setup_comparator(NC_NC_NC_NC);
setup_vref(FALSE);

// Give indiction that the microcontroller is up and running
for (i=0;i<5;i++){
blink();
}

//On boot interactive mode is on so that the user can use a terminal interface
interactive = 1;

//Main loop starts here...
while(true){  //Waits for a command to come in over the serial port in interactive mode   
if (interactive == 1)
   printf("Please enter a command (h for help):\n\r");

command = getc();

switch (command){
case 'i':  //Turn off interactive mode
   printf("Turning Off Interactive...\n\r");
   interactive = 0;
   printf("Done...\n\r");
   break;
   
case 'r':  //Reset DS2482
   if (interactive == 1){
      printf("Resetting the DS2482\n\r");
   }
   //Do the Reset
   result = ds2482_reset();
   
   if (interactive == 1){
      if (result == 1)
         printf("...Success...\n\r");
      else printf ("...Fail..\n\r");
   }
   break;
   
case 'c':  //Configure DS2482
//Active pullup should always be selected unless
//there is only a single slave on the 1-Wire line.
//0x01 1WS Disabled, SPU Disabled, 0 NC, APU Active Pullup (Normal Operation for more then one device on onewire bus)
//0x05 1WS Disabled, SPU Active, 0 NC, APU Active Pullup (Strong pullup is commonly used with 1-Wire parasitically powered temperature sensors, eeprom, A/D converters)

   if (interactive == 1){
      printf("Configuring the DS2482\n\r");
   }
   
   //Do the Config
   result = ds2482_write_config(0x01);
   
   if (interactive == 1){
      if (result == 1)
         printf("...Success...\n\r");
      else printf ("...Fail..\n\r");
   }
   break;
   
case 'R':  //Reset One Wire Bus
   if (interactive == 1){
      printf("Resetting the One Wire\n\r");
   }
   
   result = OWreset();
   
   if (interactive == 1){
      if (result == 1)
         printf("...Success...\n\r");
      else printf ("...Fail..\n\r");
   }
   break;
   
case 'n': //Read the Network Address
OWreset();
delay_ms(1);
OWWriteByte("33");
//delay_ms(20);

for(i=0; i<=7; i++) {
result = OWReadByte();
printf ("%2X",result);
delay_ms(1);
}

break;

case 's': //Read the OW status register
OWreset();
delay_ms(1);
OWWriteByte(204);  //Transmit skip Rom Command CC = 204
OWWriteByte(105);  //0x69 Transmit Read RAM command
OWWriteByte(1); //Transmit Read start address
result=OWReadByte();

break;
  


case 'f': //Fix the floating power switch

OWreset();
OWWriteByte(0xCC);
OWWriteByte(0x6C);    //Write Data Command
OWWriteByte(0x31);    //Eeprom address but actually gets written to Shadow Ram
OWWriteByte(0xE7);    //Value to make PMOD1 SWEN=0 RNAOP=0

//Copy the shadow Ram written above over to actual EEPROM
OWreset();
OWWriteByte(0xCC);
OWWriteByte(0x48);    //send the copy command
OWWriteByte(0x30);    //copy shadow ram to the block containing 31

break;   
   
   
   
default:  //Displays help message if you get an 'h' or an unknown command
   printf("PyroLogger Board Found and Responding...\n\r");
   printf("Firmware Version 2\n\r");
   printf("Interactive Mode is ON\n\r");
   printf("\n\r");
   printf("\n\r");
   printf("Command List:\n\r");
   printf("h = System Help\n\r");
   printf("i = Exit ineractive mode\n\r");
   printf("r = Reset DS2482\n\r");
   printf("c = Configure DS2482\n\r");
   printf("R = Reset One Wire Bus\n\r");
   printf("N = Print Net Address\n\r");
  
}

}
}
