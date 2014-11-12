/*
	DS2482-800 1-Wire Driver for accessing Maxim 1-wire devices

	Author:	 Charith Fernanado http://www.inmojo.com charith@inmojo.com 
	License: Released under the Creative Commons Attribution Share-Alike 3.0 License. 
			 http://creativecommons.org/licenses/by-sa/3.0
	Target:  Microchip PIC, dsPIC with CCS C Compiler


	Library Instructions:


*/

// constants/macros/typdefs
#define DS2482_I2C_ADDR		0x30	//< Base I2C address of DS2482 devices
#define POLL_LIMIT			0x30	// 0x30 is the minimum poll limit

//1-wire eeprom and silicon serial number commands
#define READ_DEVICE_ROM		0x33
#define SKIP_ROM			0xCC
#define WRITE_SCRATCHPAD	0x0F
#define READ_MEMORY			0xF0
#define COPY_SCRATCHPAD		0x55

// DS2482 command defines
#define DS2482_CMD_DRST		0xF0	//< DS2482 Device Reset
#define DS2482_CMD_SRP		0xE1	//< DS2482 Set Read Pointer
#define DS2482_CMD_WCFG		0xD2	//< DS2482 Write Configuration
#define DS2482_CMD_CHSL		0xC3	//< DS2482 Channel Select
#define DS2482_CMD_1WRS		0xB4	//< DS2482 1-Wire Reset
#define DS2482_CMD_1WWB		0xA5	//< DS2482 1-Wire Write Byte
#define DS2482_CMD_1WRB		0x96	//< DS2482 1-Wire Read Byte
#define DS2482_CMD_1WSB		0x87	//< DS2482 1-Wire Single Bit
#define DS2482_CMD_1WT		0x78	//< DS2482 1-Wire Triplet

// DS2482 status register bit defines
#define DS2482_STATUS_1WB	0x01	//< DS2482 Status 1-Wire Busy
#define DS2482_STATUS_PPD	0x02	//< DS2482 Status Presence Pulse Detect
#define DS2482_STATUS_SD	0x04	//< DS2482 Status Short Detected
#define DS2482_STATUS_LL	0x08	//< DS2482 Status 1-Wire Logic Level
#define DS2482_STATUS_RST	0x10	//< DS2482 Status Device Reset
#define DS2482_STATUS_SBR	0x20	//< DS2482 Status Single Bit Result
#define DS2482_STATUS_TSB	0x40	//< DS2482 Status Triplet Second Bit
#define DS2482_STATUS_DIR	0x80	//< DS2482 Status Branch Direction Taken

// DS2482 configuration register bit defines
#define DS2482_CFG_APU		0x01	//< DS2482 Config Active Pull-Up
#define DS2482_CFG_PPM		0x02	//< DS2482 Config Presence Pulse Masking
#define DS2482_CFG_SPU		0x04	//< DS2482 Config Strong Pull-Up
#define DS2482_CFG_1WS		0x08	//< DS2482 Config 1-Wire Speed

// DS2482 channel selection code for defines
#define DS2482_CH_IO0		0xF0	//< DS2482 Select Channel IO0
#define DS2482_CH_IO1		0xE1	//< DS2482 Select Channel IO1
#define DS2482_CH_IO2		0xD2	//< DS2482 Select Channel IO2
#define DS2482_CH_IO3		0xC3	//< DS2482 Select Channel IO3
#define DS2482_CH_IO4		0xB4	//< DS2482 Select Channel IO4
#define DS2482_CH_IO5		0xA5	//< DS2482 Select Channel IO5
#define DS2482_CH_IO6		0x96	//< DS2482 Select Channel IO6
#define DS2482_CH_IO7		0x87	//< DS2482 Select Channel IO7

// DS2482 channel selection read back code for defines
#define DS2482_RCH_IO0		0xB8	//< DS2482 Select Channel IO0
#define DS2482_RCH_IO1		0xB1	//< DS2482 Select Channel IO1
#define DS2482_RCH_IO2		0xAA	//< DS2482 Select Channel IO2
#define DS2482_RCH_IO3		0xA3	//< DS2482 Select Channel IO3
#define DS2482_RCH_IO4		0x9C	//< DS2482 Select Channel IO4
#define DS2482_RCH_IO5		0x95	//< DS2482 Select Channel IO5
#define DS2482_RCH_IO6		0x8E	//< DS2482 Select Channel IO6
#define DS2482_RCH_IO7		0x87	//< DS2482 Select Channel IO7

