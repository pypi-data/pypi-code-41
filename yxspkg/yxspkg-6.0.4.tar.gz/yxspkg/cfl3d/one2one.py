import numpy as np
import math
#blocks is a list,the info of face include block id, the id start from 0 not 1
def to_fortran_format(func):
    def deal_r(r):
        a = [(i[0]+1,i[1]+1) for i in r[:-2]]
        a.extend((r[-2]+1,r[-1]+1))
        return a
    def wrap_func(*d,**k):
        a = func(*d,**k)
        if a is not None:
            a = [deal_r(i)  for i in a]
        return a
    return wrap_func
def is_equal_face(face1,face2,res = 1e-3):
    x1,y1,z1 = face1
    x2,y2,z2 = face2
    if x1.shape != x2.shape:
        return False
    if (np.abs(x1-x2).max() < res).all() and (np.abs(y1-y2).max() < res).all() and (np.abs(z1-z2).max() < res).all():
        return True 
    else:
        return False

def is_parallel_face(face1,face2,res = 1e-3):
    x1,y1,z1 = face1
    x2,y2,z2 = face2
    dx = np.abs(x1-x2)
    dy = np.abs(y1-y2)
    dz = np.abs(z1-z2)
    if (dx.max() - dx.min() < 2*res).all() and (dy.max() - dy.min()< 2*res).all() and (dz.max()-dz.min() < 2*res).all():
        return True 
    else:
        return False

def is_rotated_face(face1,face2,res = 1e-3):
    x1,y1,_ = face1
    x2,y2,_ = face2
    dx  = (x1*x2+y1*y2)/(np.sqrt(x1*x1+y1*y1)*np.sqrt(x2*x2+y2*y2))
    if (dx.max() - dx.min() < 0.02*res).all():
        return True 
    else:
        return False

def is_equal_point(p1,p2,res = 1e-3):
    x1, y1, z1 = p1 
    x2, y2, z2 = p2
    m = ((x2-x1)**2 + (y1-y2)**2 + (z1-z2)**2)**0.5
    if m < res:
        return True 
    else:
        return False
@to_fortran_format
def Ogrid_check(block,res=1e-3):
    x,y,z = block['X'],block['Y'],block['Z']
    idim,jdim,kdim = x.shape
    if abs(x[0,0,0] - x[-1,0,0]) < res:
        if np.abs(x[0]-x[-1]).max() < res and np.abs(y[0]-y[-1]).max() < res and np.abs(z[0]-z[-1]).max() < res:
            return ((0,0),(0,jdim-1),(0,kdim-1),1,2),((idim-1,idim-1),(0,jdim-1),(0,kdim-1),1,2) 
    if abs(y[0,0,0] - y[0,-1,0]) < res:
        if np.abs(x[:,0]-x[:,-1]).max() < res and np.abs(y[:,0]-y[:,-1]).max() < res and np.abs(z[:,0]-z[:,-1]).max() < res:
            return ((0,idim-1),(0,0),(0,kdim-1),0,2),((0,idim-1),(jdim-1,jdim-1),(0,kdim-1),0,2) 
    if abs(z[0,0,0] - z[0,0,-1]) < res:
        if np.abs(x[:,:,0]-x[:,:,-1]).max() < res and np.abs(y[:,:,0]-y[:,:,-1]).max() < res and np.abs(z[:,:,0]-z[:,:,-1]).max() < res:
            return ((0,idim-1),(0,jdim-1),(0,0),0,1),((0,idim-1),(0,jdim-1),(kdim-1,kdim-1),0,1) 
    return None
def point_in_face(point,face,return_position = False,res = 1e-3):
    #Is the point in the face, if True, return True, else return None
    x,y,z = face 
    px,py,pz = point
    tx = np.abs(x - px)
    ty = np.abs(y - py)
    tz = np.abs(z - pz)
    tx_min = tx.min()
    ty_min = ty.min()
    tz_min = tz.min()
    if tx_min < res and ty_min < res and tz_min < res:
        # there is a point of face2 belongs to face1
        if return_position:
            t = tx+ty+tz
            m = np.where(t == t.min())
            return m
        return True
    else:
        return False
# def cut_face(face,px1,py1,px3,py3,xstep,ystep):
#     if py3+ystep ==-1 and px3+xstep == -1:
#         face_temp = [i[px1::xstep,py1::ystep] for i in face]
#     elif px3 + xstep == -1:
#         face_temp = [i[px1::xstep,py1:py3+ystep:ystep] for i in face]
#     elif py3+ ystep == -1:
#         face_temp = [i[px1:px3+xstep:xstep,py1::ystep] for i in face]
#     else:
#         face_temp = [i[px1:px3+xstep:xstep,py1:py3+ystep:ystep] for i in face]
#     return face_temp
def get_double_face_x(face1, face2, point1, point3, xstep, ystep,message=None):
    x1,y1,z1 = face1 
    x2,y2,z2 = face2
    # print('shape',x2.shape)
    px1,py1 = point1 
    px3,py3 = point3
    (idim1,jdim1),(idim2,jdim2) = x1.shape,x2.shape
    result = []
    xstep_t = -xstep
    if py3+ystep == -1:
        face_temp1 = [x1[:px1+xstep_t:xstep_t,py1::ystep],
                    y1[:px1+xstep_t:xstep_t,py1::ystep],
                    z1[:px1+xstep_t:xstep_t,py1::ystep]]
    else:
        face_temp1 = [x1[:px1+xstep_t:xstep_t,py1:py3+ystep:ystep],
                    y1[:px1+xstep_t:xstep_t,py1:py3+ystep:ystep],
                    z1[:px1+xstep_t:xstep_t,py1:py3+ystep:ystep]]
    width1 = face_temp1[0].shape[0]
    face_temp2 = [x2[width1-1::-1],y2[width1-1::-1],z2[width1-1::-1]]
    if is_equal_face(face_temp1,face_temp2):
        if xstep<0:
            result.append(((px1,0),(py1,py3),0,1))
        else:
            result.append(((px1,idim1-1),(py1,py3),0,1))
        result.append(((0,width1-1),(0,jdim2-1),0,1))
    else:
        print('warning1 !!!!',message)
    #find the other
    # xstep_t = xstep
    if py3 + ystep == -1:
        face_temp1 = [x1[:px3+xstep:xstep,py1::ystep],
                    y1[:px3+xstep:xstep,py1::ystep],
                    z1[:px3+xstep:xstep,py1::ystep]]
     
    else:
        face_temp1 = [x1[:px3+xstep:xstep,py1:py3+ystep:ystep],
                    y1[:px3+xstep:xstep,py1:py3+ystep:ystep],
                    z1[:px3+xstep:xstep,py1:py3+ystep:ystep]]
    width2 = face_temp1[0].shape[0]

    face_temp2 = [x2[idim2-width2:],
                    y2[idim2-width2:],
                    z2[idim2-width2:]]
    # print(face_temp1[0].shape,face_temp2[0].shape)
    if is_equal_face(face_temp1,face_temp2):
        if xstep>0:
            result.append(((0,px3),(py1,py3),0,1))
        else:
            result.append(((idim1-1,px3),(py1,py3),0,1))
        result.append(((idim2-width2,idim2-1),(0,jdim2-1),0,1))
    else:
        print('warning2 !!!!!!!!!',message)
        print('ttt',result)
    if len(result) == 0:
        result = not_connected(45,message)
    return result
