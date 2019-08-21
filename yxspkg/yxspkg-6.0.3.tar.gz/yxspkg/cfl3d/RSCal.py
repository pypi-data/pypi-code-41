from pathlib import Path
import numpy as np 
from . import one2one
import time
from yxspkg import tecfile
import math
import re
from . import functions
from . import input_cfl3d
#该模块主要是用来处理轴流式旋转机械的，并且直接可产生cfl3d可用的inp文件进行计算


def RotorStatorCal(blocks,Stator=True,res = 1e-3):
    #find IN OUT
    blocks_info = one2one.generate_blocks_info(blocks)
    blocks_faces = one2one.generate_blocks_face(blocks)
    face_z_list = [(i,key,(value[2][0]+value[2][1])/2) for i,block in enumerate(blocks_info) for key,value in block.items()]
    face_z_list.sort(key = lambda x:x[2])
    res = abs(face_z_list[0][2] - face_z_list[-1][2])*0.00001
    t = face_z_list[0][2]
    face_in_list = [i for i in face_z_list if abs(i[2]-t) < res]
    t = face_z_list[-1][2]
    face_out_list = [i for i in face_z_list if abs(i[2]-t) < res]

    used_faces = [(i,key) for i,key,_ in face_in_list+face_out_list]

    result = {'in':face_in_list,'out':face_out_list}



    face_top_list = []
    face_bottom_list = []
    for i,faces in enumerate(blocks_faces):
        for key1,key2 in (('K0','KE'),('J0','JE'),('I0','IE')):
            if (i,key1) in used_faces or (i,key2) in used_faces:
                continue
            face1x,face1y,_ = faces[key1]
            face2x,face2y,_ = faces[key2]
            d1 = np.sqrt(face1x**2 + face1y**2)
            d2 = np.sqrt(face2x**2 + face2y**2)
            d = d1-d2 
            dmin,dmax = d.min(),d.max()
            if dmin>res:
                face_top_list.append((i,key1,dmin))
                face_bottom_list.append((i,key2,dmin))
            if dmax<-res:
                face_top_list.append((i,key2,dmax))
                face_bottom_list.append((i,key1,dmax))
    result['top'] = face_top_list
    result['bottom'] = face_bottom_list

    used_faces.extend([(i,k) for i,k,d in face_top_list+face_bottom_list])
    # for i in used_faces:
    #     print(i)
    x0 = max([j[0][1] for i in blocks_info for j in i.values()])
    y0 = max([j[1][1] for i in blocks_info for j in i.values()])
    xy0norm = (x0**2+y0**2)**0.5
    amax, amin = None,None
    for i, faces in enumerate(blocks_faces):
        for key,face in faces.items():
            if (i,key) in used_faces:
                continue
            x1,y1,_ = face
            fz = x0*x1+y0*y1 
            fm = np.power(x1**2+y1**2,1/2)
            angle = fz/(fm*xy0norm)
            anglemax = angle.max()
            anglemin = angle.min()
            if amax is None or anglemax > amax:
                amax = anglemax 
                face_max = i,key,amax
            if amin is None or anglemin < amin:
                amin = anglemin
                face_min = i,key,amin
    result['periodic'] = [face_max,face_min]
    #寻找叶片壁面
    in_out_id = set([i[0] for i in result['in']+result['out']])
    ijk_to_axis = {'i':0,'j':1,'k':2}
    axis_to_ijk = 'IJK'
    for blockid,block in enumerate(blocks):
        if blockid in in_out_id:continue
        Ogrid = one2one.Ogrid_check(block)
        if Ogrid:
            _,_,_,index1,index2 = Ogrid[0]
            axis = 6 - index1 - index2 -1
            for bottom in result['bottom']:
                if bottom[0] == blockid:
                    bottom_face = bottom[1]
            axis2 = ijk_to_axis[bottom_face[0].lower()]
            axis3 = 3 - axis - axis2
            x,y,z = block['X'],block['Y'],block['Z']
            sl = [0,0,0] 
            sl[axis] = slice(0,None)
            sl1 = tuple(sl)
            x1,y1,z1 = x[sl1],y[sl1],z[sl1]
            sl[axis3] = -1
            sl2 = tuple(sl)
            x2,y2,z2 = x[sl2],y[sl2],z[sl2]
            v1 = (x1.max()-x1.min())*(y1.max()-y1.min())*(z1.max()-z1.min())
            v2 = (x2.max()-x2.min())*(y2.max()-y2.min())*(z2.max()-z2.min())
            if v1<v2:
                key = '0'
            else:
                key = 'E'
            faceId = axis_to_ijk[axis3]+key 
            result['bottom'].append((blockid,faceId, v2-v1))
    return result
