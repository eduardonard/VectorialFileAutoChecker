from tkinter import *
from tkinter.messagebox import *

from modules import *
from modules.autoCheck import *
from modules.getHoles import *

def resizing_canva(shape_canva):   #Ridimensionamento finestra per risoluzione standard
    resized_shape_canva=shape_canva
    while resized_shape_canva[0]>900 or resized_shape_canva[1]>900:
        resized_shape_canva=(resized_shape_canva[0]//2,resized_shape_canva[1]//2)
    resized_shape_canva=(resized_shape_canva[1],resized_shape_canva[0])
    return resized_shape_canva

tagli_fill_canva = cv2.resize(fill_contours(draw_elem(tagli, shape_canva)), resizing_canva(shape_canva), interpolation=cv2.INTER_NEAREST)
resized_shape_canva=resizing_canva(shape_canva)
