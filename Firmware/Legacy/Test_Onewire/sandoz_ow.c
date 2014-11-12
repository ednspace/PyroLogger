
// onewire library, for dallas onewire devices
// currently includes:
//   - generic onewire functions (init, readbyte, sendbyte, crc, etc.)
//   - ds1822 dallas-semi econo-thermometer

// (C) copyright 2003 j.d.sandoz / jds-pic !at! losdos.dyndns.org

// released under the GNU GENERAL PUBLIC LICENSE (GPL)
// refer to http://www.gnu.org/licenses/gpl.txt

// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 2 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


// ds1822 scratchpad registers
#define DS1822_SP_TLSB  0
#define DS1822_SP_TMSB  1
#define DS1822_SP_HLIM  2
#define DS1822_SP_LLIM  3
#define DS1822_SP_CFG   4
#define DS1822_SP_RES0  5
#define DS1822_SP_RES1  6
#define DS1822_SP_RES2  7
#define DS1822_SP_CRC   8

// ds1822 rom registers
#define DS1822_ROM_DEVTYPE  0
#define DS1822_ROM_SERIAL1  1
#define DS1822_ROM_SERIAL2  2
#define DS1822_ROM_SERIAL3  3
#define DS1822_ROM_SERIAL4  4
#define DS1822_ROM_SERIAL5  5
#define DS1822_ROM_SERIAL6  6
#define DS1822_ROM_CRC      7

// ds1822 command set
#define DS1822_CMD_READROM           0x33
#define DS1822_CMD_SKIPROM           0xCC
#define DS1822_CMD_CONVERTTEMP       0x44
#define DS1822_CMD_WRITESCRATCHPAD   0x4E
#define DS1822_CMD_READSCRATCHPAD    0xBE
#define DS1822_CMD_COPYSCRATCHPAD    0x48


// note that not all applications need to disable interrupts when
// performing onewire transactions.  but, if unmasked interrupts
// cause onewire timing violations, returned data will be suspect
// or there may be other, hard-to-reproduce problems.

void onewire_disable_interrupts(int disable) {
   if (disable)
     disable_interrupts(GLOBAL);
   else
     enable_interrupts(GLOBAL);
}


short int onewire_init_with_error_check() {
   onewire_disable_interrupts(TRUE);
   output_low(Pin_A5);
   delay_us( 500 ); // pull 1-wire low for reset pulse
   output_float(Pin_A5); // float 1-wire high
   delay_us( 5 );   // allow pin to stabilize
   if (!input(Pin_A5)) {
      onewire_disable_interrupts(FALSE);
      printf("One wire leads shorted\n\r");
      return ( FALSE ); // error (1-wire leads shorted)
      }
   delay_us( 80 ); // wait for presence pulse, allowing for device variation
   if (input(Pin_A5)) {
      onewire_disable_interrupts(FALSE);
      printf("No one wire device present\n\r");
      return ( FALSE ); // error (no 1-wire devices present)
      }
   delay_us( 420 ); // wait-out remaining initialisation window.
   output_float(Pin_A5);
   onewire_disable_interrupts(FALSE);
   printf("Device present and initialised\n\r");
   return ( TRUE ); // device(s) present and initialised.
}


void onewire_init() { // OK if just using a single permanently connected device
   onewire_disable_interrupts(TRUE);
   output_low(Pin_A5);
   delay_us( 500 ); // pull 1-wire low for reset pulse
   output_float(Pin_A5); // float 1-wire high
   delay_us( 80 ); // wait for presence pulse, allowing for device variation
   delay_us( 420 ); // wait-out remaining initialisation window.
   output_float(Pin_A5);
   onewire_disable_interrupts(FALSE);
}


void onewire_sendbyte(int data) {
   int count;
   //static int debugS;
   //printf(debug_putc,"0x%x >onewire_sendbyte(%u)\n\r",data,debugS++);
   onewire_disable_interrupts(TRUE);
   for (count=0; count<8; ++count) {
      output_low(Pin_A5);
      delay_us( 2 ); // pull 1-wire low to initiate write time-slot.
      output_bit(Pin_A5, shift_right(&data,1,0)); // set output bit on 1-wire
      delay_us( 60 ); // wait until end of write slot.
      output_float(Pin_A5); // set 1-wire high again,
      delay_us( 2 ); // for more than 1us minimum.
      }
   onewire_disable_interrupts(FALSE);
}


int onewire_readbyte() {
   //int count, data;
   int count,data;
   //static int debugR;
   onewire_disable_interrupts(TRUE);
   for (count=0; count<8; ++count) {
      output_low(Pin_A5);
      delay_us( 2 ); // pull 1-wire low to initiate read time-slot.
      output_float(Pin_A5); // now let 1-wire float high,
      delay_us( 8 ); // let device state stabilise,
      shift_right(&data,1,input(Pin_A5)); // and load result.
      delay_us( 120 ); // wait until end of read slot.
      }
   //printf("0x%x >onewire_readbyte(%u)\n\r",data);
   //printf("byte is ====>(%x)\n\r",data);
   onewire_disable_interrupts(FALSE);
   return( data );
}


