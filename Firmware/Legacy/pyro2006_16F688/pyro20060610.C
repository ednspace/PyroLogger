//Pyrometer Code
//Last Update ====>Friday June 30 2006
#include <16F688.h>
//#device adc=10
#use delay(clock=8000000)
#fuses NOWDT,INTRC_IO, NOPROTECT, BROWNOUT, MCLR, NOCPD, PUT, NOIESO, NOFCMEN

//Using Real Hardware Serial Port through MAX233
#use rs232(baud=9600,parity=N,xmit=PIN_C4,rcv=PIN_C5,bits=9)
#use rs232(baud=9600,parity=N,xmit=PIN_C4,rcv=PIN_C5,bits=8) 
#include <sandoz_ow.c>

int1 relay_active;
int8 j,data_MSB,data_LSB,status,data,pwm,overflow,seconds;
int16 current,temp;
float current_float,temp_float,temp_float_faren;
char command;

void blink(void);
void read_ramblock(void);
void read_netaddress(void);
void read_ambiant_temp(void);
void read_status(void);
void read_current(void);
void read_temp(void);
void scroll_test(void);
void blink(void);


#int_TIMER0
TIMER0_isr()
{
overflow ++;
if (overflow > 32){
   overflow = 0;
   seconds ++;

   if (relay_active == 1 & pwm != 0){
   output_high(PIN_A4);
   //printf ("Relay ON\r\n");
   }

   if (seconds >= 10){
   relay_active = 1;
   seconds = 0;
   }

   if (seconds > pwm){
   output_low(PIN_A4);
   //printf ("Relay Off\r\n");
   relay_active = 0;
   }
}
}

void main(){

setup_timer_0(RTCC_INTERNAL|RTCC_DIV_256);
setup_timer_1(T1_DISABLED);
setup_oscillator (OSC_8MHZ);
setup_adc_ports(NO_ANALOGS|VSS_VDD);
setup_adc(ADC_OFF);
setup_comparator(NC_NC_NC_NC);
setup_vref(FALSE);
enable_interrupts(INT_TIMER0);
enable_interrupts(GLOBAL);

relay_active = 0;
pwm = 0;
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
//printf("Please enter a command (h for help):\n\r");

command = getc();  //Gets a key from the keyboard
   switch (command){

   case 'c' :
         read_temp();
         printf("%3.2f\r\n",temp_float);
         blink();
         break;
   case 'f' :
         read_temp();
         printf("%4.2f\r\n",temp_float_faren);
         blink();
         break;
   case 'k' :
         read_current();
         printf("%4.7f\r\n",current_float);
         blink();
         break;
   case '0' :
         pwm = 0;
         break;
   case '1' :
         pwm = 1;
         break;
   case '2' :
         pwm = 2;
         break;
   case '3' :
         pwm = 3;
         break;
   case '4' :
         pwm = 4;
         break;
   case '5' :
         pwm = 5;
         break;
   case '6' :
         pwm = 6;
         break;
   case '7' :
         pwm = 7;
         break;
   case '8' :
         pwm = 8;
         break;
   case '9' :
         pwm = 9;
         break;
         }

}
}

void blink(){
output_high(PIN_C3);
delay_ms(250);
output_low(PIN_C3);
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
current_float=(current*.000015625);
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
read_current();
read_temp();
printf("mV===>(%2.3f)",current_float);
printf("    deg C===>(%3.2f)",temp_float);
printf("    deg F===>(%3.2f)\n\r",temp_float_faren);
}
