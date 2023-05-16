import ezdxf

from modules.geometry import *
from modules.draw import *

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