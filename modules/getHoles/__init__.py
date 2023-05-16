import cv2

import numpy as np
import copy

def crop_img(img, contour):   #Helper function full_contour
    x, y, w, h = cv2.boundingRect(contour)
    roi = img[y:y + h, x:x + w]
    return roi

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