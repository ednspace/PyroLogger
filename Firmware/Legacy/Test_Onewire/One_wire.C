//Test to see if we can get info from a Dallas One Wire Thermo
//Jan 10,2006
#include <16F688.h>
//#device adc=10
#use delay(clock=8000000)
#fuses NOWDT,INTRC_IO, NOPROTECT, BROWNOUT, NOMCLR, NOCPD, NOPUT, NOIESO, NOFCMEN
#use rs232(baud=9600,parity=N,xmit=PIN_C4,rcv=PIN_C5,bits=8) 
#include <sandoz_ow.c>


int8 j,data_MSB,data_LSB,status,loop_count;
int16 current,temp;
float current_float,temp_float,temp_float_faren,loop_average;
char command;

void read_ramblock(void);
void read_netaddress(void);
void read_ambiant_temp(void);
void read_status(void);
void read_current(void);
void read_temp(void);
void scroll_test(void);
//void onewire_readbyte(void);
//void onewire_sendbyte(void);
//void onewire_init(void);
//void onewire_disable_interrupts(void);

void main(){
   setup_oscillator( OSC_8MHZ );
   setup_adc_ports(sAN6|VSS_VDD);
   setup_adc(ADC_CLOCK_INTERNAL);
   setup_counters(RTCC_INTERNAL,RTCC_DIV_1);
   setup_timer_1(T1_DISABLED);
   setup_comparator(NC_NC_NC_NC);
   setup_vref(FALSE);

//Software workaround for the power switch floating
onewire_init();
onewire_sendbyte(0xCC);
onewire_sendbyte(0x6C);    //Write Data Command
onewire_sendbyte(0x31);    //Eeprom address but actually gets written to Shadow Ram
onewire_sendbyte(0xE7);    //Value to make PMOD1 SWEN=0 RNAOP=0

//Copy the shadow Ram written above over to actual EEPROM
onewire_init();
onewire_sendbyte(0xCC);
onewire_sendbyte(0x48);    //send the copy command
onewire_sendbyte(0x30);    //copy shadow ram to the block containing 31

while(true){
/*-------------------------------------------------------------------
Pull Reading From Temp Probe
-------------------------------------------------------------------*/
//Use the following to determine the state of the one wire net
//Will report if device present, not, or shorted
//Comment out rest of code
//onewire_init_with_error_check();
//read_status();
//printf("status byte is ====>(%x)\n\r",status);
printf("Please enter a command (h for help):\n\r");

command = getc();  //Gets a key from the keyboard
   switch (command){
   case 'h' :
         printf("Type any of the following commands:\n\r");
         printf("h     This Help Message\n\r");
         printf("C     Ambiant Temp in deg. C\n\r");
         printf("c     Ambiant Temp in deg. C(No Formatting)\n\r");
         printf("F     Ambiant Temp in deg. F\n\r");
         printf("f     Ambiant Temp in deg. F(No Formatting)\n\r");
         printf("N     64 bit node address in Hex\n\r");
         printf("K     Thermo millivolts\n\r");
         printf("k     Thermo millivolts(No Formatting)\n\r");
         printf("s     One line scroll test\n\r");
         break;
   case 'C' :
         read_temp();
         printf("    deg C===>(%3.2f)\n\r",temp_float);
         break;
   case 'c' :
         read_temp();
         printf("%3.2f\n\r",temp_float);
         break;
   case 'F' :
         read_temp();
         printf("    deg F===>(%3.2f)\n\r",temp_float_faren);
         break;
   case 'f' :
         read_temp();
         printf("%4.2f",temp_float_faren);
         break;
   case 'K' :
         read_current();
         printf("mV===>(%4.3f)\n\r",current_float);
         break;
   case 'k' :
         read_current();
         printf("%4.3f\n\r",current_float);
         break;
   case 's' :
         scroll_test();
         break;
   default :
         printf("Not a valid command:\n\r");
         }
         
delay_ms(1000);
}
}
void read_ramblock(){
onewire_init();
onewire_sendbyte(0xcc);  //Transmit skip Rom Command
onewire_sendbyte(0x69);  //0x69 Transmit Read RAM command
onewire_sendbyte(0x0C); //Transmit Read start address
Printf("================RamBlock====================\n\r");
for(j=0; j<=5; j++) {
onewire_readbyte();
}
Printf("===================END====================\n\r");
}

void read_netaddress(){
Printf("================Net Address====================\n\r");
onewire_init();
onewire_sendbyte(0x33);  //Transmit the ReadRom command
for(j=0; j<=7; j++) {
onewire_readbyte();
//delay_ms(1);
}
Printf("===================END====================\n\r");
}

void read_status(){
onewire_init();
onewire_sendbyte(0xCC);  //Transmit skip Rom Command
onewire_sendbyte(0x69);  //0x69 Transmit Read RAM command
onewire_sendbyte(0x01); //Transmit Read start address
status=onewire_readbyte();
}

void read_current(){
onewire_init();
onewire_sendbyte(0xCC);  //Transmit skip Rom Command
onewire_sendbyte(0x69);  //0x69 Transmit Read RAM command
onewire_sendbyte(0x0E); //Transmit Read start address
data_MSB=onewire_readbyte();
data_LSB=onewire_readbyte();
//printf("MSB ====>(%x)\n\r",data_MSB);
//printf("LSB ====>(%x)\n\r",data_LSB);
current=make16(data_MSB,data_LSB);
current=current >> 3;
//printf("current====>(%Lu)\n\r",current);
current_float=(current*.015625);
}

void read_temp(){
onewire_init();
onewire_sendbyte(0xCC);  //Transmit skip Rom Command
onewire_sendbyte(0x69);  //0x69 Transmit Read RAM command
onewire_sendbyte(0x18); //Transmit Read start address
data_MSB=onewire_readbyte();
data_LSB=onewire_readbyte();
temp=make16(data_MSB,data_LSB);
temp=temp >> 5;
temp_float=(temp *.125);
temp_float_faren=((temp_float * 1.8) + 32);
}

void scroll_test(){
loop_count = 0;
loop_average = 0;
while (loop_count < 10)
{
read_current();
read_temp();
printf("mV===>(%4.3f)",current_float);
loop_average = loop_average + current_float;
printf("    deg C===>(%3.2f)",temp_float);
printf("    deg F===>(%3.2f)\n\r",temp_float_faren);
loop_count ++;
delay_ms(1000);
}
loop_average = loop_average / 10;
printf("mV average===>(%4.3f)\n\r",loop_average);

}
