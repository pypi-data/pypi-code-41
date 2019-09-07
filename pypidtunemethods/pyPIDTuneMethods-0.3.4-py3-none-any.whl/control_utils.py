# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 16:30:21 2013

@author: elbar
"""

import control

#-------------------------------------------------------------------------------
def build_fodt_process_tf(gain=1.0, tau=1.0, dead_time=1.0, pade_order=4):
    ''' Proccess polynomial                               '''
    ''' Fisrt Order with Delay                            '''
    ''' Proccess : F(s) = K / (tau*s + 1)                 '''
    _num = [gain]
    _den = [tau, 1]
    _g = control.TransferFunction(_num, _den)
    _pade_num, _pade_den = control.pade(dead_time, pade_order)
    _g_delay = control.TransferFunction(_pade_num, _pade_den)
    return _g * _g_delay
#-------------------------------------------------------------------------------
def build_int_process_tf(gain=1.0, dead_time=1.0, pade_order=4):
    ''' Proccess polynomial                               '''
    ''' Integrating Proccess                              '''
    ''' Proccess : F(s) = K / s                           '''
    _num = [gain]
    _den = [1, 0]
    _g = control.TransferFunction(_num, _den)
    _pade_num, _pade_den = control.pade(dead_time, pade_order)
    _g_delay = control.TransferFunction(_pade_num, _pade_den)
    return _g * _g_delay
#-------------------------------------------------------------------------------
def build_pid_ideal_tf(kc=1.0, ti=1.0, td=1.0, a=0.0):
    ''' build ideal PID tranfer function                              '''
    ''' PID : PID(s) = Kc * [ 1 + 1/Ti*s  + Td*s]                     '''
    ''' 0.05 < a < 0.2                                                '''
    _g_kc = control.TransferFunction([kc], [1])
    if (ti==0):
        _g_i = control.TransferFunction([1], [1])
    else:
        _g_i = control.TransferFunction([ti, 1], [ti, 0])
    _g_d = control.TransferFunction([td, 0], [a * td, 1])
    return _g_kc * (_g_i + _g_d)
#-------------------------------------------------------------------------------
def build_pid_parallel_tf(kc=1.0, ki=1.0, kd=1.0, a=0.0):
    ''' build parallel PID tranfer function                            '''
    ''' PID : PID(s) = Kc + Ki/s  + Kd*s                               '''  
    ''' 0.05 < a < 0.2                                                '''    
    _g_kc = control.TransferFunction([kc], [1])
    if (ki==0):
        _g_i = control.TransferFunction([0], [1])
    else:
        _g_i = control.TransferFunction([ki], [1, 0])
    _g_d = control.TransferFunction([kd, 0], [a*kd/kc, 1])
    return _g_kc + _g_i + _g_d
#-------------------------------------------------------------------------------
def build_pid_series_tf(kc=1.0, ti=1.0, td=1.0, a=0.2):
    ''' build series PID tranfer function                              '''
    ''' or interacting or rate-before-reset                            '''
    ''' PID : PID(s) = Kc * [1 + 1/Ti*s] * [(Td*s + 1)/(a*Td*s + 1)]   '''
    ''' 0.05 < a < 0.2                                                '''    
    _g_kc = control.TransferFunction([kc], [1])
    if (ti==0):
        _g_i = control.TransferFunction([1], [1])
    else:
        _g_i = control.TransferFunction([ti, 1], [ti, 0])    
    _g_d = control.TransferFunction([td, 1], [a * td, 1])
    return _g_kc * _g_i * _g_d
#-------------------------------------------------------------------------------
PID_ALGORITHS = [build_pid_ideal_tf, build_pid_series_tf]
#-------------------------------------------------------------------------------
