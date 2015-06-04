################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL := cmd.exe
RM := rm -rf

USER_OBJS :=

LIBS := 
PROJ := 

O_SRCS := 
C_SRCS := 
S_SRCS := 
S_UPPER_SRCS := 
OBJ_SRCS := 
ASM_SRCS := 
PREPROCESSING_SRCS := 
OBJS := 
OBJS_AS_ARGS := 
C_DEPS := 
C_DEPS_AS_ARGS := 
EXECUTABLES := 
OUTPUT_FILE_PATH :=
OUTPUT_FILE_PATH_AS_ARGS :=
AVR_APP_PATH :=$$$AVR_APP_PATH$$$
QUOTE := "
ADDITIONAL_DEPENDENCIES:=
OUTPUT_FILE_DEP:=
LIB_DEP:=
LINKER_SCRIPT_DEP:=

# Every subdirectory with source files must be described here
SUBDIRS :=  \
../Visual\ Micro/


# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS +=  \
../CommandParser.cpp


PREPROCESSING_SRCS += 


ASM_SRCS += 


OBJS +=  \
CommandParser.o

OBJS_AS_ARGS +=  \
CommandParser.o

C_DEPS +=  \
CommandParser.d

C_DEPS_AS_ARGS +=  \
CommandParser.d

OUTPUT_FILE_PATH +=pyroLogger.elf

OUTPUT_FILE_PATH_AS_ARGS +=pyroLogger.elf

ADDITIONAL_DEPENDENCIES:=

OUTPUT_FILE_DEP:= ./makedep.mk

LIB_DEP+= 

LINKER_SCRIPT_DEP+= 


# AVR32/GNU C Compiler



./%.o: .././%.cpp
	@echo Building file: $<
	@echo Invoking: AVR8/GNU C Compiler : 4.8.1
	$(QUOTE)D:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.1061\avr8-gnu-toolchain\bin\avr-g++.exe$(QUOTE) -funsigned-char -funsigned-bitfields -D__ARM_MK20dx256__ -D__ARM_MK20DX256__ -DARDUINO=106 -DARDUINO_MAIN -D__AVR__ -DF_CPU=96000000 -DUSB_SERIAL -DLAYOUT_US_ENGLISH -D__MK20DX256__ -DTEENSYDUINO=123  -I"C:/Users/Customer/Desktop/arduino-1.0.6/hardware/tools/arm/lib/gcc/arm-none-eabi/4.8.4/include" -I"C:/Users/Customer/Desktop/arduino-1.0.6/hardware/tools/arm/lib/gcc/arm-none-eabi/4.8.4/include" -I"C:/Users/Customer/Desktop/arduino-1.0.6/hardware/tools/arm/arm/include" -I"C:/Users/Customer/Documents/Arduino/libraries" -I"D:/Program Files (x86)/Visual Micro/Visual Micro for Arduino/Micro Platforms/default/debuggers" -I"C:/Users/Customer/Desktop/arduino-1.0.6/hardware/teensy/libraries" -I"C:/Users/Customer/Desktop/arduino-1.0.6/libraries" -I"C:/Users/Customer/Desktop/arduino-1.0.6/libraries/SPI/utility" -I"C:/Users/Customer/Desktop/arduino-1.0.6/libraries/SPI" -I"C:/Users/Customer/Documents/Arduino/libraries/OneWire/utility" -I"C:/Users/Customer/Documents/Arduino/libraries/OneWire" -I"C:/Users/Customer/Documents/Arduino/libraries/Meguinolink/utility" -I"C:/Users/Customer/Documents/Arduino/libraries/Meguinolink" -I"C:/Users/Customer/Documents/Arduino/libraries/DallasTemp/utility" -I"C:/Users/Customer/Documents/Arduino/libraries/DallasTemp" -I"../../pyroLogger" -I"C:/Users/Customer/Desktop/arduino-1.0.6/hardware/teensy/cores/teensy3"  -O1 -ffunction-sections -fdata-sections -fpack-struct -fshort-enums -g2 -Wall -mmcu=atmega2560 -c -MD -MP -MF "$(@:%.o=%.d)" -MT"$(@:%.o=%.d)" -MT"$(@:%.o=%.o)"   -o "$@" "$<" 
	@echo Finished building: $<
	



# AVR32/GNU Preprocessing Assembler



# AVR32/GNU Assembler




ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

# Add inputs and outputs from these tool invocations to the build variables 

# All Target
all: $(OUTPUT_FILE_PATH) $(ADDITIONAL_DEPENDENCIES)

$(OUTPUT_FILE_PATH): $(OBJS) $(USER_OBJS) $(OUTPUT_FILE_DEP) $(LIB_DEP) $(LINKER_SCRIPT_DEP)
	@echo Building target: $@
	@echo Invoking: AVR8/GNU Linker : 4.8.1
	$(QUOTE)D:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.1061\avr8-gnu-toolchain\bin\avr-g++.exe$(QUOTE) -o$(OUTPUT_FILE_PATH_AS_ARGS) $(OBJS_AS_ARGS) $(USER_OBJS) $(LIBS) -Wl,-Map="pyroLogger.map" -Wl,--start-group  -Wl,--end-group -Wl,--gc-sections -mmcu=atmega2560  
	@echo Finished building target: $@
	"D:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.1061\avr8-gnu-toolchain\bin\avr-objcopy.exe" -O ihex -R .eeprom -R .fuse -R .lock -R .signature -R .user_signatures  "pyroLogger.elf" "pyroLogger.hex"
	"D:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.1061\avr8-gnu-toolchain\bin\avr-objcopy.exe" -j .eeprom  --set-section-flags=.eeprom=alloc,load --change-section-lma .eeprom=0  --no-change-warnings -O ihex "pyroLogger.elf" "pyroLogger.eep" || exit 0
	"D:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.1061\avr8-gnu-toolchain\bin\avr-objdump.exe" -h -S "pyroLogger.elf" > "pyroLogger.lss"
	"D:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.1061\avr8-gnu-toolchain\bin\avr-objcopy.exe" -O srec -R .eeprom -R .fuse -R .lock -R .signature -R .user_signatures "pyroLogger.elf" "pyroLogger.srec"
	"D:\Program Files (x86)\Atmel\Atmel Toolchain\AVR8 GCC\Native\3.4.1061\avr8-gnu-toolchain\bin\avr-size.exe" "pyroLogger.elf"
	
	





# Other Targets
clean:
	-$(RM) $(OBJS_AS_ARGS) $(EXECUTABLES)  
	-$(RM) $(C_DEPS_AS_ARGS)   
	rm -rf "pyroLogger.elf" "pyroLogger.a" "pyroLogger.hex" "pyroLogger.lss" "pyroLogger.eep" "pyroLogger.map" "pyroLogger.srec" "pyroLogger.usersignatures"
	