#!/usr/bin/env python
from __future__ import print_function

import numpy as np
import unsio

#
# class CSsnapshot
#
class CUNS_OUT:
    """Output Operations on UNS snapshots"""
    __uns=None
    __verbose=False
    __verbose_debug=False
    __float32=True
    __loaded=False
    __outfile=None
    __uns_type=None
    select=None
    __is_valid=False
    __data_type=None

# -----------------------------------------------------
# constructor
#
    def __init__(self,outfile, uns_type, float32=True, verbose=False, verbose_debug=False):
        """

        """
        self.__float32 = float32
        self.__outfile = outfile
        self.__uns_type = uns_type
        self.__verbose = verbose
        self.__verbose_debug = verbose_debug
        if self.__float32:
            if self.__verbose_debug:
                print("saving in SINGLE precision floating values")
            self.__data_type = np.float32
            self.__uns = unsio.CunsOut(self.__outfile,self.__uns_type)
        else:
            if self.__verbose_debug:
                print("saving in DOUBLE precision floating values")
            self.__data_type = np.float64
            self.__uns = unsio.CunsOutD(self.__outfile,self.__uns_type)
        self.__is_valid = True
# -----------------------------------------------------
# setData
#
    def setData(self,data_array,select,tag=None):
        """
        General method to set Data to uns snapshot

        Argument:
        - data_array : 1D numpy_array or single value to save
        - select : component or list of components (ex: gas or gas,stars)
        - tag    : pos,vel,mass,rho...etc see https://projets.lam.fr/projects/unsio/wiki/GetDataDescription

        IMPORTANT : if 'tag' is None, then 'select' is treated as 'tag' (see above)

        Return :
            status : 1 if success, 0 otherwise
        """
        if not self.__is_valid:
            raise RuntimeError("CUNS_OUT is not valid")

        ok=0
        if tag is None: # only one value
            tab_value_F=["time"]
            tab_value_I=["nbody","nsel"]
            if tab_value_I.count(select) > 0:
                ok=self.__uns.setValueI(select,data_array)
            else:
                ok=self.__uns.setValueF(select,data_array)
        else:
            if tag != "id": #not id, then we save float arrays
                ok = self.__uns.setArrayF(select,tag,data_array)
            else: # save id's array of integers
                ok = self.__uns.setArrayI(select,tag,data_array)

        if self.__verbose_debug:
            print("setData : [select=%s, tag=%s, ok=%d ]"%(select,tag,ok))

        return ok

# -----------------------------------------------------
# save
#
    def save(self):
        if not self.__is_valid:
            raise RuntimeError("CUNS_OUT is not valid")

        self.__uns.save()

# -----------------------------------------------------
# close
#
    def close(self):
        if not self.__is_valid:
            raise RuntimeError("CUNS_OUT is not valid")

        self.__uns.close()
