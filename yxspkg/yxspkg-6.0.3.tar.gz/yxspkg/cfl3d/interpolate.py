from yxspkg import tecfile 
import numpy as np
import math
import json
import sys
import time
from pathlib import Path
def get_one2one_data(inpfile):
    fp = open(inpfile)
    def getline(line):
        line = line.split()
        grid = int(line[1])
        istart_end = int(line[2]),int(line[5])
        jstart_end = int(line[3]),int(line[6])
        kstart_end = int(line[4]),int(line[7])
        v1 = int(line[8])
        v2 = int(line[9])
        return grid,(istart_end,jstart_end,kstart_end,v1,v2)
    one2oneData = None 
    shapes=[]
    periodicData = []
    file_suffix = inpfile.split('.')[-1]
    if file_suffix =='inp':
        while True:
            line = fp.readline().lower()
            if line.find('idim')!=-1 and line.find('jdim')!=-1 and line.find('kdim') !=-1:
                while True:
                    line = fp.readline().split()
                    if len(line) == 3:
                        shapes.append(tuple([int(i) for i in line]))
                    else:
                        break 
                continue
            if line.find('bctype') != -1 and line.find('ndata') != -1:
                nface = 0
                while True:
                    line = fp.readline().lower()
                    if line.find('mseq') != -1:
                        break 
                    if line.find('bctype') != -1 and line.find('ndata') != -1:
                        nface += 1
                    k = line.split()
                    if len(k) == 8 and k[0].isdigit():
                        if k[2].isdigit() and int(k[2]) == 2005:
                            fp.readline()
                            t = fp.readline().split()
                            periodicData.append((
                                int(k[0]),
                                nface,
                                int(k[3]),
                                int(k[4]),
                                int(k[5]),
                                int(k[6]),
                                int(t[0]),
                                float(t[1]),
                                float(t[2]),
                                float(t[3]),
                            ))

            if line.find('1-1') != -1:
                fp.readline()
                one_length = int(fp.readline())
                fp.readline()
                start = [getline(fp.readline()) for i in range(one_length)]
                fp.readline()
                end = [getline(fp.readline()) for i in range(one_length)]
                one2oneData = [(i1,i2,j1,j2) for (i1,i2),(j1,j2) in zip(start,end)]
                break
    elif file_suffix == 'json':
        json_data = json.load(open(inpfile))
        print(json_data)
    return one2oneData,periodicData,shapes

def get_face_pattern(one2oneData):
    def number_to_slice(i0,i1):
        if i1==i0:
            return i0-1
        elif i1>i0:
            return slice(i0,i1-1)
        else:
            return slice(i0-2,i1-1,-1)
    def parse11(odata,tdata):
        blockid,d1 = odata
        tid,d2 = tdata
        r1 = [number_to_slice(*i) for i in d1[:3]]
        r2 = [number_to_slice(*i) for i in d2[:3]]
        if (d1[-2]-d1[-1])*(d2[-2]-d2[-1]) < 0:
            is_trans = True 
        else:
            is_trans = False 
        return blockid-1,r1,tid-1,r2,is_trans
    return [parse11(i[:2],i[2:]) for i in one2oneData]