def get_matched_face(face1,face2,point1,point3,xstep,ystep,message):
    px1,py1 = point1 
    px3,py3 = point3
    if (px1 - px3) * xstep>0:
        #across x axis
        return get_double_face_x(face1,face2,point1,point3,xstep,ystep,message)
    elif (py1 - py3) * ystep>0:
        #across y axis
        face1_T = [i.T for i in face1]
        face2_T = [i.T for i in face2]
        point1_T = py1,px1 
        point3_T = py3,px3
        result = get_double_face_x(face1_T,face2_T,point1_T, point3_T, ystep, xstep,message)
        if result:
            result = [(i2,i1,i3,i4) for i1,i2,i3,i4 in result]
        return result
    else:
        # x_index = range(px1, px3+xstep, xstep)
        # y_index = range(py1, py3+ystep, ystep)
        # print(x_index,y_index,x1.shape)
        if py3+ystep ==-1 and px3+xstep == -1:
            face1_temp = [i[px1::xstep,py1::ystep] for i in face1]
        elif px3 + xstep == -1:
            face1_temp = [i[px1::xstep,py1:py3+ystep:ystep] for i in face1]
        elif py3+ ystep == -1:
            face1_temp = [i[px1:px3+xstep:xstep,py1::ystep] for i in face1]
        else:
            face1_temp = [i[px1:px3+xstep:xstep,py1:py3+ystep:ystep] for i in face1]
        if is_equal_face(face1_temp,face2):
            idim2,jdim2 = face2[0].shape
            result = ((px1,px3),(py1,py3),0,1),((0,idim2-1),(0,jdim2-1),0,1)
            return result
    return None

def not_connected(code=0,message='no message', warningOutput=False):
    #没有匹配到网格，但是这个情况有点奇怪
    if warningOutput:
        print("warning!please insure your grid is correct! code:",code,message)
    return None
def SmallInBig(face1,face2,face1_info,face2_info,res = 1e-3,message = None, warningOutput = True):
    #there is one point of face2 belong to face1
    oblock1,oblock2 = message[-2:]
    x1,y1,z1 = face1
    x2,y2,z2 = face2
    idim1,jdim1 = x1.shape
    idim2,jdim2 = x2.shape
    if idim1*jdim1 < idim2*jdim2:
        exchange = True
        face1,face2 = face2,face1
        face1_info,face2_info = face2_info,face1_info
        x1,y1,z1 = face1
        x2,y2,z2 = face2
        idim1,jdim1 = x1.shape
        idim2,jdim2 = x2.shape
        oblock1,oblock2 = oblock2, oblock1
    else:
        exchange = False
    p3 = x2[-1,-1],y2[-1,-1],z2[-1,-1]
    
    pif3 = point_in_face(p3,face1,return_position=True)

    if pif3:
        p1 = x2[0,0],y2[0,0],z2[0,0]
        pif = point_in_face(p1,face1,return_position=True)
        # print('pif3',x2.shape)
        if pif:
            # print('pif1')
            px1,py1 = pif
            px3,py3 = pif3
            
            px1,py1 = px1[0],py1[0]
            px3,py3 = px3[0],py3[0]


            p2 = x2[0,-1],y2[0,-1],z2[0,-1]
            pif2 = point_in_face(p2,face1,return_position=True)
            if pif2:
                px2, py2 = pif2 
                px2, py2 = px2[0],py2[0]
                # 其中face2的三个顶点都在face1上，再检查face2面上的非顶点的一个点是否在face1上
                # 避免两个面组成环的形式出现
            
                p_in = x2[1,1],y2[1,1],z2[1,1]
                pif_in = point_in_face(p_in,face1,return_position=False)
                if not pif_in:
                    return not_connected('circle',message, warningOutput)
            else:
                return not_connected(2,message, warningOutput)
            if px1 == px2 == px3 or py1 == py2 == py3:
                #三个点在一条线
                return None
            
            #检查是否需要转置后再对应

            if px2 == px1:
                is_transpose = False 
            else:
                is_transpose = True
            
            if is_transpose:
                x2, y2, z2 = x2.T, y2.T, z2.T
                face2 = [x2, y2, z2]
                idim2, jdim2 = x2.shape

            #检查轴的对应方向
            if px2>px3:
                xstep = -1 
            else:
                xstep = 1 
            if py1>py2:
                ystep = -1
            else:
                ystep = 1
            pdy = x2[0,1], y2[0,1], z2[0,1]
            pdx = x2[1,0], y2[1,0], z2[1,0]

            if idim1 > px1+xstep and jdim1 > py1:
                f1pdx = x1[px1+xstep,py1],y1[px1+xstep,py1],z1[px1+xstep,py1]
            else:
                if idim1 == px1+xstep and xstep == 1:
                    f1pdx = x1[0,py1],y1[0,py1],z1[0,py1]
                else:
                    raise Exception('condition not find of x')
            if idim1 > px1 and jdim1 > py1+ystep: 
                f1pdy = x1[px1,py1+ystep],y1[px1,py1+ystep],z1[px1,py1+ystep]
            else:
                if jdim1 == py1+ystep and ystep == 1:
                    f1pdy = x1[px1,0],y1[px1,0],z1[px1,0]
                else:
                    raise Exception('condition not find of y')

            if not is_equal_point(pdx,f1pdx):
                xstep = -xstep
                #往相反的方向检查 也可能因为网格数对不上 而出错 而这种情况可能是不存在正确匹配面的，所以排除
                if xstep+px1 >= x1.shape[0]:
                    return None

                f1pdx2 = x1[px1+xstep,py1],y1[px1+xstep,py1],z1[px1+xstep,py1]
                if not is_equal_point(pdx,f1pdx2):
                    if oblock1 is True:
                        return None 
                    else:
                        return not_connected(12,message)
            if not is_equal_point(pdy,f1pdy):
                ystep = -ystep
                #往相反的方向检查 也可能因为网格数对不上 而出错 而这种情况可能是不存在正确匹配面的，所以排除
                if py1+ystep >= x1.shape[1]:
                    return
                f1pdy2 = x1[px1,py1+ystep],y1[px1,py1+ystep],z1[px1,py1+ystep]
                if not is_equal_point(pdy,f1pdy2):
                    if oblock1 is True:
                        return None 
                    else:
                        return not_connected(344 ,message,warningOutput)

            point1 = px1,py1 
            point3 = px3,py3
            result = get_matched_face(
                face1, face2, point1, point3, xstep, ystep,message
            )
            if result:
                if len(result) == 2:
                    r1, r2 = result
                    if is_transpose:
                        r2 = r2[1],r2[0],r2[3],r2[2]
                    if exchange:
                        result = r2,r1 
                    else:
                        result = r1,r2 
                    return result
                elif len(result) == 4:
                    r1,r2,r3,r4 = result
                    if is_transpose:
                        r2 = r2[1],r2[0],r2[3],r2[2]
                        r4 = r4[1],r4[0],r4[3],r4[2]
                    if exchange:
                        result = r2,r1,r4,r3
                    else:
                        result = r1,r2,r3,r4
                    return result
            else:
                if oblock1 is True and oblock2 is True:
                    return None 
                else:
                    return not_connected(4,message, warningOutput)
    return not_connected('没有找到',message, warningOutput)
def FindPointInLines(points, lines, res = 1e-3):
    length = points.shape[0]
    p = points[0]
    for k,line in enumerate(lines):
        t1 = np.abs(line - p ).sum(1).min()
        if t1 < res:
            return 0,k
    for i in range(6,-1,-1):
        step = 2**i
        for j in range(0,length,step):
            if j % (step*2) == 0:
                continue 
            p = points[j]
            for k,line in enumerate(lines):
                t1 = np.abs(line - p ).sum(1).min()
                if t1 < res:
                    return j,k
    return None, None
