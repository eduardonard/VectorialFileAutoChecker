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