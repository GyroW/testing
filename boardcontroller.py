#-------------------------------------------------------------------------------#

#       Name: boardcontroller.py                                                #

#       Purpose: Controls RPI for mechanical pinball                            #

#       GPIO-Library:   RPi.GPIO 0.5.3a                                         #

#                                                                               #

#       Author: Pridopia,       James   Clarke                                  #
#       Author: Technicum,      Wouter  Lemoine
#       Author: ON4ABS,         Mark    Berwaers
#       Website: www.pridopia.co.uk                                             #

#                                                                               #

#       Created:        12/09/2013                                              #
#       Modified:       x/02/2017                                               #

#-------------------------------------------------------------------------------#



import time, sys,       signal, os
import random
import RPi.GPIO as GPIO



GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)



SPI_SLAVE_ADDR  =       0x40

SPI_IOCTRL                      =       0x0A



SPI_IODIRA                      =       0x00

SPI_IODIRB                      =       0x10



SPI_GPIOA                               =       0x12

SPI_GPIOB                               =       0x13



SPI_SLAVE_WRITE =       0x00

SPI_SLAVE_READ  =       0x01



SCLK                            =       11

MOSI                            =       10

MISO                            =       9

CS                              =       8




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



def     sendValue(value):

                for     i       in range(8):
                                
                                if (value       &       0x80):

                                                GPIO.output(MOSI,       GPIO.HIGH)

                                else:
 
                                                GPIO.output(MOSI,       GPIO.LOW)

                                GPIO.output(SCLK,       GPIO.HIGH)
                                GPIO.output(SCLK,       GPIO.LOW)
        
                                value   <<=     1
                        


def     sendSPI(opcode, addr,   data):

                GPIO.output(CS, GPIO.LOW)
                if addr == "O_GPIOA" or addr == "O_GPIOB":
                    data = data ^ 0xFF

                sendValue(opcode|SPI_SLAVE_WRITE)

                sendValue(addr)

                sendValue(data)

                GPIO.output(CS, GPIO.HIGH)



def     readSPI(opcode, addr):

                GPIO.output(CS, GPIO.LOW)
                sendValue(opcode|SPI_SLAVE_READ)
                sendValue(addr)



                value   =       0

                for     i       in range(8):
                                value   <<=     1
                                if(GPIO.input(MISO)):

                                                value   |= 0x01

                                GPIO.output(SCLK,       GPIO.HIGH)
                                GPIO.output(SCLK,       GPIO.LOW)



                GPIO.output(CS, GPIO.HIGH)
                return value
                
                
def reset_regs():
                for device_address in [0x40,0x42,0x44,0x46]:
                        # I_IOCON_2 = 0x15 !!
                        
                        # if in Bank 1 then back to bank 0 else write to O_OLATB(no effect)
                        sendSPI(device_address,I_IOCON_2,0x28) 
      
      
                        # now always in bank 0 ( set SEQOP and HAEN ) 
                        sendSPI(device_address,O_IOCON,0x28) 
      
                
                        sendSPI(device_address,O_IODIRA,0x00)   # all pins output
                        sendSPI(device_address,O_IODIRB,0x00)   # all pins output
                        
                        #clear all other registers except O_IOCON and O_IOCON_2
                        for regaddress in [O_IPOLA, O_IPOLB, O_GPINTENA, O_GPINTENB, O_DEFVALA, O_DEFVALB, O_INTCONA, O_INTCONB, O_GPPUA, O_GPPUB, O_INTFA, O_INTFB, O_INTCAPA, O_INTCAPB, O_GPIOA, O_GPIOB, O_OLATA, O_OLATB]:
                                sendSPI(device_address,regaddress,0)                            
                

                                

yarddirection = 0  #0 = right 1 = left
yards = 0           #starting yardsunits
yardsten = 0        #starting yardsten 
points = 0          #testing punten
targetshit = 0      #Aantal Targets Hit
bonus = 0