def CalDeltaAngle(line):
    px,py,pz = line
    max_angle = 0
    max_number = -1
    for i in range(1,len(px)-1):
        x1,y1,z1 = px[i-1],py[i-1],pz[i-1]
        x2,y2,z2 = px[i],py[i],pz[i]
        x3,y3,z3 = px[i+1],py[i+1],pz[i+1]
        dx1,dy1,dz1 = x2-x1,y2-y1,z2-z1
        dx2,dy2,dz2 = x3-x2,y3-y2,z3-z2

        mul = dx1*dx2+dy1*dy2+dz1*dz2 
        norm = ((dx1**2+dy1**2+dz1**2)*(dx2**2+dy2**2+dz2**2))**0.5
        cosv = mul/norm 
        if cosv>1:cosv = 1
        if cosv<-1:cosv = -1
        angle = math.acos(cosv)
        if angle > max_angle:
            max_angle = angle 
            max_number = i 
    return max_number,max_angle/3.1415*180
def SplitBlock(blocks,splicted,init_q):
    bl = blocks[splicted]
    x,y,z = bl['X'],bl['Y'],bl['Z']
    max_axis,max_angle,max_number = -1,0,0
    for i in range(3):
        for j in (0,-1):
            if i == 0:
                line = x[:,j,j],y[:,j,j],z[:,j,j]
            elif i == 1:
                line = x[j,:,j],y[j,:,j],z[j,:,j]
            else:
                line = x[j,j,:],y[j,j,:],z[j,j,:]
            max_n,max_a = CalDeltaAngle(line)
            if max_a > max_angle:
                max_angle = max_a
                max_axis = i
                max_number = max_n
    sl = [slice(0,None)]*3
    sl[max_axis] = slice(0,max_number+1)
    sl1 = tuple(sl)
    bl1 = {'X':x[sl1],'Y':y[sl1],'Z':z[sl1]}
    sl[max_axis] = slice(max_number,None)
    sl2 = tuple(sl)
    bl2 = {'X':x[sl2],'Y':y[sl2],'Z':z[sl2]}
    block_list = blocks[:splicted] + [bl1,bl2] + blocks[splicted+1:]
    if init_q:
        ql = init_q[splicted]
        ql1,ql2 = dict(),dict()
        for key,val in ql.items():
            if isinstance(key,str):
                ql1[key] = val 
                ql2[key] = val 
            else:
                ql1[key] = val[sl1]
                ql2[key] = val[sl2]
        init_q[splicted] = ql2
        init_q.insert(splicted,ql1)
    return block_list

