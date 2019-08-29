from pathlib import Path
import time
import math
import numpy as np 
from yxspkg import tecfile
from functools import wraps
import re
from scipy.interpolate import RegularGridInterpolator
def result_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t = func(*args, **kwargs)
        if t is None:
            return np.array([])
        t = [i.split() for i in t]
        try:
            t = np.array(t,dtype='float64')
        except:
            print(t)
        if not t.any():
            return t
        self = args[0]
        if self.blk is None:
            #取self.blk 为blk序列中的众数
            m = t[:,1]
            m = m[1:] - m[:-1]
            m = t[:,1][np.where(m==0)]
            self.blk = m[0]

        t = t[np.where(np.abs(t[:,1] - self.blk)<0.01)]
        return t
    return wrapper
class Residual:
    def __init__(self,filename):
        self.filename = Path(filename)
        self.pos=-1
        self.titles = None
        self.re_res = None
        self.latest_mtime = 0
        self.re_res = self.get_re_res()
        self.blk = None
    def get_re_res(self):
        fp = open(self.filename,'r')
        for i in fp:
            if i.find('total res.')!=-1:
                self.titles = re.split(' {2,}',i)
                n = len(self.titles) - 3
                return re.compile('\s+\d+\s+\d+\s+\d+\s+([-\.\d]+E[\+-]\d+\s+){{{n}}}'.format(n = n))
        return None

    @result_wrapper
    def get(self):
        mtime = self.filename.lstat().st_mtime
        if mtime <= self.latest_mtime:
            return []
        self.latest_mtime = mtime
        fp = open(self.filename,'r')
        if self.re_res is None:
            t = self.get_re_res()
            if t is not None:
                self.re_res = t
            else:
                return None
        fp.seek(self.pos+1,0)
        res_list = [i for i in fp if self.re_res.match(i)]
        self.pos = fp.tell()
        return res_list
    def get_history(self):
        fp = open(self.filename,'r')
        is_title = False
        title_re = re.compile(' *iteration *residual *CL *CD *CY *CMY.*')
        data_re  = re.compile('( +\d+)( +[\.\dEe\+\-]+)( +[\.\dEe\+\-]+)( +[\.\dEe\+\-]+)( +[\.\dEe\+\-]+)( +[\.\dEe\+\-]+)')
        result = []
        for line in fp:
            if title_re.match(line):
                is_title = True 
                continue
            if is_title==True:
                t = data_re.findall(line)
                if t:
                    result.append(t)
                else:
                    break
        if not is_title:
            return np.array([])
        result = np.array(result,dtype = 'float32').reshape((len(result),-1))
        if len(result) > 200:
            k = len(result) // 200
            result = result[::k,:]
        result = np.hstack((result[:,-2:],result,(result[:,-2:])))
        result[:,4] = result[:,3]
        return result
def q2szplt(szplt_name,g,q,P,T,lref=1,gamma=1.4,R=287.14):
    if isinstance(g,str):
        g = tecfile.read(g) 
    if isinstance(q,str):
        q = tecfile.read(q)
    Tref = T
    Pref = P
    Rhoref = Pref/(R*Tref)
    aref = (gamma*R*Tref)**0.5
    result = dict()
    cp = gamma/(gamma-1)*R
    for zone_id,(mesh,data) in enumerate(zip(g,q)):
        density = data[0]
        u = data[1]/density 
        v = data[2]/density 
        w = data[3]/density
        p = (data[4]-0.5*(u*u+v*v+w*w)*density)*(gamma-1)
        T = ((gamma*p)/density)*Tref
        u *= aref
        v *= aref
        w *= aref
        density =density * Rhoref
        velocity = (u*u+v*v+w*w)**0.5
        p *= Rhoref*aref*aref
        
        t_total = T + velocity**2/(2*cp)
        ptp = (t_total/T)**(gamma/(gamma-1))
        p_total = p*ptp
        new_dict ={}
        new_dict['X'] = mesh['X']
        new_dict['Y'] = mesh['Y']
        new_dict['Z'] = mesh['Z']
        new_dict['density'] = density
        new_dict['velocity_x'] = u 
        new_dict['velocity_y'] = v 
        new_dict['velocity_z'] = w 
        new_dict['velocity_mag'] = velocity
        new_dict['pressure']=p 
        new_dict['total_pressure'] = p_total
        new_dict['temperature']=T 
        new_dict['total_temperature']=t_total
        result['zone_{}'.format(zone_id)] = new_dict
    tecfile.write(szplt_name,result)
    return result
