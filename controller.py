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



def sendValue(value):
    for     i       in range(8):
        if (value       &       0x80):
            GPIO.output(MOSI,       GPIO.HIGH)
        else:
            GPIO.output(MOSI,       GPIO.LOW)

        GPIO.output(SCLK,       GPIO.HIGH)
        GPIO.output(SCLK,       GPIO.LOW)
        value   <<=     1

def sendSPI(opcode, addr,   data):
    GPIO.output(CS, GPIO.LOW)
    sendValue(opcode|SPI_SLAVE_WRITE)
    sendValue(addr)
    sendValue(data)
    GPIO.output(CS, GPIO.HIGH)
                        
def readSPI(opcode, addr):
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

def setup(): #Sets up GPIO, lights, variables, inputs, pull-up resistors
    GPIO.setup(SCLK, GPIO.OUT)                      #Sets the Raspberry's GPIO correctly to interface with the expansion board
    GPIO.setup(MOSI, GPIO.OUT)
    GPIO.setup(MISO, GPIO.IN)
    GPIO.setup(CS,   GPIO.OUT)
    GPIO.output(CS, GPIO.HIGH)
    GPIO.output(SCLK, GPIO.LOW)
    reset_regs()
    #Set as Input
    sendSPI(0x46, O_IODIRA, 0xFF)
    sendSPI(0x46, O_IODIRB, 0xFF)
    #Enable Pullup
    sendSPI(0x46, O_GPPUA, 0xFF)
    sendSPI(0x46, O_GPPUB, 0xFF)
    #Inverse Polarity of Input 
    sendSPI(0x46, O_IPOLA, 0xFF)
    sendSPI(0x46, O_IPOLB, 0xFF)

#starting dictionaries
DictSingleyards = {'yard1': 1, 'yard2': 1, 'yard3': 1, 'yard4': 1, 'yard5': 1, 'yard6': 1, 'yard7': 1, 'yard8': 1, 'yard9' :1, 'yard10': 1} #1 -10
DictDecayards = {'yardsleft': 1, 'yards10': 1, 'yards20': 1, 'yards30': 1, 'yards40': 1, 'yards50': 1, 'yards-40': 1, 'yards-30': 1, 'yards-20': 1, 'yards-10': 1, 'yardsright': 1} #Left, 10, 20, 30, 40, 50, -40, -30, -20, -10, Right
DictGoalscores = {'5000': 1, 'extra ball': 1, 'special': 1}
DictLTDscores = {'goal': 1, 'special': 1}
DictBonus = {'1000': 1, '2000': 1, '3000': 1, '4000': 1, '5000': 1, '6000': 1, '7000': 1, '8000': 1, '9000': 1, '10000': 1}
DictPijltjes = {'left': 1, 'right': 1}
Dict30yardswlit = {'1': 1, '2': 1, '3': 1, '4': 1}

#starting index of dictionaries above
IndexSingleyards = ['yard1', 'yard2', 'yard3', 'yard4', 'yard5', 'yard6', 'yard7', 'yard8', 'yard9', 'yard10']
IndexDecayards = ['yardsleft', 'yards10', 'yards20', 'yards30', 'yards40', 'yards50', 'yards-40', 'yards-30', 'yards-20', 'yards-10', 'yardsright']

#starting lights

#starting variables
ShootAgain = 1
DoubleBonus = 1
Kicker = 1
yardsvalue = 0
decayardsvalue = 0
yardsdirection = True #Go to Right
#setup inputs

#setup pull-up resistors
    
def main():             #Hoofdprogramma
    setup()
    walkinglight(0x40, O_GPIOA, 1) 
#    while 1:
#        Scan.feel()
######################################
#Speelfuncties
######################################
def special():          #Zal een special geven
    print("special")

def extraball():        #Zal voorkomen dat de spelercount omhoog gaat en dat het "shoot again" lampje aangaat
    print("extra ball")

def goal():             #Kijkt welke lampje boven de goal aan is
    print("goal")

def doublebonus():      #Zorgt ervoor dat de bonus zal verdubbelt worden
    print("doublebonus")

def addbonus(amount):   #Voegt bonuspunten toe
    print("bonus")

def lasttargetdown():   #Kijkt welke lampje langs de droptarget aan is
    print("lasttarget down")

def addyards(amount):    #Voegt yards toe en zorgt ervoor dat de lampjes gestuurd worden
    global DictSingleyards
    global DictDecayards
    global yardsvalue
    global decayardsvalue
    if yardsdirection: 
        yardsvalue +=  amount
    else:
        yardsvalue -=  amount
    while yardsvalue > 10:
        decayardsvalue += 1
        yardsvalue -= 10
    while yardsvalue < 0:
        decayardsvalue -= 1
        yardsvalue += 10
    if decayardsvalue < 0 and yardsvalue < 0:
        decayardsvalue = 0
        yardsvalue = 0
    if decayardsvalue > 11:
        goal()
        decayardsvalue = 0
        yardsvalue = 0
    #######################
    #Lights
    #######################
    for i in range(0, len(IndexSingleyards)):               #Resets dictionary to default state (all 1s)
        DictSingleyards[IndexSingleyards[i]] = 1            #It's set to 1 because lights will turn on when given ground, and off when given 3.3V
    for i in range(0, len(IndexDecayards)):
        DictDecayards[IndexDecayards[i]] = 1
    DictSingleyards[IndexSingleyards[yardsvalue - 1]] = 0   #Sets appropriate value (depending on yardvalue) to 0 -> this lite will be on
    DictDecayards[IndexDecayards[decayardsvalue]] = 0       #Sets appropriate value (depending on decayardvalue) to 0 -> this lite will be on