// DS2482 read pointer code defines
#define DS2482_READPTR_SR	0xF0	//< DS2482 Status Register
#define DS2482_READPTR_RDR	0xE1	//< DS2482 Read Data Register
#define DS2482_READPTR_CSR	0xD2	//< DS2482 Channel Selection Register
#define DS2482_READPTR_CR	0xC3	//< DS2482 Configuration Register


// DS2482 Funtion definition
int ds2482_reset(void);
int ds2482_detect(void);
int ds2482_write_config(unsigned char config);
int ds2482_channel_select(int channel); 
int oneWire_reset(void);
void oneWire_WriteBit(unsigned char sendbit);
unsigned char oneWire_ReadBit(void);
unsigned char oneWire_TouchBit(unsigned char sendbit);
void oneWire_WriteByte(unsigned char sendbyte);
unsigned char oneWire_ReadByte(void);
void oneWire_BlockTransfer(unsigned char *transfer_buffer, int length);
unsigned char oneWire_TouchByte(unsigned char sendbyte);





int ds2482_reset(){
	unsigned char status; 
	i2c_start(slaves);
	i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_WRITE);
	i2c_write(slaves, DS2482_CMD_DRST);
	i2c_start(slaves);
	i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_READ);
	status = i2c_read(slaves, I2C_READ_NACK);
	i2c_stop(slaves);
	
	// check for failure due to incorrect read back of status
	return ((status & 0xf7) == 0x10);
	
}	


int ds2482_detect(){
	if(!ds2482_reset())
		return false;
		
	if(!ds2482_write_config(DS2482_CFG_APU))
		return false;
		
	return true;
}	



int ds2482_write_config(unsigned char config){

unsigned char read_config; 

i2c_start(slaves);
i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_WRITE);
i2c_write(slaves, DS2482_CMD_WCFG);
I2C_write(slaves, config | (~config << 4));
i2c_start(slaves);
i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_READ);
read_config = i2c_read(slaves, I2C_READ_NACK);
i2c_stop(slaves);

// check for failure due to incorrect read back
if (config != read_config){
	DS2482_reset();
	return false;
}

return true;

}


int ds2482_channel_select(int channel){

unsigned char ch, ch_read, read_channel; 

switch (channel){
	default: case 0: ch = DS2482_CH_IO0; ch_read = DS2482_RCH_IO0; break;
	case 1: ch = DS2482_CH_IO1; ch_read = DS2482_RCH_IO1; break;
	case 2: ch = DS2482_CH_IO2; ch_read = DS2482_RCH_IO2; break;
	case 3: ch = DS2482_CH_IO3; ch_read = DS2482_RCH_IO3; break;
	case 4: ch = DS2482_CH_IO4; ch_read = DS2482_RCH_IO4; break;
	case 5: ch = DS2482_CH_IO5; ch_read = DS2482_RCH_IO5; break;
	case 6: ch = DS2482_CH_IO6; ch_read = DS2482_RCH_IO6; break;
	case 7: ch = DS2482_CH_IO7; ch_read = DS2482_RCH_IO7; break;
}

i2c_start(slaves);
i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_WRITE);
i2c_write(slaves, DS2482_CMD_CHSL);
I2C_write(slaves, ch);
i2c_start(slaves);
i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_READ);
read_channel = i2c_read(slaves, I2C_READ_NACK);
i2c_stop(slaves);

return (read_channel == ch_read);

}


int oneWire_reset(void){

unsigned char status = 0; 
int poll_count = 0;

i2c_start(slaves);
i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_WRITE);
i2c_write(slaves, DS2482_CMD_1WRS);
delay_us(1);
i2c_start(slaves);
i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_READ);
status = i2c_read(slaves, I2C_READ_ACK);

