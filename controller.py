import time, sys,       signal, os
import random
import RPi.GPIO as GPIO
from Tkinter import * 


GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

SPI_SLAVE_ADDR = 0x40
SPI_IOCTRL = 0x0A
SPI_IODIRA = 0x00
SPI_IODIRB = 0x10
SPI_GPIOA = 0x12
SPI_GPIOB = 0x13
SPI_SLAVE_WRITE = 0x00
SPI_SLAVE_READ = 0x01
SCLK = 11
MOSI = 10
MISO = 9
CS = 8

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

class Feeler:        #Debouncing utility, starts a new instance every time we start counting again so we don't overlap
    def __init__(m,maxv,func):
            m.maxval=maxv
            m.teller=maxv
            m.oldstate=0
            m.func=func

    def feel(m):
        a=readSPI(0x46, O_GPIOA)
        b=readSPI(0x46, O_GPIOB)
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
    visual()
    #Set as Input
    sendSPI(0x46, O_IODIRA, 0xFF)
    sendSPI(0x46, O_IODIRB, 0xFF)
    #Enable Pullup
    sendSPI(0x46, O_GPPUA, 0xFF)
    sendSPI(0x46, O_GPPUB, 0xFF)
    #Inverse Polarity of Input 
    sendSPI(0x46, O_IPOLA, 0xFF)
    sendSPI(0x46, O_IPOLB, 0xFF)
    #Starting Lights
    DictPijltjes['right'] = 0
    DictLTDscores['goal'] = 0
    DictGoalscores['5000'] = 0
    ejectball()

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
IndexBonus = ['1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000', '9000', '10000']

#starting variables
ballingame = 1
maxballs = 5
maxplayers = 0
playeringame = 0
Gameover = True
gui = Tk()
QPP1 = StringVar() 
QPP2 = StringVar() 
QPP3 = StringVar() 
QPP4 = StringVar() 
Qballingame = StringVar()
PP1 = 0
PP2 = 0
PP3 = 0
PP4 = 0

Shootagain = 1
DoubleBonus = 1
Kicker = 1
yardsvalue = 0
decayardsvalue = 0
bonus = 0
points = 0
targetshit = 0
#Yardsdirection is deprecated as it is now handled with DictPijltjes

#Visualvariables
xpadding = 50
ypadding = 250
fontsize = 70
textcolour      ='#00468B'
textfont        ='Helvetica'
activecolour    ='#FFDE00'
inactivecolour  ='#149CD8'
gui = Tk()
w = gui.winfo_screenwidth() 
h = gui.winfo_screenheight()
gui.overrideredirect(1)
gui.geometry("%dx%d+0+0" % (w, h))

def visual():           #Visual Initialization
    print("visual has been run")
    
    bgimage = PhotoImage(file = 'background.gif')                               #Sets background image
    x = Label(image=bgimage) 
    x.place(x=0, y=0, relwidth=1, relheight=1)

    Speler1 = Label(text='Speler 1', fg=textcolour, font=(textfont, fontsize))  #Creert label met correcte tekst, kleur, font en grootte
    Speler2 = Label(text='Speler 2', fg=textcolour, font=(textfont, fontsize))
    Speler3 = Label(text='Speler 3', fg=textcolour, font=(textfont, fontsize))
    Speler4 = Label(text='Speler 4', fg=textcolour, font=(textfont, fontsize))
    Ballingame = Label(text='Ball in game', fg = textcolour, font=(textfont, fontsize/2))

    Speler1.grid(row=0,column=0, sticky=E)                                      #Plaatst de labels op de correcte plaats met desnodig padding
    Speler2.grid(row=0,column=2, sticky=W, padx=xpadding)
    Speler3.grid(row=2,column=0, sticky=E, )
    Speler4.grid(row=2,column=2, sticky=W, padx=xpadding)
    Ballingame.grid(row=0, column=1)

