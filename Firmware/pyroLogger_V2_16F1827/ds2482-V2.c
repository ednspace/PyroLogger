//DS2482.h
//DS2482-800 device driver
//Code is based on Dallas App Note # 3684

//function headers:
int DS2482_reset(void);
int DS2482_write_config(unsigned char);
unsigned char OWTouchBit(unsigned char);
unsigned char OWTouchByte(unsigned char);
unsigned char DS2482_search_triplet(search_direction);
int OWReset(void);
int OWSearch(void);
//void calc_crc8(void);
//Global Variables / Defines:
unsigned char I2C_WRITE= 0;
unsigned char I2C_READ= 1;
#define DS2482_Base_Addr 0x30       //Address of DS2482 on I2C Buss if pins 6, 7 and 8 are tried low
#define NACK 0
#define ACK 1
#define STATUS_1WB  0b00000001
#define STATUS_PPD  0b00000010
#define STATUS_SD   0b00000100
#define STATUS_LL   0b00001000
#define STATUS_RST  0b00010000
#define STATUS_SBR  0b00100000
#define STATUS_TSB  0b01000000
#define STATUS_DIR  0b10000000
#define POLL_LIMIT 16               //Number of time to retry OW Buss Scan Waiting to unbusy it self

unsigned char CMD_DRST=0XF0;
unsigned char CMD_WCFG=0XD2;
unsigned char CMD_CHSL=0XC3;
unsigned char CMD_SRP=0XE1;
unsigned char CMD_1WRS=0XB4;
unsigned char CMD_1WWB=0XA5;
unsigned char CMD_1WRB=0X96;
unsigned char CMD_1WSB=0X87;
unsigned char CMD_1WT=0X78;



// DS2482 state
unsigned char I2C_address;
int c1WS, cSPU, cPPM, cAPU, CONFIG_APU=0x01;
int short_detected;
//--------------------------------------------------------------------------
// DS2482 Detect routine that sets the I2C address and then performs a
// device reset followed by writing the configuration byte to default values:
// 1-Wire speed (c1WS) = standard (0)
// Strong pullup (cSPU) = off (0)
// Presence pulse masking (cPPM) = off (0)
// Active pullup (cAPU) = on (CONFIG_APU = 0x01)
//
// Returns: TRUE if device was detected and written
// FALSE device not detected or failure to write configuration byte
//
int DS2482_detect(unsigned char addr)
{
   // set global address
   I2C_address = addr;
   // reset the DS2482 ON selected address
   if (!DS2482_reset())   
      return FALSE;
   // default configuration
   c1WS = FALSE;
   cSPU = FALSE;
   cPPM = FALSE;
   cAPU = CONFIG_APU;
   // write the default configuration setup
   if (!DS2482_write_config(c1WS | cSPU | cPPM | cAPU))   
      return FALSE;
   return TRUE;
}



//--------------------------------------------------------------------------
// Perform a device reset on the DS2482
//
// Returns: TRUE if device was reset
// FALSE device not detected or failure to perform reset
//
int DS2482_reset(void)
{
   unsigned char status;
   // Device Reset
   // S AD,0 [A] DRST [A] Sr AD,1 [A] [SS] A\ P
   // [] indicates from slave
   // SS status byte to read to verify state
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_WRITE);
   I2C_write(CMD_DRST);
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_READ);
   status = I2C_read(NACK);
   I2C_stop();
   // check for failure due to incorrect read back of status
   return ((status & 0xF7) == 0x10);
}




//--------------------------------------------------------------------------
// Write the configuration register in the DS2482. The configuration
// options are provided in the lower nibble of the provided config byte.
// The uppper nibble in bitwise inverted when written to the DS2482.
//
// Returns: TRUE: config written and response correct
// FALSE: response incorrect
//
int DS2482_write_config(unsigned char config)
{
   unsigned char read_config;
   // Write configuration (Case A)
   // S AD,0 [A] WCFG [A] CF [A] Sr AD,1 [A] [CF] A\ P
   // [] indicates from slave
   // CF configuration byte to write
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_WRITE);
   I2C_write(CMD_WCFG);
   I2C_write(config | (~config << 4));
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_READ);
   read_config = I2C_read(NACK);
   I2C_stop();
   // check for failure due to incorrect read back
   if (config != read_config)
   {
      // handle error
      // ...
      DS2482_reset();
      return FALSE;
   }

   return TRUE;
}