def interpolate_center2grid(qdata, patterns ,scalars=[],is_double=False):
    #qdata 以及 qdata【0】都是list数据类型
    if isinstance(qdata[0], dict):
        keys = [i for i in qdata[0] if isinstance(i, int)]
        keys.sort()
        aux_data = [{key:val for key,val in q.items() if isinstance(key, str)} for q in qdata]
        qdata = [[i[k] for k in keys] for i in qdata]
    else:
        keys = None
    patterns = [i if i else [] for i in patterns]
    def interpolate_body(data):
        #插值网格块内的数据
        if is_double:
            fdtype='float64'
        else:
            fdtype='float32'
        temp = np.zeros([i+1 for i in data.shape],dtype=fdtype)
        temp[1:-1, 1:-1, 1:-1] = 0.125*(data[1:, 1:, 1:] + data[1:, :-1, 1:] + data[1:, :-1, :-1] + data[1:, 1:, :-1] +
                                        data[:-1, 1:, 1:] + data[:-1, :-1, 1:] + data[:-1, :-1, :-1] + data[:-1, 1:, :-1])
        #面网格采取4分之一的
        p=(0,-1)
        temp[p,1:-1,1:-1] = (data[p,1:,1:] + data[p,:-1,:-1] + data[p,1:,:-1] + data[p,:-1,1:])/4
        temp[1:-1,p,1:-1] = (data[1:,p,1:] + data[:-1,p,:-1] + data[1:,p,:-1] + data[:-1,p,1:])/4
        temp[1:-1,1:-1,p] = (data[1:,1:,p] + data[:-1,:-1,p] + data[1:,:-1,p] + data[:-1,1:,p])/4
        #棱网格取二分之一，
        i,j = list(zip(*[(i,j) for i in [0,-1] for j in [0,-1]]))
        temp[i,j,1:-1] = (data[i,j,1:] + data[i,j,:-1])/2
        temp[i,1:-1,j] = (data[i,1:,j] + data[i,:-1,j])/2
        temp[1:-1,i,j] = (data[1:,i,j] + data[:-1,i,j])/2
        # 顶点取最近一个点
        i,j,k = list(zip(*[(i,j,k) for i in [0,-1] for j in [0,-1] for k in [0,-1]]))
        temp[i,j,k] = data[i,j,k]
        return temp
    grid_data = [[interpolate_body(data) for data in qs] for qs in qdata]
    face_pattern, line_pattern, point_pattern, periodic_pattern = patterns
    #面网格插值
    for bid1, r1, bid2, r2, is_trans in face_pattern:
        i1,j1,k1 = r1 
        i2,j2,k2 = r2
        for nd in range(len(qdata[0])):
            data1 = grid_data[bid1][nd]
            data2 = grid_data[bid2][nd]
            if is_trans:
                data1[i1,j1,k1] = (data1[i1,j1,k1] + data2[i2,j2,k2].T )/2
                data2[i2,j2,k2] = data1[i1,j1,k1].T
            else:
                data1[i1,j1,k1] =( data1[i1,j1,k1] + data2[i2,j2,k2])/2
                data2[i2,j2,k2] = data1[i1,j1,k1]
    #棱网格插值 和 角点网格插值
    for lines in line_pattern+point_pattern:
        for nd in range(len(qdata[0])):
            t0 = None 
            coeff0 = 0
            for bid,i,j,k,coeff in lines:
                coeff0 += coeff
                t = grid_data[bid][nd][i,j,k]*coeff
                if t0 is None:
                    t0 = t 
                else:
                    t0 += t
            t0 /= coeff0
            for bid,i,j,k,coeff in lines:
                grid_data[bid][nd][i,j,k] = t0
    #周期面处理
    if periodic_pattern:
        per_pattern,per_points,vectors = periodic_pattern
        if not scalars:
            vector_set = set([j for i in vectors for j in i])
            for i in range(len(qdata[0])):
                if i not in vector_set:
                    scalars.append(i)

        for bid1, r1, theta1, bid2, r2, theta2, is_trans in per_pattern:
            i1,j1,k1 = r1 
            i2,j2,k2 = r2
            data1 = grid_data[bid1]
            data2 = grid_data[bid2]
            for nd in scalars:
                t = (data1[nd][i1,j1,k1] + data2[nd][i2,j2,k2])/2 
                data1[nd][i1,j1,k1] = t
                data2[nd][i2,j2,k2] = t
            for vdx,vdy in vectors:
                tx = data1[vdx][i1,j1,k1]*math.cos(theta1) + data1[vdy][i1,j1,k1]*math.sin(theta1)
                ty = data1[vdx][i1,j1,k1]*(-math.sin(theta1)) + data1[vdy][i1,j1,k1]*math.cos(theta1)
                tx = (data2[vdx][i2,j2,k2] + tx)/2 
                ty = (data2[vdy][i2,j2,k2] + ty)/2

                data2[vdx][i2,j2,k2] = tx
                data2[vdy][i2,j2,k2] = ty
                data1[vdx][i1,j1,k1] = tx*math.cos(theta2) + ty*math.sin(theta2)
                data1[vdy][i1,j1,k1] = tx*(-math.sin(theta2)) + ty*math.cos(theta2)
        #周期面上存在非周期块上的点时 用周期面上的点赋值
        for ps in per_points:
            bidp,ip,jp,kp,_ = ps[0]
            for nd in range(len(qdata[0])):
                ds = grid_data[bidp][nd][ip,jp,kp]
                for bid,i,j,k,_ in ps[1]:
                    grid_data[bid][nd][i,j,k] = ds

    if keys is not None:
        grid_data = [{key:val for key,val in zip(keys,q)} for q in grid_data]
        [gdata.update(adata) for gdata,adata in zip(grid_data,aux_data)]
    return grid_data