def updatevisual():
    print("updated the visual")
    global QPP1 
    global QPP2 
    global QPP3
    global QPP4
    global Qballingame
    QPP1.set(PP1) 
    QPP2.set(PP2)
    QPP3.set(PP3)
    QPP4.set(PP4)
    Qballingame.set(ballingame)
    #Maakt de VPP1-4 labels
    if playeringame == 1:
        VPP1 = Label(textvariable=QPP1, fg=activecolour,      font=(textfont, fontsize))
    else:
        VPP1 = Label(textvariable=QPP1, fg=inactivecolour,    font=(textfont, fontsize))
    if playeringame == 2:
        VPP2 = Label(textvariable=QPP2, fg=activecolour,      font=(textfont, fontsize))
    else:
        VPP2 = Label(textvariable=QPP2, fg=inactivecolour,    font=(textfont, fontsize))
    if playeringame == 3:
        VPP3 = Label(textvariable=QPP3, fg=activecolour,      font=(textfont, fontsize))
    else:
        VPP3 = Label(textvariable=QPP3, fg=inactivecolour,    font=(textfont, fontsize))
    if playeringame == 4:
        VPP4 = Label(textvariable=QPP4, fg=activecolour,      font=(textfont, fontsize))
    else:
        VPP4 = Label(textvariable=QPP4, fg=inactivecolour,    font=(textfont, fontsize))
    Vballingame = Label(text="bal:", textvariable=Qballingame, fg = inactivecolour, font=(textfont, fontsize/2))
    VPP1.grid(row=1,column=0, pady=(0,ypadding))                                #Makes sure VPP1-4 exists
    VPP2.grid(row=1,column=2, pady=(0,ypadding))
    VPP3.grid(row=3,column=0)
    VPP4.grid(row=3,column=2)
    Vballingame.grid(row=1, column=1)
    gui.update_idletasks()
    gui.update()
    
    
def main():             #Hoofdprogramma
    setup()
    setlites()
#    startknop()
    updatevisual()
    global bonus    
    runtime = 2
    if runtime == 1:
        for addr in [0x40, 0x42, 0x44]:
            for side in [O_GPIOA, O_GPIOB]:
                walkinglight(addr, side, 1)
                sendSPI(addr, side, 0xFF)
    if runtime == 2:
        while 1:
            Scan.feel()
    if runtime == 3:
	while 1:
	    time.sleep(2)
	    addbonus(1000)
            addyards(1)
            setlites()
	    if bonus == 20000:
		bonus = 0
    if runtime == 4:
	reset_regs()