def q2nq(q,density0,temperature,gamma=1.4,R=287.14):
    acu_vel = (gamma*R*temperature)**0.5
    result = []
    for data in q:
        density = data[0]
        u = data[1]/density 
        v = data[2]/density 
        w = data[3]/density
        p = (data[4]-0.5*(u*u+v*v+w*w)*density)*(gamma-1)
        u *= acu_vel 
        v *= acu_vel 
        w *= acu_vel
        density =density * density0 
        p *= density0*acu_vel*acu_vel
        new_dict ={}
        new_dict[0] = density
        new_dict[1] = u 
        new_dict[2] = v 
        new_dict[3] = w 
        new_dict[4] = p 
        result.append(new_dict)
    return result
def nq2q(nq,density0,temperature,velocity,gamma=1.4,R=287.14):
    acu_vel = (gamma*R*temperature)**0.5
    result = []
    for data in nq:
        density = data[0]/density0 
        u = data[1] / acu_vel
        v = data[2] / acu_vel
        w = data[3] / acu_vel
        p = data[4] /(density0*acu_vel**2)
        e = p/(gamma-1)+0.5*density*(u*u+v*v+w*w)
        u *= density 
        v *= density 
        w *= density
        new_dict = dict() 
        new_dict[0] = density 
        new_dict[1] = u 
        new_dict[2] = v 
        new_dict[3] = w 
        new_dict[4] = e 
        new_dict['time'] = 0.0
        new_dict['mach'] = 0.0
        new_dict['Re'] = 0.0 
        new_dict['alpha'] = 0.0
        result.append(new_dict)
    return result
def szplt2nq(szplt):
    t = szplt
    keys = list(t.keys())
    keys.sort(key = lambda x:int(x[6:]))
    nqfile = []
    gfile = []
    for i in keys:
        data = t[i]
        g = {'X':data['CoordinateX'],'Y':data['CoordinateY'],'Z':data['CoordinateZ']}
        gfile.append(g)
        q_dict={
            0:data['Density'],
            1:data['VelocityXYZ.vx'],
            2:data['VelocityXYZ.vy'],
            3:data['VelocityXYZ.vz'],
            4:data['Pressure'],
            'mach':0.0,
            'alpha':0.0,
            'Re':1.0,
            'time':1.0
        }
        nqfile.append(q_dict)
    return nqfile,gfile
def interpolateblock(data,toshape,method='linear'):
    fromshape = data.shape
    if fromshape == toshape:
        return data    
    x = np.linspace(0,1,fromshape[0])
    y = np.linspace(0,1,fromshape[1])
    z = np.linspace(0,1,fromshape[2])
    inter_fun = RegularGridInterpolator((x,y,z),data,method=method)
    x2 = np.linspace(0,1,toshape[0])
    y2 = np.linspace(0,1,toshape[1])
    z2 = np.linspace(0,1,toshape[2])
    f = np.meshgrid(x2,y2,z2,indexing='ij')
    t = np.stack(f,axis=3)
    k = inter_fun(t)
    return k
def rotate_block(block,angle):
    sint = math.sin(angle)
    cost = math.cos(angle)
    x = block['X']*cost-sint*block['Y']
    block['Y'] = sint*block['X'] + cost*block['Y']
    block['X'] = x 
    return block