def get_lines_common(one2oneData):
    def number_to_line(data):
        _,d1 = data
        axis1,axis2 = d1[-2]-1,d1[-1]-1
        axis0 = 3-axis1-axis2
        pos1 = [None,None,None]
        pos1[axis1] = d1[axis1]
        pos1[axis2] = d1[axis2][0]
        pos1[axis0] = d1[axis0][0]

        pos2 = [None,None,None]
        pos2[axis1] = d1[axis1]
        pos2[axis2] = d1[axis2][1]
        pos2[axis0] = d1[axis0][0]

        pos3 = [None,None,None]
        pos3[axis1] = d1[axis1][0]
        pos3[axis2] = d1[axis2]
        pos3[axis0] = d1[axis0][0]

        pos4 = [None,None,None]
        pos4[axis1] = d1[axis1][1]
        pos4[axis2] = d1[axis2]
        pos4[axis0] = d1[axis0][0]
        return (pos1,axis1),(pos2,axis1),(pos3,axis2),(pos4,axis2)
    def parse_line(odata,tdata):
        if tdata[0]<odata[0]:
            tdata,odata = odata,tdata
        blockid1 = odata[0]
        blockid2 = tdata[0]

        olines = number_to_line(odata)
        tlines = number_to_line(tdata)

        return [((blockid1,l1),(blockid2,l2)) for l1,l2 in zip(olines,tlines)]

    def adjust_lines_order(lines):
        (bid1,(ijk1,axis1)),(bid2,(ijk2,axis2)) = lines
        if ijk1[axis1][0] > ijk1[axis1][1]:
            ijk1[axis1] = ijk1[axis1][1],ijk1[axis1][0]
            ijk2[axis2] = ijk2[axis2][1],ijk2[axis2][0]
        return (bid1,(tuple(ijk1),axis1)),(bid2,(tuple(ijk2),axis2))
    lineinfo2 = [adjust_lines_order(j) for i in one2oneData for j in parse_line(i[:2],i[2:])]
    lineinfo2.sort(key=lambda x:min(x[0][0],x[1][0]))
    lines_list = []
    for line1,line2 in lineinfo2:
        for lset in lines_list:
            if (line1 in lset) or (line2 in lset):
                lset.add(line1)
                lset.add(line2)
                break 
        else:
            lines_list.append(set((line1,line2)))
    return [tuple(i) for i in lines_list]
