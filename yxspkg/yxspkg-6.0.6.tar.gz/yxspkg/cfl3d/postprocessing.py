from pathlib import Path
import json
from . import data_format as df
from . import interpolate
from yxspkg import tecfile
import sys
import numpy as np
from . import RSCal
def get_info(inpfile):
    print(inpfile)
    fp = open(inpfile)
    fp.readline()
    mesh_file = fp.readline().strip()
    output_mesh = fp.readline().strip()
    output_q = fp.readline().strip()
    info = {'mesh_file':mesh_file,'output_mesh':output_mesh,"output_q":output_q}
    while True:
        s = fp.readline().lower()
        if s.find("mach")!=-1 and s.find('ialph')!=-1:
            data = [float(i) for i in fp.readline().split()]
            info['mach'] = data[0]
            info['reue'] = data[3]
            info['T'] = data[4]/9*5
            break 
    json_data = ''
    for i in fp:
        if i.startswith('{'):
            json_data = i
            break
    if json_data:
        json_data += fp.read()
        json_data = json.loads(json_data)
        info.update(json_data)
    return info
    
def cal_area_zone(zone,xtag = 'CoordinateX', ytag = 'CoordinateY', ztag='CoordinateZ'):
    def cal_area(p1,p2,p3,p4):
        v1 = np.cross(p2-p1,p3-p1)*0.5
        v1+= np.cross(p3-p1,p4-p1)*0.5 
        s  = ((v1**2).sum(axis=-1)**0.5)[:,:,:,None]
        return np.concatenate((v1,s),axis=-1)
    t=np.concatenate((zone[xtag][:,:,:,None],zone[ytag][:,:,:,None],zone[ztag][:,:,:,None]),axis=-1)
    p1 = t[:-1,:-1,:-1]
    p2 = t[ 1:,:-1,:-1]
    p3 = t[ 1:, 1:,:-1]
    p4 = t[:-1, 1:,:-1]
    p5 = t[:-1,:-1, 1:]
    p6 = t[ 1:,:-1, 1:]
    p7 = t[ 1:, 1:, 1:]
    p8 = t[:-1, 1:, 1:]
    s1 = cal_area(p1,p4,p8,p5)
    s2 = cal_area(p2,p3,p7,p6)
    s3 = cal_area(p2,p1,p5,p6)
    s4 = cal_area(p3,p4,p8,p7)
    s5 = cal_area(p1,p2,p3,p4)
    s6 = cal_area(p5,p6,p7,p8)
    return s1,s2,s3,s4,s5,s6
def main():
    if len(sys.argv)>1:
        inpfile = Path(sys.argv[1] )
    else:
        inps = [i for i in Path('./').glob('*.inp') if i.name != 'tempz3y2x1.inp']
        if len(inps) > 1:
            print("which file?")
            for i,f in enumerate(inps):
                print(f"{i+1}: {f}")
            x = input("type the number:")
            inpfile = inps[int(x)-1]
        elif len(inps)==0:
            print("no available file")
            inpfile = None
        else:
            inpfile = inps[0]
    if not inpfile:
        return
    info = get_info(inpfile)
    togrid = info.get('togrid',None)
    if togrid:
        patterns = interpolate.get_patterns(str(inpfile),vectors=info.get('vectors',[]))
        is_double = info.get("double",False)
    while True:
        datafile = info['output_q']
        outfile = str(info.get('output','*.szplt'))
        if outfile.find('*')!=-1:
            stem = Path(datafile).stem 
            outfile = outfile.replace('*',stem)
        qdata = tecfile.read(datafile)
        if togrid:
            qdata = interpolate.interpolate_center2grid(qdata,patterns,is_double=is_double)

        if outfile.endswith('szplt'):
            rho = info.get('density',None)
            R = info.get('R',287.14)
            gamma = info.get('gamma',1.4)
            T = info['T']
            if rho:
                P = rho*R*T 
            else:
                P = info['pressure']
            t = df.q2szplt(None,info['mesh_file'],qdata,P,T,gamma=gamma,R=R)
        else:
            t = qdata
        tecfile.write(outfile,t)
        break
    return outfile
def center_value(data):
    return 0.25*(data[1:, 1:] + data[:-1, 1:] + data[ :-1, :-1] + data[ 1:, :-1])
