#-------------------------------------------------------------------------------
# Name:        PIDRecipe
# Purpose:
#
# Author:      elbar
#
# Created:     12/10/2012
# Copyright:   (c) elbar 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import logging

logger = logging.getLogger("PIDTuneMethodsLog")

# Constants
#-------------------------------------------------------------------------------
P_CONTROL = 0
PI_CONTROL = 1
PID_CONTROL = 2
PID_CONTROL_SMALL_OVERSHOOT = 3
PID_CONTROL_NO_OVERSHOOT = 4

PROCCESS = ['First order', 'Integrating']

PID_METHODS_FODT = ['Manual',
                'Ziegler-Nichols',
                'Cohen-Coon',
                'ITAE load change',
                'ITAE set point change',
                'Lambda',
                'IMC']

PID_METHODS_I = ['Manual',
                 'Lambda',
                 'IMC']

PID_METHODS_TYPES_FODT = [[2],
                      [0, 1, 2],
                      [0, 1, 2],
                      [1, 2],
                      [1, 2],
                      [1],
                      [1, 2]]

PID_METHODS_TYPES_I = [[0, 1, 2],
                    [1],
                    [0]]

PID_TYPES = ['P', 'PI', 'PID']
#-------------------------------------------------------------------------------
def ZN_ultimate(control, Kcu, wu):
#------- Not Used -------    
#Ziegler-Nichols Ultimate-Gain Method
#Kcu =  critical (ultimate) gain
#wu  =  ultimate frequency in radian/time unit
#Pu  =  ultimate period in time unit

    logger.info("ZN Ultimate-Gain Method : Control Type = {}".format(PID_TYPES[control]))

    Pu= 2 * 3.1415 / wu

    if (control == P_CONTROL):
        Kc = 0.5 * Kcu
        logger.info("Kc : %.2f" % (Kc))
        return Kc, 0.0, 0.0
    elif (control == PI_CONTROL):
        Kc = 0.455 * Kcu
        taui = 0.833 * Pu
        logger.info("Kc : %.2f, Ti : %.2f" % (Kc, taui))
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        Kc = 0.588 * Kcu
        taui = 0.5 * Pu
        taud = 0.125 * Pu
        logger.info("Kc : %.2f, Ti : %.2f, Td : %.2f" % (Kc, taui, taud))
        return Kc, taui, taud
    elif (control == PID_CONTROL_SMALL_OVERSHOOT):
        Kc = 0.333 * Kcu
        taui = 0.5 * Pu
        taud = 0.5 * Pu
        logger.info("Kc : %.2f, Ti : %.2f, Td : %.2f" % (Kc, taui, taud))
        return Kc, taui, taud
    elif (control == PID_CONTROL_NO_OVERSHOOT):
        Kc = 0.2 * Kcu
        taui = 0.5 * Pu
        taud = 0.333 * Pu
        logger.info("Kc : %.2f, Ti : %.2f, Td : %.2f" % (Kc, taui, taud))
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def ZN(control, K, tau, td, dummy=0):
#Ziegler-Nichols Method
#K   =  steady steady gain
#td  =  dead time <> 0
#tau =  time constant

    logger.info("ZN Method : Control Type = {}".format(PID_TYPES[control]))

    tdT = td / tau

    if (control == P_CONTROL):
        Kc = 1.0 /(K * tdT)
        logger.info("Kc : %.2f" % (Kc))
        return Kc, 0.0, 0.0
    elif (control == PI_CONTROL):
        Kc = 0.9 / (K * tdT)
        taui = 3.3 * td
        logger.info("Kc : %.2f, Ti : %.2f" % (Kc, taui))
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        Kc = 1.2 / (K * tdT)
        taui = 2.0 * td
        taud = 0.5 * td
        logger.info("Kc : %.2f, Ti : %.2f, Td : %.2f" % (Kc, taui, taud))
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def cohen_coon(control, K, tau, td, dummy=0):
#Cohen-Coon Method
#K   =  steady steady gain
#td  =  dead time <> 0
#tau =  time constant

    logger.info("Cohen-Coon Method : Control Type = {}".format(PID_TYPES[control]))

    tdT = td / tau

    if (control == P_CONTROL):
        Kc = tau * (1.0 + tdT / 3.0) / (K * td)
        logger.info("Kc : %.2f" % (Kc))
        return Kc, 0.0, 0.0
    elif (control == PI_CONTROL):
        Kc = tau * (0.9 + tdT / 3.0) / (K * td)
        taui = td * (30.0 + 3.0 * tdT) / (9.0 + 20.0 * tdT)
        logger.info("Kc : %.2f, Ti : %.2f" % (Kc, taui))
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        Kc = tau * (4.0 / 3.0 + tdT / 4.0) / (K * td);
        taui = td * (32.0 + 6.0 * tdT) / (13.0 + 8.0 * tdT);
        taud = td * 4.0 / (11.0 + 2.0 * tdT);
        logger.info("Kc : %.2f, Ti : %.2f, Td : %.2f" % (Kc, taui, taud))
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def ITAE_load(control, K, tau, td, dummy=0):
#ITAE load change Method
#K   =  steady steady gain
#td  =  dead time <> 0
#tau =  time constant

    logger.info("ITAE load change Method : Control Type = {}".format(PID_TYPES[control]))

    tdT = td / tau

    if (control == P_CONTROL):
        print("P Control is not supported")
    elif (control == PI_CONTROL):
        a1 = 0.859
        b1 = -0.977
        a2 = 0.674
        b2 = 0.68
        Kc = a1 * (tdT ** b1) / K
        taui = tau * (tdT ** b2) / a2
        logger.info("Kc : %.2f, Ti : %.2f" % (Kc, taui))
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        a1 = 1.357
        b1 = -0.947
        a2 = 0.842
        b2 = 0.738
        a3 = 0.381
        b3 = 0.995
        Kc = a1 * (tdT ** b1) / K
        taui = tau * (tdT ** b2) / a2
        taud = a3 * tau * (tdT ** b3)
        logger.info("Kc : %.2f, Ti : %.2f, Td : %.2f" % (Kc, taui, taud))
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def ITAE_set_point(control, K, tau, td, dummy=0):
#ITAE set point change Method
#K   =  steady steady gain
#td  =  dead time <> 0
#tau =  time constant

    logger.info("ITAE set point change Method : Control Type = {}".format(PID_TYPES[control]))

    tdT = td / tau

    if (control == P_CONTROL):
        print("P Control is not supported")
    elif (control == PI_CONTROL):
        a1 = 0.586
        b1 = -0.916
        a2 = 1.03
        b2 = -0.165
        Kc = a1 * (tdT ** b1) / K
        taui = tau / (a2 + b2 * tdT)
        logger.info("Kc : %.2f, Ti : %.2f" % (Kc, taui))
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        a1 = 0.965
        b1 = -0.855
        a2 = 0.796
        b2 = -0.147
        a3 = 0.308
        b3 = 0.9292
        Kc = a1 * (tdT ** b1) / K
        taui = tau / (a2 + b2 * tdT)
        taud = a3 * tau * (tdT ** b3)
        logger.info("Kc : %.2f, Ti : %.2f, Td : %.2f" % (Kc, taui, taud))
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def direct_synthesis(control, K, tau, td, tauc=0):
#------- Not Used -------    
#Direct synthesis PI Method
#K   =  steady steady gain
#td  =  dead time >= 0
#tau =  time constant
#tauc=  system time constant

    logger.info("Direct synthesis PI Method")

    if (tauc == 0):
        tauc = td * 2.0
    Kc = 1.0 * tau / K / (td + tauc)
    taui = tau
    logger.info("Kc : %.2f, Ti : %.2f" % (Kc, taui))
    return Kc, taui, 0.0