int onewire_ds1822_read_scratchpad(int field) { /* returns config bitfield */
   int data[9];

   onewire_init();
   onewire_sendbyte(DS1822_CMD_SKIPROM);
   onewire_sendbyte(DS1822_CMD_READSCRATCHPAD);

   data[DS1822_SP_TLSB]=onewire_readbyte();    // 0 Tlsb
   data[DS1822_SP_TMSB]=onewire_readbyte();    // 1 Tmsb
   data[DS1822_SP_HLIM]=onewire_readbyte();    // 2 Thlim
   data[DS1822_SP_LLIM]=onewire_readbyte();    // 3 Tllim
   data[DS1822_SP_CFG]=onewire_readbyte();     // 4 Config
   data[DS1822_SP_RES0]=onewire_readbyte();    // 5 RES0
   data[DS1822_SP_RES1]=onewire_readbyte();    // 6 RES1
   data[DS1822_SP_RES2]=onewire_readbyte();    // 7 RES2
   data[DS1822_SP_CRC]=onewire_readbyte();     // 8 CRC

   if (field > 8) {
      //printf(debug_putc,"ERR! >scratchpad field 0x%x out of range (ds1822)\n\r",field);
      return(0);
      }
   else {
      //printf(debug_putc,"0x%x >scratchpad field 0x%x (ds1822)\n\r",data[field],field);
      return(data[field]);
      }
}


int onewire_ds1822_read_rom(int field) { /* rtns ROM info, one byte at a time */
   int data[8];

   if (!onewire_init_with_error_check())
     return (0);
   onewire_sendbyte(DS1822_CMD_READROM);

   data[DS1822_ROM_DEVTYPE]=onewire_readbyte();   // 0 family code
   data[DS1822_ROM_SERIAL1]=onewire_readbyte();   // 1 serial number LSB
   data[DS1822_ROM_SERIAL2]=onewire_readbyte();   // 2 serial number
   data[DS1822_ROM_SERIAL3]=onewire_readbyte();   // 3 serial number
   data[DS1822_ROM_SERIAL4]=onewire_readbyte();   // 4 serial number
   data[DS1822_ROM_SERIAL5]=onewire_readbyte();   // 5 serial number
   data[DS1822_ROM_SERIAL6]=onewire_readbyte();   // 6 serial number MSB
   data[DS1822_ROM_CRC]=onewire_readbyte();       // 7 CRC

   if (field > 7) {
      //printf(debug_putc,"ERR! >rom field 0x%x out of range (ds1822)\n\r",field);
      return(0);
      }
   else {
      //printf(debug_putc,"0x%x >rom field 0x%x (ds1822)\n\r",data[field],field);
      return(data[field]);
      }
}


int onewire_crc(int oldcrc, int newbyte) {
   // see http://pdfserv.maxim-ic.com/arpdf/AppNotes/app27.pdf
   int shift_reg, data_bit, sr_lsb, fb_bit, j;

   shift_reg=oldcrc;
   for(j=0; j<8; j++) {   // for each bit
      data_bit = (newbyte >> j) & 0x01;
      sr_lsb = shift_reg & 0x01;
      fb_bit = (data_bit ^ sr_lsb) & 0x01;
      shift_reg = shift_reg >> 1;
      if (fb_bit)
         shift_reg = shift_reg ^ 0x8c;
      }
   return(shift_reg);
}


int onewire_ds1822_set_temperature_resolution(int resolution) { /* set up for nbit resolution */
   int resolution_cfgfield;

   if ((resolution < 9) || (resolution > 12))
      resolution=9;

   resolution_cfgfield=((resolution-9)<<5);  // see DS1822 datasheet page 7

   if (!onewire_init_with_error_check())
     return (0);
   onewire_sendbyte(DS1822_CMD_SKIPROM);
   onewire_sendbyte(DS1822_CMD_WRITESCRATCHPAD);

   onewire_sendbyte(0b01111101);   // set max TH threshold (125'C)
   onewire_sendbyte(0b11001001);   // set min TL threshold (-55'C)
   onewire_sendbyte(resolution_cfgfield);    // Temp resolution, set to nbit

   onewire_init(); // reset
   onewire_sendbyte(DS1822_CMD_SKIPROM);
   onewire_sendbyte(DS1822_CMD_COPYSCRATCHPAD);
   delay_ms(15); // allow time for flash memory write.

   return( (onewire_ds1822_read_scratchpad(DS1822_SP_CFG) & 0b01100000)>>5 );
}


int onewire_ds1822_read_temp_c_lite() { /* 0 to 125'C byte rtnd, nonparasitic mode */
   int temperatureLSB, temperatureMSB, config, delaymult;

   config=((onewire_ds1822_read_scratchpad(DS1822_SP_CFG) && 0b01100000)>>5);
      // each addn'l resolution bit needs twice the base conversion time!
   if (!onewire_init_with_error_check())
     return (0);
   onewire_sendbyte(DS1822_CMD_SKIPROM);
   onewire_sendbyte(DS1822_CMD_CONVERTTEMP);

   delaymult=1<<config;
      //printf(debug_putc,"0x%x >delay_mult (ds1822)\n\r",delaymult);

   while (delaymult--)
      delay_ms(100); // allow worst case time for temp. conversion.

   temperatureLSB = onewire_ds1822_read_scratchpad(DS1822_SP_TLSB);
   temperatureMSB = onewire_ds1822_read_scratchpad(DS1822_SP_TMSB);

   if (temperatureMSB & 0b11111000) // if temp is negative rtn 0
      return(0);
   else {                           // else rtn the positive temp
      temperatureLSB=((temperatureLSB & 0b11110000)>>4);
      temperatureMSB=((temperatureMSB & 0b00000111)<<4);
      }
   return(temperatureMSB | temperatureLSB);  // OR msb&lsb
}





