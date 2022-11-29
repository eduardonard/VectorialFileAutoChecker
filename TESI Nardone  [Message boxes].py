from tkinter import Canvas
from tkinter import messagebox
from tkinter import *
import tkinter
import cv2
import ezdxf
import numpy as np
import copy
from glob import glob
import math
import sys

def getMinXY(shapes,max_pt):   #Coordinata minima del layer con denominazione alfabetica
    minX, minY = 99999, 99999
    for e in shapes:
        if e.dxftype() == 'LINE' and e.dxf.layer.isdigit() == False:
            if e.dxf.start[0] > max_pt.dxf.end[0] and e.dxf.end[0] > max_pt.dxf.end[0]:
                minX = min(minX, e.dxf.start[0])
                minX = min(minX, e.dxf.end[0])
                minY = min(minY, e.dxf.start[1])
                minY = min(minY, e.dxf.end[1])
        elif e.dxftype == 'ARC' and e.dxf.layer.isdigit() == False:
            if e.start_point[0]>max_pt.dxf.end[0] and e.end_point[0]>max_pt.dxf.end[0]:
                minX = min(minX, e.dxf.center[0])
                minY = min(minY, e.dxf.center[1])
    return minX, minY

def getMaxXY(shapes,max_pt):   #Coordinata massima del layer con denominazione alfabetica
    maxX, maxY = -99999, -99999
    for e in shapes:
        if e.dxftype() == 'LINE' and e.dxf.layer.isdigit() == False:
            if e.dxf.start[0] > max_pt.dxf.end[0] and e.dxf.end[0] > max_pt.dxf.end[0]:
                maxX = max(maxX, e.dxf.start[0])
                maxX = max(maxX, e.dxf.end[0])
                maxY = max(maxY, e.dxf.start[1])
                maxY = max(maxY, e.dxf.end[1])
        elif e.dxftype == 'ARC' and e.dxf.layer.isdigit() == False:
            if e.start_point[0] > max_pt.dxf.end[0] and e.end_point[0] > max_pt.dxf.end[0]:
                maxX = max(maxX, e.dxf.center[0])
                maxY = max(maxY, e.dxf.center[1])
    return maxX, maxY

def getXY(point, base):   #Helper function
    x, y = point[0], point[1]
    return int(absdiff(x, base[0])), int(absdiff(y, base[1]))

def absdiff(num1, num2):  #Helper function
    if num1 <= num2:
        return num2 - num1
    else:
        return num1 - num2

def get_ids(msp, baseX, baseY, max_pt, layer, nome):  #Costruzione dizionario degli elementi che compongono il disegno
    line = {}
    arc = {}
    circle = {}
    n = 0
    for e in msp:
        if e.dxftype() == 'LINE' and layer in e.dxf.layer:
            if e.dxf.start[0] >= max_pt.dxf.end[0] and e.dxf.end[0] >= max_pt.dxf.end[0]:
                x1, y1 = getXY(e.dxf.start, (baseX, baseY))
                x2, y2 = getXY(e.dxf.end, (baseX, baseY))
                id_elem = nome+"_"+str(n)
                n+=1
                line[id_elem] = [x1, y1, x2, y2]
        if e.dxftype() == 'ARC' and layer in e.dxf.layer:
            if e.start_point[0] >= max_pt.dxf.end[0] and e.end_point[0] >= max_pt.dxf.end[0]:
                centerX, centerY = getXY(e.dxf.center, (baseX, baseY))
                radius = int(e.dxf.radius)
                start_angle = int(e.dxf.start_angle)
                end_angle = int(e.dxf.end_angle)
                id_elem = nome+"_"+str(n)
                n+=1
                arc[id_elem] = [centerX, centerY, radius, start_angle, end_angle]
        if e.dxftype() == 'CIRCLE' and layer in e.dxf.layer:
            n += 1
            if e.dxf.center[0] >= max_pt.dxf.end[0]:
                centerX, centerY = getXY(e.dxf.center, (baseX, baseY))
                radius = int(e.dxf.radius)
                id_elem = nome+"_"+str(n)
                n+=1
                circle[id_elem] = [centerX, centerY, radius]
    info = {"line":line, "arc":arc, "circle":circle}
    return info