def AutoGenerateInputDdata(blocks,stators=None,rotors=None,split_blocks=None,rpm = 10,merged = True,bc2006=True,**karg):
    blocks_old = blocks 
    split_blocks.sort()
    split_blocks = list(split_blocks)
    split_blocks_old = tuple(split_blocks)
    stators_old, rotors_old = tuple(stators), tuple(rotors)
    def after_split(splitid,stage):
        t = [(i+1 if i>splitid else i) for i in stage]
        if splitid in t:
            t.append(splitid+1)
        t.sort()
        return t
    init_file = karg.get('init_file')
    if init_file:
        init_q = tecfile.read(init_file)
        assert len(init_q) == len(blocks)
        for i,j in zip(blocks,init_q):
            toshape = i['X'].shape
            for key,val in j.items():
                if isinstance(key,str):
                    continue
                todata = functions.interpolateblock(val,toshape)
                j[key] = todata
    else:
        init_q = None
    if split_blocks is not None:
        for i in range(len(split_blocks)):
            splictid = split_blocks[i]
            if not merged:
                init_q_split = init_q 
            else:
                init_q_split = None
            blocks = SplitBlock(blocks,splictid,init_q_split)
            for j in range(i+1,len(split_blocks)):
                split_blocks[j] += 1
            stators = [after_split(splictid,i) for i in stators]
            rotors  = [after_split(splictid,i) for i in rotors]
    if init_file:
        for q in init_q:
            for key,val in q.items():
                if isinstance(key,str):
                    continue 
                center = (val[1:,1:,1:]+
                         val[1:,:-1,1:]+
                         val[1:,1:,:-1]+
                         val[1:,:-1,:-1]+
                         val[:-1,1:,1:]+
                         val[:-1,:-1,1:]+
                         val[:-1,1:,:-1]+
                         val[:-1,:-1,:-1])/8
                if center.dtype != np.float32:
                    center = center.astype('float32')
                q[key] = center
        init_path =str( Path(karg['workdir']) / 'init.q')
        tecfile.write(init_path, init_q)
    boundary_stators = []
    for stator in stators:
        blocks_stator = [blocks[i] for i in stator]
        m = RotorStatorCal(blocks_stator,Stator=True)
        t = {k:[(stator[i[0]],i[1],i[2]) for i in v] for k,v in m.items()}
        boundary_stators.append((min(stator),t))
    boundary_rotors = []
    for rotor in rotors:
        blocks_rotor = [blocks[i] for i in rotor]
        m = RotorStatorCal(blocks_rotor,Stator=True)
        t = {k:[(rotor[i[0]],i[1],i[2]) for i in v] for k,v in m.items()}
        boundary_rotors.append((min(rotor),t))
   
    periodic_faces = [(i['periodic'][0][:2],i['periodic'][1][:2],True) for _,i in boundary_stators+boundary_rotors]
    periodic_result = list()
    one2oneData = one2one.one2one(blocks,periodic_faces,periodic_faces_result=periodic_result)

    assert len(periodic_faces) == len(periodic_result)

    one2oneData = [i for i in one2oneData if i not in periodic_result]
    
    rotors_id = [i[0] for i in boundary_rotors]

    boundary_conditions = boundary_stators + boundary_rotors
    boundary_conditions.sort(key = lambda x:x[0])
    boundary_result = {}
    for (f1,f2,_),(_,one1,_,one2) in zip(periodic_faces,periodic_result):
        bl1,key1 = f1
        bl2,key2 = f2
        face1 = one2one.GetFace(blocks[bl1], key1)
        face2 = one2one.GetFace(blocks[bl2], key2)
        p0 = face1[0][0,0],face1[1][0,0]
        angle1 = one2one.GetFaceAngle(p0,face1)
        angle2 = one2one.GetFaceAngle(p0,face2)
        delta = angle2[-1] - angle1[-1]
        delta *= -180/math.pi
        key = '{}{}'.format(bl1+1,key1)
        boundary_result[key] = {'bctype':2005,'one2one':one1,'auxdata':(bl2+1,0,0,delta)}
        key = '{}{}'.format(bl2+1,key2)
        boundary_result[key] = {'bctype':2005,'one2one':one2,'auxdata':(bl1+1,0,0,-delta)}
    for rs_id,condition in boundary_conditions:
        if rs_id in rotors_id:
            rotated = 1
        else:
            rotated = -1
        for i in condition['bottom']:
            key = '{}{}'.format(i[0]+1,i[1])
            boundary_result[key]={'bctype':2004}
        for i in condition['top']:
            key = '{}{}'.format(i[0]+1,i[1])
            boundary_result[key]={'bctype':-rotated*2004}
    for i in boundary_conditions[0][1]['in']:
        key = '{}{}'.format(i[0]+1,i[1])
        boundary_result[key] = {'bctype':2003,'data':karg['in_condition']}

    top_face_dict = {i[0]:i[1] for i in boundary_conditions[-1][1]['top']}
    IJK_123 = dict(zip("IJK",(1,2,3)))
    if bc2006:
        for i in boundary_conditions[-1][1]['out']:
            key = '{}{}'.format(i[0]+1,i[1])
            faceId = top_face_dict[i[0]]
            intdir = IJK_123[faceId[0]]
            if faceId[-1] == '0':
                intdir *= -1
            boundary_result[key] = {'bctype':2006,'data':(0,0,intdir,3)}
    else:
        for i in boundary_conditions[-1][1]['out']:
            key = '{}{}'.format(i[0]+1,i[1])
            
            boundary_result[key] = {'bctype':2002}
    
    patchedData = list()
    steady = karg.get('steady',False)
    # periodic_result_block = set([j for i in periodic_result for j in (i[0]-1,i[2]-1)])
    for i in range(len(boundary_conditions) - 1):
        rs_id1,condition1 = boundary_conditions[i]
        rs_id2,condition2 = boundary_conditions[i+1]
        face1 = [i[:2] for i in condition1['out']]
        face2 = [i[:2] for i in condition2['in']]
        if rs_id1 in rotors_id:
            face1,face2 = face2,face1
        rotate_angle = 'positive'
        if rpm < 0:
            rotate_angle = 'negative'
        t = [one2one.patchedFace2Faces(blocks,ff1,face2,'rotor',rotate_angle,steady) for ff1 in face1]
        patchedData.extend(t)
        t = [one2one.patchedFace2Faces(blocks,ff2,face1,'stator',rotate_angle,steady) for ff2 in face2]
        patchedData.extend(t)

    # calculate rotated_degree
    if rotors:
        t = [abs(k[-1]) for tof,fromf in patchedData for k in fromf if abs(k[-1])>0.000001 and k[0][0] == rotors_id[0]]
        rotated_degree = min(t)/3.1415926*180

    if merged:
        for i in reversed(split_blocks):
            blocks, one2oneData, patchedData, boundary_result = one2one.MergeBlocks(blocks,i,i+1,one2oneData,patchedData,boundary_result)
    if merged:
        nrotors = rotors_old
    else:
        nrotors = rotors
    if rotors_old and steady is False:
        rotated_dict = {'axis':(0,0,1),'max':rotated_degree, 'rpm':rpm}
        rotatedBlocks = {i+1:rotated_dict for rotor in nrotors for i in rotor}
    else:
        rotatedBlocks = None
    #check oneonedata
    if merged:
        multi = stators_old + rotors_old
    else:
        multi = stators + rotors
    # for i in multi:
    #     print(i)
    for ii,(bl1,_,bl2,_) in enumerate(one2oneData):
        for sr in multi:
            if bl1-1 in sr:
                if bl2-1 in sr:
                    break 
                else:
                    print('warning',ii,bl1,bl2)
        else:
            print(ii,bl1,bl2)
            raise Exception('oneonedata error')
    return blocks,one2oneData,patchedData,boundary_result,rotatedBlocks