class Feeler:                                                   #Debouncing utility, starts a new instance every time we start counting again so we don't overlap
        def __init__(m,maxv,func):
                m.maxval=maxv
                m.teller=maxv
                m.oldstate=0
                m.func=func

        def feel(m):
                a=readSPI(0x46, O_GPIOA)
                b=readSPI(0x46, O_GPIOB)&0xF0
                if a or b:
                        if m.teller>0:
                                m.teller-=1
                                if m.teller==0:
                                        if m.oldstate==0:
                                                m.oldstate=1
                                                m.func(a,b)
                                                # doe iets
                else:
                        if m.teller<m.maxval:
                                m.teller+=1
                                if m.teller==m.maxval:
                                        if m.oldstate==1:
                                                m.oldstate=0
                                                #doe iets
                                                
                





def     main():

                GPIO.setup(SCLK, GPIO.OUT)                      #Sets the Raspberry's GPIO correctly to interface with the expansion board

                GPIO.setup(MOSI, GPIO.OUT)

                GPIO.setup(MISO, GPIO.IN)

                GPIO.setup(CS,   GPIO.OUT)

                GPIO.output(CS, GPIO.HIGH)

                GPIO.output(SCLK, GPIO.LOW)
                reset_regs()
                #declaring some variables


#               print(readSPI(0x40, O_IODIRA))

                sendSPI(0x46, O_IODIRA, 0xFF)                   #Sets the switches as input instead of output
                sendSPI(0x46, O_IODIRB, 0xF0)
                #Start of game lights:
                sendSPI(0x40, O_GPIOA, 0x80)
                sendSPI(0x40, O_GPIOB, 0x20)
                sendSPI(0x42, O_GPIOA, 0x03)
                sendSPI(0x42, O_GPIOB, 0x2A)
                #inverses polarity of input pins:
                sendSPI(0x46, O_IPOLA, 0xFF)
                sendSPI(0x46, O_IPOLB, 0xF0)
                #enable pull up:
                sendSPI(0x46, O_GPPUA, 0xFF)
                sendSPI(0x46, O_GPPUB, 0xF0)

                while 1:                
                        Scan.feel()
#               debug(0x40)
#               debug(0x42)
#               debug(0x44)
#               debug(0x46)





                                
                        
        



                
def     Menu(a,b):
            switchbankone=toBinary(a)
            switchbanktwo=toBinary(b)


            global targetshit
            global yardsten
            #   [toprollover 1, toprollover 2,  toprollover 3,  tolrollover4,   ster,   popbumper,  targets,    spinner ] 
            #en [outlane,       achterbank,     bank,           outhole,        /,      /,          /,          /       ]
            #print(switchbankone)
            #print(switchbanktwo)
           
            if switchbankone[0] == 1:#toprollover 1
                if toBinary(readSPI(0x42, O_GPIOB))[4]: 
                    yard(30)
                punten(500) 
            if switchbankone[1] == 1:#toprollover 2
                punten(500)
                if toBinary(readSPI(0x42, O_GPIOB))[5]: 
                    yard(30)
            if switchbankone[2] == 1:#toprollover 3
                punten(500)
                if toBinary(readSPI(0x42, O_GPIOB))[6]: 
                    yard(30)
            if switchbankone[3] == 1:#toprollover 4
                punten(500)
                if toBinary(readSPI(0x42, O_GPIOB))[7]: 
                    yard(30)
            if switchbankone[4] == 1:#ster
                punten(100)
                changeyardsdirection()
                bonus(1000)

            if switchbankone[5] == 1:#popbumper
                punten(50)
                yard(1)
                randomtoplights()
            if switchbankone[6] == 1:#targets
                punten(1000)
                bonus(1000)
                yard(5)
            if switchbankone[7] == 1:#spinner
                punten(10) 
                changeyardsdirection()
            if switchbanktwo[0] == 1:#outlane
                print("outlane")
                punten(1000)
                yard(10)
            if switchbanktwo[1] == 1:#achterbank
                bonus(1000)
                punten(500)
                yard(1)
            if switchbanktwo[2] == 1:#bank drop down targers 
                targetshit = targetshit + 1
                punten(300)

            if switchbanktwo[3] == 1:#outhole
                outhole()                                       #place holder function depends on bram 
            if targetshit == 7:
                if toBinary(readSPI(0x42, O_GPIOB))[2] == 1:
                    goal()
                elif toBinary(readSPI(0x42, O_GPIOB))[3] == 1:
                    special()
                targetshit = 0
                
            if yardsten == 11:
                goal()
                yards = 1
                yardsten = 0



