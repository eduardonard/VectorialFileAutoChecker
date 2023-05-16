from tkinter import *
from tkinter.messagebox import *

from modules import *
from modules.autoCheck import *
from modules.getHoles import *
from modules.menu import *



def dialog():   #Costruzione del menu per l'utente
    root=Tk()
    root.geometry("200x200")


    tagli_canva = resized_drawing(tagli, shape_canva, resized_shape_canva)
    pieghe_canva = resized_drawing(pieghe, shape_canva, resized_shape_canva)
    perforatore_canva = resized_drawing(perforatore, shape_canva, resized_shape_canva)
    tagliacordone_canva = resized_drawing(tagliacordone, shape_canva, resized_shape_canva)
    tutto_canva = cv2.bitwise_or(tagli_canva, pieghe_canva)
    tutto_canva = cv2.bitwise_or(tutto_canva, perforatore_canva)
    tutto_canva = cv2.bitwise_or(tutto_canva, tagliacordone_canva)

    tagli_button=Button(root, text="tagli",state=NORMAL,command=lambda:cv2.imshow("tagli", tagli_canva))
    pieghe_button=Button(root, text="pieghe",state=NORMAL,command=lambda:cv2.imshow("pieghe", pieghe_canva))
    if "PERFORATORE4PT" in recognised_layers:
        perforatore_button=Button(root, text="perforatore",state=NORMAL,command=lambda:cv2.imshow("perforatore", perforatore_canva))
    else:
        perforatore_button=Button(root, text="perforatore",state=NORMAL,command=lambda: showinfo("Errore","Il layer è vuoto"))
    if "TC4PT"  in recognised_layers:
        tc_button=Button(root, text="tagliacordone",state=NORMAL,command=lambda:cv2.imshow("taglia cordone", tagliacordone_canva))
    else:
        tc_button=Button(root, text="tagliacordone",state=NORMAL,command=lambda: showinfo("Errore","Il layer è vuoto"))
    tutto_button=Button(root, text="tutto",state=NORMAL,command=lambda:cv2.imshow("tutto", tutto_canva))
    taglifill_button=Button(root, text="taglifill",state=NORMAL,command=lambda:cv2.imshow("tagli fill", tagli_fill_canva))
    buchi_button = Button(root, text="Controllo buchi",state=NORMAL,command=lambda:holes_check(tagli_canva, shape_canva, tagli))

    tagli_button.pack(side=TOP,fill=X)
    pieghe_button.pack(side=TOP,fill=X)
    perforatore_button.pack(side=TOP,fill=X)
    tc_button.pack(side=TOP,fill=X)
    tutto_button.pack(side=BOTTOM,fill=X)
    taglifill_button.pack(side=BOTTOM,fill=X)
    buchi_button.pack(side=BOTTOM,fill=X)
    root.mainloop()