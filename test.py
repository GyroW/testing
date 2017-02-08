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



def ChangeLed(Input):

	Bank = Input[0]

	Port = Input[1]

	Led  = Input[2]

	Bank = Bank.upper()

	if Bank == "A":

		Addr = 0x40

	elif Bank == "B":

		Addr = 0x42

	elif Bank == "C":

		Addr = 0x44

	elif Bank == "D":

		Addr = 0x46

	else:

		Quit()



	if Led == "1":

		Out = "00000001"

	elif Led == "2":

		Out = "00000010"

	elif Led == "3":

		Out = "00000100"

	elif Led == "4":

		Out = "00001000"

	elif Led == "5":

		Out = "00010000"

	elif Led == "6":

		Out = "00100000"

	elif Led == "7":

		Out = "01000000"

	elif Led == "8":

		Out = "10000000"

	else:

		Menu("Incorrect LED selected")



	if Port == "1":

		Bin = bin(int('{:08}'.format(readSPI(Addr, 0x0A))) ^ int(Out, 2))

		sendSPI( Addr, 0x0A, int(Bin, 2) )

		Menu("")

	if Port == "2":

		Bin = bin(int('{:08}'.format(readSPI(Addr, 0x1A))) ^ int(Out, 2))

		sendSPI( Addr, 0x1A, int(Bin, 2) )

		Menu("")







def sendValue(value):

    for i in range(8):

        if (value & 0x80):

            GPIO.output(MOSI, GPIO.HIGH)

        else:

            GPIO.output(MOSI, GPIO.LOW)

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



def handler(signum, frame):

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



	print("Ended Via Ctrl+Z.")

	sys.exit()



def Quit():

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



	print("Ended Via RESet.")

	sys.exit()





signal.signal(signal.SIGTSTP, handler)



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



    sendSPI(0x40, 0x0A, 0xFF)

    sendSPI(0x40, 0x1A, 0xFF)



    sendSPI(0x40, 0x0A, 0x00)

    sendSPI(0x40, 0x1A, 0x00)



    GPIO.output(CS,   GPIO.HIGH)

    GPIO.output(SCLK, GPIO.LOW)



    Menu("")



def Menu(Error):



	try:

	    while True:
		
		print("Output Test for 23s17-4port MCP23S17")
		
		B1 = '{:08b}'.format(readSPI(0x40, 0x0A))

		B2 = '{:08b}'.format(readSPI(0x40, 0x1A))

		B3 = '{:08b}'.format(readSPI(0x42, 0x0A))

		B4 = '{:08b}'.format(readSPI(0x42, 0x1A))

		B5 = '{:08b}'.format(readSPI(0x44, 0x0A))

		B6 = '{:08b}'.format(readSPI(0x44, 0x1A))

		B7 = '{:08b}'.format(readSPI(0x46, 0x0A))

		B8 = '{:08b}'.format(readSPI(0x46, 0x1A))

		print("    8   7   6   5   4   3   2   1")

		print("A1 [%s] [%s] [%s] [%s] [%s] [%s] [%s] [%s]" % (B1[0], B1[1], B1[2], B1[3], B1[4], B1[5], B1[6], B1[7]) )

		print("A2 [%s] [%s] [%s] [%s] [%s] [%s] [%s] [%s]" % (B2[0], B2[1], B2[2], B2[3], B2[4], B2[5], B2[6], B2[7]) )

		print("B1 [%s] [%s] [%s] [%s] [%s] [%s] [%s] [%s]" % (B3[0], B3[1], B3[2], B3[3], B3[4], B3[5], B3[6], B3[7]) )

		print("B2 [%s] [%s] [%s] [%s] [%s] [%s] [%s] [%s]" % (B4[0], B4[1], B4[2], B4[3], B4[4], B4[5], B4[6], B4[7]) )

		print("C1 [%s] [%s] [%s] [%s] [%s] [%s] [%s] [%s]" % (B5[0], B5[1], B5[2], B5[3], B5[4], B5[5], B5[6], B5[7]) )

		print("C2 [%s] [%s] [%s] [%s] [%s] [%s] [%s] [%s]" % (B6[0], B6[1], B6[2], B6[3], B6[4], B6[5], B6[6], B6[7]) )

		print("D1 [%s] [%s] [%s] [%s] [%s] [%s] [%s] [%s]" % (B7[0], B7[1], B7[2], B7[3], B7[4], B7[5], B7[6], B7[7]) )

		print("D2 [%s] [%s] [%s] [%s] [%s] [%s] [%s] [%s]" % (B8[0], B8[1], B8[2], B8[3], B8[4], B8[5], B8[6], B8[7]) )

		print(Error)

		print("Enter the Bank ( A-B ), Port ( 1-2 ) and LED number ( 1-8 ).")

		print("Type RES to Reset.")

            	print("Example \"A21\" or \"a21\" will Toggle Bank A, Port 2, LED 1.")

		Input = raw_input(">")

		Input = Input.upper()

		if Input == "RES":

			Quit()

		if Input[0] != "A" and Input[0] != "B" and Input[0] != "C" and Input[0] != "D":

			Menu("Incorrect Bank entered: "+Input[0])

		if len(Input) < 3:

			Menu("Incorrect Input.")

		elif len(Input) > 3:

			Menu("Too many letters / numbers.")

		else:

			ChangeLed(Input)

	except KeyboardInterrupt:

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



		print("Ended Via KeyboardInterrupt ( Ctrl+C )")

		sys.exit()





if __name__ == '__main__':

    main()