do{
	status = i2c_read(slaves, status & DS2482_STATUS_1WB);
} while((status & DS2482_STATUS_1WB) && (poll_count++ < POLL_LIMIT));

//write final NACK i2c command for confirmation 
i2c_read(slaves, I2C_READ_NACK);

//fprintf(usb, "status reg: %u\r\n", status);

i2c_stop(slaves);

if(poll_count >= POLL_LIMIT){
	DS2482_reset();
	return false;
}

// check for presence detect
if(status & DS2482_STATUS_PPD)
	return true;
else
	return false;

}


void oneWire_WriteBit(unsigned char sendbit){
	oneWire_TouchBit(sendbit);
}

unsigned char oneWire_ReadBit(void){
	return oneWire_TouchBit(0x01);
}

unsigned char oneWire_TouchBit(unsigned char sendbit){
unsigned char status;
int poll_count = 0;

i2c_start(slaves);
i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_WRITE);
i2c_write(slaves, DS2482_CMD_1WSB);
i2c_write(slaves, sendbit ? 0x80:0x00);
i2c_start(slaves);
i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_READ);
status = i2c_read(slaves, I2C_READ_ACK);

do{
	status = i2c_read(slaves, status & DS2482_STATUS_1WB);
} while ((status & DS2482_STATUS_1WB) && (poll_count++ < POLL_LIMIT));

i2c_read(slaves, I2C_READ_NACK);

i2c_stop(slaves);

if(poll_count >= POLL_LIMIT){
	DS2482_reset();
	return false;
}

// check for single bit result
if(status & DS2482_STATUS_SBR)
	return true;
else
	return false;

}


void oneWire_WriteByte(unsigned char sendbyte){
	unsigned char status;
	int poll_count = 0;
	
	i2c_start(slaves);
	i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_WRITE);
	i2c_write(slaves, DS2482_CMD_1WWB);
	i2c_write(slaves, sendbyte);
	i2c_start(slaves);
	i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_READ);
	status = i2c_read(slaves, I2C_READ_ACK);

	do{
		status = i2c_read(slaves, status & DS2482_STATUS_1WB);
	} while ((status & DS2482_STATUS_1WB) && (poll_count++ < POLL_LIMIT));
	
	//write final NACK i2c command for confirmation 
	i2c_read(slaves, I2C_READ_NACK);
		
	i2c_stop(slaves);
	
	if(poll_count >= POLL_LIMIT)
		DS2482_reset();
			
}


unsigned char oneWire_ReadByte(void){
	unsigned char data, status;
	int poll_count = 0;
	
	i2c_start(slaves);
	i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_WRITE);
	i2c_write(slaves, DS2482_CMD_1WRB);
	i2c_start(slaves);
	i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_READ);
	status = i2c_read(slaves, I2C_READ_ACK);

	do{
		status = i2c_read(slaves, status & DS2482_STATUS_1WB);
	} while ((status & DS2482_STATUS_1WB) && (poll_count++ < POLL_LIMIT));
	
	//write final NACK i2c command for confirmation 
	i2c_read(slaves, I2C_READ_NACK);

	i2c_stop(slaves);
	
	if(poll_count >= POLL_LIMIT){
		DS2482_reset();
		return false; 
	}
	
	i2c_start(slaves);
	i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_WRITE);
	i2c_write(slaves, DS2482_CMD_SRP);
	i2c_write(slaves, DS2482_READPTR_RDR);
	i2c_start(slaves);
	i2c_write(slaves, DS2482_I2C_ADDR | I2C_FLAG_READ);
	data = i2c_read(slaves, I2C_READ_NACK);
	i2c_stop(slaves);
		
	return data;
}


void oneWire_BlockTransfer(unsigned char *transfer_buffer, int length){
	int i;
	for(i = 0; i < length; i++)
		transfer_buffer[i] = oneWire_TouchByte(transfer_buffer[i]);
			
}

unsigned char oneWire_TouchByte(unsigned char sendbyte){
	if(sendbyte == 0xff)
		return oneWire_ReadByte();
	else{
		oneWire_WriteByte(sendbyte);
		return sendbyte;
	}
}