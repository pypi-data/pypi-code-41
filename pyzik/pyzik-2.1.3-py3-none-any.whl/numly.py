# -*- coding: utf-8 -*-
"""
Created on Sun Aug 25 00:12:16 2019

@author: jazzn
"""

import pandas as pd
import numpy as np
from pyzik.pandly import scatter2D,scatter3D,draw_vectors

class Fplot:
    __G2D = 'scatter2D'
    __G3D = 'scatter3D'
    __GV2 = 'vector2D'
    __GV3 = 'vector3D'
    __expectDaxis={__G2D:list(set(dict(titre="",ortho='auto', unsur=1, 
              shape=None, quadril_x=0, quadril_y=0,subplots=False, xlabel='', ylabel='',xorder='normal'))),
            __G3D:list(set(dict(titre="un titre", unsur=1))),
            __GV2:list(set(dict(unsur=1,scalvect=1,titre="sans titre",quadril_x=0,quadril_y=0,xlabel='',ylabel=''))),
                 __GV3:list(set(dict(unsur=1,scalvect=1,titre="sans titre",quadril_x=0,quadril_y=0,quadril_z=0,
                                     xlabel='',ylabel='',zlabel='')))}
    __expectD={__G2D:list(set(dict(style_tracer='o',color='auto',fill=''))),
            __G3D:list(set(dict(color='auto',style_tracer='o'))),
            __GV2:[],__GV3:[]}
    
    def __check_assert(self,typ='axis',**d):
        for kd in d:
            if typ == 'axis':
                assert kd in Fplot.__expectDaxis[self.__kind],f"bad argument {kd} ...\n use :\n{Fplot.__expectDaxis[self.__kind]}"
            else:
                assert kd in Fplot.__expectD[self.__kind],f"bad argument {kd} ...\n use :\n{Fplot.__expectD[self.__kind]}"
                
    def __init__(self,kind='scatter2D',**d):
        assert kind in [Fplot.__G2D,Fplot.__G3D,Fplot.__GV2,Fplot.__GV3],f"kind must be in {[Fplot.__G2D,Fplot.__G3D,Fplot.__GV2,Fplot.__GV3]}"
        self.__kind = kind
        self.__check_assert(typ='axis',**d)
        self.__df=[]
        self.__d = {}
        self.__d.update(self.__clean_axis_dict(d))
        self.__init = True

    
    def __clean_axis_dict(self,d):
        return {k:v for k,v in d.items() if k in Fplot.__expectDaxis[self.__kind]}  
    
    def draw_vector2D(self,point=tuple(),vector=tuple(),**d):
        try:
            g = self.__init
        except:
            self.__init__(kind=Fplot.__GV2)
        assert self.__kind == Fplot.__GV2,f"use draw_vector2D only if u want draw 2D gfx with vectors, change ur kind type to: {Fplot.__GV2}"
        assert len(point)==2,'point must have 2 coordinates'
        assert len(vector)==2,'vector must have 2 coordinates'
        #assert len(set([len(i) for i in point+vector]))==1,'arrays must have same lenght'
        self.__check_assert(typ='xyz',**d)
        datf = pd.DataFrame({'x':point[0],'y':point[1],'ux':vector[0],'uy':vector[1]})
        datf.info = ''
        self.__df = [datf]
        self.__d.update(self.__clean_dict(d))
    
    
    def draw_vector3D(self,point=tuple(),vector=tuple(),**d):
        try:
            g = self.__init
        except:
            self.__init__(kind=Fplot.__GV3)
        assert self.__kind == Fplot.__GV3,f"use draw_vector2D only if u want draw 2D gfx with vectors, change ur kind type to: {Fplot.__GV2}"
        assert len(point)==3,'point must have 2 coordinates'
        assert len(vector)==3,'vector must have 2 coordinates'
        assert len(set([len(i) for i in point+vector]))==1,'arrays must all be same length'
        self.__check_assert(typ='xyz',**d)
        datf = pd.DataFrame({'x':point[0],'y':point[1],'z':point[2],'ux':vector[0],'uy':vector[1],'uz':vector[2]})
        datf.info = ''
        self.__df = [datf]
        self.__d.update(self.__clean_dict(d))
        
    def plot(self,x,y,label='',**d):
        try:
            g = self.__init
        except:
            self.__init__(kind=Fplot.__G2D)
        assert self.__kind == 'scatter2D',f"use add_plot2D only if u want draw 2D gfx, change ur kind type to: {Fplot.__G2D}"
        assert isinstance(x,(np.ndarray,list)),"x must be numpy array or list"
        assert isinstance(y,(np.ndarray,list)),"x must be numpy array or list"
        assert len(x)==len(y),"arrays must have same lenght"
        self.__check_assert(typ='xyz',**d)
        datf = pd.DataFrame({'x':x,'y':y})
        datf.info = label
        self.__df.append(datf)
        self.__d.update(self.__clean_dict(d))
    
    def title(self,title):
        self.__d.update({'titre':title})
        return self
    
    def xlabel(self,xlabel):
        self.__d.update(self.__clean_axis_dict({'xlabel':xlabel}))
        return self
    
    def ylabel(self,ylabel):
        self.__d.update(self.__clean_axis_dict({'ylabel':ylabel}))
        return self
    
    def zlabel(self,zlabel):
        self.__d.update(self.__clean_axis_dict({'zlabel':zlabel}))
        return self
    
    def xgrid(self,xgrid):
        self.__d.update(self.__clean_axis_dict({'quadril_x':xgrid}))
        return self
    
    def ygrid(self,ygrid):
        self.__d.update(self.__clean_axis_dict({'quadril_y':ygrid}))
        return self
    
    def zgrid(self,zgrid):
        self.__d.update(self.__clean_axis_dict({'quadril_z':zgrid}))
        return self
    
    def marker(self,marker):
        self.__d.update(self.__clean_dict({'style_tracer':marker}))
        return self
    
    def subplots(self,subplots):
        self.__d.update(self.__clean_axis_dict({'subplots':subplots}))
        return self
    
    def xorder(self,xorder):
        self.__d.update(self.__clean_axis_dict({'xorder':xorder}))
        return self
        
    def scalvect(self,scalvect):
        self.__d.update(self.__clean_axis_dict({'scalvect':scalvect}))
        return self

    def unsur(self,unsur):
        self.__d.update(self.__clean_axis_dict({'unsur':unsur}))
        return self
    
    def plot3D(self,x,y,z,label,**d):        
        try:
            g = self.__init
        except:
            self.__init__(kind=Fplot.__GV2)
        assert self.__kind == Fplot.__G3D,f"use add_plot3D only if u want draw 3D gfx, change ur kind type to: {Fplot.__G3D}"
        assert isinstance(x,(np.ndarray,list)),"x must be numpy array or list"
        assert isinstance(y,(np.ndarray,list)),"x must be numpy array or list"
        assert isinstance(z,(np.ndarray,list)),"x must be numpy array or list"
        assert (len(x)==len(y)) and (len(x)==len(z)),'arrays must all be same length'
        self.__check_assert(typ='xyz',**d)
        datf = pd.DataFrame({'x':x,'y':y,'z':z})
        datf.info = label
        self.__df.append(datf)
        self.__d.update(self.__clean_dict(d))
    
    def __repr__(self):
        return ''
    
    def __clean_dict(self,d):
        return {k:v for k,v in d.items() if k in Fplot.__expectD[self.__kind]}   

    def show(self):
        dd = self.__clean_axis_dict(self.__d)
        if self.__kind == Fplot.__G2D:
            if len(self.__df)>1:
                return self.__df[0].scatter2D(x='x',y='y',other_df=self.__df[1:],**self.__d),self.__init__(kind=Fplot.__G2D,**dd)
            else:
                return self.__df[0].scatter2D(x='x',y='y',**self.__d),self.__init__(kind=Fplot.__G2D,**dd)
        elif self.__kind == Fplot.__G3D:
            if len(self.__df)>1:
                return self.__df[0].scatter3D(x='x',y='y',z='z',other_df=self.__df[1:],**self.__d),self.__init__(kind=Fplot.__G3D,**dd)
            else:
                return self.__df[0].scatter3D(x='x',y='y',z='z',**self.__d),self.__init__(kind=Fplot.__G3D,**dd)
        elif self.__kind == Fplot.__GV2:
            return self.__df[0].draw_vectors(point=('x','y'),vector=('ux','uy'),**self.__d),self.__init__(kind=Fplot.__GV2,**dd)
        elif self.__kind == Fplot.__GV3:
            return self.__df[0].draw_vectors(point=('x','y','z'),vector=('ux','uy','uz'),**self.__d),self.__init__(kind=Fplot.__GV3,**dd)

    