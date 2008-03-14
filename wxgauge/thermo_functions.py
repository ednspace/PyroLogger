import serial
global ser 
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
print ser
#Function Definitions
def get_faren(address):
	ser.flushInput()
	ser.write("\r")
	ser.write("F")
	ser.write(address)
	ser.write("\r")
	#line = ser.read(5)
	line = ser.readline()
	ser.flushInput()
	return line

def get_celsius(address):
	ser.flushInput()
	ser.write("\r")
	ser.write("C")
	ser.write(address)
	ser.write("\r")
	#line = ser.read(5)
	line = ser.readline()
	ser.flushInput()
	return float(line)

def get_uv(address):
	ser.flushInput()
	ser.write("\r")
	ser.write("K")
	ser.write(address)
	ser.write("\r")
	#line = ser.read(9)
	line = ser.readline()
	ser.flushInput()
	return float(line)

def reverse_poly(x):
    #Takes in Temp in deg C and gives back Uv's, used to adjust for ambiant temperature
    coeffecients = [-1.76E1, 3.8921E1, 1.8559E-2, -9.9458E-5, 3.18409E-7, -5.607284E-10, 5.607506E-13, -3.20207E-16, 9.71511E-20, -1.21047E-23]

    a0 = 1.18597600000E2
    a1 = -0.118343200000E-3
    a2 = 0.126968600000E3

    e = 2.71828182

    result2 = 0.0
    added = 0.0
    power = 0

    exponent_value = x - a2
    exponent_value = exponent_value * exponent_value
    exponent_value = a1 * exponent_value
    added = pow(e,exponent_value)
    added = added * a0

    for c in coeffecients:
        result2 = (result2 + c * pow(x,power))
        power = power + 1
    result2 = result2 + added
    result2 = result2 / 1000000
    return (result2)

def convert_uv(uv):
    coefficients = [0.226584602, 24152.10900, 67233.4248, 2210340.682, -860963914.9, 4.83506e10, -1.18452e12, 1.38690e13, -6.33708e13]
    result1 = 0.0
    power = 0
    for c in coefficients:
        result1 = result1 + c * pow(uv,power)
        power = power + 1
    result1 = round(result1,2)
    return result1