def FindBoundPointInLine(pStart,pEnd,points,line,res = 1e-5):
    # res = 
    distance = lambda line0,p0:1 if np.abs(line0 - p0).sum(1).min() < res else -1
    stateS = distance(line,points[pStart])
    # step = 1 if pEnd > pStart else -1
    # for ii in range(pStart,pEnd+step,step):
    #     if distance(line,points[ii]) == 1:
    #         print(ii)
    #         break
    while True:
        pM = (pEnd+pStart) // 2
        stateM = distance(line,points[pM])
        if stateM*stateS<0:
            pEnd = pM 
            # stateE = stateM
        else:
            pStart = pM 
            stateS = stateM
        if pEnd - pStart <= 1:
            if stateS == 1:
                # print('start',pStart,pEnd)
                return pStart 
            else:
                # print('end',pStart,pEnd)
                return pEnd
def FindPartInFace(face1,face2,res = 1e-3):
    x1,y1,z1 = face1
    x2,y2,z2 = face2
    points0 = np.vstack([x2[:,0], y2[:,0], z2[:,0]]).T
    points1 = np.vstack([x2[:,-1], y2[:,-1], z2[:,-1]]).T
    line1 = np.vstack([x1[:,0],y1[:,0],z1[:,0]]).T
    line2 = np.vstack([x1[:,-1],y1[:,-1],z1[:,-1]]).T
    lines = [line1, line2]
    pN,lineN = FindPointInLines(points0,lines)
    if pN is None:
        return None,None
    
    p1 = FindBoundPointInLine(0,pN,points0,lines[lineN])
    # print(p1,pN,"7777777777")
    p2 = FindBoundPointInLine(pN,points0.shape[0],points0,lines[lineN])
    if np.abs(lines[1-lineN] - points1[p1]).sum(1).min()>res:
        return None,None
    if np.abs(lines[1-lineN] - points1[p2]).sum(1).min()>res:
        return None,None

    if p1 == p2:
        return None,None
    else:
        return p1,p2
@to_fortran_format
def face2face(face1,face2,face1_info,face2_info,res = 1e-3,message = None):
    def TransPartConnectResult(r1,r2,exchange,face1_T,face2_T,p1):

        r2 = (r2[0][0]+p1,r2[0][1]+p1),r2[1],r2[2],r2[3]
        if exchange:
            r1,r2 = r2,r1 
            face1_T,face2_T = face2_T,face1_T
        if face1_T:
            r1 = r1[1], r1[0], r1[3], r1[2]
        if face2_T:
            r2 = r2[1], r2[0], r2[3], r2[2]
        return r1,r2

    oblock1,oblock2 = message[-2:]
    (x1min,x1max),(y1min,y1max),(z1min,z1max) = face1_info
    (x2min,x2max),(y2min,y2max),(z2min,z2max) = face2_info
    if x2min - x1max > res or x1min - x2max > res:

        return None
    if y2min - y1max > res or y1min - y2max > res:

        return None
    if z2min - z1max > res or z1min - z2max > res:
 
        return None
    x1,y1,z1 = face1
    x2,y2,z2 = face2
    idim1,jdim1 = x1.shape
    idim2,jdim2 = x2.shape
    if x1.shape == x2.shape:
        if np.abs(x1 - x2).max() < res and np.abs(y1 - y2).max() < res and np.abs(z1 - z2).max() < res:
            return ((0,idim1-1),(0,jdim1-1),0,1),((0,idim2-1),(0,jdim2-1),0,1)
    if (idim1>=idim2 and jdim1>=jdim2) or (idim1<=idim2 and jdim1<=jdim2) or \
        (idim1>=jdim2 and jdim1>=idim2) or (idim1<=jdim2 and jdim1<=idim2):
        #face1 is a big face, face2 is included in face1,if face1 is smaller than face2, exchange them.
        # print('first ')
        a = SmallInBig(face1,face2,face1_info,face2_info,message=message, warningOutput=False)
        # a = None
        if a:
            return a
        else:
            #满足一个面比一个面小，但是小的面上的顶点不在，这时候face1是大的面face2是小的面  注意后面进行交换
            #确保第face1是大面
            if idim1*jdim1 < idim2*jdim2:
                exchange = True
                face1,face2 = face2,face1
                face1_info,face2_info = face2_info,face1_info
                x1,y1,z1 = face1
                x2,y2,z2 = face2
                idim1,jdim1 = x1.shape
                idim2,jdim2 = x2.shape
                message = list(message)
                message[-2],message[-1] = oblock2, oblock1
            else:
                exchange = False

            #确保face1的j轴小于等于i轴
            if jdim1 > idim1:
                face1_T = True 
                x1,y1,z1 = face1
                face1 = x1.T, y1.T, z1.T 
                x1,y1,z1 = face1
                idim1,jdim1 = jdim1, idim1
            else:
                face1_T = False

            if jdim1 == jdim2 or jdim1 == idim2:
                p1 = None
                if idim2 == jdim2:
                    p1,p2 = FindPartInFace(face1,face2)
                    if p1 is not None:
                        equalCheck = True 
                    else:
                        equalCheck = False
                else:
                    equalCheck = False
                if jdim1 == idim2 and equalCheck is False:
                    face2_T = True 
                    x2,y2,z2 = face2
                    face2 = x2.T, y2.T, z2.T 
                    x2,y2,z2 = face2
                    idim2,jdim2 = jdim2, idim2
                else:
                    face2_T = False
                if p1 is None:
                    p1,p2 = FindPartInFace(face1,face2)
                    # print(p1,p2)
         
                if p1 is not None:
                    # print(p1,p2)
                    # p1+=1
                    face2 = x2[p1:p2+1], y2[p1:p2+1], z2[p1:p2+1]
                    # print(face2[1].max(), face2[1].min())
                    # print('second')
                    t = SmallInBig(face1,face2,face1_info,face2_info,message=message)
                    if t:
                        if len(t) == 2:
                            r1,r2 = t
                            return TransPartConnectResult(r1,r2,exchange,face1_T,face2_T,p1)
                        elif len(t) is 4:
                            r1,r2,r3,r4 = t
                            r1,r2 = TransPartConnectResult(r1,r2,exchange,face1_T,face2_T,p1)
                            r3,r4 = TransPartConnectResult(r3,r4,exchange,face1_T,face2_T,p1)
                            return r1,r2,r3,r4

            else:
                return not_connected("四个顶点都不在面上 且没有一条边是相等的",message)
    else:
        return not_connected('不存在所属关系',message)

    return None

def generate_blocks_info(blocks):
    def get_block_info(block):
        face_info = dict()
        x,y,z = block['X'],block['Y'],block['Z']
        face_info['K0'] = (x[:,:,0].min(), x[:,:,0].max()), ( y[:,:,0].min(), y[:,:,0].max()),  (z[:,:,0].min(), z[:,:,0].max())
        face_info['KE'] = (x[:,:,-1].min(),x[:,:,-1].max()), (y[:,:,-1].min(),y[:,:,-1].max()), (z[:,:,-1].min(),z[:,:,-1].max())
        face_info['J0'] = (x[:,0,:].min(), x[:,0,:].max()), ( y[:,0,:].min(), y[:,0,:].max()),  (z[:,0,:].min(), z[:,0,:].max())
        face_info['JE'] = (x[:,-1,:].min(),x[:,-1,:].max()), (y[:,-1,:].min(),y[:,-1,:].max()), (z[:,-1,:].min(),z[:,-1,:].max())
        face_info['I0'] = (x[0,:,:].min(), x[0,:,:].max()), ( y[0,:,:].min(), y[0,:,:].max()),  (z[0,:,:].min(), z[0,:,:].max())
        face_info['IE'] = (x[-1,:,:].min(),x[-1,:,:].max()), (y[-1,:,:].min(),y[-1,:,:].max()), (z[-1,:,:].min(),z[-1,:,:].max())
        return face_info
    return [get_block_info(i) for i in blocks]
