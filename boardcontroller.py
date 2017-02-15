#-------------------------------------------------------------------------------#

#	Name: boardcontroller.py						#

#	Purpose: Controls RPI for mechanical pinball				#

#	GPIO-Library:	RPi.GPIO 0.5.3a						#

#										#

#	Author:	Pridopia,	James	Clarke					#
#	Author:	Technicum, 	Wouter 	Lemoine
#	Author: ON4ABS, 	Mark 	Berwaers
#	Website: www.pridopia.co.uk						#

#										#

#	Created:	12/09/2013						#
#	Modified:	x/02/2017						#

#-------------------------------------------------------------------------------#



import time, sys,	signal,	os

import RPi.GPIO	as GPIO



GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)



SPI_SLAVE_ADDR	=	0x40

SPI_IOCTRL			=	0x0A



SPI_IODIRA			=	0x00

SPI_IODIRB			=	0x10



SPI_GPIOA				=	0x12

SPI_GPIOB				=	0x13



SPI_SLAVE_WRITE	=	0x00

SPI_SLAVE_READ	=	0x01



SCLK				=	11

MOSI				=	10

MISO				=	9

CS				=	8







I_IODIRA   = 0x00 
I_IODIRB   = 0x10 
I_IPOLA    = 0x01 
I_IPOLB    = 0x11 
I_GPINTENA = 0x02 
I_GPINTENB = 0x12 
I_DEFVALA  = 0x03 
I_DEFVALB  = 0x13 
I_INTCONA  = 0x04 
I_INTCONB  = 0x14 
I_IOCON    = 0x05 
I_IOCON    = 0x15 
I_GPPUA    = 0x06 
I_GPPUB    = 0x16 
I_INTFA    = 0x07 
I_INTFB    = 0x17 
I_INTCAPA  = 0x08 
I_INTCAPB  = 0x18 
I_GPIOA    = 0x09 
I_GPIOB    = 0x19 
I_OLATA    = 0x0A 
I_OLATB    = 0x1A 


O_IODIRA   = 0x00 
O_IODIRB   = 0x01 
O_IPOLA    = 0x02 
O_IPOLB    = 0x03 
O_GPINTENA = 0x04 
O_GPINTENB = 0x05 
O_DEFVALA  = 0x06 
O_DEFVALB  = 0x07 
O_INTCONA  = 0x08 
O_INTCONB  = 0x09 
O_IOCON    = 0x0A 
O_IOCON    = 0x0B 
O_GPPUA    = 0x0C 
O_GPPUB    = 0x0D 
O_INTFA    = 0x0E 
O_INTFB    = 0x0F 
O_INTCAPA  = 0x10 
O_INTCAPB  = 0x11 
O_GPIOA    = 0x12 
O_GPIOB    = 0x13 
O_OLATA    = 0x14 
O_OLATB    = 0x15  













def	sendValue(value):

		for	i	in range(8):

				if (value	&	0x80):

						GPIO.output(MOSI,	GPIO.HIGH)
#						 print("MOSI High")
				else:
 
						GPIO.output(MOSI,	GPIO.LOW)
#						 print("MOSI LOW")
				GPIO.output(SCLK,	GPIO.HIGH)
				GPIO.output(SCLK,	GPIO.LOW)
	
				value	<<=	1
			


def	sendSPI(opcode,	addr,	data):

		GPIO.output(CS,	GPIO.LOW)

		sendValue(opcode|SPI_SLAVE_WRITE)

		sendValue(addr)

		sendValue(data)

		GPIO.output(CS,	GPIO.HIGH)



def	readSPI(opcode,	addr):

		GPIO.output(CS,	GPIO.LOW)
		sendValue(opcode|SPI_SLAVE_READ)
		sendValue(addr)



		value	=	0

		for	i	in range(8):
				value	<<=	1
				if(GPIO.input(MISO)):

						value	|= 0x01

				GPIO.output(SCLK,	GPIO.HIGH)
				GPIO.output(SCLK,	GPIO.LOW)



		GPIO.output(CS,	GPIO.HIGH)
		return value