def     changeyardsdirection():                                 #changes what direction the yards should go to, when triggered
            global yarddirection                                #toggles direction
            if yarddirection == 0:
                yarddirection = 1
            elif yarddirection == 1:
                yarddirection = 0
            #print(yarddirection)                               #debug 
            toggle(0x42, O_GPIOA, 2)
            toggle(0x42, O_GPIOA, 3)

def     yard(amount):                                           #Controls the yardage and corresponding lights!
            #print(yards)
            #print(yardsten)
            global yarddirection                                #    
            global yards                                        #
            global yardsten                                     #
            yardstate = toBinary(readSPI(0x40, O_GPIOB))        #2de rij in excel bestand
            if yarddirection == 0:                              #Direction of arrow 0 is to the right, 1 is to the left
                yards = yards + amount                          #
            elif yarddirection == 1:                            #
                yards = yards - amount                          #
            while yards > 10:                                   #If we are multiple times over 10 hence the while loop
                yardsten = yardsten + 1                         #If we go above 10 we add to the yardsten (issue with splitting numbers)
                yards = yards - 10                              #Subtract 10 from yards to get to our number
            while yards < 1 and yardsten > 0:                   #When the ball is moving backwards we need to go down unless we are already at 0
                yards = 10 + yards                              #Yards is negative hence "+" this will make yards a single digit number or 10
                yardsten = yardsten - 1                         #We're going backwards and when we're below 0 in the single yards we go down a ten
            if yards < 1 and yardsten == 0:                     #If we're totally at the left we can't go more left so we just make yards 1 again
                yards = 1                                       #
            if yardsten < 0:                                    #If yardsten somehow goes below 0 we make it 0 just to be sure...
                yardsten = 0                                    #
            if yards == 1:
                sendSPI(0x40, O_GPIOA, 0x80)                    #1ste rij in excel bestand
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
            #print(yardstate)                                    #debug
            #print(yardstateB)
               



def     randomtoplights():
            toplitestateA = toBinary(readSPI(0x44, O_GPIOA))    
            toplitestataB = toBinary(readSPI(0x44, O_GPIOB))
            toplitestateA[3] = random.randint(0, 1)             
            toplitestateB[4] = random.randint(0, 1)             
            toplitestateA[4] = random.randint(0, 1)             
            toplitestateB[5] = random.randint(0, 1)             
            sendSPI(0x44, O_GPIOA, binToHex(toplitestateA)) 
            sendSPI(0x44, O_GPIOB, binToHex(toplitestateB)) 
def     special():                                              #defines what special does
                print("special got")            
def     extra_ball():                                           #triggers extra ball lite and does extra ball thing
                toggle(0x44, O_GPIOA, 5)
                print("extra ball got")
def     goal():         
            if toBinary(readSPI(0x42, O_GPIOA))[7] == 1:        #checks what lite is on, acts according to
                punten(5000)
            elif toBinary(readSPI(0x42, O_GPIOB))[0] == 1:
                extra_ball()
            elif toBinary(readSPI(0x42, O_GPIOB))[1] == 1:
                special()
            addbonus(2000)