def get_id_general(shape):   #Helper function
    h, w = shape
    general = {
        'line': {
            'separation': [int(w//2),0,int(w//2),int(h-1)],
            'generic': [0,0,0,0]
        },
        'arc': {},
        'circle': {}
    }
    return general

def get_id_elems(path):   #Definizione del dominio nel quale si ricercano gli elementi del CAD
    cad = ezdxf.readfile(path)
    msp = cad.modelspace()

    if 'T' not in cad.layers:
        count = 0
        for e in msp:
            if e.dxftype() == 'LINE':
                if count == 0:
                    max_pt = e
                elif e.dxf.end[0] < max_pt.dxf.end[0]:
                    max_pt = e
                    # print_entity(e)
                count+=1
    else:
        # calcolo dal layer T il punto minimo di X che devono avere gli attributi da estrarre
        entities = msp.query('LINE[layer=="T"]')
        count = 0
        for e in entities:
            if e.dxftype() == 'LINE':
                if count==0:
                    max_pt = e
                elif e.dxf.end[0] > max_pt.dxf.end[0]:
                    max_pt = e
                # print_entity(e) # print information about entity in dxf (lines)
            count+=1

    # estraggo info su coordinate della parte di CAD da salvare
    minX, minY = getMinXY(msp, max_pt)
    maxX, maxY = getMaxXY(msp, max_pt)
    baseX, baseY = minX, minY
    absMaxX, absMaxY = absdiff(maxX, 0), absdiff(maxY, 0)
    shape_canva = (int(maxY-minY)+1, int(maxX-minX)+1)

    ##############################################################
    # plot del cad in base alle informazioni raccolte
    tagli = get_ids(msp, baseX, baseY, max_pt, 'TAGLIO4PT', 'cut')
    pieghe = get_ids(msp, baseX, baseY, max_pt, 'CORDONATORE4PT', 'fold')
    perforatore = get_ids(msp, baseX, baseY, max_pt, 'PERFORATORE4PT', 'perf')
    tagliacordone = get_ids(msp, baseX, baseY, max_pt, 'TC4PT', 'cutfold')
    #general = get_id_general(shape_canva)
    general = { "general":{
            str(-1): [], #altezza_cartone
            str(-2): [], #larghezza_cartone
            str(-3): None,
            str(-4): None,
            str(-5): None,
        }
    }

    return tagli, pieghe, perforatore, tagliacordone, general, shape_canva

def draw_elem(cad_elem, shape):   #Funzione disegnatrice
    canvas = np.zeros((shape[0], shape[1], 3), np.uint8)
    for elem, info in cad_elem["line"].items():
        x1, y1, x2, y2 = info
        canvas = cv2.line(canvas, (x1, y1), (x2, y2), (255, 255, 255), 2)
    for elem, info in cad_elem["arc"].items():
        centerX, centerY, radius, start_angle, end_angle = info
        if start_angle > 180 and end_angle < start_angle:
            canvas = cv2.ellipse(canvas, (centerX, centerY), (radius, radius), 180,
                                    start_angle - 180, 180 + end_angle, (255, 255, 255), 2)
        else:
            canvas = cv2.ellipse(canvas, (centerX, centerY), (radius, radius), 0,
                                    start_angle, end_angle, (255, 255, 255), 2)
    for elem, info in cad_elem["circle"].items():
        centerX, centerY, radius = info
        canvas = cv2.circle(canvas, (centerX, centerY), radius, (255, 255, 255), 2)
    return canvas

def crop_img(img, contour):   #Helper function full_contour
    x, y, w, h = cv2.boundingRect(contour)
    roi = img[y:y + h, x:x + w]
    return roi

def filter_contours(cnt):   #Helper function full_contour
    filtered=[]
    for c in cnt:
        circle = cv2.minEnclosingCircle(c)
        len_circle = math.pi * circle[1] * circle[1]
        len_area = cv2.contourArea(c)
        if len_area > 300 or abs(len_area-len_circle) < 50:
            filtered.append(c)
    return filtered

def fill_contours(ref):   #Crea il disegno per il controllo dei contorni
    gray_ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
    _, thresh_ref = cv2.threshold(gray_ref, 140, 255, cv2.THRESH_BINARY)
    contours_ref, _ = cv2.findContours(thresh_ref, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours_ref = filter_contours(contours_ref)
    cv2.drawContours(ref, contours_ref, 0, (255,255,255), thickness=cv2.FILLED) #draw only those having area > 300
    for c in contours_ref:
        if cv2.contourArea(c) < 35000:
            cv2.drawContours(ref, [c], 0, (0,0,0), thickness=cv2.FILLED)
    return ref

def get_holes_contour(ref):   #Helper function full_contour
    gray_ref = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
    _, thresh_ref = cv2.threshold(gray_ref, 140, 255, cv2.THRESH_BINARY)
    contours_ref, _ = cv2.findContours(thresh_ref, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    crop_ref = crop_img(ref, contours_ref[0])

    gray_ref = cv2.cvtColor(crop_ref, cv2.COLOR_BGR2GRAY)
    _, thresh_ref = cv2.threshold(gray_ref, 140, 255, cv2.THRESH_BINARY)
    contours_ref, _ = cv2.findContours(thresh_ref, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(crop_ref, contours_ref, -1, (0, 255, 0), 2)

    return contours_ref

def drawRect(rect, i, image, color):   #Helper function holes_check
    box = np.int0(cv2.boxPoints(rect))
    cv2.drawContours(image, [box], 0, color, thickness=cv2.FILLED)
    cv2.putText(image, i, (int(rect[0][0]),int(rect[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,0), 1)
    
def drawRectbin(rect, i, image, color):   #Helper function holes_check
    box = np.int0(cv2.boxPoints(rect))
    cv2.drawContours(image, [box], 0, (0,0,255), 2)
    cv2.putText(image, str(i), (int(rect[0][0]),int(rect[0][1])), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 1)

def get_holes_id(contours, canva):   #Helper function holes_check
    new_canva = canva.copy()
    n = len(contours) - 1
    holes = {}
    
    i = 1
    while i <= n:
        center, size, angle = cv2.minAreaRect(contours[i])
        id_text = "buco_"+str(i)
        holes[id_text] = [center, (size[0]+1, size[1]+1), angle] #1
        rect = [center, size, angle]
        drawRectbin(rect, i, new_canva, 255)
        i+=1
    cv2.imshow("outputrect", new_canva)
    cv2.waitKey(0)

    return holes

def check_canva_black(canva):   #Helper function holes_check
    if np.mean(canva) == 0.0:
        return True
    else:
        return False

def get_elem_of_holes(holes, tagli, shape):   #Helper function holes_check
    canva = np.zeros((shape[0], shape[1], 3), np.uint8)
    holes_con_elem = {}
    for buco, info in holes.items():
        center, size, angle = info
        line = []
        arc = []
        circle = []
        for elem, info_elem in tagli["line"].items():
            x1,y1,x2,y2 = info_elem
            cv2.line(canva, (x1,y1), (x2,y2), (255, 255, 255), 1)
            drawRect((center, size, angle), "", canva, (0,0,0))
            if check_canva_black(canva):
                line.append(elem)
            canva = np.zeros_like(canva)
        for elem, info_elem in tagli["arc"].items():
            centerX, centerY, radius, start_angle, end_angle = info_elem
            if start_angle > 180 and end_angle < start_angle:
                cv2.ellipse(canva, (centerX, centerY), (radius, radius), 180,
                                        start_angle - 180, 180 + end_angle, (255, 255, 255), 1)
            else:
                cv2.ellipse(canva, (centerX, centerY), (radius, radius), 0,
                                        start_angle, end_angle, (255, 255, 255), 1)
            drawRect((center, size, angle), "", canva, (0,0,0))
            if check_canva_black(canva):
                arc.append(elem)
            canva = np.zeros_like(canva)
        for elem, info_elem in tagli["circle"].items():
            centerX, centerY, radius = info_elem
            cv2.circle(canva, (centerX, centerY), radius, (255, 255, 255), 1)
            drawRect((center, size, angle), "", canva, (0,0,0))
            if check_canva_black(canva):
                circle.append(elem)
            canva = np.zeros_like(canva)
        holes_con_elem[buco] = {"line":line, "arc":arc, "circle":circle}
    return holes_con_elem

def get_elem_of_contour(contours, holes, tagli, holes_elem):   #Helper function holes_check
    contorno = contours[0]
    center, size, angle = cv2.minAreaRect(contorno)

    cut_non_utilizzati = copy.deepcopy(tagli)

    for buco, info in holes_elem.items():
        for type_elem, cuts in info.items():
            for cut in cuts:
                if cut in cut_non_utilizzati[type_elem]:
                    cut_non_utilizzati[type_elem].pop(cut)

    line = []
    arc = []
    circle = []
    for type_elem, cuts in cut_non_utilizzati.items():
        if type_elem == "line":
            for cut in cuts:
                line.append(cut)
        if type_elem == "arc":
            for cut in cuts:
                arc.append(cut)
        if type_elem == "circle":
            for cut in cuts:
                circle.append(cut)
    holes_elem["buco_0"] = {"line":line, "arc":arc, "circle":circle}
    
    holes["buco_0"] = [center, size, angle]

def check_elem_holes(shape, holes, tagli, holes_elem):   #Helper function holes_check
    for buco, info in holes_elem.items():
        canva = np.zeros((shape[0], shape[1], 3), np.uint8)
        center, size, angle = holes[buco]
        drawRect((center, size, angle), buco, canva, (0,0,255))
        for type_elem, cuts in info.items():
            for cut in cuts:
                if type_elem == "line":
                    x1, y1, x2, y2 = tagli[type_elem][cut]
                    cv2.line(canva, (x1, y1), (x2, y2), (255,255,255), 1)
                if type_elem == "arc":
                    centerX, centerY, radius, start_angle, end_angle = tagli[type_elem][cut]
                    if start_angle > 180 and end_angle < start_angle:
                        cv2.ellipse(canva, (centerX, centerY), (radius, radius), 180,
                                                start_angle - 180, 180 + end_angle, (255, 255, 255), 1)
                    else:
                        cv2.ellipse(canva, (centerX, centerY), (radius, radius), 0,
                                                start_angle, end_angle, (255, 255, 255), 1)
                if type_elem == "circle":
                    centerX, centerY, radius = tagli[type_elem][cut]
                    cv2.circle(canva, (centerX, centerY), radius, (255, 255, 255), 1)
        cv2.imshow("check", canva)
        cv2.waitKey(0)

def holes_check(tagli_canva, shape_canva, tagli):
    contours = get_holes_contour(tagli_canva) #get contours dei holes del cad  
    cv2.waitKey()
    holes = get_holes_id(contours, tagli_canva) #costruisco gli id dei holes, id="buco_X", info sono i risultati di minarearect
    #holes_elem = get_elem_of_holes(holes, tagli, shape_canva) #ricavo gli elementi di taglio relativi ai holes
    #get_elem_of_contour(contours, holes, tagli, holes_elem) #ricavo gli elementi di taglio relativi al contorno, aggiunge un elemento a holes_elem
    #check_elem_holes(shape_canva, holes, tagli, holes_elem)  

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
            tkinter.messagebox.showinfo('Errore Layer', 'Mancanza dei layer TAGLIO4PT o CORDONATORE4PT, essenziali per la costruzione della scatola.\nPresenza dei layer: '+str(unrecognised_layers)+" non riconosciuti dal programma")
            sys.exit()
        tkinter.messagebox.showinfo('Errore Layer','Mancanza dei layer TAGLIO4PT o CORDONATORE4PT, essenziali per la costruzione della scatola.\nControllare eventuali errori di battitura')
        sys.exit()
    if empty_layer_check(tagli) == True:
        tkinter.messagebox.showinfo("Attenzione","Il layer TAGLI4PT è vuoto, è necessario per la costruzione della scatola")
        sys.exit()
    if empty_layer_check(pieghe) == True:
        tkinter.messagebox.showinfo("Attenzione","Il layer CORDONATORE4PT è vuoto, è necessario per la costruzione della scatola")
        sys.exit()
    for i in shape_canva:
        if i<1:
            tkinter.messagebox.showerror('Errore dimensioni', 'Dimensioni del cad negative ' + str(shape_canva))
            sys.exit()
    #Fine parte automatica
    #Controllo guidato
    msg_box_dimensioni=tkinter.messagebox.askquestion('Dimensioni scatola', str('Controllo iniziale automatico completato.\nLe dimensioni della scatola ('+str(shape_canva[0])+"x"+str(shape_canva[1])+') sono corrette?'))
    if msg_box_dimensioni=="no":                                            #Controllo da parte dell'operatore su dimensioni
        tkinter.messagebox.showerror('Errore dimensioni', 'Controllare eventuali linee che fuoriescono dal bordo del disegno')
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
    
    msg_box_layer_riconosciuti=tkinter.messagebox.askquestion("Controllo layer",str_box)
    if msg_box_layer_riconosciuti == "no":
        tkinter.showerror("Errore layer","Controllare denominazione layer")
        sys.exit()
    
    return recognised_layers
    
def resizing_canva(shape_canva):   #Ridimensionamento finestra per risoluzione standard
    resized_shape_canva=shape_canva
    while resized_shape_canva[0]>900 or resized_shape_canva[1]>900:
        resized_shape_canva=(resized_shape_canva[0]//2,resized_shape_canva[1]//2)
    resized_shape_canva=(resized_shape_canva[1],resized_shape_canva[0])
    return resized_shape_canva

def menu(tagli_canva, pieghe_canva, perforatore_canva, tagliacordone_canva,tutto_canva):   #Costruzione del menu per l'utente
    root=Tk()
    root.geometry("200x200")
    tagli_button=Button(root, text="tagli",state=NORMAL,command=lambda:cv2.imshow("tagli", tagli_canva))
    pieghe_button=Button(root, text="pieghe",state=NORMAL,command=lambda:cv2.imshow("pieghe", pieghe_canva))
    if "PERFORATORE4PT" in recognised_layers:
        perforatore_button=Button(root, text="perforatore",state=NORMAL,command=lambda:cv2.imshow("perforatore", perforatore_canva))
    else:
        perforatore_button=Button(root, text="perforatore",state=NORMAL,command=lambda:tkinter.messagebox.showinfo("Errore","Il layer è vuoto"))
    if "TC4PT"  in recognised_layers:
        tc_button=Button(root, text="tagliacordone",state=NORMAL,command=lambda:cv2.imshow("taglia cordone", tagliacordone_canva))
    else:
        tc_button=Button(root, text="tagliacordone",state=NORMAL,command=lambda:tkinter.messagebox.showinfo("Errore","Il layer è vuoto"))
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

def resized_drawing(what, shape_canva, resized_shape_canva):   ##Ridimensionamento disegno per risoluzione standard
    return(cv2.resize(draw_elem(what, (shape_canva[0]+10,shape_canva[1]+10)), resized_shape_canva, interpolation=cv2.INTER_NEAREST))

if len(sys.argv)!=2: #Errore Drag and Drop
    tkinter.messagebox.showerror('Errore drag and drop', 'Per controllare il file eseguire un drag and drop sul programma python\nControllare inoltre che il formato sia .dxf')
    sys.exit()

cads = glob(sys.argv[1])  #Input del disegno

for cad in cads:
    print("Controllo automatico del file ",cad)
    tagli, pieghe, perforatore, tagliacordone, general, shape_canva = get_id_elems(cad)
    recognised_layers=auto_check(cad, shape_canva)

    resized_shape_canva=resizing_canva(shape_canva)

    tagli_canva = resized_drawing(tagli, shape_canva, resized_shape_canva)
    pieghe_canva = resized_drawing(pieghe, shape_canva, resized_shape_canva)
    perforatore_canva = resized_drawing(perforatore, shape_canva, resized_shape_canva)
    tagliacordone_canva = resized_drawing(tagliacordone, shape_canva, resized_shape_canva)
    tutto_canva = cv2.bitwise_or(tagli_canva, pieghe_canva)
    tutto_canva = cv2.bitwise_or(tutto_canva, perforatore_canva)
    tutto_canva = cv2.bitwise_or(tutto_canva, tagliacordone_canva)
    tagli_fill_canva = cv2.resize(fill_contours(draw_elem(tagli, shape_canva)), resized_shape_canva, interpolation=cv2.INTER_NEAREST)
    menu(tagli_canva, pieghe_canva, perforatore_canva, tagliacordone_canva,tutto_canva)