//--------------------------------------------------------------------------
// Select the 1-Wire channel on a DS2482-800.
//
// Returns: TRUE if channel selected
// FALSE device not detected or failure to perform select
//
int DS2482_channel_select(int channel)
{
   unsigned char ch, ch_read, check;
   // Channel Select (Case A)
   // S AD,0 [A] CHSL [A] CC [A] Sr AD,1 [A] [RR] A\ P
   // [] indicates from slave
   // CC channel value
   // RR channel read back
   I2C_start();
   I2C_write(I2C_address | I2C_WRITE);
   I2C_write(CMD_CHSL);
   switch (channel)
   {
      default: case 0: ch = 0xF0; ch_read = 0xB8; break;
               case 1: ch = 0xE1; ch_read = 0xB1; break;
               case 2: ch = 0xD2; ch_read = 0xAA; break;
               case 3: ch = 0xC3; ch_read = 0xA3; break;
               case 4: ch = 0xB4; ch_read = 0x9C; break;
               case 5: ch = 0xA5; ch_read = 0x95; break;
               case 6: ch = 0x96; ch_read = 0x8E; break;
               case 7: ch = 0x87; ch_read = 0x87; break;
   };
   I2C_write(ch);
   I2C_start();
   I2C_write(I2C_address | I2C_READ);
   check = I2C_read(NACK);
   I2C_stop();
   // check for failure due to incorrect read back of channel
   return (check == ch_read);
}





//--------------------------------------------------------------------------
// Reset all of the devices on the 1-Wire Net and return the result.
//
// Returns: TRUE(1): presence pulse(s) detected, device(s) reset
// FALSE(0): no presence pulses detected
//
int OWReset(void)
{
   unsigned char status;
   int poll_count = 0;
   // 1-Wire reset
   // S AD,0 [A] 1WRS [A] Sr AD,1 [A] [Status] A [Status] A\ P
   // \--------/
   // [] indicates from slave
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_WRITE);
   I2C_write(CMD_1WRS);
   I2C_stop();
   /*
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_READ);   
   status = I2C_read(ACK);
   do
   {
     status= I2C_read(ACK);
     // status = (status & STATUS_1WB);
   }
   while ((status & STATUS_1WB) && (poll_count++ < POLL_LIMIT));
   
   I2C_stop();
   // check for failure due to poll limit reached
   if (poll_count >= POLL_LIMIT)
   {
      // handle error
      //lcd_gotoxy(1,1);
     // print(lcd_putc,"OW pole timed out");
      // ...
      DS2482_reset();
   return FALSE;
   }

   // check for short condition
   if (status & STATUS_SD)
      short_detected = TRUE;
   else
      short_detected = FALSE;
      // check for presence detect
   if (status & STATUS_PPD)
      return TRUE;
   else
      return FALSE;
      
 */
}




//--------------------------------------------------------------------------
// Send 1 bit of communication to the 1-Wire Net.
// The parameter 'sendbit' least significant bit is used.
//
// 'sendbit' - 1 bit to send (least significant byte)
//
void OWWriteBit(unsigned char sendbit)
{
OWTouchBit(sendbit);
}
//--------------------------------------------------------------------------
// Reads 1 bit of communication from the 1-Wire Net and returns the
// result
//
// Returns: 1 bit read from 1-Wire Net
//
unsigned char OWReadBit(void)
{
return OWTouchBit(0x01);
}




//--------------------------------------------------------------------------
// Send 1 bit of communication to the 1-Wire Net and return the
// result 1 bit read from the 1-Wire Net. The parameter 'sendbit'
// least significant bit is used and the least significant bit
// of the result is the return bit.
//
// 'sendbit' - the least significant bit is the bit to send
//
// Returns: 0: 0 bit read from sendbit
// 1: 1 bit read from sendbit
//
unsigned char OWTouchBit(unsigned char sendbit)
{
unsigned char status;
int poll_count = 0;
// 1-Wire bit (Case B)
// S AD,0 [A] 1WSB [A] BB [A] Sr AD,1 [A] [Status] A [Status] A\ P
// \--------/
// Repeat until 1WB bit has changed to 0
// [] indicates from slave
// BB indicates byte containing bit value in msbit
I2C_start();
I2C_write(I2C_address | I2C_WRITE);
I2C_write(CMD_1WSB);
I2C_write(sendbit ? 0x80 : 0x00);
I2C_start();
I2C_write(I2C_address | I2C_READ);
// loop checking 1WB bit for completion of 1-Wire operation
// abort if poll limit reached
status = I2C_read(ACK);
do
{
status = I2C_read(status & STATUS_1WB);
}
while ((status & STATUS_1WB) && (poll_count++ < POLL_LIMIT));
I2C_stop();
// check for failure due to poll limit reached
if (poll_count >= POLL_LIMIT)
{
// handle error
// ...
DS2482_reset();
return 0;
}
// return bit state
if (status & STATUS_SBR)
   return 1;
else
  return 0;
}





