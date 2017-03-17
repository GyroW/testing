from  Tkinter import *
import time 
xpadding = 600
ypadding = 300
fontsize = 70
playeringame = 1
#colours and font
textcolour      ='#00468B'
textfont        ='Helvetica'
activecolour    ='#FFDE00'
inactivecolour  ='#149CD8'

gui = Tk()
i = StringVar() 
#w, h = gui.winfo_screenwidth(), gui.winfo_screenheight()
#gui.overrideredirect(1)
#gui.geometry("%dx%d+0+0" % (w, h))
bgimage = PhotoImage(file = 'background.gif')
x = Label(image=bgimage) 
x.place(x=0, y=0, relwidth=1, relheight=1)

Speler1 = Label(text='Speler 1', fg=textcolour, font=(textfont, fontsize))
Speler2 = Label(text='Speler 2', fg=textcolour, font=(textfont, fontsize))
Speler3 = Label(text='Speler 3', fg=textcolour, font=(textfont, fontsize))
Speler4 = Label(text='Speler 4', fg=textcolour, font=(textfont, fontsize))

Speler1.grid(row=0,column=0, sticky=E)
Speler2.grid(row=0,column=2, sticky=W, padx=xpadding)
Speler3.grid(row=2,column=0, sticky=E, )
Speler4.grid(row=2,column=2, sticky=W, padx=xpadding)


#print(c.winfo_height(), c.winfo_width())

def func():
    global playeringame
    i.set(int(input()))
    
def task():
    

    print(playeringame)
    if playeringame == 1:
        VPP1 = Label(textvariable=i, fg=activecolour,      font=(textfont, fontsize))
    else:
        VPP1 = Label(textvariable=i, fg=inactivecolour,    font=(textfont, fontsize))
    if playeringame == 2:
        VPP2 = Label(textvariable=i, fg=activecolour,      font=(textfont, fontsize))
    else:
        VPP2 = Label(textvariable=i, fg=inactivecolour,    font=(textfont, fontsize))
    if playeringame == 3:
        VPP3 = Label(textvariable=i, fg=activecolour,      font=(textfont, fontsize))
    else:
        VPP3 = Label(textvariable=i, fg=inactivecolour,    font=(textfont, fontsize))
    if playeringame == 4:
        VPP4 = Label(textvariable=i, fg=activecolour,      font=(textfont, fontsize))
    else:
        VPP4 = Label(textvariable=i, fg=inactivecolour,    font=(textfont, fontsize))

    VPP1.grid(row=1,column=0, pady=(0,ypadding))
    VPP2.grid(row=1,column=2, pady=(0,ypadding))
    VPP3.grid(row=3,column=0)
    VPP4.grid(row=3,column=2)
#    gui.update_idletasks()
#    gui.update()
#    
    func() 
#       
#    VPP1.destroy() 
#    VPP2.destroy()
#    VPP3.destroy()
#    VPP4.destroy()
#    gui.update_idletasks()
#    gui.update()

while 1:
    task()