def get_line_pattern(lines_commom,shapes):
    def convert_to_slice(line,shape):
        bid,(ijk,axis) = line 
        bid -= 1
        t1,t2 = ijk[axis]
        axis1 = (axis+1)%3 
        axis2 = (axis+2)%3
        if (ijk[axis1] == 1 or ijk[axis1] == shape[axis1]) and (ijk[axis2]==1 or ijk[axis2] == shape[axis2]):
            coeff = 2 
        else:
            coeff = 4
        if t2>t1:
            t = slice(t1,t2-1)
        else:
            t = slice(t1-2,t2-1,-1)
        i = t if axis==0 else ijk[0]-1
        j = t if axis==1 else ijk[1]-1
        k = t if axis==2 else ijk[2]-1
        return bid,i,j,k,coeff
    return [[convert_to_slice(j,shapes[j[0]-1]) for j in i] for i in lines_commom]
def get_point_pattern(lines_common,shapes):
    def get_coeff(idim,jdim,kdim,i,j,k):
        s = 0
        if i==0 or i==idim:
            s+=1 
        if j==0 or j==jdim:
            s+=1
        if k==0 or k==kdim:
            s+=1
        if s==3:
            coeff = 1 
        elif s==2:
            coeff = 2 
        elif s==1:
            coeff = 4
        else:
            raise Exception('error')
        return coeff
    def split_2_points(line,shape):
        bid,(ijk,axis) = line 
        bid -= 1
        t1,t2 = ijk[axis]
        t1-=1
        t2-=1
        i1 = t1 if axis==0 else ijk[0]-1
        j1 = t1 if axis==1 else ijk[1]-1
        k1 = t1 if axis==2 else ijk[2]-1

        i2 = t2 if axis==0 else ijk[0]-1
        j2 = t2 if axis==1 else ijk[1]-1
        k2 = t2 if axis==2 else ijk[2]-1
        idim,jdim,kdim = shape 
        idim,jdim,kdim = idim-1,jdim-1,kdim-1
        coeff1 = get_coeff(idim,jdim,kdim,i1,j1,k1)
        coeff2 = get_coeff(idim,jdim,kdim,i2,j2,k2)
        return (bid,i1,j1,k1,coeff1),(bid,i2,j2,k2,coeff2)
    def is_union(point_list,ps):
        is_in = False
        for p in ps:
            for pset in point_list:
                if p in pset:
                    pset.update(ps)
                    is_in = True
                    break 
            if is_in:
                break 
        if not is_in:
            point_list.append(set(ps))
    def update_point_list(points):
        point_list = [set(points[0]) ]
        for ps in points[1:]:
            ps_in_list = False
            for p in ps:
                for i in point_list:
                    if p in i:
                        i.update(ps)
                        ps_in_list = True
                        break 
            if ps_in_list is False:
                point_list.append(set(ps))
        return point_list
    points = [kk for i in lines_common for kk in zip(*[split_2_points(j,shapes[j[0]-1]) for j in i])]
    point_result = update_point_list(points)
    return point_result
