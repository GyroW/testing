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
I_IOCON_2  = 0x15 
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
O_IOCON_2  = 0x0B 
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

				else:
 
						GPIO.output(MOSI,	GPIO.LOW)

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
		
		
def reset_regs():
		for device_address in [0x40,0x42,0x44,0x46]:
			# I_IOCON_2 = 0x15 !!
			
			# if in Bank 1 then back to bank 0 else write to O_OLATB(no effect)
		    	sendSPI(device_address,I_IOCON_2,0x28) 
      
      
       			# now always in bank 0 ( set SEQOP and HAEN ) 
		    	sendSPI(device_address,O_IOCON,0x28) 
      
            	
			sendSPI(device_address,O_IODIRA,0x00) # all pins input
			sendSPI(device_address,O_IODIRB,0x00) # all pins input
			
			#clear all other registers except O_IOCON and O_IOCON_2
			for regaddress in [O_IPOLA, O_IPOLB, O_GPINTENA, O_GPINTENB, O_DEFVALA, O_DEFVALB, O_INTCONA, O_INTCONB, O_GPPUA, O_GPPUB, O_INTFA, O_INTFB, O_INTCAPA, O_INTCAPB, O_GPIOA, O_GPIOB, O_OLATA, O_OLATB]:
				sendSPI(device_address,regaddress,0)				
		

				

def	main():

		GPIO.setup(SCLK, GPIO.OUT) #Sets the Raspberry's GPIO correctly	to interface with the expansion board

		GPIO.setup(MOSI, GPIO.OUT)

		GPIO.setup(MISO, GPIO.IN)

		GPIO.setup(CS,	 GPIO.OUT)

		GPIO.output(CS,	GPIO.HIGH)

		GPIO.output(SCLK, GPIO.LOW)
		reset_regs()
                #declaring some variables
                yardsdirection = 0  #0 = right 1 = left
                yards = 0           #starting yardsunits
                yardsten = 0        #starting yardsten 
                points = 0          #testing punten
                targetshit = 0      #Aantal Targets Hit


#		print(readSPI(0x40, O_IODIRA))

                sendSPI(0x46, O_IODIRA, 0xFF)
                sendSPI(0x46, O_IODIRB, 0xF0)
		Menu("")
#		debug(0x40)
#		debug(0x42)
#		debug(0x44)
#		debug(0x46)
		