def generate_blocks_face(blocks):
    def get_block_faces(block):
        faces = dict()
        x,y,z = block['X'],block['Y'],block['Z']
        faces['K0'] = x[:,:,0],  y[:,:,0],  z[:,:,0]
        faces['KE'] = x[:,:,-1], y[:,:,-1], z[:,:,-1]
        faces['J0'] = x[:,0,:],  y[:,0,:],  z[:,0,:]
        faces['JE'] = x[:,-1,:], y[:,-1,:], z[:,-1,:]
        faces['I0'] = x[0,:,:],  y[0,:,:],  z[0,:,:]
        faces['IE'] = x[-1,:,:], y[-1,:,:], z[-1,:,:]
        return faces 
    return [get_block_faces(block) for block in blocks]

def one2one(blocks,periodic_faces=None,periodic_faces_result = None,periodic_only = False):
    #perodic_faces is list like  [((block1,face1),(block2,face2),rotated),....]
    #example [((0,'I0'),(1,'IE'),False),...],block id is ctype, start from 0
    def get_periodic_():
        for (id1,key1),(id2,key2),rotated in periodic_faces:

            face1 = blocks_faces[id1][key1]
            face2 = blocks_faces[id2][key2]
            # if not rotated:
            rr = get_periodic_faces(face1,face2,rotated)
        
            if rr is not None:
                (r1,r2) = rr
                r1 = expand_to_3d(key1,r1,blocks[id1]['X'].shape)
                r2 = expand_to_3d(key2,r2,blocks[id2]['X'].shape)
                result.append((id1+1,r1,id2+1,r2))
            # else:
            #     r1,r2 = get_periodic_faces(face1,face2,rotated)
            #     raise Exception('rotated periodic faces')

    

    def expand_to_3d(key,result,shape):
        #因为face2face返回的结果是针对一个二维的平面，并不包含第三个轴，所以需要转换到和Ogrid_check的结果一样的结果
        idim,jdim,kdim = shape 
        r1,r2,index1,index2 = result
        if key[0] == 'I':
            if key[1] == '0':
                result0 = (1,1), r1, r2, index1+1,index2+1
            else:
                result0 = (idim,idim), r1, r2, index1+1,index2+1
        elif key[0] == 'J':
            if key[1] == '0':
                result0 = r1, (1,1), r2, index1,index2+1
            else:
                result0 = r1, (jdim,jdim), r2, index1,index2+1
        elif key[0]=='K':
            if key[1] == '0':
                result0 = r1,r2, (1,1),index1,index2
            else:
                result0 = r1,r2, (kdim,kdim),index1,index2
        else:
            raise Exception('key is an error variables x ,y,z not in key.')
        return result0

    blocks_info = generate_blocks_info(blocks)
    blocks_faces = generate_blocks_face(blocks)
    result = []
    keys = ['K0','KE','J0','JE','I0','IE']
    try:
        oblocks = dict()
        for i,block in enumerate(blocks):
            k = Ogrid_check(block)
            if k is not None:
                oblocks[i] = True 
                result.append((i+1,k[0],i+1,k[1]))
        if periodic_faces:
            length1 = len(result)
            get_periodic_()
            if periodic_faces_result is not None:
                periodic_faces_result.extend(result[length1:])
        if periodic_only:
            return result
        for i,block in enumerate(blocks):
            # if i != 3:
            #     continue
            for j in range(len(blocks)):
                # if j != 6:
                #     continue
                if i>=j:
                    continue
                for key1 in keys:
                    face1 = blocks_faces[i][key1]
                    info1 = blocks_info[i][key1]
                    for key2 in keys:
                        # if key1 != 'KE' or key2 != 'IE':
                        #     continue
                        face2 = blocks_faces[j][key2]
                        info2 = blocks_info[j][key2]
                        t = face2face(face1,face2,info1,info2,message=(i+1,j+1,key1,key2,oblocks.get(i,False),oblocks.get(j,False)))

                        if t is not None:
                            if len(t) == 2:
                                r1,r2 = t
                             
                                r1 = expand_to_3d(key1,r1,block['X'].shape)
                                r2 = expand_to_3d(key2, r2, blocks[j]['X'].shape)
                                result.append((i+1,r1,j+1,r2))
                            elif len(t) == 4:
                                r1,r2,r3,r4 = t 
                                r1 = expand_to_3d(key1,r1,block['X'].shape)
                                r2 = expand_to_3d(key2, r2, blocks[j]['X'].shape)
                                r3 = expand_to_3d(key1,r3,block['X'].shape)
                                r4 = expand_to_3d(key2, r4, blocks[j]['X'].shape)
                                result.extend(((i+1,r1,j+1,r2),(i+1,r3,j+1,r4)))

    except Exception as e:
        print(e)
        print(i,j,key1,key2,'yyyyyyyyyyyyyyyyyyyyy')
        raise Exception('stop')
    #检查是否通过oneone检测
    Varify_one2one(blocks,result)

    return result
def Varify_one2one(blocks,result):
    def get_face(block,r,bid):
        ((i1,i2),(j1,j2),(k1,k2),ind1,ind2) = r
        x,y,z = block['X'],block['Y'],block['Z']
        istep = 1 if i2>i1 else -1
        jstep = 1 if j2>j1 else -1
        kstep = 1 if k2>k1 else -1
        i1,j1,k1 = i1-1,j1-1,k1-1
        inds = ind1 + ind2
        if 6 - inds == 1:
            h,w = abs(j2-j1-1)+1,abs(k2-k1-1)+1
            face = x[i1,j1::jstep,k1::kstep][:h,:w],y[i1,j1::jstep,k1::kstep][:h,:w],z[i1,j1::jstep,k1::kstep][:h,:w]
        elif 6 - inds == 2:
            h,w = abs(i2-i1-1)+1,abs(k2-k1-1)+1
            face = x[i1::istep,j1,k1::kstep][:h,:w],y[i1::istep,j1,k1::kstep][:h,:w],z[i1::istep,j1,k1::kstep][:h,:w]
        elif 6 - inds == 3:
            h,w = abs(i2-i1-1)+1,abs(j2-j1-1)+1
            face = x[i1::istep,j1::jstep,k1][:h,:w],y[i1::istep,j1::jstep,k1][:h,:w],z[i1::istep,j1::jstep,k1][:h,:w]
        else:
            raise Exception('One2One check error')
        if ind1 > ind2:
            face = face[0].T,face[1].T,face[2].T 
        return face
    for bid1,r1,bid2,r2 in result:
        f1 = get_face(blocks[bid1-1],r1,bid1)
        f2 = get_face(blocks[bid2-1],r2,bid2)
        t = is_equal_face(f1,f2)
        if t is False:
            t = is_parallel_face(f1,f2)
        if t is False:
            t = is_rotated_face(f1,f2)
        if t is False:
            print(bid1,r1,bid2,r2)
            raise Exception('One2One check error 12')