def toplights():        #Kijkt als het lampje boven het contact aan is
    print("toplights")

def outhole():          #Zorgt voor de spelercount, ejectball en countbonus
    print("outhole")

def ejectball():        #Trekt de relais kortstondig aan nadat de bal kwijt wordt gespeeld
    print("ejectball")

def countbonus():       #Telt de bonus punten op nadat de bal kwijt wordt gespeeld, zorgt ook voor doublebonus
    print("countbonus")

#####################################
#Algemene Functies
#####################################
def debug(code):        #Leest elke adres van een bepaalde IC uit
    for i in [O_IPOLA, O_IPOLB, O_GPINTENA, O_GPINTENB, O_DEFVALA, O_DEFVALB, O_INTCONA, O_INTCONB, O_GPPUA, O_GPPUB, O_INTFA, O_INTFB, O_INTCAPA, O_INTCAPB, O_GPIOA, O_GPIOB, O_OLATA, O_OLATB]:
        print(code, i, "=", readSPI(code, i)) 

def walkinglight(opcode, addr, speed):     #Om alle lampjes te testen
    for i in range(0,7):
        listwalk = [1, 1, 1, 1, 1, 1, 1, 1] 
        listwalk[i] = 0 
        sendSPI(opcode, addr, mkhex(listwalk))
        time.sleep(speed)

def mklst(x):           #Maakt van een hexadecimaal getal een binaire lijst
    return [1 if (1<<j)&x else 0 for j in range(7,-1,-1)]

def mkhex(lijst):       #Maakt van bovenstaande lijst terug een getal
    return int(''.join(map(str, lijst)), 2) 
def togglevar(var):
    if var == 1:
        var = 0
    elif var == True:
        var = False
    elif var == 0:
        var = 1
    elif var == False:
        var = True
    return var

def setlites():
    list0x40A = [DictSingleyards['yard1'], DictSingleyards['yard2'], DictSingleyards['yard3'], DictSingleyards['yard4'], DictSingleyards['yard5'], DictSingleyards['yard6'], DictSingleyards['yard7'], DictSingleyards['yard8']]
    list0x40B = [DictSingleyards['yard9'], DictSingleyards['yard10'], DictDecayards['yardsleft'],  DictDecayards['yards10'], DictDecayards['yards20'], DictDecayards['yards30'], DictDecayards['yards40'], DictDecayards['yards50']]
    list0x42A = [DictDecayards['yards-40'], DictDecayards['yards-30'], DictDecayards['yards-20'], DictDecayards['yards-10'], DictDecayards['yardsright'], DictPijltjes['left'], DictPijltjes['right'], DictGoalscores['5000']]
    list0x42B = [DictGoalscores['extra ball'], DictGoalscores['special'], DictLTDscores['goal'], DictLTDscores['special'], DictBonus['4000'], DictBonus['5000'], DictBonus['6000'], DictBonus['7000']] 
    list0x44A = [DictBonus['1000'], DictBonus['2000'], DictBonus['3000'], Dict30yardswlit['1'], Dict30yardswlit['3'], ShootAgain, 0, 0]
    list0x44B = [DictBonus['9000'], DictBonus['10000'], DoubleBonus, DictBonus['8000'], Dict30yardswlit['2'], Dict30yardswlit['4'], Kicker, 0]
     
    hex0x40A = mkhex(list0x40A)
    hex0x40B = mkhex(list0x40B)
    hex0x42A = mkhex(list0x42A)
    hex0x42B = mkhex(list0x42B)
    hex0x44A = mkhex(list0x44A)
    hex0x44B = mkhex(list0x44B)
    
    print(hex0x40A)
    print(hex0x40B)
    print(hex0x42A)
    print(hex0x42B)
    print(hex0x44A)
    print(hex0x44B)
    sendSPI(0x40, O_GPIOA, hex0x40A) 
    sendSPI(0x40, O_GPIOB, hex0x40B) 
    sendSPI(0x42, O_GPIOA, hex0x42A) 
    sendSPI(0x42, O_GPIOB, hex0x42B) 
    sendSPI(0x44, O_GPIOA, hex0x44A) 
    sendSPI(0x44, O_GPIOB, hex0x44B) 
    
    
if __name__ == '__main__':
        
#            Scan=Feeler(30,Menu)

            main()
                
            reset_regs()
 
