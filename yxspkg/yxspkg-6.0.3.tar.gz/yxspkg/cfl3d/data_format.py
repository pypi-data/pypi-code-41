from yxspkg import tecfile

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
        new_dict['CoordinateX'] = mesh['X']
        new_dict['CoordinateY'] = mesh['Y']
        new_dict['CoordinateZ'] = mesh['Z']
        new_dict['Temperature']=T 
        new_dict['TemperatureStagnation']=t_total
        new_dict['Pressure']=p 
        new_dict['PressureStagnation'] = p_total
        new_dict['VelocityX'] = u 
        new_dict['VelocityY'] = v 
        new_dict['VelocityZ'] = w 
        new_dict['VelocityMagnitude'] = velocity
        new_dict['Density'] = density
        
        
        
        result['zone{}'.format(zone_id+1)] = new_dict
    if szplt_name:
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

if __name__=='__main__':
    pass