def set_inputfile(workdir,input_filename,mesh_file,LREF,stators=None,rotors=None,split_blocks = None,
                 merged=True,periodic_steps = 200,rpm = 0,number_of_time_step=2000,
                 CFL_number=5,xmach=None,env_viscosity=1.716e-5,env_temperature = None,
                 turbulence_model=5,
                 output_pressure = 106000,
                 **kargs):  

    bs = tecfile.read(mesh_file)
    bs = one2one.AdjustNegativeGrid(bs)
    Pt,Tt = kargs['total_pressure'] , kargs['total_temperature'] 
    t = AutoGenerateInputDdata(bs,stators=stators,rotors=rotors,
             split_blocks=split_blocks,rpm =rpm,merged=merged,bc2006 = kargs.get('bc2006',True),
             in_condition = (Pt,Tt),init_file = kargs.get('init_file'),workdir=workdir,steady=kargs.get('steady',False))
    bs,one2oneData,patchedData,boundary_result,rotatedBlocks = t
    if rotatedBlocks:
        keys = list(rotatedBlocks.keys())
        v = rotatedBlocks[keys[0]]['max']
        v /= periodic_steps
        t = rpm / 60
        dtime = v / (t*360)
        print('time step',dtime)
    else:
        dtime = 1e-5
    if kargs.get('steady'):
        number_of_time_step = 1
    IUNST = 1
    init_file = kargs.get('init_file')
    if init_file:
        init_file = 'init.q'
    a = input_cfl3d.inputFile(
        workdir=workdir,
        gridfile = bs,
        input_filename=input_filename,
        LREF = LREF,
        CFL_number=CFL_number,
        xmach = xmach,
        env_viscosity=env_viscosity,
        env_temperature = kargs['total_temperature'] ,
        env_pressure = kargs['total_pressure'],
        env_gamma = kargs['env_gamma'],
        turbulence_model=5,
        output_pressure = output_pressure,
        I2D = kargs.get('I2D',0),IUNST=kargs.get('IUNST',IUNST),MOVIE=kargs.get('MOVIE',0),
        rotated_center=kargs.get('rotated_center',True),
        NWREST=kargs.get('NWREST',100),IREST=kargs.get('IREST',0),
        number_of_time_step=number_of_time_step,time_step = dtime,
        BOUNDARY = boundary_result,
        oneOne = one2oneData,
        patchedData = patchedData,ITOSS = kargs.get('ITOSS',0),ITMAX = kargs.get('ITMAX',None),
        rotatedBlocks = rotatedBlocks,
        IPTYPE = kargs.get('IPTYPE',1),
        NCYC = kargs.get('NCYC',20),
        ITA = kargs.get('ITA',-2),
        NCG = kargs.get('NCG',2),
        restart_file = kargs.get('restart_file',None),
        IYXS = kargs.get('IYXS'),
        init_file = init_file,
        IALPH = kargs.get('IALPH',1)

    )
    a.start_write()