def game(A, B):         #Handles switches
	global targetshit
        global DictLTDscores
	global DictGoalscores
	switchbankone = mklst(B)
        switchbanktwo = mklst(A)
	print(switchbankone)
	print(switchbanktwo)
        print(Dict30yardswlit)            
    
        if switchbanktwo[4] == 1:
            startknop()
            
        if Gameover == False:       #Only work if not in gameover mode

            
            if switchbanktwo[7] == 1:#toprollover 1
                print("top rollover 1")
	        punten(500)
                if Dict30yardswlit['1'] == 0: 
                   addyards(30)
                   if bonus == 10000:
		        if DictLTDscores['goal'] == 0:
			    DictLTDscores['goal'] = 1
			    DictLTDscores['special'] = 0


            if switchbankone[1] == 1:#toprollover 2
                print("top rollover 2")
                punten(500)
                if Dict30yardswlit['2'] == 0:
                    addyards(30)
                    if bonus == 10000:
		        if DictLTDscores['goal'] == 0:
			    DictLTDscores['goal'] = 1
			    DictLTDscores['special'] = 0

            
            if switchbankone[2] == 1:#toprollover 3
                print("top rollover 3")
                punten(500)
                if Dict30yardswlit['3'] == 0:
                    addyards(30)
                    print(bonus)
		    if bonus == 10000:
		        if DictLTDscores['goal'] == 0:
			    DictLTDscores['goal'] = 1
			    DictLTDscores['special'] = 0

            
            if switchbankone[3] == 1:#toprollover 4
                print("top rollover 4")
                punten(500)
                if Dict30yardswlit['4'] == 0: 
                    addyards(30)
                    if bonus == 10000:
		        if DictLTDscores['goal'] == 0:
			    DictLTDscores['goal'] = 1
			    DictLTDscores['special'] = 0

            
            if switchbankone[4] == 1:#ster
                print("ster")
		punten(100)
                changeyardsdirection()
		if bonus == 10000:
		    if DictGoalscores['5000'] == 0 and DictGoalscores['extra ball'] == 1 and DictGoalscores['special'] == 1:
			DictGoalscores['5000'] = 1
			DictGoalscores['extra ball'] = 0
		print(DictGoalscores)		
		addbonus(1000)

            
            if switchbankone[5] == 1:#popbumper
                print("popbumper")
		punten(50)
                addyards(1)
                randomtoplights()

            
            if switchbankone[6] == 1:#targets
                print("targets")
		punten(1000)
                addbonus(1000)
                addyards(5)
		if DictGoalscores['5000'] == 1 and DictGoalscores['extra ball'] == 0 and DictGoalscores['special'] == 1:
		    DictGoalscores['extra ball'] = 1
		    DictGoalscores['special'] = 0

            
            if switchbanktwo[5] == 1:#spinner
                print("spinner")
		punten(10) 
                addyards(1)

            
            if switchbanktwo[0] == 1:#outlane
                print("outlane")
                punten(1000)
                addyards(10)

            
            if switchbanktwo[1] == 1:#achterbank
                print("targets archetr bank")
		addbonus(1000)
                punten(500)
                addyards(1)

            
            if switchbanktwo[2] == 1:#bank drop down targers 
                print("droptarget")
		targetshit += 1
                punten(300)

            
            if switchbanktwo[3] == 1:#outhole
                outhole() 
	    
            
            setlites()
            updatevisual()
	    lasttargetdown() #check if 7 targets have been hit

######################################
#Speelfuncties Basically, sets up variables according to what you've done.
######################################
def special():          #Zal een special geven
    doublebonus()
    extraball()
    punten(10000)
    addbonus(3000)
    print("special")

def extraball():        #Zal voorkomen dat de spelercount omhoog gaat en dat het "shoot again" lampje aangaat
    global Shootagain
    print("extra ball")
    Shootagain = 0

def goal():             #Kijkt welke lampje boven de goal aan is
    print("goal")
    if DictGoalscores['5000'] == 0:
            print("5000 scored")        
            punten(5000)
    elif DictGoalscores['extra ball'] == 0:
            print("goal scored")
            extraball()
    elif DictGoalscores['special'] == 0:   
            print("special scored")
            special()

def doublebonus():      #Zorgt ervoor dat de bonus zal verdubbelt worden
    print("doublebonus")
    global DoubleBonus
    DoubleBonus = 0 

def addbonus(amount):   #Voegt bonuspunten toe
    global bonus
    global DictBonus
    print("bonus")
    for i in DictBonus:               #Resets dictionary to default state (all 1s)
        DictBonus[i] = 1            #It's set to 1 because lights will turn on when given ground, and off when given 3.3V
    if bonus < 10000:
        bonus += amount 
    DictBonus[IndexBonus[(bonus/1000)-1]] = 0
    print(bonus)

def lasttargetdown():   #Kijkt welke lampje langs de droptarget aan is
    global targetshit
    if targetshit == 7:
        print("lasttarget down")
        if DictLTDscores['goal'] == 0:
            goal()
        elif DictLTDscores['special']:
            special()
        targetshit = 0