def	main():

		GPIO.setup(SCLK, GPIO.OUT) #Sets the Raspberry's GPIO correctly	to interface with the expansion board

		GPIO.setup(MOSI, GPIO.OUT)

		GPIO.setup(MISO, GPIO.IN)

		GPIO.setup(CS,	 GPIO.OUT)



#		 sendSPI(0x40, 0x0A, 0x00) #This means:	Bank A,	Row	1, LED's 0b00000000
#
#		 sendSPI(0x40, 0x1A, 0x00) #This means:	Bank A,	Row	2, LED's 0b00000000
#
#		 sendSPI(0x42, 0x0A, 0x00) #This means:	Bank B,	Row	1, LED's 0b00000000
#
#		 sendSPI(0x42, 0x1A, 0x00) # and So	forth
#
#		 sendSPI(0x44, 0x0A, 0x00) # Basically sets all the pins low
#
#		 sendSPI(0x44, 0x1A, 0x00)
#
#		 sendSPI(0x46, 0x0A, 0x00)
#
#		 sendSPI(0x46, 0x1A, 0x00)
#
#
		sendSPI(0x40, O_IOCON, 0x8) # IOCON: I/O EXPANDER CONFIGURATION REGISTER	
		sendSPI(0x42, O_IOCON, 0x8) # See datasheet page 21
		sendSPI(0x44, O_IOCON, 0x8) # Use hardware address(0x8) 
		sendSPI(0x46, O_IOCON, 0x8) # sets bank to 1 so A is 0x0? and B is 0x1?
#
#
#
#
		sendSPI(0x40, O_IODIRA, 0xFF) # Toggles input/output state of pin, 0 = output, 1 = input			
#		sendSPI(0x42, 0x00, 0x00)
#		sendSPI(0x44, 0x00, 0x00)
#		sendSPI(0x46, 0x00, 0x00)
#		sendSPI(0x40, 0x10, 0x00)
#       	sendSPI(0x42, 0x10, 0x00)
#       	sendSPI(0x44, 0x10, 0x00)
#	       	sendSPI(0x46, 0x10, 0x00)


#	For example 	sendSPI(0x40, 0x00, 0xFF) sets all pins of row 1 	of the first bank 	of the first 	IC as input
#			sendSPI(0x42, 0x10, 0x81) sets the first and last pin 	of the second bank 	of the second 	IC as input
		#sendSPI(0x40, 0x01, 0x00) # Sets input polarity of pin, 0 = normal, 1 = inverse 
#		Don't really need to touch this I suppose???
#
#
#
#		sendSPI(0x40, 0x12, 0xFF) # Not sure what this is since it's B  	INTERRUPT-ON-CHANGE PINS
#		sendSPI(0x40, 0x13, 0xFF) # Same here, 					DEFAULT VALUE REGISTER 


		GPIO.output(CS,	GPIO.HIGH)

		GPIO.output(SCLK, GPIO.LOW)
		print(readSPI(0x40, O_IODIRA))
		Menu("")
		debug(0x40)
		debug(0x42)
		debug(0x44)
		debug(0x46)
		
def	Menu(Error):
	
	
	#while True:
 	for i in range(0,256):
 		print(i)
		sendSPI(0x40,	O_OLATB,	i)
		#sendSPI(0x42,	O_OLATB,	i)
		sendSPI(0x42,	O_OLATA,	i)
		sendSPI(0x44,	O_OLATB,	i)
		#sendSPI(0x46,	O_OLATB,	255-i)
		time.sleep(0.01)	
		#sendSPI(0x42,	O_OLATB,	0x81)	
		#print(readSPI(0x46, 0x1A))
	
	Input = raw_input("Enter to stop")

	print("0x09=0x{0:02X}".format(readSPI(0x40,	I_GPIOA)))	#0x09 leest uit van 1ste rij
	print("0x19=0x{0:02X}".format(readSPI(0x40,	I_GPIOB)))	#0x19 leest uit van 2de rij