def transfer_one2one_str(result):
    result.sort(key=lambda x:x[0])
    def expand_var(vv):
        GRID,((ISTA,IEND),(JSTA,JEND),(KSTA,KEND),ISVA1,ISVA2) = vv
        return GRID,ISTA,JSTA,KSTA,IEND,JEND,KEND,ISVA1,ISVA2
    bstr = ['   1-1 BLOCKING DATA:']
    bstr.append('{:>10s}'.format('NBLI'))
    bstr.append('{:>10d}'.format(len(result)))
    title = '   NUMBER   GRID   :   ISTA   JSTA   KSTA   IEND   JEND   KEND   ISVA1   ISVA2'
    bstr.append(title)
    str_format = '{:>9d}{:>7d}{:>11d}'+'{:>7d}'*5+'{:>8d}'*2
    bstr += [str_format.format(i+1,*expand_var(v[:2])) for i,v in enumerate(result)]
    bstr.append(title)
    bstr += [str_format.format(i+1,*expand_var(v[2:])) for i,v in enumerate(result)]

    return '\n'.join(bstr)
def get_periodic_faces(face1,face2,rotated = False,res = 1e-3):
    #该函数返回结果是 fortran类型 start from 1

    if not rotated:
        x1,y1,z1 = face1 
        x2,y2,z2 = face2
        px1,py1,pz1 = 0,0,0
        px2,py2,pz2 = 0,0,0
        for i,j in [(0,0),(-1,-1),(0,-1),(-1,0)]:
            px1+=x1[i,j]
            py1+=y1[i,j]
            pz1+=z1[i,j]
            px2+=x2[i,j]
            py2+=y2[i,j]
            pz2+=z2[i,j]
        x2 =x2 - (px2-px1)/4
        y2 =y2 - (py2-py1)/4
        z2 =z2 - (pz2-pz1)/4
        face2 = x2,y2,z2
        a = SmallInBig(face1,face2,None,None,message=(False,False))
        if a:
            r1,r2 = a 
            r1 = ((r1[0][0]+1,r1[0][1]+1),(r1[1][0]+1,r1[1][1]+1),r1[2]+1,r1[3]+1)
            r2 = ((r2[0][0]+1,r2[0][1]+1),(r2[1][0]+1,r2[1][1]+1),r2[2]+1,r2[3]+1)
        rr = r1,r2
        return rr
    else:
        return get_rotated_periodic_faces(face1,face2)
def get_rotated_periodic_faces(face1,face2,res = 1e-3):
    x1,y1,z1 = face1
    x2,y2,z2 = face2
    idim1,jdim1 = x1.shape 
    idim2,jdim2 = x2.shape 
    
    if idim1 == idim2 and jdim1 == jdim2 :
        if (abs(z2[0,0] - z1[-1,0])<res and abs(z2[0,-1] - z1[-1,-1]) < res) or \
        (abs(z2[0,0] - z1[-1,-1])<res and abs(z2[0,-1] - z1[-1,0]) < res):
            iTranspose = -1
            x2, y2, z2 = x2[::-1],y2[::-1],z2[::-1]
        else:
            iTranspose = 1
        d1 = (x1[(0,-1),:][:,(0,-1)]**2 + y1[(0,-1),:][:,(0,-1)]**2)**0.5
        d2 = (x2[(0,-1),:][:,(0,-1)]**2 + y2[(0,-1),:][:,(0,-1)]**2)**0.5
        if (abs(d2[0,0] - d1[0,-1])<res and abs(d2[0,-1] - d1[0,0]) < res):
            jTranspose = -1
            x2, y2, z2 = x2[:,::-1],y2[:,::-1],z2[:,::-1]
        else:
            jTranspose = 1
        da = (x2*x1 + y2*y1)/(((x2**2+y2**2)*(x1**2+y1**2))**(1/2))
        
        if da.max() - da.min() > res:
            
            print('Warning these two faces may not be rotated periodic',da.max() - da.min())
            return None
        return ((1,idim1),(1,jdim1),1,2), ((1,idim2)[::iTranspose],(1,jdim2)[::jTranspose],1,2)
    else:
        
        print(idim1,idim2,jdim1,jdim2,'\nthis conditon may not be concerned!!')
        return None

        raise Exception('this conditon may not be concerned!!')

def GetFace(block,faceId):
    x,y,z = block['X'], block['Y'], block['Z']
    if faceId[1] == '0':
        dim = 0 
    else:
        dim = -1
    if faceId[0].upper() == 'I':
        return x[dim],y[dim],z[dim]
    elif faceId[0].upper() == 'J':
        return x[:,dim],y[:,dim],z[:,dim]
    elif faceId[0].upper() == 'K':
        return x[:,:,dim],y[:,:,dim],z[:,:,dim]
    else:
        raise Exception('faceId error',faceId)
def GetFaceAngle(point0,face,pos=None):
    #默认旋转轴是z轴
    def get_p_list(face,pos):
        x,y = face[:2]
        p_list = [(0,0),(0,-1),(-1,-1),(-1,0)]
        distance = [((i,j),math.sqrt(x[i,j]**2+y[i,j]**2)) for i,j in p_list]
        distance.sort(key = lambda k:k[1])
        # print(distance,'distahce')
        distance = [i[0] for i in distance]
        if pos.lower() == 'top':
            return distance[-2:]
        else:
            return distance[:2]
    px,py = point0[:2]
    x,y = face[:2]
    norm0 = math.sqrt(px*px+py*py)
    amax,amin = -600,600
    if pos is None:
        p_list = [(0,0),(0,-1),(-1,-1),(-1,0)]
    else:
        p_list = get_p_list(face,pos)
    for i, j in p_list:
        px1,py1 = x[i,j], y[i,j]
        fz = px*px1 + py*py1 
        fm = norm0*math.sqrt(px1*px1+py1*py1)
        t = fz/fm
        t = 1 if t>1 else t 
        t = -1 if t<-1 else t
        angle = math.acos(t)
        if px*py1 - py*px1<0:
            angle = -angle
        amin = min(amin,angle)
        amax = max(amax,angle)
    return amax - amin ,amin,amax
# def GetLinesAngle(point0,lines):
#     #默认旋转轴是z轴
#     px,py = point0[:2]
#     norm0 = math.sqrt(px**2 + py**2)
#     amax,amin = -600,600
#     for pxpy in lines:
#         for px1,py1 in pxpy:
#             fz = px*px1 + py*py1 
#             fm = norm0*math.sqrt(px1*px1+py1*py1)
#             t = fz/fm
#             t = 1 if t>1 else t 
#             t = -1 if t<-1 else t
#             angle = math.acos(t)
#             if px*py1 - py*px1<0:
#                 angle = -angle
#             amin = min(amin,angle)
#             amax = max(amax,angle)
#     return amax - amin ,amin,amax
def FindBottomTopLine(surf):
    in_face_x, in_face_y = surf
    point00 = in_face_x[0,0],in_face_y[0,0]
    point01 = in_face_x[0,-1],in_face_y[0,-1]
    point11 = in_face_x[-1,-1],in_face_y[-1,-1]
    point10 = in_face_x[-1,0],in_face_y[-1,0]
    
    point_list = [point00,point01,point11,point10]
    distance = []
    for i,(px,py) in enumerate(point_list):
        if i == 3:
            j = 0
        else:
            j = i+1
        p2x,p2y = point_list[j]
        pxm,pym = (px+p2x)/2 , (py+p2y)/2
        distance.append((i,j,math.sqrt(pxm**2+pym**2)))
    distance.sort(key = lambda x:x[-1])
    in_top_line = distance[-1]
    in_bottom_line = distance[0]
    return in_top_line,in_bottom_line,point_list