#-------------------------------------------------------------------------------
def IMC_fodt(control, K, tau, td, tauc=0):
#IMC PID Method for First Order with Dead Time Process
#K   =  steady steady gain
#td  =  dead time >= 0
#tau =  time constant
#tauc=  system time constant

    logger.info("IMC PID Method for First Order with Dead Time Process")
    
    if (tauc == 0):
        tauc = td * 2.0 / 3.0

    if (control == PI_CONTROL):
        Kc = tau / (K * (tauc + td))
        taui = tau
        logger.info("Kc : %.2f, Ti : %.2f" % (Kc, taui))
        return Kc, taui, 0.0
    elif (control == PID_CONTROL):
        Kc = (td + 2.0 * tau) / (K * (td + 2.0 * tauc))
        taui = tau + td / 2.0
        taud = tau * td / (td + 2.0 * tau)
        logger.info("Kc : %.2f, Ti : %.2f, Td : %.2f" % (Kc, taui, taud))
        return Kc, taui, taud
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def IMC_i(control, K, tau=0, td=0, tauc=0):
#IMC PID Method for integrating process
#K   =  steady steady gain
#tauc=  system time constant

    logger.info("IMC PID Method for Integrating Process")
    
    if (control == P_CONTROL):
        Kc = 1.0  / (K * tauc)
        logger.info("Kc : %.2f" % Kc)
        return Kc, 0.0, 0.0
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def lmbd_fodt(control, K, tau, td, lmbd):
#lambda PID Method for First Order with Dead Time Process
#K   =  steady steady gain
#td  =  dead time >= 0
#tau =  time constant
#lmbd   =  lambda parameter -> system time constant

    logger.info("Lambda PID Method for First Order with Dead Time Process")

    _lambda = lmbd

    if (control == PI_CONTROL):
        Kc = tau / (K * (td + _lambda))
        taui = tau
        logger.info("Kc : %.2f, Ti : %.2f" % (Kc, taui))
        return Kc, taui, 0.0
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------

def lmbd_i(control, K, tau, td, lmbd):
#lambda PID Method for integrating process
#K   =  steady steady gain
#td  =  dead time >= 0
#tau =  time constant
#lmbd   =  lambda parameter -> system time constant

    logger.info("Lambda PID Method for Integrating Process")

    _lambda = lmbd

    if (control == PI_CONTROL):
        taui = 2 * _lambda + td
        Kc = taui / ((_lambda + td) ** 2)
        logger.info("Kc : %.2f, Ti : %.2f" % (Kc, taui))
        return Kc, taui, 0.0
    else:
        logger.error("Control Type is not supported")
        return -1
#-------------------------------------------------------------------------------
def manual_fodt(control, K, tau, td, lmbd):
#manual selection
#K   =  steady steady gain
#td  =  dead time >= 0
#tau =  time constant
#lmbd   =  lambda parameter -> system time constant

    logger.info("Manual selection for First Order with Dead Time Process")
    #do nothing
    return 0.0, 0.0, 0.0
#-------------------------------------------------------------------------------
def manual_i(control, K, tau, td, lmbd):
#manual selection
#K   =  steady steady gain
#td  =  dead time >= 0
#tau =  time constant
#lmbd   =  lambda parameter -> system time constant

    logger.info("Manual selection for Integrating Process")
    #do nothing
    return K, tau, 0.0
#-------------------------------------------------------------------------------
PID_RECIPIES_FODT = [manual_fodt, ZN, cohen_coon, ITAE_load, ITAE_set_point, lmbd_fodt, IMC_fodt]
PID_RECIPIES_I = [manual_i, lmbd_i, IMC_i]
#-------------------------------------------------------------------------------
