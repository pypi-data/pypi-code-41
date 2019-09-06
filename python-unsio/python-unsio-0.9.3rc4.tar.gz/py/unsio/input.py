#!/usr/bin/env python
from __future__ import print_function

import numpy as np
import unsio

#
# class CSsnapshot
#
class CUNS_IN:
    """Input Operations on UNS snapshots

    This class provide methods for loading data stored in an UNS compatible snapshots

    """
    __uns=None
    __verbose=False
    __float32=True
    __loaded=False
    simname=None
    select=None
#
# constructor
#
    def __init__(self,simname,select="all",times="all",float32=True,verbose=False,verbose_debug=False):
        """
        The Constructor for CUNS_IN class

        example :
           - instantiate an object to load components gas and stars of snapshot "mysnap"
             with double precision

           import unsio.input as uns_in
           my_in=uns_in.CUNS_IN("mysnap","gas,stars",float32=False)

        Args:
            simname (str) : snapshot's file name or simulation's name

            select  (str) : selected components to be loaded. It's a list of components
                            separated with coma ",".
                            Known components are: disk,gas,halo,bndry,bulge,all

                            example :
                              select="gas,disk"
                              select="halo"
                            (default: all)

            times   (str) : specify on which range of time data must be loaded.

                            example :
                              times="100"  (load time 100)
                              times="0:10" (load 0<=time<=10)
                              times="all"  (load all times)
                            (default: all)

            float32 (bool): load data in float value or double value.

                            example:
                              float32=True (load in float)
                              float32=False (load in double)
                            (default: True)
        """
        #select=select.encode('ascii')
        #times=times.encode('ascii')
        self.__verbose=verbose
        self.simname=simname
        self.select=select

        self.__vdebug=verbose_debug
        if self.__vdebug:
            print(">> 32 bits floating value",float32)
        if simname is not None:
            #self.simname=self.simname.encode('ascii')
            if float32:
                if self.__vdebug:
                    print("32 bits",self.simname,self.select,times,verbose,type(self.simname),type(self.select))
                self.__uns=unsio.CunsIn(self.simname,self.select,times,verbose)
            else:
                if self.__vdebug:
                    print("64 bits",simname,select,times,verbose)
                self.__uns=unsio.CunsInD(self.simname,self.select,times,verbose)
            if not self.__uns.isValid():
                raise RuntimeError("UNS not valid")
        else:
            None

    def debugOn(self):
        self.__vdebug=True
#
# nextFrame
#
    def nextFrame(self,bits=""):
        """
        Load the next snapshot. Data retreival depend from bits (array selected) and
        components selected during instanciation.

        Args :
             bits (str) : It's a based string variable which control which arrays will be loaded according to components selected
                          Each characters of the string represents a different arrays.

                          example :
                            bits="mxv" will load masses (m), positions(x) and velocities(v)
                            bits="xRH" will load postions(x), densities(R) and hsml(H)

                          for a complete bits explanation, please visit :
                          https://projets.lam.fr/projects/unsio/wiki/UnsioVariablesUtilisation#How-to-select-data-at-loading
                          (default: all)

        Return :
            int: 1 success (something has been loaded), 0 otherwise

        """
        if not self.__uns.isValid():
            raise RuntimeError("UNS not valid")
        else:
            ok=self.__uns.nextFrame(bits)
            if ok:
                self.__loaded=True
            return ok
#
# close
#
    def close(self):
        """close opened snapshot"""

        if not self.__uns.isValid():
            raise RuntimeError("UNS not valid")
        self.__uns.close()
#
# kill
#
    def kill(self):
        """close opened snapshot"""

        if not self.__uns.isValid():
            raise RuntimeError("UNS not valid")
        self.close()
#
# getInterfaceType
#
    def getInterfaceType(self):
        """return uns snapshot's Interface type"""

        if not self.__uns.isValid():
            raise RuntimeError("UNS not valid")
        return self.__uns.getInterfaceType()
#
# getFileStructure
#
    def getFileStructure(self):
        """return uns snapshot's File structure"""

        if not self.__uns.isValid():
            raise RuntimeError("UNS not valid")
        return self.__uns.getFileStructure()
#
# getFileName
#
    def getFileName(self):
        """return uns snapshot's File name"""

        if not self.__uns.isValid():
            raise RuntimeError("UNS not valid")
        return self.__uns.getFileName()
#
# getData
#
    def getData(self,select,tag=None,data_type=np.float32):
        """
        General method to get Data Array/Value respecting to components
        example :
           - to get positions from gas component
             status,pos=obj.getData("gas","pos")

           - to get concatened positions from gas and stars component
             status,pos=obj.getData("gas,stars","pos")

           - to get simulation Time
             status,time=obj.getData("time")

        Args:
            select (str) : component or list of components separeted with a coma
                           example :
                              select="gas"
                              select="gas,stars"
            tag    (str) : array to get
                           example :
                              tag="pos"
                              tag="acc"
                              pos,vel,mass,rho...etc see https://projets.lam.fr/projects/unsio/wiki/GetDataDescription

            IMPORTANT : if 'tag' is None, then 'select' is treated as 'tag' (see above)

        Return :
            status,numpy_array       (if tag is not None)
            status,value             (if tag is None)
            in both case, status=1 if success, 0 otherwise
        """

        if not self.__uns.isValid():
            raise RuntimeError("UNS not valid")
        if not self.__loaded:
            raise RuntimeError("Snapshot not loaded")

        status=1
        if tag != "id":
            ret_data=np.zeros(0,dtype=data_type) # initalyse an empty array
        else:
            ret_data=np.zeros(0,dtype=np.int32) # initalyse an empty array

        for comp in select.split(","):
            if self.__vdebug:
                print ("comp :", comp)
            ok,type,data=self.__getData(comp,tag,data_type)
            if (ok) :
                if type==2: # array
                    ret_data = np.append(ret_data,data)
                else:
                    ret_data = data
            else:
                status=0 # one component missing
            if self.__vdebug and type==2:
                print ("ok=",ok," data=",data.size," ret_data=",ret_data.size)
        return status,ret_data
#
# __getData
#
    def __getData(self,comp_value,tag=None,data_type=np.float32):
        if self.__vdebug:
            print ("array=",tag,data_type)
        if tag is None: # only one value
            tab_value_F=["time"]
            tab_value_I=["nbody","nsel"]
            ok=0
            ret_data=np.zeros(1,dtype=data_type)
            data=0
            # proceed __uns.getValue()
            if tab_value_I.count(comp_value) > 0:
                ok,ret_data[0]=self.__uns.getValueI(comp_value)
                data=int(ret_data[0])
            else:
                ok,ret_data[0]=self.__uns.getValueF(comp_value)
                data=float(ret_data[0])
            #ret_data[0]=data
            if self.__vdebug:
                print ("ok,data",ok,data)
            return ok,1,data
        else:
            if tag != "id":
                ok,data=self.__uns.getArrayF(comp_value,tag)
            else:
                ok,data=self.__uns.getArrayI(comp_value,tag)
            return ok,2,data
