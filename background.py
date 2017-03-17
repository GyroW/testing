import tkinter
HOOGTE = 500
BREEDTE = 1000
venster = tkinter.Tk()
c = tkinter.Canvas(venster, width=BREEDTE, height=HOOGTE, bg='black')
image = tkinter.PhotoImage(file = 'giphy.gif')
c.create_image(10, 10, image = image, anchor = 'nw')
c.pack()
#score voor speler 1
c.create_text(30, 10, text='SCORE 1', fill='white')
def toon_score_1(score):
    c.itemconfig(score_text, text=str(score))
#score voor speler 2
c.create_text(950, 10, text='SCORE 2', fill='white')
def toon_score_2(score):
    c.itemconfig(score_text, text=str(score))
#score voor speler 3
c.create_text(30, 250, text='SCORE 3', fill='white')
def toon_score_1(score):
    c.itemconfig(score_text, text=str(score))
#score voor speler 4
c.create_text(950, 250, text='SCORE 4', fill='white')
def toon_score_4(score):
    c.itemconfig(score_text, text=str(score))


venster.mainloop()
