yardsdirection = 0  
yards = 0
yardsten = 0
def toBinary(getal):
    binair = str("{0:b}".format(getal))
    length = 8 - len(binair)
    binair = ('0' * length + binair)
    return list(map(int, list(binair)))
def binToHex(lijst):
    string = ''.join(map(str, lijst))
    return hex(int(string, 2))
def toggle(lamp):
    state = toBinary(0)
    if state[lamp] == 0:
        state[lamp] = 1
    elif state[lamp] == 1:
        state[lamp] = 0
    return state
def changeyardsdirection():
    global yardsdirection
    if yardsdirection == 0:
        yardsdirection = 1
    elif yardsdirection == 1:
        yarddirection = 0
def     yard(amount):
            global yardsdirection                       #Stel: we beginnen met yards 0 en yardsten 0
            global yards                                #We scoren 30 yards met yard(30)
            global yardsten                             #
            if yardsdirection == 0:                     #
                    yards = yards + amount              #
            elif yardsdirection == 1:                   #
                    yards = yards - amount              #
            while yards > 10:
                    yardsten = yardsten + 1
                    yards = yards - 10
            if yards < 0:
                    yards = 0
            print(yards)
            print(yardsten)
print(toBinary(85))

