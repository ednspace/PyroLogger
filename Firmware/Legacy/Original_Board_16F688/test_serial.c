//Pyrometer Code
//Last Update ====>Saturday September 08 2007
#include <16F688.h>
#include<stdlib.h>
#use delay(clock=8000000)
#fuses NOWDT,INTRC_IO, NOPROTECT, BROWNOUT, MCLR, NOCPD, PUT, NOIESO, NOFCMEN

//Using Real Hardware Serial Port through MAX233
#use rs232(baud=9600,parity=N,xmit=PIN_C4,rcv=PIN_C5,bits=8) 

char command[5];
int8 first_num,sec_num,add;

void main(){
//Can't remove the oscillator setting as no longer works
setup_oscillator (OSC_8MHZ);
setup_timer_0(RTCC_INTERNAL|RTCC_DIV_256);
setup_timer_1(T1_DISABLED);
setup_adc_ports(NO_ANALOGS|VSS_VDD);
setup_adc(ADC_OFF);
setup_comparator(NC_NC_NC_NC);
setup_vref(FALSE);


while(true){

printf("Enter Command\n\r");
gets(command); 

if (command[0] == 'R')
	printf("I got a read command\n\r");
	
}
}