//--------------------------------------------------------------------------
// Send 8 bits of communication to the 1-Wire Net and verify that the
// 8 bits read from the 1-Wire Net are the same (write operation).
// The parameter 'sendbyte' least significant 8 bits are used.
//
// 'sendbyte' - 8 bits to send (least significant byte)
//
// Returns: TRUE: bytes written and echo was the same
// FALSE: echo was not the same
//
void OWWriteByte(unsigned char sendbyte)
{
   printf("chr=%2X",sendbyte);
   unsigned char status;
   int poll_count = 0;
   // 1-Wire Write Byte (Case B)
   // S AD,0 [A] 1WWB [A] DD [A] Sr AD,1 [A] [Status] A [Status] A\ P
   // \--------/
   // Repeat until 1WB bit has changed to 0
   // [] indicates from slave
   // DD data to write
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_WRITE);
   I2C_write(CMD_1WWB);
   I2C_write(sendbyte);
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_READ);
   // loop checking 1WB bit for completion of 1-Wire operation
   // abort if poll limit reached
   status = I2C_read(ACK);
   do
   {
      status = I2C_read(status & STATUS_1WB);
   }
   while ((status & STATUS_1WB) && (poll_count++ < POLL_LIMIT));
   
   I2C_stop();
   
   // check for failure due to poll limit reached
   if (poll_count >= POLL_LIMIT)
   {
      // handle error
      // ...
      DS2482_reset();
   }
}





//--------------------------------------------------------------------------
// Send 8 bits of read communication to the 1-Wire Net and return the
// result 8 bits read from the 1-Wire Net.
//
// Returns: 8 bits read from 1-Wire Net
//
unsigned char OWReadByte(void)
{
   unsigned char data, status;
   int poll_count = 0;
   // 1-Wire Read Bytes (Case C)
   // S AD,0 [A] 1WRB [A] Sr AD,1 [A] [Status] A [Status] A\
   // \--------/
   // Repeat until 1WB bit has changed to 0
   // Sr AD,0 [A] SRP [A] E1 [A] Sr AD,1 [A] DD A\ P
   //
   // [] indicates from slave
   // DD data read
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_WRITE);
   I2C_write(CMD_1WRB);
   
   /*
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_READ);
   // loop checking 1WB bit for completion of 1-Wire operation
   // abort if poll limit reached
   status = I2C_read(ACK);
   do
   {
      status = I2C_read(status & STATUS_1WB);
   }
   while ((status & STATUS_1WB) && (poll_count++ < POLL_LIMIT));
   // check for failure due to poll limit reached
   if (poll_count >= POLL_LIMIT)
   {
      // handle error
      // ...
      DS2482_reset();
      return 0;
   }
   */
   delay_ms(1);
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_WRITE);
   I2C_write(CMD_SRP);
   //I2C_write(0x96);
   I2C_write(0xE1);
   I2C_start();
   I2C_write(DS2482_Base_Addr | I2C_READ);
   data = I2C_read(NACK);
   I2C_stop();
   return data;
}




//--------------------------------------------------------------------------
// The 'OWBlock' transfers a block of data to and from the
// 1-Wire Net. The result is returned in the same buffer.
//
// 'tran_buf' - pointer to a block of unsigned
// chars of length 'tran_len' that will be sent
// to the 1-Wire Net
// 'tran_len' - length in bytes to transfer
//
void OWBlock(unsigned char *tran_buf, int tran_len)
{
   int i;
   for (i = 0; i < tran_len; i++)
   tran_buf[i] = OWTouchByte(tran_buf[i]);
}
//--------------------------------------------------------------------------
// Send 8 bits of communication to the 1-Wire Net and return the
// result 8 bits read from the 1-Wire Net. The parameter 'sendbyte'
// least significant 8 bits are used and the least significant 8 bits
// of the result are the return byte.
//
// 'sendbyte' - 8 bits to send (least significant byte)
//
// Returns: 8 bits read from sendbyte
//
unsigned char OWTouchByte(unsigned char sendbyte)
{
   if (sendbyte == 0xFF)
   
      return OWReadByte();
   
   else
   {
      OWWriteByte(sendbyte);
      return sendbyte;
   }
}



// Search state
unsigned char ROM_NO[8];
int LastDiscrepancy;
int LastFamilyDiscrepancy;
int LastDeviceFlag;
unsigned char crc8;
//--------------------------------------------------------------------------
// Find the 'first' devices on the 1-Wire network
// Return TRUE : device found, ROM number in ROM_NO buffer
// FALSE : no device present
//
int OWFirst()
{
   // reset the search state
   LastDiscrepancy = 0;
   LastDeviceFlag = FALSE;
   LastFamilyDiscrepancy = 0;
   return OWSearch();
}
//--------------------------------------------------------------------------
// Find the 'next' devices on the 1-Wire network
// Return TRUE : device found, ROM number in ROM_NO buffer
// FALSE : device not found, end of search
//
int OWNext()
{
   // leave the search state alone
   return OWSearch();
}