def     outhole():                                              #Need to know how bram will handle next player, I'll act according to
            print("bal kwijt")                                  #Needs add bonus function that will add the bonus to the player
            if toBinary(readSPI(0x44, O_GPIOA))[5] == 1:
                toggle(0x44, O_GPIOA, 5)

            countbonus()
            addbonus(0)
            LTD = toBinary(readSPI(0x42, O_GPIOB)
            if ballingame == 5: 
                LTD[2] = 0
                LTD[3] = 1
            else:
                LTD[2] = 1
                LTD[3] = 0
            
            
            sleep(2)
            eject()
def     eject()
            toggle(0x44, O_GPIOB, 6)
            toggle(0x44, O_GPIOB, 6)

def     punten(amount):                                         #placeholder punten functie (bram)
            global points 
            points = points + amount    
            print(points) 

def     addbonus(amount):                                          #Only 1000*n
            global bonus
            bonuslitesstateA =  toBinary(readSPI(0x44, O_GPIOA))
            bonuslitesstateB =  toBinary(readSPI(0x44, O_GPIOB))
            bonuslitesstateC =  toBinary(readSPI(0x42, O_GPIOB))
            goalscorestateA =   toBinary(readSPI(0x42, O_GPIOA))
            goalscorestateB =   toBinary(readSPI(0x42, O_GPIOB))
            bonus = bonus + amount
            if bonus < 5000:
                goalscorestateA[7] = 1
                goalscorestateB[0] = 0
                goalscorestateB[1] = 0
               
            if bonus == 12000 and goalscorestateA[7] == 1:
                goalscorestateA[7] = 0
                goalscorestateB[0] = 1
                goalscorestateB[1] = 0
            elif bonus == 12000 and goalscorestateB[0] == 1:
                goalscorestateA[7] = 0
                goalscorestateB[0] = 0
                goalscorestateB[1] = 1
                            
            if bonus > 10000:
                bonus = 10000
            if bonus == 1000:
                bonuslitestateA[0] =1                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =0                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =0                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =0                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =0                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =0                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =0                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =0                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =0                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =0                           #10000      0x44, O_GPIOB, 1
            if bonus == 2000:
                bonuslitestateA[0] =0                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =1                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =0                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =0                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =0                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =0                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =0                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =0                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =0                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =0                           #10000      0x44, O_GPIOB, 1
            if bonus == 3000:
                bonuslitestateA[0] =0                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =0                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =1                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =0                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =0                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =0                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =0                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =0                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =0                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =0                           #10000      0x44, O_GPIOB, 1
            if bonus == 4000:
                bonuslitestateA[0] =0                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =0                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =0                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =1                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =0                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =0                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =0                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =0                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =0                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =0                           #10000      0x44, O_GPIOB, 1
            if bonus == 5000:
                bonuslitestateA[0] =0                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =0                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =0                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =0                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =1                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =0                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =0                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =0                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =0                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =0                           #10000      0x44, O_GPIOB, 1
            if bonus == 6000:
                bonuslitestateA[0] =0                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =0                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =0                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =0                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =0                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =1                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =0                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =0                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =0                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =0                           #10000      0x44, O_GPIOB, 1
            if bonus == 7000:
                bonuslitestateA[0] =0                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =0                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =0                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =0                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =0                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =0                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =1                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =0                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =0                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =0                           #10000      0x44, O_GPIOB, 1
            if bonus == 8000:
                bonuslitestateA[0] =0                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =0                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =0                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =0                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =0                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =0                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =0                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =1                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =0                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =0                           #10000      0x44, O_GPIOB, 1
            if bonus == 9000:
                bonuslitestateA[0] =0                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =0                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =0                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =0                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =0                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =0                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =0                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =0                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =1                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =0                           #10000      0x44, O_GPIOB, 1
            if bonus == 10000:
                bonuslitestateA[0] =0                           #1000       0x44, O_GPIOA, 0
                bonuslitestateA[1] =0                           #2000       0x44, O_GPIOA, 1
                bonuslitestateA[2] =0                           #3000       0x44, O_GPIOA, 2
                bonuslitestateC[4] =0                           #4000       0x42, O_GPIOB, 4
                bonuslitestateC[5] =0                           #5000       0x42, O_GPIOB, 5
                bonuslitestateC[6] =0                           #6000       0x42, O_GPIOB, 6
                bonuslitestateC[7] =0                           #7000       0x42, O_GPIOB, 7
                bonuslitestateB[3] =0                           #8000       0x44, O_GPIOB, 3
                bonuslitestateB[0] =0                           #9000       0x44, O_GPIOB, 0
                bonuslitestateB[1] =1                           #10000      0x44, O_GPIOB, 1
            sendSPI(0x44, O_GPIOA, binToHex(bonuslitestateA))
            sendSPI(0x44, O_GPIOB, binToHex(bonuslitestateB))
            sendSPI(0x42, O_GPIOA, binToHex(goalscorestateA))
            sendSPI(0x42, O_GPIOB, binToHex(goalscorestateB))


def     countbonus():
            global bonus
            global points
            if toBinary(readSPI(0x44, O_GPIOB))[2] == 1:
                bonus = bonus * 2
            points = points + bonus
            bonus = 0

def     debug(code):
            print(code,     "O_IODIRA  ",           readSPI(code,   O_IODIRA  ))
            print(code,     "O_IODIRB  ",           readSPI(code,   O_IODIRB  ))
            print(code,     "O_IPOLA   ",           readSPI(code,   O_IPOLA   ))
            print(code,     "O_IPOLB   ",           readSPI(code,   O_IPOLB   ))
            print(code,     "O_GPINTENA",           readSPI(code,   O_GPINTENA))
            print(code,     "O_GPINTENB",           readSPI(code,   O_GPINTENB))
            print(code,     "O_DEFVALA ",           readSPI(code,   O_DEFVALA ))
            print(code,     "O_DEFVALB ",           readSPI(code,   O_DEFVALB ))
            print(code,     "O_INTCONA ",           readSPI(code,   O_INTCONA ))
            print(code,     "O_INTCONB ",           readSPI(code,   O_INTCONB ))
            print(code,     "O_IOCON   ",           readSPI(code,   O_IOCON   ))
            print(code,     "O_IOCON_2 ",           readSPI(code,   O_IOCON_2 ))
            print(code,     "O_GPPUA   ",           readSPI(code,   O_GPPUA   ))
            print(code,     "O_GPPUB   ",           readSPI(code,   O_GPPUB   ))
            print(code,     "O_INTFA   ",           readSPI(code,   O_INTFA   ))
            print(code,     "O_INTFB   ",           readSPI(code,   O_INTFB   ))
            print(code,     "O_INTCAPA ",           readSPI(code,   O_INTCAPA ))
            print(code,     "O_INTCAPB ",           readSPI(code,   O_INTCAPB ))
            print(code,     "O_GPIOA   ",           readSPI(code,   O_GPIOA   ))
            print(code,     "O_GPIOB   ",           readSPI(code,   O_GPIOB   ))
            print(code,     "O_OLATA   ",           readSPI(code,   O_OLATA   ))
            print(code,     "O_OLATB   ",           readSPI(code,   O_OLATB   ))

def     toBinary(getal):
            binair = str("{0:b}".format(getal))
            length = 8 - len(binair)
            binair = ('0' * length + binair)
            return list(map(int, list(binair)))
     
def     binToHex(lijst):
            string = ''.join(map(str, lijst))
            return int(string, 2)

def     toggle(opcode, addr, lamp):
            state = toBinary(readSPI(opcode, addr))
            if state[lamp] == 0:
                state[lamp] = 1
            elif state[lamp] == 1:
                state[lamp] = 0
            sendSPI(opcode, addr, binToHex(state))




if __name__ == '__main__':
        
            Scan=Feeler(30,Menu)

            main()
                
            reset_regs()