if __name__ == '__main__':
    g1 = '/home/yxs/F/pythonAPP/cfl3d_pyui/RS_work/rotate323_mesh.g'
    g2 = '/home/yxs/F/learning/CFL3D/323_0409/new_grid_323_0409_nogap/323_0409.g'
    g3 = '/home/yxs/F/learning/CFL3D/323_0409/ok/new_grid_323_0409_nogap/323_0409.g'
    set_inputfile(
        workdir='./test3',
        input_filename = 'rotate323_0409.inp',
        mesh_file = g3,
        LREF = 1.0/1000,
        stators=[range(15),range(15,25)],
        rotors=[range(25,40)],
        split_blocks=[19,24],
        rpm =15000,merged=False,periodic_steps=200,
        number_of_time_step=2000,
        MOVIE = 100,  #每多少步自动保存
        CFL_number=3,  
        xmach = 0.4,
        env_viscosity=1.716e-5,
        env_gamma = 1.4,
        total_pressure = 101325,
        total_temperature = 288.15,
        output_pressure = 106000,
        turbulence_model=5,
        IPTYPE = 0,
        NCYC = 20,
        ITA = -2,  #时间采用二阶精度
        NCG = 2,  #多重网格
        rotated_center=True,
        bc2006=False,
        IYXS = 3,
        IALPH=0,
        steady=False
        # init_file = '/home/yxs/F/learning/CFL3D/323_0409/numeca_0409_323_steady/new_grid_323_0409_nogap/323_0409_steady/323_0409_steady/323_0409_steady_323_0411_STEADY/323_0409_steady_323_0411_STEADY.q'
        # restart_file = '/home/yxs/F/learning/CFL3D/323_304/323_304_e1/rotate323_restart.bin',
    )