def GetFacesAngle(point0,faces,position = 'Top'):
    bottom_top_lines = [FindBottomTopLine(f[:2]) for f in faces]
    
    bottom_lines = [(points[ib],points[jb]) for (it,jt,_),(ib,jb,_),points in bottom_top_lines]
    if position == 'Top':
        top_lines = [(points[it],points[jt]) for (it,jt,_),(ib,jb,_),points in bottom_top_lines]
        return GetLinesAngle(point0,top_lines)
    else:
        bottom_lines = [(points[ib],points[jb]) for (it,jt,_),(ib,jb,_),points in bottom_top_lines]
        return GetLinesAngle(point0, bottom_lines)

# def PatchedInterfaceRotatedSingle(blocks,faces1,faces2,periodic1 = 0,periodic2 = 1,position = 'Top'):
#     #faces1:[(2,'I0'),(3,'J0')]
#     #默认face2是旋转面
#     fs1 = [GetFace(blocks[i], faceId) for i,faceId in faces1]
#     fs2 = [GetFace(blocks[i], faceId) for i,faceId in faces2]
    

#     fx,fy,_ = fs1[0]
#     point0 = fx[0,0], fy[0,0]
#     GetFacesAngle(point0,fs1,position)

#     angleSpan1, angle1Min, angle1Max = GetFacesAngle(point0,fs1,position)
#     angleSpan2, angle2Min, angle2Max = GetFacesAngle(point0,fs2,position)
    

#     # angle2Min = min([i[1] for i in angles2])
#     # angle2Max = max([i[2] for i in angles2])
#     # angleSpan2 = angle2Max - angle2Min

#     # angleSpan1 = 2*np.pi/round(2*np.pi/angleSpan1)
#     # angleSpan2 = 2*np.pi/round(2*np.pi/angleSpan2)
#     #旋转过后的角度
#     if periodic1>0:
#         angle1MaxRotated = angle1Max + angleSpan1*periodic1 
#         angle1MinRotated = angle1Min 
#     elif periodic1<0:
#         angle1MaxRotated = angle1Max 
#         angle1MinRotated = angle1Min + angleSpan1*periodic1 
#     else:
#         angle1MaxRotated = angle1Max 
#         angle1MinRotated = angle1Min
    
#     if periodic2>0:
#         angle2MaxRotated = angle2Max + angleSpan2*periodic2
#         angle2MinRotated = angle2Min 
#     elif periodic2<0:
#         angle2MaxRotated = angle2Max 
#         angle2MinRotated = angle2Min + angleSpan2*periodic2
#     else:
#         angle2MaxRotated = angle2Max 
#         angle2MinRotated = angle2Min 
#     # if not patchedPeriodic:
#     f1tof2Positive = math.ceil((angle2MaxRotated - angle1MinRotated)/angleSpan1)
#     f1tof2Negative = -(math.ceil((angle1MaxRotated - angle2MinRotated )/angleSpan1) - 1)

#     f2tof1Positive = math.ceil((angle1MaxRotated - angle2MinRotated)/angleSpan2)
#     f2tof1Negative = -(math.ceil((angle2MaxRotated - angle1MinRotated )/angleSpan2) - 1)

#     return (faces1, angleSpan1, f1tof2Negative, f1tof2Positive), (faces2, angleSpan2, f2tof1Negative, f2tof1Positive)
#     # else:
#     #     assert abs(angleSpan1 - angleSpan2)<1e-3
#     #     dt = (angle2Max - angle1Max)/angleSpan1
#     #     return (faces1, angleSpan1, dt, dt), (faces2, angleSpan2, -dt, -dt)
def PatchedInterfaceRotatedPeriodic(blocks,faces1,faces2):
    #计算旋转周期壁面，该壁面无法进行oneoneblock赋值，只能进行插值计算
    fs1 = [GetFace(blocks[i], faceId) for i,faceId in faces1]
    fs2 = [GetFace(blocks[i], faceId) for i,faceId in faces2]
    

    fx,fy,_ = fs1[0]
    point0 = fx[0,0], fy[0,0]

    angels1 = [GetFaceAngle(point0,i) for i in fs1]
    angels2 = [GetFaceAngle(point0,i) for i in fs2]
    ma1_list = [i[2] for i in angels1]
    ma2_list = [i[2] for i in angels2]
    ma1,ma2 = max(ma1_list),max(ma2_list)
    span = ma2 - ma1 
    return (faces1,span,1,1), (faces2, span, -1, -1)

# def PatchedInterfaceRotated(blocks,faces1,faces2,periodic1 = 0,periodic2 = 1,patchedPeriodic = False):
#     if patchedPeriodic:
#         return PatchedInterfaceRotatedPeriodic(blocks, faces1, faces2)
#     (f1,a1,n1,p1),(f2,a2,n2,p2) = PatchedInterfaceRotatedSingle(blocks,faces1,faces2,periodic1 ,periodic2  ,position = 'Top')
#     (_,a3,n11,p11),(_,a4,n22,p22) = PatchedInterfaceRotatedSingle(blocks,faces1,faces2,periodic1 ,periodic2 ,position = 'Bottom')
#     t = (f1,a1,min(n1,n11),max(p1,p11)),(f2,a2,min(n2,n22),max(p2,p22))
#     # print(a1,a2,n1,p1,n2,p2)
#     # print(a1,a3,n11,p11,n22,p22)
#     return t
def MergeBlocks(blocks,b1,b2,one2oneData=None,patchedData=None,boundaryData=None):
    #b1,b2 start from 0
    if b2 < b1:
        b1, b2 = b2, b1
    block1 = blocks[b1]
    block2 = blocks[b2]
    shape1, shape2 = block1['X'].shape, block2['X'].shape
    def detectEqualFace(dim,pos):
        if dim == 0:
            face1 = block1['X'][pos],block1['Y'][pos],block1['Z'][pos]
            face20 = block2['X'][0],block2['Y'][0],block2['Z'][0]
            face21 = block2['X'][-1],block2['Y'][-1],block2['Z'][-1]
        elif dim == 1:
            face1 = block1['X'][:,pos],block1['Y'][:,pos],block1['Z'][:,pos]
            face20 = block2['X'][:,0],block2['Y'][:,0],block2['Z'][:,0]
            face21 = block2['X'][:,-1],block2['Y'][:,-1],block2['Z'][:,-1]
        elif dim == 2:
            face1 = block1['X'][:,:,pos],block1['Y'][:,:,pos],block1['Z'][:,:,pos]
            face20 = block2['X'][:,:,0],block2['Y'][:,:,0],block2['Z'][:,:,0]
            face21 = block2['X'][:,:,-1],block2['Y'][:,:,-1],block2['Z'][:,:,-1]
        else:
            raise Exception('dim Error')
        if is_equal_face(face1,face20):
            return 0
        elif is_equal_face(face1,face21):
            return -1
        else:
            return None
    dim1 = None
    for i in range(3):
        for j in [0,-1]:
            t = detectEqualFace(i,j)
            if t is not None:
                dim1,pos1,dim2,pos2 = i,j,i,t
    if dim1 is None:
        raise Exception('No detect equal face')
    assert pos1 == -1 and pos2 == 0
    blocks.pop(b2)
    h,w,d = shape2
    kk = [0,0,0]
    kk[dim2] = 1
    h1,w1,d1 = kk
    block1['X'] = np.concatenate((block1['X'],block2['X'][h1:h,w1:w,d1:d]),axis = dim2)
    block1['Y'] = np.concatenate((block1['Y'],block2['Y'][h1:h,w1:w,d1:d]),axis = dim2)
    block1['Z'] = np.concatenate((block1['Z'],block2['Z'][h1:h,w1:w,d1:d]),axis = dim2)
    if one2oneData:
        def deal_one2one(rr,b1,b2):
            bb1,rr1,bb2,rr2 = rr
            bb1 -= 1
            bb2 -= 1
            result = []
            length = shape1[dim1]-1
            delete_face = False
            for b,r in [(bb1,rr1),(bb2,rr2)]:
                if b > b2:
                    b = b - 1 
                elif b == b2:
                    b = b1 
                    ise,jse,kse,v1,v2 = r
                    if dim2 == 0:
                        
                        if ise[0] == 1 and ise[1] == 1:
                            delete_face = True
                        ise = ise[0]+length, ise[1]+length
                    elif dim2 == 1:
                        
                        if jse[0] == 1 and jse[1] == 1:
                            delete_face = True
                        jse = jse[0]+length, jse[1]+length
                    elif dim2 == 2:
                        if kse[0] == 1 and kse[1] == 1:
                            delete_face = True
                        kse = kse[0]+length, kse[1]+length
                        
                    r = ise,jse,kse,v1,v2
                result.extend((b+1,r))
            if delete_face:
                return None 
            else:
                return result
        result_one2one = [deal_one2one(i,b1,b2) for i in one2oneData]
        result_one2one = [i for i in result_one2one if i]
        Varify_one2one(blocks,result_one2one)
    else:
        result_one2one = None
    if patchedData:
        t = b1,b2,shape1,shape2,dim1
        mfun = mergedPatchedData
        patchedData2 = [(mfun(i[0],t),[mfun(ff,t) for ff in i[1]]) for i in patchedData]
    else:
        patchedData2 = None
    if boundaryData:
        boundaryData2 = dict()
        for key,value in boundaryData.items():
            blockid = int(key[:-2])-1
            if blockid == b2:
                assert value['bctype'] != 2005
                continue 
            elif blockid == b1:
                assert value['bctype'] != 2005
                continue
            elif blockid > b2:
                blockid -= 1
            key = '{}{}'.format(blockid+1,key[-2:])
            boundaryData2[key] = value
    else:
        boundaryData2 = None
    return blocks,result_one2one, patchedData2, boundaryData2
