import tkinter
from tkinter.messagebox import *
import ezdxf

import sys

from modules import *

def empty_layer_check(layer):   #Helper function auto_check
    if (layer.get("line")=={} and layer.get("arc")=={} and layer.get("circle")=={}):
        return (True)
    else:
        return(False)
    
def auto_check(cad,shape_canva):   #Controllo del file CAD
    controllo_cad=ezdxf.readfile(cad)
    recognised_layers=[]
    empty_layers=[]
    unrecognised_layers=[]
    mandatory_layers=['TAGLIO4PT','CORDONATORE4PT']
    working_layers=["T",'TAGLIO4PT','CORDONATORE4PT','PERFORATORE4PT','TC4PT']
    common_layers=["QUOTE","Defpoints","DEFPOINTS"]
    for layer in controllo_cad.layers:   #Costruzione lista layer riconosciuti e non riconosciuti
        if layer.dxf.name in working_layers:
            recognised_layers.append(layer.dxf.name)
        if layer.dxf.name not in common_layers and layer.dxf.name not in working_layers:
            unrecognised_layers.append(layer.dxf.name)

    if all(elem in recognised_layers for elem in mandatory_layers)==False:  #Controllo mancanza layer fondamentali e/o presenza layer estranei
        if len(unrecognised_layers)!=0:
            showinfo('Errore Layer', 'Mancanza dei layer TAGLIO4PT o CORDONATORE4PT, essenziali per la costruzione della scatola.\nPresenza dei layer: '+str(unrecognised_layers)+" non riconosciuti dal programma")
            sys.exit()
        showinfo('Errore Layer','Mancanza dei layer TAGLIO4PT o CORDONATORE4PT, essenziali per la costruzione della scatola.\nControllare eventuali errori di battitura')
        sys.exit()
    if empty_layer_check(tagli) == True:
        showinfo("Attenzione","Il layer TAGLI4PT è vuoto, è necessario per la costruzione della scatola")
        sys.exit()
    if empty_layer_check(pieghe) == True:
        showinfo("Attenzione","Il layer CORDONATORE4PT è vuoto, è necessario per la costruzione della scatola")
        sys.exit()
    for i in shape_canva:
        if i<1:
            showerror('Errore dimensioni', 'Dimensioni del cad negative ' + str(shape_canva))
            sys.exit()
    #Fine parte automatica
    #Controllo guidato
    msg_box_dimensioni=askquestion('Dimensioni scatola', str('Controllo iniziale automatico completato.\nLe dimensioni della scatola ('+str(shape_canva[0])+"x"+str(shape_canva[1])+') sono corrette?'))
    if msg_box_dimensioni=="no":                                            #Controllo da parte dell'operatore su dimensioni
        showerror('Errore dimensioni', 'Controllare eventuali linee che fuoriescono dal bordo del disegno')
        sys.exit()
    #Inizio controllo guidato layer
    
    str_box = ""

    if "PERFORATORE4PT" in recognised_layers:  #Controllo layer presenti ma vuoti
        if empty_layer_check(perforatore) == True:
            recognised_layers.remove("PERFORATORE4PT")
            empty_layers.append("PERFORATORE4PT")
    if "TC4PT" in recognised_layers:
        if empty_layer_check(tagliacordone) == True:
            recognised_layers.remove("TC4PT")
            empty_layers.append("TC4PT")
    if empty_layer_check(perforatore) == False and empty_layer_check(tagliacordone) == False:
        pass
    else:
        str_box = str_box +("Layer riconosciuti non vuoti: " + str(recognised_layers) + "\n")
    
    if len(empty_layers)!=0:
        str_box = str_box + ("Layer riconosciuti ma vuoti: " + str(empty_layers) + "\n")
    if len(unrecognised_layers)!=0:
        str_box = str_box + ("Layer non riconosciuti: "+str(unrecognised_layers)+"\n")    
    
    msg_box_layer_riconosciuti=askquestion("Controllo layer",str_box)
    if msg_box_layer_riconosciuti == "no":
        tkinter.showerror("Errore layer","Controllare denominazione layer")
        sys.exit()
    return recognised_layers

recognised_layers = auto_check(cad, shape_canva)