def	Menu(Error):
            switchbank1 = toBinary(readSPI(0x46, O_GPIOA)
            switchbank2 = toBinary(readSPI(0x46, O_GPIOB)
            global targetshit
            global yardsten
            #   [toprollover 1, toprollover 2,  toprollover 3,  tolrollover4,   ster,   popbumper,  targets,    spinner ] 
            #en [outlane,       achterbank,     bank,           outhole,        /,      /,          /,          /       ]
            print(switchbank1)
            print(switchbank2)
           
            if switchbank1[0] == 1:#toprollover 1
                if toBinary(readSPI(0x42, OGPIOB)[7]: 
                    yard(30)
                punten(500) 
            if switchbank1[1] == 1:#toprollover 2
                punten(500)
            if switchbank1[2] == 1:#toprollover 3
                punten(500)
            if switchbank1[3] == 1:#toprollover 4
                punten(500)
            if switchbank1[4] == 1:#ster
               punten(100)
               changeyardsdirection()

            if switchbank1[5] == 1:#popbumper
                
            if switchbank1[6] == 1:#targets
                targetshit = targetshit + 1
            if switchbank1[7] == 1:#spinner
                punten(10)    
            if switchbank2[0] == 1:#outlane
                punten(1000)
                yard(10)
            if switchbank2[1] == 1:#achterbank
                punten(500)
                yard(5)
            if switchbank2[2] == 1:#bank
                
            if switchbank2[3] == 1:#outhole
                
            if targetshit == 7:
                if toBinary(readSPI(0x42, O_GPIOB)[2] == 1:
                    goal()
                elif toBinary(readSPI(0x42, O_GPIOB[3] == 1:
                    special()
                targetshit = 0
                
            if yardsten == 11:
                goal()
                yardsten = 0



def     changeyardsdirection():                                 #changes what direction the yards should go to, when triggered
            global yardsdirection                               #toggles direction
            if yardsdirection == 0:
                yardsdirection = 1
            elif yardsdirection == 1:
                yarddirection = 0
            print(yarddirection)                                #debug 
            toggle(0x42, O_GPIOA, 2)
            toggle(0x42, O_GPIOA, 3)

def     yard(amount):
            global yardsdirection                               #    
            global yards                                        #
            global yardsten                                     #
            yardstate = toBinary(readSPI(0x40, O_GPIOB)         #2de rij in excel bestand
            if yardsdirection == 0:                             #
                    yards = yards + amount                      #
            elif yardsdirection == 1:                           #
                    yards = yards - amount                      #
            while yards > 10:                                   #Als yards meer is dan 10 dan moeten we yardsten optellen 
                    yardsten = yardsten + 1                     #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    yards = yards - 10                          #als pijltje omgekeerd staat!!!
            if yards < 1:
                    yards = 1
            if yards == 1:
                    sendSPI(0x40, O_GPIOA, 0x80)                #1ste rij in excel bestand
                    yardstate[0] = 0
                    yardstate[1] = 0
            if yards == 2:
                    sendSPI(0x40, O_GPIOA, 0x40)
                    yardstate[0] = 0
                    yardstate[1] = 0
            if yards == 3:
                    sendSPI(0x40, O_GPIOA, 0x20)
                    yardstate[0] = 0
                    yardstate[1] = 0
            if yards == 4:
                    sendSPI(0x40, O_GPIOA, 0x10)
                    yardstate[0] = 0
                    yardstate[1] = 0
            if yards == 5:
                    sendSPI(0x40, O_GPIOA, 0x08)
                    yardstate[0] = 0
                    yardstate[1] = 0
            if yards == 6:
                    sendSPI(0x40, O_GPIOA, 0x04)
                    yardstate[0] = 0
                    yardstate[1] = 0
            if yards == 7:
                    sendSPI(0x40, O_GPIOA, 0x02)
                    yardstate[0] = 0
                    yardstate[1] = 0
            if yards == 8:
                    sendSPI(0x40, O_GPIOA, 0x01)
                    yardstate[0] = 0
                    yardstate[1] = 0
            if yards == 9:
                    sendSPI(0x40, O_GPIOA, 0x00)
                    yardstate[0] = 1
                    yardstate[1] = 0
            if yards == 10:
                    sendSPI(0x40, O_GPIOA, 0x00)
                    yardstate[0] = 0
                    yardstate[1] = 1
            
            yardstateB = toBinary(readSPI(0x42, O_GPIOA))       #leest 3de rij in excel bestand
            
            if yardsten == 1:                                   #Yards Heel links
                    yardstate[2] =  1
                    yardstate[3] =  0
                    yardstate[4] =  0
                    yardstate[5] =  0
                    yardstate[6] =  0
                    yardstate[7] =  0
                    yardstateB[0] = 0
                    yardstateB[1] = 0
                    yardstateB[2] = 0
                    yardstateB[3] = 0
                    yardstateB[4] = 0
            if yardsten == 2:
                    yardstate[2] =  0
                    yardstate[3] =  1
                    yardstate[4] =  0
                    yardstate[5] =  0
                    yardstate[6] =  0
                    yardstate[7] =  0
                    yardstateB[0] = 0
                    yardstateB[1] = 0
                    yardstateB[2] = 0
                    yardstateB[3] = 0
                    yardstateB[4] = 0
            if yardsten == 3:
                    yardstate[2] =  0
                    yardstate[3] =  0
                    yardstate[4] =  1
                    yardstate[5] =  0
                    yardstate[6] =  0
                    yardstate[7] =  0
                    yardstateB[0] = 0
                    yardstateB[1] = 0
                    yardstateB[2] = 0
                    yardstateB[3] = 0
                    yardstateB[4] = 0
            if yardsten == 4:
                    yardstate[2] =  0
                    yardstate[3] =  0
                    yardstate[4] =  0
                    yardstate[5] =  1
                    yardstate[6] =  0
                    yardstate[7] =  0
                    yardstateB[0] = 0
                    yardstateB[1] = 0
                    yardstateB[2] = 0
                    yardstateB[3] = 0
                    yardstateB[4] = 0
            if yardsten == 5:
                    yardstate[2] =  0
                    yardstate[3] =  0
                    yardstate[4] =  0
                    yardstate[5] =  0
                    yardstate[6] =  1
                    yardstate[7] =  0
                    yardstateB[0] = 0
                    yardstateB[1] = 0
                    yardstateB[2] = 0
                    yardstateB[3] = 0
                    yardstateB[4] = 0
            if yardsten == 6:                                   #Yards int midden   
                    yardstate[2] =  0
                    yardstate[3] =  0
                    yardstate[4] =  0
                    yardstate[5] =  0
                    yardstate[6] =  0
                    yardstate[7] =  1
                    yardstateB[0] = 0
                    yardstateB[1] = 0
                    yardstateB[2] = 0
                    yardstateB[3] = 0
                    yardstateB[4] = 0
            if yardsten == 7:
                    yardstate[2] =  0
                    yardstate[3] =  0
                    yardstate[4] =  0
                    yardstate[5] =  0
                    yardstate[6] =  0
                    yardstate[7] =  0
                    yardstateB[0] = 1
                    yardstateB[1] = 0
                    yardstateB[2] = 0
                    yardstateB[3] = 0
                    yardstateB[4] = 0
            if yardsten == 8:
                    yardstate[2] =  0
                    yardstate[3] =  0
                    yardstate[4] =  0
                    yardstate[5] =  0
                    yardstate[6] =  0
                    yardstate[7] =  0
                    yardstateB[0] = 0
                    yardstateB[1] = 1
                    yardstateB[2] = 0
                    yardstateB[3] = 0
                    yardstateB[4] = 0
            if yardsten == 9:
                    yardstate[2] =  0
                    yardstate[3] =  0
                    yardstate[4] =  0
                    yardstate[5] =  0
                    yardstate[6] =  0
                    yardstate[7] =  0
                    yardstateB[0] = 0
                    yardstateB[1] = 0
                    yardstateB[2] = 1
                    yardstateB[3] = 0
                    yardstateB[4] = 0
            if yardsten == 10:
                    yardstate[2] =  0
                    yardstate[3] =  0
                    yardstate[4] =  0
                    yardstate[5] =  0
                    yardstate[6] =  0
                    yardstate[7] =  0
                    yardstateB[0] = 0
                    yardstateB[1] = 0
                    yardstateB[2] = 0
                    yardstateB[3] = 1
                    yardstateB[4] = 0
            if yardsten == 11:                                  #Yards heel rechts 
                    yardstate[2] =  0
                    yardstate[3] =  0
                    yardstate[4] =  0
                    yardstate[5] =  0
                    yardstate[6] =  0
                    yardstate[7] =  0
                    yardstateB[0] = 0
                    yardstateB[1] = 0
                    yardstateB[2] = 0
                    yardstateB[3] = 0
                    yardstateB[4] = 1



            sendSPI(0x40, O_GPIOB, binToHex(yardstate))         #sets lites according to what yards we're on
            sendSPI(0x42, O_GPIOA, binToHex(yardstateB))
            print(yardstate)                                    #debug
            print(yardstateB)
               



                    


def     special():                                              #defines what special does
            
def     extra_ball():                                           #triggers extra ball lite and does extra ball thing
            
def     goal():         
            if toBinary(readSPI(0x42, O_GPIOA)[7] == 1:         #checks what lite is on, acts according to
                punten(5000)
            elif toBinary(readSPI(0x42, O_GPIOB)[0] == 1:
                extra_ball()
            elif toBinary(readSPI(0x42, O_GPIOB)[1] == 1:
                special()


def     punten(amount):                                         #placeholder punten functie (bram)
            global points 
            points = points + amount    
            print(points) 
                    
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
		print(code,	"O_IOCON_2 ",		readSPI(code,	O_IOCON_2 ))
		print(code,	"O_GPPUA   ",		readSPI(code,	O_GPPUA   ))
 		print(code,	"O_GPPUB   ",		readSPI(code,	O_GPPUB   ))
 		print(code,	"O_INTFA   ",		readSPI(code,	O_INTFA   ))
 		print(code,	"O_INTFB   ",		readSPI(code,	O_INTFB   ))
		print(code,	"O_INTCAPA ",		readSPI(code,	O_INTCAPA ))
		print(code,	"O_INTCAPB ",		readSPI(code,	O_INTCAPB ))
		print(code,	"O_GPIOA   ",		readSPI(code,	O_GPIOA   ))
		print(code,	"O_GPIOB   ",		readSPI(code,	O_GPIOB   ))
		print(code,	"O_OLATA   ",		readSPI(code,	O_OLATA   ))
		print(code,	"O_OLATB   ",		readSPI(code,   O_OLATB   ))

def toBinary(getal):
    binair = str("{0:b}".format(getal))
    length = 8 - len(binair)
    binair = ('0' * length + binair)
    return list(map(int, list(binair)))
     
def binToHex(lijst):
    string = ''.join(map(str, lijst))
    return hex(int(string, 2))

def toggle(opcode, addr, lamp):
    state = toBinary(readSPI(opcode, addr)
    if state[lamp] == 0:
        state[lamp] = 1
    elif state[lamp] == 1:
        state[lamp] = 0
    sendSPI(opcode, addr, binToHex(state))




if __name__ == '__main__':

		main()
		
		reset_regs()



