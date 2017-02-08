#-------------------------------------------------------------------------------#

# Name:         23s17-4port-s-v103.py						#

# Purpose:      4 Port, 2 Bank Controller, V1.03, Simple GUI			#

# GPIO-Library: RPi.GPIO 0.5.3a							#

#										#

# Author:       Pridopia, James Clarke						#
# Author:	Technicum, Wouter Lemoine
# Website:      www.pridopia.co.uk						#

#										#

# Created:      12/09/2013							#

#-------------------------------------------------------------------------------#



import time, sys, signal, os

import RPi.GPIO as GPIO



GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)



SPI_SLAVE_ADDR  = 0x40

SPI_IOCTRL      = 0x0A



SPI_IODIRA      = 0x00

SPI_IODIRB      = 0x10



SPI_GPIOA       = 0x12

SPI_GPIOB       = 0x13



SPI_SLAVE_WRITE = 0x00

SPI_SLAVE_READ  = 0x01



SCLK        = 11

MOSI        = 10

MISO        = 9

CS          = 8




def sendValue(value):

    for i in range(8):

        if (value & 0x80):

            GPIO.output(MOSI, GPIO.HIGH)
            print("MOSI High")
        else:
 
            GPIO.output(MOSI, GPIO.LOW)
            print("MOSI LOW")
        GPIO.output(SCLK, GPIO.HIGH)
        GPIO.output(SCLK, GPIO.LOW)
  
        value <<= 1
      


def sendSPI(opcode, addr, data):

    GPIO.output(CS, GPIO.LOW)

    sendValue(opcode|SPI_SLAVE_WRITE)

    sendValue(addr)

    sendValue(data)

    GPIO.output(CS, GPIO.HIGH)



def readSPI(opcode, addr):

    GPIO.output(CS, GPIO.LOW)
    sendValue(opcode|SPI_SLAVE_READ)
    sendValue(addr)



    value = 0

    for i in range(8):
        value <<= 1
        if(GPIO.input(MISO)):

            value |= 0x01

        GPIO.output(SCLK, GPIO.HIGH)
        GPIO.output(SCLK, GPIO.LOW)



    GPIO.output(CS, GPIO.HIGH)
    return value

def main():



    GPIO.setup(SCLK, GPIO.OUT) #Sets the Raspberry's GPIO correctly to interface with the expansion board

    GPIO.setup(MOSI, GPIO.OUT)

    GPIO.setup(MISO, GPIO.IN)

    GPIO.setup(CS,   GPIO.OUT)



    sendSPI(0x40, 0x0A, 0x00) #This means: Bank A, Row 1, LED's 0b00000000

    sendSPI(0x40, 0x1A, 0x00) #This means: Bank A, Row 2, LED's 0b00000000

    sendSPI(0x42, 0x0A, 0x00) #This means: Bank B, Row 1, LED's 0b00000000

    sendSPI(0x42, 0x1A, 0x00) # and So forth

    sendSPI(0x44, 0x0A, 0x00)

    sendSPI(0x44, 0x1A, 0x00)

    sendSPI(0x46, 0x0A, 0x00)

    sendSPI(0x46, 0x1A, 0x00)


    sendSPI(0x40, 0x05, 0x00) #What does this do? What is this 0x05?

    sendSPI(0x42, 0x05, 0x00) # and this?

    sendSPI(0x44, 0x05, 0x00) # and this?

    sendSPI(0x46, 0x05, 0x00) # and this?



    sendSPI(0x40, 0x00, 0x00) # and this? And 0x00?

    sendSPI(0x40, 0x01, 0x00) # and this? 0x01?



    sendSPI(0x40, 0x12, 0x00) # and this? 0x12? 

    sendSPI(0x40, 0x13, 0x00) # and also this? 0x13? #And why does it only do the previous 4 on bank A (0x40)


    GPIO.output(CS,   GPIO.HIGH)

    GPIO.output(SCLK, GPIO.LOW)

    Menu("")

def Menu(Error):

	while True:
		variable1 = readSPI(0x40, 0x0A)
		print("dit is variable1", variable1)		
       
	#	print(readSPI(0x40, 0x0A))
	#	print(readSPI(0x40, 0x1A))	
	#	print(readSPI(0x42, 0x0A))
	#	print(readSPI(0x42, 0x1A))	
	#	print(readSPI(0x44, 0x0A))
	#	print(readSPI(0x44, 0x1A))
	#	print(readSPI(0x46, 0x0A))	
	#	print(readSPI(0x46, 0x1A))

if __name__ == '__main__':

    main()