if __name__=='__main__':
    # f = '/home/yxs/F/learning/CFL3D/323_304/323_304_e2/rotate323_cfl3d.out'
    # f2 = '/home/yxs/F/pythonAPP/cfl3d_pyui/RS_work/rotate323_cfl3d.out'
    # res = Residual(f2)
    # k = res.get_history()
    # print(k.shape)
    # for i in k:
    #     print(i)
    # print(res.titles)
    # print(k)

    # p = Path('/home/yxs/F/learning/CFL3D/CFL3D/U-Duct-e6-SA_6.7.2/cfl3d.out')
    # print(p.lstat())
    from yxspkg import tecfile
    q2szplt(
        '/home/yxs/F/learning/CFL3D/323_0409/ok/steady_323_0409_ok_freeze(复件)/rotate323_0409_lref1_output.szplt',
        '/home/yxs/F/learning/CFL3D/323_0409/ok/steady_323_0409_ok_freeze(复件)/rotate323_0409_lref1_output.g',
        '/home/yxs/F/learning/CFL3D/323_0409/ok/steady_323_0409_ok_freeze(复件)/q_and_boundary.q',
        90748.287,279.215
    )
   
    # def double_shape(shape):
    #     i,j,k = shape 
    #     return i,321,101
    # a = tecfile.read('/home/yxs/F/pythonAPP/julia_CFD/transdiff_p3d.g')
    # a = [{key:interpolateblock(i[key],double_shape(i[key].shape)) for key in "XYZ"} for i in a]
    # tecfile.write("/home/yxs/F/pythonAPP/julia_CFD/transdiff_p3d2.g",a)
    # qfile = '/home/yxs/F/learning/CFL3D/323_0409/numeca_0409_323_steady/new_grid_323_0409_nogap/323_0409_steady/323_0409_steady/323_0409_steady_323_0411_STEADY/323_0409_steady_323_0411_STEADY.q'
    # q = tecfile.read(qfile)
    # gfile = '/home/yxs/F/learning/CFL3D/323_0409/test2/rotate323_0409_mesh.g'
    # g = tecfile.read(gfile)
    # bs = [rotate_block(g[i],-4/180*3.1415) for i in range(15,15+12)]
    # g = g[:15]+bs+g[27:]
    # print(len(g))
    # tecfile.write('/home/yxs/F/learning/CFL3D/323_0409/test2/rotate323_0409_mesh2.g',g)
    # print(len(g),len(q))
    # for i,j in zip(g,q):
    #     toshape = i['X'].shape
    #     for key,value in j.items():
    #         if isinstance(key,str):
    #             continue
    #         todata = interpolateblock(value,toshape)
    #         # print(todata.dtype,key)
    #         j[key] = todata
    # print(q[0][0].shape,g[0]['X'].shape)
    # q = tecfile.read('/home/yxs/F/learning/CFL3D/323_0409/323_new_bc2009_unsteady/1/mesh_0006.q')
    # t = q2nq(q,1.34115,232.558)
    # tecfile.write('/home/yxs/F/learning/CFL3D/323_0409/323_new_bc2009_unsteady/1/mesh_0006_nq.q',t)
    # tecfile.write('/home/yxs/F/learning/CFL3D/323_0409/cfl3d_test_0409_323grid/rotate323_0409_mesh.q',q)
    # nq = tecfile.read('/home/yxs/F/pythonAPP/cfl3d_pyui/initial_field_test/init_nq.q')
    # q2 = nq2q(nq,1.2,300,200)
    # for i,j in zip(q,q2):
    #     for m in range(5):
    #         d1 = i[m]
    #         d2 = j[m]
    #         d = np.abs(d1-d2)
    #         d = d.max() - d.min()
    #         if d>1e-6:
    #             raise Exception('error')
    # tecfile.write('init_test.q',q2)
    # szplt = tecfile.read('/home/yxs/F/learning/CFL3D/323_0409/numeca_0409_323_steady/new_grid_323_0409_nogap/323_0409_steady/323_0409_steady/323_0409_steady_323_0411_STEADY/323_0409_steady_323_0411_STEADY.szplt')
    # nq,g = szplt2nq(szplt)
    # q = nq2q(nq,1.2,280,122)
    # tecfile.write('/home/yxs/F/learning/CFL3D/323_0409/numeca_0409_323_steady/new_grid_323_0409_nogap/323_0409_steady/323_0409_steady/323_0409_steady_323_0411_STEADY/323_0409_steady_323_0411_STEADY.g',g)
    # tecfile.write('/home/yxs/F/learning/CFL3D/323_0409/numeca_0409_323_steady/new_grid_323_0409_nogap/323_0409_steady/323_0409_steady/323_0409_steady_323_0411_STEADY/323_0409_steady_323_0411_STEADY.q',q)