def addyards(amount):    #Voegt yards toe en zorgt ervoor dat de lampjes gestuurd worden
    global DictSingleyards
    global DictDecayards
    global yardsvalue
    global decayardsvalue
    if DictPijltjes['right'] == 0: 
        yardsvalue +=  amount
    else:
        yardsvalue -=  amount
    while yardsvalue > 10:
        decayardsvalue += 1
        yardsvalue -= 10
    while yardsvalue < 0:
        decayardsvalue -= 1
        yardsvalue += 10
    if decayardsvalue < 0:
        decayardsvalue = 0
        yardsvalue = 0
    if decayardsvalue >= 11:
        goal()
        decayardsvalue = 0
        yardsvalue = 0
    for i in DictSingleyards:               #Resets dictionary to default state (all 1s)
        DictSingleyards[i] = 1            #It's set to 1 because lights will turn on when given ground, and off when given 3.3V
    for i in DictDecayards:
        DictDecayards[i] = 1
    DictSingleyards[IndexSingleyards[yardsvalue - 1]] = 0   #Sets appropriate value (depending on yardvalue) to 0 -> this lite will be on
    DictDecayards[IndexDecayards[decayardsvalue]] = 0       #Sets appropriate value (depending on decayardvalue) to 0 -> this lite will be on
    print(yardsvalue)
    print(decayardsvalue)

def outhole():              #Zorgt voor de spelercount, ejectball en countbonus
    global DictPijltjes
    global DictGoalscores
    global DictLTDscores
    global Shootagain
    print("outhole")
    countbonus()
    time.sleep(2)
    ejectball()
    setlites()
    DictPijltjes['right'] = 0 
    DictPijltjes['left'] = 1
    DictGoalscores['5000'] = 0
    DictGoalscores['extra ball'] = 1
    DictGoalscores['special'] = 1
    DictLTDscores['goal'] = 0
    DictLTDscores['special'] = 1
    for i in DictBonus:
        DictBonus[i] = 1
    #Spelercount
    global ballingame
    global playeringame
    if Gameover == False:    
        if Shootagain == 1:     #If false
            playeringame += 1   #Add to playeringame
        if playeringame > maxplayers:
            playeringame = 1
            ballingame += 1     #If we exceed maximum amount of players, go to next ball
        if ballingame > maxballs: #If we exceed maximum amount of balls, gameover
            gameover()
    if ballingame == 5:
        doublebonus()
    Shootagain = 1
    setlites()

def gameover():
    global Gameover
    global ballingame
    global maxplayers
    global PP1
    global PP2
    global PP3
    global PP4
    Gameover = True
    ballingame = 1
    maxplayers = 0
#    resetvisual()
    time.sleep(5)
    PP1 = 0
    PP2 = 0
    PP3 = 0
    PP4 = 0
    updatevisual()


def startknop():
    print("startknop")
    global maxplayers
    global Gameover
    global playeringame
    if maxplayers == 0:
        Gameover = False
        playeringame = 1
    if ballingame == 1 and maxplayers < 4:
        maxplayers += 1

def ejectball():            #Trekt de relais kortstondig aan nadat de bal kwijt wordt gespeeld
    print("ejectball")
    global Kicker
    Kicker = 0
    setlites()
    time.sleep(0.05)
    Kicker = 1
    setlites()

def countbonus():           #Telt de bonus punten op nadat de bal kwijt wordt gespeeld, zorgt ook voor doublebonus
    print("countbonus")
    global bonus
    if DoubleBonus == 0:
        bonus *= 2
    punten(bonus) 
    bonus = 0

def changeyardsdirection(): #Verandert richting van pijltjes
    print("changeyardsdirection")
    global DictPijltjes

    DictPijltjes['left'] = togglevar(DictPijltjes['left'])
    DictPijltjes['right'] = togglevar(DictPijltjes['right'])

def punten(amount):         #Voorziet punten (WIP)
    global PP1
    global PP2
    global PP3
    global PP4
    if playeringame == 1:
        PP1 += amount
    if playeringame == 2:
        PP2 += amount
    if playeringame == 3:
        PP3 += amount
    if playeringame == 4:
        PP4 += amount
    print("Ball in game:", ballingame)
    print("Player in game:", playeringame)
    print("Punten Speler 1:", PP1)
    print("Punten Speler 2:", PP2)
    print("Punten Speler 3:", PP3)
    print("Punten Speler 4:", PP4)

