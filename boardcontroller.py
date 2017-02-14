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
		sendSPI(0x40, 0x05, 0xA0) # IOCON: I/O EXPANDER CONFIGURATION REGISTER	
		sendSPI(0x42, 0x05, 0xA0) # See datasheet page 21
		sendSPI(0x44, 0x05, 0xA0) # Disabled automatic address pointer 
		sendSPI(0x46, 0x05, 0xA0) # sets bank to 1 so A is 0x0? and B is 0x1?
#
#
#
#
		sendSPI(0x40, 0x00, 0xFF) # Toggles input/output state of pin, 0 = output, 1 = input 		
		sendSPI(0x42, 0x00, 0xFF)
		sendSPI(0x44, 0x00, 0xFF)
		sendSPI(0x46, 0x00, 0xFF)
# For example sendSPI(0x40, 0x00, 0xFF) sets all pins of row 1 on the first bank of the first IC as input sendSPI(0x42, 0x10, 0x81) sets the first and last pin of the second bank of the second IC as input
#		sendSPI(0x40, 0x01, 0xFF) # Sets input polarity of pin, 0 = normal, 1 = inverse # Don't really need to touch this I suppose
#
#
#
		sendSPI(0x40, 0x12, 0xFF) # Not sure what this is since it's B  	INTERRUPT-ON-CHANGE PINS
		sendSPI(0x40, 0x13, 0xFF) # Same here, 					DEFAULT VALUE REGISTER 


		GPIO.output(CS,	GPIO.HIGH)

		GPIO.output(SCLK, GPIO.LOW)

		Menu("")

def	Menu(Error):
	
	#while True:
 
		#sendSPI(0x40,	0x0A,	0x00)	#print(readSPI(0x40, 0x0A))
	
		Input = raw_input("Enter to stop")

		print(readSPI(0x40,	0x09))	#0x09 leest uit van 1ste rij
		print(readSPI(0x40,	0x19))	#0x19 leest uit van 2de rij
		print(readSPI(0x42,	0x09))		 
		print(readSPI(0x42,	0x19))
 		print(readSPI(0x44,	0x09))
               	print(readSPI(0x44,	0x19))
               	print(readSPI(0x46,	0x09))
               	print(readSPI(0x46,	0x19))


if __name__ == '__main__':

		main()


