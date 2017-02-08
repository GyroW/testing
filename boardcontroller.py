#-------------------------------------------------------------------------------#

# Name:         23s17-4port-s-v103.py						#

# Purpose:      4 Port, 2 Bank Controller, V1.03, Simple GUI			#

# GPIO-Library: RPi.GPIO 0.5.3a							#

#										#

# Author:       Pridopia, James Clarke						#

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
           # print("value in die if loop", value)
           # print("Mosi pin nu hoog")
        else:

            GPIO.output(MOSI, GPIO.LOW)
           # print("Mosi pun nu laag")

        GPIO.output(SCLK, GPIO.HIGH)
        #print("SCLK nu hoog")
        GPIO.output(SCLK, GPIO.LOW)
        #print("SCLK nu laag")
        #print(value, "voor die rare operator")
        value <<= 1
        #print(value, "achter die rare operator")


def sendSPI(opcode, addr, data):

    GPIO.output(CS, GPIO.LOW)

    sendValue(opcode|SPI_SLAVE_WRITE)

    sendValue(addr)

    sendValue(data)

    GPIO.output(CS, GPIO.HIGH)



def readSPI(opcode, addr):

    GPIO.output(CS, GPIO.LOW)
    print("CS is nu laag")	
    sendValue(opcode|SPI_SLAVE_READ)
    print(opcode,"sent")	
    sendValue(addr)
    print(addr, "sent")


    value = 0

    for i in range(8):

        value <<= 1
        print(value)
        if(GPIO.input(MISO)):

            value |= 0x01

        GPIO.output(SCLK, GPIO.HIGH)
        print("SCLK nu hoog")
        GPIO.output(SCLK, GPIO.LOW)
        print("SCLK nu laag")


    GPIO.output(CS, GPIO.HIGH)
    print("CS is nu hoog")
    return value






def main():



    GPIO.setup(SCLK, GPIO.OUT)

    GPIO.setup(MOSI, GPIO.OUT)

    GPIO.setup(MISO, GPIO.IN)

    GPIO.setup(CS,   GPIO.OUT)



    sendSPI(0x40, 0x0A, 0x00)

    sendSPI(0x40, 0x1A, 0x00)

    sendSPI(0x42, 0x0A, 0x00)

    sendSPI(0x42, 0x1A, 0x00)

    sendSPI(0x44, 0x0A, 0x00)

    sendSPI(0x44, 0x1A, 0x00)

    sendSPI(0x46, 0x0A, 0x00)

    sendSPI(0x46, 0x1A, 0x00)


    sendSPI(0x40, 0x05, 0x00)

    sendSPI(0x42, 0x05, 0x00)

    sendSPI(0x44, 0x05, 0x00)

    sendSPI(0x46, 0x05, 0x00)



    sendSPI(0x40, 0x00, 0x00)

    sendSPI(0x40, 0x01, 0x00)



    sendSPI(0x40, 0x12, 0x00)

    sendSPI(0x40, 0x13, 0x00)



#    sendSPI(0x40, 0x0A, 0xFF)

#    sendSPI(0x40, 0x1A, 0xFF)



#    sendSPI(0x40, 0x0A, 0x00)

#    sendSPI(0x40, 0x1A, 0x00)



    GPIO.output(CS,   GPIO.HIGH)

    GPIO.output(SCLK, GPIO.LOW)



    Menu("")



def Menu(Error):

	while True:
		variable1 = readSPI(0x40, 0x0A)
		print("dit is variable1", variable1)		
       			


	#	sendSPI(0x40, 0x0A, 0xFF)
	#	print(variable1)
	#	print(readSPI(0x40, 0x0A))
	#	print(readSPI(0x40, 0x1A))	
		
	#	print(readSPI(0x42, 0x0A))
	#	print(readSPI(0x42, 0x1A))	
		
	#	print(readSPI(0x44, 0x0A))
	#	print(readSPI(0x44, 0x1A))
		
	#	print(readSPI(0x46, 0x0A))	
	#	print(readSPI(0x46, 0x1A))

	#	if readSPI(0x40, 0x0A) == 255:
	#	
	#		sendSPI(0x40, 0x0A, 0xFF)
	#		sendSPI(0x40, 0x1A, 0xFF)
	#		sendSPI(0x42, 0x0A, 0xFF)
	#		sendSPI(0x42, 0x1A, 0xFF)
	#		sendSPI(0x44, 0x0A, 0xFF)
	#		sendSPI(0x44, 0x1A, 0xFF)
	#		sendSPI(0x46, 0x0A, 0xFF)
	#		sendSPI(0x46, 0x1A, 0xFF)

	#	if readSPI(0x40, 0x0A) == 0:
	#	
	#		sendSPI(0x40, 0x0A, 0x00)
	#		sendSPI(0x40, 0x1A, 0x00)
	#		sendSPI(0x42, 0x0A, 0x00)
	#		sendSPI(0x42, 0x1A, 0x00)
	#		sendSPI(0x44, 0x0A, 0x00)
	#		sendSPI(0x44, 0x1A, 0x00)
	#		sendSPI(0x46, 0x0A, 0x00)
	#		sendSPI(0x46, 0x1A, 0x00)

if __name__ == '__main__':

    main()