def mergedPatchedData(element_patchedData,mergedData):
    (blockId,faceId),xie_eta = element_patchedData[:2]
    if mergedData:
        if faceId[0].lower() == 'i':
            dimf = 0
        elif faceId[0].lower() == 'j':
            dimf = 1
        else:
            dimf = 2
    else:
        return element_patchedData

    targetId,mergeId,(h1,w1,d1),(h2,w2,d2),dim1 = mergedData

    if blockId > mergeId:
        blockId = blockId - 1
    elif blockId == mergeId:
        blockId = targetId
        h,w,d = h1+h2-1, w1+w2 -1, d1+d2-1
        if dim1 is 0:
            h,w,d = h1+h2-1,w1,d1 
            w1,d1 = 1,1
        elif dim1 is 1:
            h,w,d = h1,w1+w2-1,d1 
            h1,d1 = 1,1
        else:
            h,w,d = h1,w1,d1+d2-1
            h1,w1 = 1,1
        if dim1 != dimf:
            if dimf is 0:
                #xie = j  eta = k 
                xie_eta = w1,w,d1,d
            elif dimf is 1:
                #xie = k  eta = i
                xie_eta = d1,d,h1,h
            elif dimf is 2:
                #xie = j eta = i
                xie_eta = w1,w,h1,h
    elif blockId == targetId:
        blockId = targetId
        if dim1 != dimf:
            if dimf is 0 :
                #xie = j  eta = k 
                xie_eta = 1,w1,1,d1
            elif dimf is 1:
                #xie = k  eta = i
                xie_eta = 1,d1,1,h1
            elif dimf is 2:
                #xie = j eta = i
                xie_eta = 1,w1,1,h1
    
    if len(element_patchedData) == 2:
        return (blockId, faceId), xie_eta
    elif len(element_patchedData) ==3:
        return  (blockId, faceId), xie_eta,element_patchedData[2]
    else:
        raise Exception('Error 2342354')

def tetrahedronArea(p1,p2,p3,p4):
    px,py,pz = p4
    v1x,v1y,v1z = p1[0] - px, p1[1] - py, p1[2] - pz
    v2x,v2y,v2z = p2[0] - px, p2[1] - py, p2[2] - pz
    v3x,v3y,v3z = p3[0] - px, p3[1] - py, p3[2] - pz
    tx = v1y*v2z - v2y*v1z 
    ty = v1z*v2x - v2z*v1x 
    tz = v1x*v2y - v1y*v2x 
    volume = tx*v3x + ty*v3y + tz*v3z 
    return volume/6
def hexahedronArea(p1,p2,p3,p4,p5,p6,p7,p8):
    v  = tetrahedronArea(p2,p4,p5,p1)
    v += tetrahedronArea(p7,p2,p5,p6)
    v += tetrahedronArea(p4,p7,p5,p8)
    v += tetrahedronArea(p4,p2,p7,p3)
    v += tetrahedronArea(p7,p5,p2,p4)
    return v
def CheckBlockVolume(block):
    x,y,z = block['X'], block['Y'], block['Z']
    t = [(0,0,0),(1,0,0),(1,1,0),(0,1,0),
        (0,0,1),(1,0,1),(1,1,1),(0,1,1)]
    p = [(x[i],y[i],z[i]) for i in t]
    volume = hexahedronArea(*p)
    return volume
def AdjustNegativeGrid(blocks):
    return [{k:v[::-1,:,:] for k,v in b.items()} if CheckBlockVolume(b)<0 else b for b in blocks]
def patchedFace2Faces(blocks,face1,faces,faces_type,rotate_angle='positive',steady=False):
    if faces_type.lower() == 'periodic':
        _,f2 = PatchedInterfaceRotatedPeriodic(blocks,[face1],faces)
        rotate_angle = f2[1]*f2[2]
        to_face_result = face1,(0,0,0,0)
        from_face_result = [(faces[0],(0,0,0,0),rotate_angle)]
        return to_face_result,from_face_result
    face1_xyz = GetFace(blocks[face1[0]],face1[1])
    point0 = face1_xyz[0][-1,-1],face1_xyz[1][-1,-1],face1_xyz[2][-1,-1]
    faces_xyz = [GetFace(blocks[bid],key) for bid,key in faces]
    # k = GetFacesAngle(point0,faces_xyz,'Top')
    # print(k)
    face1_theta_top = GetFaceAngle(point0,face1_xyz,'Top')
    face1_theta_bottom = GetFaceAngle(point0,face1_xyz,'bottom')

    faces_theta_top = [GetFaceAngle(point0,i,'Top') for i in faces_xyz]
    faces_theta_bottom = [GetFaceAngle(point0,i,'bottom') for i in faces_xyz]

    theta_min = [i[-2] for i in faces_theta_top]
    theta_max = [i[-1] for i in faces_theta_top]
    theta_delta = [i[0] for i in faces_theta_top]
    Theta = sum(theta_delta)#整个faces的角度
    print(Theta,faces)
    print(max(theta_max) - min(theta_min))
    assert abs(max(theta_max) - min(theta_min) - Theta) < 0.00001

    faces_theta_top_extend = [(face_number,j,delta,amin+j*Theta,amax+j*Theta) for face_number,(delta,amin,amax) in enumerate(faces_theta_top) for j in range(-3,4)]
    faces_theta_bottom_extend = [(face_number,j,delta,amin+j*Theta,amax+j*Theta) for face_number,(delta,amin,amax) in enumerate(faces_theta_bottom) for j in range(-3,4)]
    if rotate_angle.lower() == 'positive':
        rotate_angle = Theta 
    elif rotate_angle.lower() == 'negative':
        rotate_angle = -Theta
    else:
        rotate_angle = float(rotate_angle)
        
    if steady:
        rotate_angle = 0

    if faces_type.lower() == 'rotor':
        rotate_angle *=-1
    pd,pmi,pma = face1_theta_top
    face1_theta_top_extend = [pd+abs(rotate_angle),min(pmi,pmi+rotate_angle),max(pma,pma+rotate_angle)]
    face1_theta_bottom_extend = [
        face1_theta_bottom[0]+abs(rotate_angle),
        min(face1_theta_bottom[1],face1_theta_bottom[1]+rotate_angle),
        max(face1_theta_bottom[2],face1_theta_bottom[2]+rotate_angle)
    ]
    def isPatched(element_faces,element_face1):
        _,_,_,mi,ma = element_faces 
        _,fmi,fma = element_face1 
        if fmi <= mi <= fma or fmi <= ma <= fma:
            return True
        else:
            return False
    f1 = [i for i in faces_theta_top_extend if isPatched(i,face1_theta_top_extend)]
    f2 = [i for i in faces_theta_bottom_extend if isPatched(i,face1_theta_bottom_extend)]
    from_faces = list({i[:2] for i in f1+f2})
    from_faces.sort(key = lambda x:faces_theta_top[x[0]][1]+x[1]*Theta)
    to_face_result = face1,(0,0,0,0)
    from_faces_result = [(faces[i],(0,0,0,0),j*Theta) for i,j in from_faces]
    return to_face_result,from_faces_result