//--------------------------------------------------------------------------
// The 'OWSearch' function does a general search. This function
// continues from the previous search state. The search state
// can be reset by using the 'OWFirst' function.
// This function contains one parameter 'alarm_only'.
// When 'alarm_only' is TRUE (1) the find alarm command
// 0xEC is sent instead of the normal search command 0xF0.
// Using the find alarm command 0xEC will limit the search to only
// 1-Wire devices that are in an 'alarm' state.
//
// Returns: TRUE (1) : when a 1-Wire device was found and its
// Serial Number placed in the global ROM
// FALSE (0): when no new device was found. Either the
// last search was the last device or there
// are no devices on the 1-Wire Net.
//
int OWSearch(void)
{
   int id_bit_number;
   int last_zero, rom_byte_number, search_result;
   int id_bit, cmp_id_bit;
   unsigned char rom_byte_mask, search_direction, status;
   // initialize for search
   id_bit_number = 1;
   last_zero = 0;
   rom_byte_number = 0;
   rom_byte_mask = 1;
   search_result = FALSE;
   crc8 = 0;
   // if the last call was not the last one
   if (!LastDeviceFlag)
   {
      // 1-Wire reset
      if (!OWReset())
      {
         // reset the search
         LastDiscrepancy = 0;
         LastDeviceFlag = FALSE;
         LastFamilyDiscrepancy = 0;
         return FALSE;
      }
      // issue the search command
      OWWriteByte(0xF0);
      // loop to do the search
      do
      {
         // if this discrepancy if before the Last Discrepancy
         // on a previous next then pick the same as last time
         if (id_bit_number < LastDiscrepancy)
         {
            if ((ROM_NO[rom_byte_number] & rom_byte_mask) > 0)
               search_direction = 1;
            else
               search_direction = 0;
         }
         else
         {
             // if equal to last pick 1, if not then pick 0
            if (id_bit_number == LastDiscrepancy)
               search_direction = 1;
            else
               search_direction = 0;
         }
         // Perform a triple operation on the DS2482 which will perform
         // 2 read bits and 1 write bit
         status = DS2482_search_triplet(search_direction);
         // check bit results in status byte
         id_bit = ((status & STATUS_SBR) == STATUS_SBR);
         cmp_id_bit = ((status & STATUS_TSB) == STATUS_TSB);
         search_direction =((status & STATUS_DIR) == STATUS_DIR) ? (byte)1 : (byte)0;
                               
         // check for no devices on 1-Wire
         if ((id_bit) && (cmp_id_bit))
            break;
         else
         {
            if ((!id_bit) && (!cmp_id_bit) && (search_direction == 0))
         {
            last_zero = id_bit_number;
            // check for Last discrepancy in family
            if (last_zero < 9)
               LastFamilyDiscrepancy = last_zero;
         }
         // set or clear the bit in the ROM byte rom_byte_number
         // with mask rom_byte_mask
         if (search_direction == 1)
            ROM_NO[rom_byte_number] |= rom_byte_mask;
         else
            ROM_NO[rom_byte_number] &= (byte)~rom_byte_mask;
         // increment the byte counter id_bit_number
         // and shift the mask rom_byte_mask
         id_bit_number++;
         rom_byte_mask <<= 1;
         // if the mask is 0 then go to new SerialNum byte rom_byte_number
         // and reset mask
         if (rom_byte_mask == 0)
         {
            //calc_crc8(ROM_NO[rom_byte_number]); // accumulate the CRC
            rom_byte_number++;
            rom_byte_mask = 1;
         }
      }
   }
   while(rom_byte_number < 8); // loop until through all ROM bytes 0-7
   // if the search was successful then
   if (!((id_bit_number < 65) || (crc8 != 0)))
   {
      // search successful so set LastDiscrepancy,LastDeviceFlag
      // search_result
      LastDiscrepancy = last_zero;
      // check for last device
      if (LastDiscrepancy == 0)
      LastDeviceFlag = TRUE;
      search_result = TRUE;
      }
   }

   // if no device found then reset counters so next
   // 'search' will be like a first
   if (!search_result || (ROM_NO[0] == 0))
   {
      LastDiscrepancy = 0;
      LastDeviceFlag = FALSE;
      LastFamilyDiscrepancy = 0;
      search_result = FALSE;
   }
   return search_result;
}