def get_periodic_pattern(periodicData,shapes):

    def convert_to_per(f1,f2,shapes):
        #bid1, r1, theta1, bid2, r2, theta2, is_trans
        bid1,faceid1,theta1 = f1[0],f1[1],f1[-1]
        bid2,faceid2,theta2 = f2[0],f2[1],f2[-1]
        r1 = [slice(None,None)]*3 
        r1[faceid1//2] =0 if faceid1 % 2 == 0 else -1 
        r2 = [slice(None,None)]*3 
        r2[faceid2//2] =0 if faceid2 % 2 == 0 else -1 
        theta1 = theta1/180*math.pi 
        theta2 = theta2/180*math.pi
        return bid1-1,r1,theta1,bid2-1,r2,theta2,False
    to_faces = [i for i in periodicData if i[-1]>0]
    from_faces = [i for i in periodicData if i[-1]<0]
    periodic_faces = []
    for i in from_faces:
        for j in to_faces:
            if i[6]==j[0]:
                periodic_faces.append(convert_to_per(i,j,shapes))
                break 
    return periodic_faces
def get_patterns(input_file,vectors=None):
    def get_face_of_line(bid,i,j,k):
        if not isinstance(i,int):
            if j==0:
                if k==0:
                    faces = 2,4
                else:
                    faces = 2,5
            else:
                if k==0:
                    faces = 3,4
                else:
                    faces = 3,5
        elif not isinstance(j,int):
            if i==0:
                if k==0:
                    faces=0,4
                else:
                    faces=0,5
            else:
                if k==0:
                    faces=1,4
                else:
                    faces=1,5
        else:
            if i==0:
                if j==0:
                    faces = 0,2
                else:
                    faces = 0,3
            else:
                if j==0:
                    faces = 1,2 
                else:
                    faces = 1,3
        return [(bid,i) for i in faces]
    def in_periodic_face(lines,per_faces,per_blocks):
        if len(lines)<=2:
            return None
        result = []
        first_line = None
        for lid,(bid,i,j,k,coeff) in enumerate(lines):
            if coeff==4:
                return None
            if (bid in per_blocks) or (first_line is not None):
                for pface in get_face_of_line(bid,i,j,k):
                    if pface in per_faces:
                        if first_line is None:
                            # input('hhhhhhhh')
                            result.extend(lines[0:lid])
                            first_line = bid,i,j,k,None
                            # print(result)
                        break
                else:
                    if first_line is not None:
                        # input('99999999999')
                        result.append((bid,i,j,k,None))
                        # print(first_line,result)

        if first_line:
            return expand_line(first_line),[expand_line(i) for i in result]
        else:
            return None
    def expand_slice(sl):
        start = sl.start 
        end = sl.stop
        step = sl.step 
        if step is None:
            step = 1 
        return slice(start-step,end+step,step)
    def expand_line(line):
        #将线扩展到周边的棱和顶点处 
        bid,i,j,k,coeff = line 
        if not isinstance(i,int):
            i = expand_slice(i)
        elif not isinstance(j,int):
            j = expand_slice(j)
        else:
            k = expand_slice(k)
        return bid,i,j,k,coeff
    one2oneData,periodicData,shapes = get_one2one_data(input_file)

    face_pattern = get_face_pattern(one2oneData)
    lines_common = get_lines_common(one2oneData)
    line_pattern = get_line_pattern(lines_common,shapes)
    point_pattern = get_point_pattern(lines_common,shapes)
    if periodicData:
        periodic_pattern = get_periodic_pattern(periodicData,shapes)
        vectors = vectors if vectors else [] 
        per_faces = set([(i[0]-1,i[1]) for i in periodicData])
        per_blocks = set([i[0]-1 for i in periodicData])
        lines_per = [in_periodic_face(i,per_faces,per_blocks) for i in line_pattern]
        lines_per = [i for i in lines_per if i]
        periodic_pattern = periodic_pattern,lines_per,vectors
    else:
        periodic_pattern = None

    return face_pattern,line_pattern,point_pattern,periodic_pattern
def auto_run(json_file = 's.json'):
    jdata = json.loads(open(json_file).read())
    patterns = get_patterns(jdata['inpfile'],vectors=jdata.get('vectors',[]))
    is_double = jdata.get('double',False)
    datafile = jdata['datafile']
    if isinstance(datafile,str):
        datafile = [datafile,]
    outfile = jdata.get('outfile',None)
    if outfile is None:
        outfile = [str(Path(i).with_name('grid_'+Path(i).name)) for i in datafile]
    for i,j  in zip(datafile,outfile):
        print(i)
        qdata = tecfile.read(i)
        t = interpolate_center2grid(qdata,patterns,is_double=is_double)
        tecfile.write(j,t)
if __name__=='__main__':
    import time 
    s = time.time()
    auto_run("/home/yxs/F/learning/CFL3D/CFL3D/Stage-B_SA_pb99240-6.7.2/s.json")
    e = time.time()
    print('time: {:.4}s'.format(e-s))