def randomtoplights():      #Maakt de lampjes willekeurig
    global Dict30yardswlit 
    print("randomtoplights")
    Dict30yardswlit['1'] = random.randint(0, 1)
    Dict30yardswlit['2'] = random.randint(0, 1)
    Dict30yardswlit['3'] = random.randint(0, 1)
    Dict30yardswlit['4'] = random.randint(0, 1)

#####################################
#Algemene Functies
#####################################
def debug(code):        #Leest elke adres van een bepaalde IC uit
    for i in [O_IPOLA, O_IPOLB, O_GPINTENA, O_GPINTENB, O_DEFVALA, O_DEFVALB, O_INTCONA, O_INTCONB, O_GPPUA, O_GPPUB, O_INTFA, O_INTFB, O_INTCAPA, O_INTCAPB, O_GPIOA, O_GPIOB, O_OLATA, O_OLATB]:
        print(code, i, "=", readSPI(code, i)) 

def walkinglight(opcode, addr, speed):     #Om alle lampjes te testen
    for i in range(0,8):                    #8 not inclusive
        listwalk = [1, 1, 1, 1, 1, 1, 1, 1] 
        listwalk[i] = 0 
        sendSPI(opcode, addr, mkhex(listwalk))
        print(opcode, addr, i)
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

def setlites(): #Compiles 6 lists, one for each address on each chip (2*3) and sends it to the chip
    list0x40A = [DictSingleyards['yard1'], DictSingleyards['yard2'], DictSingleyards['yard3'], DictSingleyards['yard4'], DictSingleyards['yard5'], DictSingleyards['yard6'], DictSingleyards['yard7'], DictSingleyards['yard8']]
    list0x40B = [DictSingleyards['yard9'], DictSingleyards['yard10'], DictDecayards['yardsleft'],  DictDecayards['yards10'], DictDecayards['yards20'], DictDecayards['yards30'], DictDecayards['yards40'], DictDecayards['yards50']]
    list0x42A = [DictDecayards['yards-40'], DictDecayards['yards-30'], DictDecayards['yards-20'], DictDecayards['yards-10'], DictDecayards['yardsright'], DictPijltjes['right'], DictPijltjes['left'], DictGoalscores['5000']]
    list0x42B = [DictGoalscores['extra ball'], DictGoalscores['special'], DictLTDscores['goal'], DictLTDscores['special'], DictBonus['4000'], DictBonus['5000'], DictBonus['6000'], DictBonus['7000']] 
    list0x44A = [DictBonus['1000'], DictBonus['2000'], DictBonus['3000'], Dict30yardswlit['1'], Dict30yardswlit['3'], Shootagain, 1, 1]
    list0x44B = [DictBonus['9000'], DictBonus['10000'], DoubleBonus, DictBonus['8000'], Dict30yardswlit['2'], Dict30yardswlit['4'], Kicker, 1]
     
    hex0x40A = mkhex(list0x40A)
    hex0x40B = mkhex(list0x40B)
    hex0x42A = mkhex(list0x42A)
    hex0x42B = mkhex(list0x42B)
    hex0x44A = mkhex(list0x44A)
    hex0x44B = mkhex(list0x44B)
    
#    print(hex0x40A)
#    print(hex0x40B)
#    print(hex0x42A)
#    print(hex0x42B)
#    print(hex0x44A)
#    print(hex0x44B)
    sendSPI(0x40, O_GPIOA, hex0x40A) 
    sendSPI(0x40, O_GPIOB, hex0x40B) 
    sendSPI(0x42, O_GPIOA, hex0x42A) 
    sendSPI(0x42, O_GPIOB, hex0x42B) 
    sendSPI(0x44, O_GPIOA, hex0x44A) 
    sendSPI(0x44, O_GPIOB, hex0x44B) 
    
    
if __name__ == '__main__':
        Scan=Feeler(10,game)    #Detects a change in inputs, if it's set to a certain state for longer than "30" counts it executes "game"
        main()                  #Main loop
 