def translatePatcheDataToString(blocks,pdata,ITOSS=0,ITMAX=0):
    if ITMAX is None:
        ITMAX = 0
    def getITMAX_ITOSS(faces,itmax=0):
        if itmax is not 0:
            return itmax,0
        blockId, faceId = faces[0]
        i,j,k = blocks[blockId]['X'].shape
        key = faceId[0].lower()
        if key == 'i':
            t = max(j,k)
        elif key == 'j':
            t = max(i,k)
        else:
            t = max(i,j)
        if t>itmax:
            itmax = t 
        return t,0
    title = '  DYNAMIC PATCH INPUT DATA\n    NINTER\n{:>10d}\n   INT  IFIT    LIMIT    ITMAX    MCXIE    MCETA      C-0    IORPH    ITOSS\n'
    title_block = [getITMAX_ITOSS(to_face,ITMAX) for to_face,_ in pdata]
    NINTER = len(pdata)
    result = title.format(NINTER)
    fstr1 = '{:>6d}'*2+'{:>9d}'*7+'\n'
    for i,(itmax,itoss) in enumerate(title_block):
        result += fstr1.format(i+1,1,1,itmax,0,0,0,0,itoss)

    fstr2 = '   INT    TO     XIE1     XIE2     ETA1     ETA2      NFB\n'
    fstr2 += '{:>6d}'*2+'{:>9d}'*5+'\n'
    translate_table = str.maketrans('ijkIJK0eE','123123122')

    fromStr1 = '        FROM     XIE1     XIE2     ETA1     ETA2    FACTJ    FACTK\n'
    fromStr1 += '{:>12d}'+'{:>9d}'*4+'{:>9.4f}{:9.4f}\n'
    dxStr = '          DX       DY       DZ   DTHETX   DTHETY   DTHETZ\n'
    dxStr += '{:>12.4f}'+'{:>9.4f}'*5+'\n'
    fromStr = fromStr1+dxStr

    strings_result = [result]
    for i,(((toid,tokey),(xie1,xie2,eta1,eta2)),from_faces) in enumerate(pdata):
        TO = '{}{}'.format(toid+1,tokey.translate(translate_table))
        if xie1 != 0:
            print((xie1,xie2,eta1,eta2),toid,tokey)
        strings_result.append(fstr2.format(i+1,int(TO),xie1,xie2,eta1,eta2,len(from_faces)))
        for (fromId,faceId),(xie1,xie2,eta1,eta2),delta_theta in from_faces:
            FROM = '{}{}'.format(fromId+1,faceId.translate(translate_table))
            delta_theta = delta_theta/3.1415926*180
            t = fromStr.format(int(FROM),xie1,xie2,eta1,eta2,0,0,0,0,0,0,0,delta_theta)
            strings_result.append(t)
    return ''.join(strings_result)
if __name__=='__main__':
    #检查one2one中设置周期面时候的序号问题 放假之前没有解决
    from yxspkg import plot3d
    # t = plot3d.read('')
    t = plot3d.read('/home/yxs/F/learning/CFL3D/CFL3D/Stage-B_SA_pb99240-6.7.2/Stage_B_250w.g')
    # t = plot3d.read('/home/yxs/F/pythonAPP/cfl3d_pyui/test.g')
    # t = [t[13],t[25]]
    # t = plot3d.read('/home/yxs/F/pythonAPP/cfl3d_pyui/RS_work/rotate323_mesh.g')
    # '''
    # (([(2, 'KE'), (4, 'KE'), (5, 'KE'), (7, 'KE'), (9, 'KE'), (10, 'KE'), (12, 'KE'), (14, 'KE'), (15, 'KE')], 27.69230767779229, 0, 3), 
    # ([(16, 'K0'), (19, 'K0'), (20, 'IE'), (22, 'K0'), (25, 'K0'), (26, 'IE')], 27.6923076964478, -2, 1))
    # '''
    # x = patchedFace2Faces(t,(9,'KE'),[(15, 'K0'), (18, 'K0'), (19, 'IE'), (21, 'K0'), (24, 'K0'), (25, 'IE')],'rotor')
    # print(x)
    # x = patchedFace2Faces(t,(15,'IE'),[(14,'IE')],'periodic')
    # k = translatePatcheDataToString(t,[x])
    # print(k)
    # periodic_faces=[((0,'I0'),(0,'IE'),False),((1,'I0'),(1,'IE'),False),((2,'IE'),(5,'IE'),False)]
    # periodic_faces = None
    k = one2one(t)
    print(len(k))
    # q = transfer_one2one_str(k)
    # print(q)
    # print(oneData == oneData2,'ererere')
    #patchedSurface
    # p1 = PatchedInterfaceRotated(t,[(14,'Ie'),], [(15,'Ie'),],0,0,True)
    # p2 = PatchedInterfaceRotated(t,[(1,'K0'),(3,'K0'),(4,'Ke')], [(5,'Ke'),(8,'Ke'),(9,'Ie')],0,1)
    # p3 = PatchedInterfaceRotated(t,[(11,'Ke'),(14,'Ke'),(15,'K0')], [(6,'K0'),(8,'K0'),(10,'Ke')],0,1)
    # patchedData = [[BlockIdPlus(t) for t in p] for p in [p1,p2,p3]]
    # for i in patchedData:
    #     print(i)
    # m = patched(patchedData[2:3])
    # for i in m:
    #     print(i[0])
    # print(m)
    # blocks,_,pd = MergeBlocks(t,9,10,one2oneData=None,patchedData=m)
    # print('##################################################################')
    # print(pd)
    # for (f1,f2),fs in pd:
    #     print(f1,f2,len(fs))
    # # zz = translatePatcheDataToString(blocks,pd)
    # # print(zz)
    # hexahedronArea(
    #     (0,0,0),(1,0,0),(1,1,0),(0,1,0),
    #     (0,0,1),(1,0,1),(1,1,1),(0,1,1)
    # )
    # t = AdjustNegativeGrid(t)
    # AdjustNegativeGrid(t)