#		print(readSPI(0x42,	0x09))		 
#		print(readSPI(0x42,	0x19))
# 		print(readSPI(0x44,	0x09))
#              	print(readSPI(0x44,	0x19))
#              	print(readSPI(0x46,	0x09))
#              	print(readSPI(0x46,	0x19))
#





def 	debug(code):

		print(code,	"O_IODIRA  ",	 	readSPI(code,	O_IODIRA  ))
		print(code,	"O_IODIRB  ",		readSPI(code,	O_IODIRB  ))
		print(code,	"O_IPOLA   ",		readSPI(code,	O_IPOLA   ))
		print(code,	"O_IPOLB   ",		readSPI(code,	O_IPOLB   ))
		print(code,	"O_GPINTENA",		readSPI(code,	O_GPINTENA))
 		print(code,	"O_GPINTENB",		readSPI(code,	O_GPINTENB))
 		print(code,	"O_DEFVALA ",		readSPI(code,	O_DEFVALA ))
 		print(code,	"O_DEFVALB ",		readSPI(code,	O_DEFVALB ))
		print(code,	"O_INTCONA ",		readSPI(code,	O_INTCONA ))
		print(code,	"O_INTCONB ",		readSPI(code,	O_INTCONB ))
		print(code,	"O_IOCON   ",		readSPI(code,	O_IOCON   ))
		print(code,	"O_IOCON   ",		readSPI(code,	O_IOCON   ))
		print(code,	"O_GPPUA   ",		readSPI(code,	O_GPPUA   ))
 		print(code,	"O_GPPUB   ",		readSPI(code,	O_GPPUB   ))
 		print(code,	"O_INTFA   ",		readSPI(code,	O_INTFA   ))
 		print(code,	"O_INTFB   ",		readSPI(code,	O_INTFB   ))
		print(code,	"O_INTCAPA ",		readSPI(code,	O_INTCAPA ))
		print(code,	"O_INTCAPB ",		readSPI(code,	O_INTCAPB ))
		print(code,	"O_GPIOA   ",		readSPI(code,	O_GPIOA   ))
		print(code,	"O_GPIOB   ",		readSPI(code,	O_GPIOB   ))
		print(code,	"O_OLATA   ",		readSPI(code,	O_OLATA   ))
		print(code,	"O_OLATB   ",		readSPI(code, O_OLATB   ))


if __name__ == '__main__':

		main()
		
		
		#sendSPI(0x40, 0x0A, 0x00) # IOCON: I/O EXPANDER CONFIGURATION REGISTER	
		#sendSPI(0x42, 0x0A, 0x00) # See datasheet page 21
		#sendSPI(0x44, 0x0A, 0x00) # Disabled automatic address pointer 
		#sendSPI(0x46, 0x0A, 0x00) # sets bank to 1 so A is 0x0? and B is 0x1?
		#
		sendSPI(0x40, O_OLATB, 0x00) # IOCON: I/O EXPANDER CONFIGURATION REGISTER	
		sendSPI(0x42, O_OLATB, 0x00) # See datasheet page 21
		sendSPI(0x44, O_OLATB, 0x00) # Disabled automatic address pointer 
		sendSPI(0x46, O_OLATB, 0x00) # sets bank to 1 so A is 0x0? and B is 0x1?
		
		sendSPI(0x40, O_OLATA, 0x00) # IOCON: I/O EXPANDER CONFIGURATION REGISTER	
		sendSPI(0x42, O_OLATA, 0x00) # See datasheet page 21
		sendSPI(0x44, O_OLATA, 0x00) # Disabled automatic address pointer 
		sendSPI(0x46, O_OLATA, 0x00) # sets bank to 1 so A is 0x0? and B is 0x1?

		#sendSPI(0x40, I_IOCON, 0x00) # IOCON: I/O EXPANDER CONFIGURATION REGISTER	
		#sendSPI(0x42, I_IOCON, 0x00) # See datasheet page 21
		#sendSPI(0x44, I_IOCON, 0x00) # Disabled automatic address pointer 
		#sendSPI(0x46, I_IOCON, 0x00) # sets bank to 1 so A is 0x0? and B is 0x1?
		


