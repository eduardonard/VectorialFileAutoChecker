import cv2
import numpy as np
import math

from modules.geometry import *

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

def resized_drawing(what, shape_canva, resized_shape_canva):   ##Ridimensionamento disegno per risoluzione standard
    return(cv2.resize(draw_elem(what, (shape_canva[0]+10,shape_canva[1]+10)), resized_shape_canva, interpolation=cv2.INTER_NEAREST))