def get_area(face,areas):
    blockid,faceSE = face 
    area = areas[blockid]
    faceSE = faceSE.upper()
    if faceSE == 'I0':
        farea = area[0][0,:,:]
    elif faceSE == 'K0':
        farea = area[4][:,:,0]
    elif faceSE == 'KE':
        farea = area[5][:,:,-1]
    else:
        print("error")
        exit() 
    return farea 
def get_var(face,zones,var,farea):
    blockid,faceSE = face 
    zone = zones[blockid]
    value = zone[var]
    faceSE = faceSE.upper()
    if faceSE == 'I0':
        fvar  = value[0,:,:]
    elif faceSE == 'K0':
        fvar  = value[:,:,0]
    elif faceSE == 'KE':
        fvar  = value[:,:,-1]
    else:
        print("error")
        exit() 
    if farea.shape[0] != fvar.shape[0]:
        fvar = center_value(fvar)
    return fvar
def get_mass(face,zones,areas,vrho="Density",vu='VelocityX',vv='VelocityY',vw='VelocityZ'):
    farea = get_area(face,areas)
    rho   = get_var(face,zones,vrho,farea)
    u     = get_var(face,zones,vu  ,farea)
    v     = get_var(face,zones,vv  ,farea)
    w     = get_var(face,zones,vw  ,farea)
    mass  = (u*farea[:,:,0]+v*farea[:,:,1]+w*farea[:,:,2])*rho 
    if face[1][1] == '0':
        mass *= -1
    s = farea[:,:,3].sum()
    return mass,s
def face_sum(face,zones,var,areas,weight='area'):
    farea= get_area(face,areas)
    fvar = get_var(face,zones,var,farea)
    if weight == 'area':
        farea = farea[:,:,3]
    elif weight == 'mass':
        farea = get_mass(face,zones,areas)[0]
    return (farea*fvar).sum(),farea.sum()
def multi_faces_average(faces,zones,areas,var='Pressure',weight='area'):
    v0,s0 = 0,0
    for i in faces:
        v,s = face_sum(i[:2],zones,var,areas,weight)
        v0 += v 
        s0 += s 
    return v0/s0
def convert2blocks(zone,xtag = 'CoordinateX', ytag = 'CoordinateY', ztag='CoordinateZ'):
    return {'X':zone[xtag],'Y':zone[ytag],'Z':zone[ztag]}
def cal_mass(faces,zones,areas):
    v0, s0 = 0,0 
    for i in faces:
        v,s = get_mass(i[:2],zones,areas)
        v0 += v.sum()
        s0 += s 
    return v0
def cal_average(zones,stages = None):
    areas = [cal_area_zone(zones[i]) for i in range(len(zones))]
    blocks= [convert2blocks(zones[i]) for i in range(len(zones))]
    t = RSCal.RotorStatorCal(blocks)
    faces_in = t['in']
    faces_out= t['out']
    mass_in = cal_mass(faces_in,zones,areas)
    mass_out= cal_mass(faces_out,zones,areas)
    pt_in = multi_faces_average(faces_in,zones,areas,weight='mass',var='PressureStagnation')
    pt_out = multi_faces_average(faces_out,zones,areas,weight='mass',var='PressureStagnation')
    tt_in = multi_faces_average(faces_in,zones,areas,weight='mass',var='TemperatureStagnation')
    tt_out = multi_faces_average(faces_out,zones,areas,weight='mass',var='TemperatureStagnation')
    k = 1.4 
    pi = pt_out/pt_in 
    coeff = (pi**((k-1)/k)-1)/(tt_out/tt_in-1)
    print('进口总压',pt_in)
    print('出口总压',pt_out)
    print('压比',pi)
    print('进口总温',tt_in)
    print('出口总温',tt_out)
    print('温比',tt_out/tt_in)
    print('效率',coeff)
    print('进口流量', abs(mass_in))
    print('出口流量',abs(mass_out))
    return pt_in,pt_out,pi,coeff,abs(mass_in),abs(mass_out)
if __name__=='__main__':
    outfile = main()
    # cfl3d_case = '/home/yxs/F/learning/CFL3D/323_0409/ok/series/323_new_bound_0001/rotate323_0409_lref1_output.szplt'
    f = tecfile.read(outfile)
    cal_average(f)
    # print(f[0]['CoordinateX'][:,:,:,None])
    