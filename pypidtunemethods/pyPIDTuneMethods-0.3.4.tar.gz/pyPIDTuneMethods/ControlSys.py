# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 16:30:21 2013

@author: elbar
"""

from numpy import polyadd, polymul
from scipy import signal
import control

#-------------------------------------------------------------------------------
class FODTPoly():
    ''' Proccess polynomial                               '''
    ''' Fisrt Order with Delay                            '''
    ''' Proccess : F(s) = K / (tau*s + 1)                 '''
    ''' num = [K], [den] = [tau, 1]                       '''

    def __init__(self, gain=1.0, tau=1.0, dead_time=1.0, pade_order=4):
        ''' init vars '''
        self.gain = gain
        self.tau = tau
        self.dead_time = dead_time
        self.pade_order = pade_order
        self.num = []
        self.den = []
        self.g = None # process tf
        self.g_delay = None # delay tf
        self.g_process = None # process tf with delay
        self._build_tf()

    def _build_tf(self):
        ''' build transfer function '''
        self.num = [self.gain]
        self.den = [self.tau, 1]
        self.g = control.TransferFunction(self.num, self.den)
        _pade_num, _pade_den = control.pade(self.dead_time, self.pade_order)
        self.g_delay = control.TransferFunction(_pade_num, _pade_den)
        self.g_process = self.g * self.g_delay

    def __str__(self):
        ''' tf string representation '''
        if (self.g):
            _str = "Process G = %s" % (self.g)
        else:
            _str = ''
        return _str

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class IntgrPoly():
    ''' Proccess polynomial                               '''
    ''' Integrating Proccess                              '''
    ''' Proccess : F(s) = K / s                           '''
    ''' num = [K], [den] = [1, 0]                         '''

    def __init__(self, gain=1.0, dead_time=1.0, pade_order=4):
        ''' init vars '''
        self.gain = gain
        self.dead_time = dead_time
        self.pade_order = pade_order
        self.num = []
        self.den = []
        self.g = None # process tf
        self.g_delay = None # delay tf
        self.g_process = None # process tf with delay
        self._build_tf()

    def _build_tf(self):
        ''' build transfer function '''
        self.num = [self.gain]
        self.den = [1, 0]
        self.g = control.TransferFunction(self.num, self.den)
        _pade_num, _pade_den = control.pade(self.dead_time, self.pade_order)
        self.g_delay = control.TransferFunction(_pade_num, _pade_den)
        self.g_process = self.g * self.g_delay

    def __str__(self):
        ''' tf string representation '''
        if (self.g):
            _str = "Process G = %s" % (self.g)
        else:
            _str = ''
        return _str

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class PIDPoly():
    ''' PID Transfer function                                               '''
    ''' PID Ideal : PID(s) = Kc * [Ti*Td*s^2  + Ti*s + 1] /                 ''' 
    '''                           [Ti*s]                                    '''
    ''' PID Real  : PID(s) = Kc * [(a + 1)Ti*Td*s^2  + (Ti + a*Td)*s + 1] / '''
    '''                           [a*Ti*Td*s^2 + Ti*s]                      '''    

    def __init__(self, kc=1.0, ti=1.0, td=1.0):
        ''' init vars '''
        self.kc = kc
        if (ti):
            self.ti = ti
        else:
            self.ti = 0.0
        if (td):
            self.td = td
        else:
            self.td = 0.0
        self.a = 0.2
        self.g = None # process tf
        self.g_kc = None
        self.g_i = None
        self.g_d = None
        self._build_tf_real()

    def _build_tf_ideal(self):
        ''' build ideal PID tranfer function '''
        ''' PID Ideal : PID(s) = Kc * [Ti*Td*s^2  + Ti*s + 1] /                 ''' 
        '''                           [Ti*s]                                    '''        
        self.g_kc = control.TransferFunction([self.kc], [1])
        self.g_i = control.TransferFunction([self.ti, 1], [self.ti, 0])
        self.g_d = control.TransferFunction([self.td, 1], [self.a * self.td, 1])
        self.g = self.g_kc * self.g_i * self.g_d

    def _build_tf_real(self):
        ''' build real PID tranfer function '''
        ''' PID Real  : PID(s) = Kc * [(a + 1)*Ti*Td*s^2  + (Ti + a*Td)*s + 1] /'''
        '''                           [a*Ti*Td*s^2 + Ti*s]                      '''        
        self.g_kc = control.TransferFunction([self.kc], [1])
        self.g_i = control.TransferFunction([self.ti, 1], [self.ti, 0])
        self.g_d = control.TransferFunction([self.td, 1], [self.a * self.td, 1])
        self.g = self.g_kc * self.g_i * self.g_d

    def __str__(self):
        ''' tf string representation '''
        if (self.g):
            _str = "PID G = %s" % (self.g)
        else:
            _str = ''
        return _str

#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
class ClosedLoopPoly():
    ''' Closed loop polynomial                            '''

    def __init__(self, sys, pid):
        ''' init vars '''
        self.sys = sys
        self.pid = pid
        self.g = None # pid tf

    def _build_tf(self):
        ''' build transfer function '''
        self.g = control.feedback(sys, pid, -1)

    def __str__(self):
        ''' tf string representation '''
        if (self.g):
            _str = "Closed Loop G = %s" % (self.g)
        else:
            _str = ''
        return _str

#-------------------------------------------------------------------------------
