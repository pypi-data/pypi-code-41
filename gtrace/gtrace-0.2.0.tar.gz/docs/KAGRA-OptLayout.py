'''
KAGRA-OptLayout.py

This program constructs the optical layout of the main IFO.
'''

#{{{ ==== Import modules ====

import gtrace.beam as beam
import gtrace.optcomp as opt
from gtrace.nonsequential import non_seq_trace
from gtrace.draw.tools import drawAllBeams, drawAllOptics, transAll, rotateAll, drawOptSys
import gtrace.draw as draw
import gtrace.draw.renderer as renderer
from gtrace.unit import *
import gtrace.optics.gaussian as gauss
from gtrace.optics.cavity import Cavity
import numpy as np
pi = np.pi
import scipy as sp
import scipy.optimize as sopt
import copy
from scipy.constants import c

#}}}

#{{{ Utility Functions

#{{{ ** Function to propagate beams from ITMs **

def propagateOpticalPathFromITM(beamX, beamY):
    '''
    Propagate beams from ITMs to the PRM and SRM
    beamX and beamY are the source beams.
    Typically, these are beams at the waist positions of the
    arm cavities pointing toward ITMs.
    '''
    beamDictX = {}
    beamDictY = {}    

#{{{ From ITMX
    
    #Hit ITMX
    beams = ITMX.hitFromHR(beamX, order=0)
    beamToITMX = beams['input']
    beamDictX['beamToITMX'] = beamToITMX
    b = beamToITMX.copy()
    b.propagate(b.length)
    beamDictX['beamOnITMX'] = b
    beamITMXs1 = beams['s1']
    beamITMXt1 = beams['t1']
    beamITMXt1.optDist = beamITMXt1.optDist - beamITMXs1.optDist
    beamITMXt1.Gouyx = beamITMXt1.Gouyx - beamITMXs1.Gouyx
    beamITMXt1.Gouyy = beamITMXt1.Gouyy - beamITMXs1.Gouyy
    beamITMXs1.optDist = 0.0
    beamITMXs1.Gouyx = 0.0
    beamITMXs1.Gouyy = 0.0
    beamDictX['beamITMXs1'] = beamITMXs1


    #Hit BS
    beams = BS.hitFromAR(beamITMXt1, order=1)
    beamDictX['beamITMXtoBS'] = beams['input']    
    beamDictX['beamBSs1'] = beams['s1']
    beamDictX['beamBSs2'] = beams['s2']
    beamDictX['beamBStoPR3'] = beams['t1']
    beamDictX['beamBStoSR3'] = beams['r2']
    beamBSt1 = beams['t1']
    beamBSr2 = beams['r2']

#{{{ #PRC Path

    
    #Hit PR3
    beams = PR3.hitFromHR(beamBSt1,order=0)
    beamDictX['beamBStoPR3'] = beams['input']
    beamPR3r1 = beams['r1']

    #Hit PR2
    beams = PR2.hitFromHR(beamPR3r1,order=0)
    beamDictX['beamPR3toPR2'] = beams['input']
    beamPR2r1 = beams['r1']

    #Hit PRM
    beams = PRM.hitFromHR(beamPR2r1,order=0)
    beamDictX['beamPR2toPRM'] = beams['input']
    beamDictX['beamPRMs1'] = beams['s1']
    beamDictX['beamPRMt1'] = beams['t1']    
    b = beams['input'].copy()
    b.propagate(b.length)
    beamDictX['beamOnPRM'] = b

#}}}

#{{{ #SRC Path
    
    #Hit SR3
    beams = SR3.hitFromHR(beamBSr2,order=0)
    beamDictX['beamBStoSR3'] = beams['input']
    beamSR3r1 = beams['r1']

    #Hit SR2
    beams = SR2.hitFromHR(beamSR3r1,order=0)
    beamDictX['beamSR3toSR2'] = beams['input']
    beamSR2r1 = beams['r1']

    #Hit SRM
    beams = SRM.hitFromHR(beamSR2r1,order=0)
    beamDictX['beamSR2toSRM'] = beams['input']
    beamDictX['beamSRMs1'] = beams['s1']
    beamDictX['beamSRMt1'] = beams['t1']    
    b = beams['input'].copy()
    b.propagate(b.length)
    beamDictX['beamOnSRM'] = b

#}}}

#}}}

#{{{ From ITMY
    
    #Hit ITMY
    beams = ITMY.hitFromHR(beamArmWaistY, order=0)
    beamToITMY = beams['input']
    beamDictY['beamToITMY'] = beamToITMY
    b = beamToITMY.copy()
    b.propagate(b.length)
    beamDictY['beamOnITMY'] = b
    beamITMYs1 = beams['s1']
    beamITMYt1 = beams['t1']
    beamITMYt1.optDist = beamITMYt1.optDist - beamITMYs1.optDist
    beamITMYt1.Gouyx = beamITMYt1.Gouyx - beamITMYs1.Gouyx
    beamITMYt1.Gouyy = beamITMYt1.Gouyy - beamITMYs1.Gouyy
    beamITMYs1.optDist = 0.0
    beamITMYs1.Gouyx = 0.0
    beamITMYs1.Gouyy = 0.0
    beamDictY['beamITMYs1'] = beamITMYs1


    #Hit BS
    beams = BS.hitFromHR(beamITMYt1, order=1)
    beamDictY['beamITMYtoBS'] = beams['input']    
    beamDictY['beamBSs1'] = beams['s1']
    beamDictY['beamBSs2'] = beams['s2']
    beamDictY['beamBStoPR3'] = beams['r1']
    beamDictY['beamBStoSR3'] = beams['t1']
    beamBSt1 = beams['t1']
    beamBSr1 = beams['r1']

#{{{ #PRC Path

    
    #Hit PR3
    beams = PR3.hitFromHR(beamBSr1,order=0)
    beamDictY['beamBStoPR3'] = beams['input']
    beamPR3r1 = beams['r1']

    #Hit PR2
    beams = PR2.hitFromHR(beamPR3r1,order=0)
    beamDictY['beamPR3toPR2'] = beams['input']
    beamPR2r1 = beams['r1']

    #Hit PRM
    beams = PRM.hitFromHR(beamPR2r1,order=0)
    beamDictY['beamPR2toPRM'] = beams['input']
    beamDictY['beamPRMs1'] = beams['s1']
    beamDictY['beamPRMt1'] = beams['t1']
    b = beams['input'].copy()
    b.propagate(b.length)
    beamDictY['beamOnPRM'] = b

#}}}

#{{{ #SRC Path
    
    #Hit SR3
    beams = SR3.hitFromHR(beamBSt1,order=0)
    beamDictY['beamBStoSR3'] = beams['input']
    beamSR3r1 = beams['r1']

    #Hit SR2
    beams = SR2.hitFromHR(beamSR3r1,order=0)
    beamDictY['beamSR3toSR2'] = beams['input']
    beamSR2r1 = beams['r1']

    #Hit SRM
    beams = SRM.hitFromHR(beamSR2r1,order=0)
    beamDictY['beamSR2toSRM'] = beams['input']
    beamDictY['beamSRMs1'] = beams['s1']
    beamDictY['beamSRMt1'] = beams['t1']    
    b = beams['input'].copy()
    b.propagate(b.length)
    beamDictY['beamOnSRM'] = b

#}}}

#}}}

#{{{ Check results

    result = {}

    #Gouy Phases
    result['AvgGouyPRCX'] = (beamDictX['beamPRMs1'].Gouyx + beamDictY['beamPRMs1'].Gouyx)/2
    result['AvgGouyPRCY'] = (beamDictX['beamPRMs1'].Gouyy+beamDictY['beamPRMs1'].Gouyy)/2
    result['AvgGouySRCX'] = (beamDictX['beamSRMs1'].Gouyx + beamDictY['beamSRMs1'].Gouyx)/2
    result['AvgGouySRCY'] = (beamDictX['beamSRMs1'].Gouyy+beamDictY['beamSRMs1'].Gouyy)/2

    #ROC of PRM and SRM
    (q1, match1) = gauss.optimalMatching(beamDictX['beamOnPRM'].qx, beamDictX['beamOnPRM'].qy)
    (q2, match2) = gauss.optimalMatching(beamDictY['beamOnPRM'].qx, beamDictY['beamOnPRM'].qy)
    (q0, match0) = gauss.optimalMatching(q1,q2)    
    result['PRM ROC'] = gauss.q2R(q0)
    result['PRC Mode matching'] = (match0, match1, match2)
    result['q-parameter on PRM'] = q0
    (q1, match1) = gauss.optimalMatching(beamDictX['beamOnSRM'].qx, beamDictX['beamOnSRM'].qy)
    (q2, match2) = gauss.optimalMatching(beamDictY['beamOnSRM'].qx, beamDictY['beamOnSRM'].qy)
    (q0, match0) = gauss.optimalMatching(q1,q2)    
    result['SRM ROC'] = gauss.q2R(q0)
    result['SRC Mode matching'] = (match0, match1, match2)
    result['q-parameter on SRM'] = q0
    
    #Beam spot sizes
    result['PRM Spot Size'] = (beamDictX['beamOnPRM'].wx + beamDictX['beamOnPRM'].wy
                                             + beamDictY['beamOnPRM'].wx + beamDictY['beamOnPRM'].wy)/4
    result['PR2 Spot Size'] = (beamDictX['beamPR2toPRM'].wx + beamDictX['beamPR2toPRM'].wy
                                             + beamDictY['beamPR2toPRM'].wx + beamDictY['beamPR2toPRM'].wy)/4
    result['PR3 Spot Size'] = (beamDictX['beamPR3toPR2'].wx + beamDictX['beamPR3toPR2'].wy
                                             + beamDictY['beamPR3toPR2'].wx + beamDictY['beamPR3toPR2'].wy)/4

    result['SRM Spot Size'] = (beamDictX['beamOnSRM'].wx + beamDictX['beamOnSRM'].wy
                                             + beamDictY['beamOnSRM'].wx + beamDictY['beamOnSRM'].wy)/4
    result['SR2 Spot Size'] = (beamDictX['beamSR2toSRM'].wx + beamDictX['beamSR2toSRM'].wy
                                             + beamDictY['beamSR2toSRM'].wx + beamDictY['beamSR2toSRM'].wy)/4
    result['SR3 Spot Size'] = (beamDictX['beamSR3toSR2'].wx + beamDictX['beamSR3toSR2'].wy
                                             + beamDictY['beamSR3toSR2'].wx + beamDictY['beamSR3toSR2'].wy)/4

#}}}

#{{{ Return results
    return (result, beamDictX, beamDictY)
#}}}

#}}}

#{{{ *** Function to propagate input beam throughout the IFO ***

#This function does a similar task as constructLCGTOpticalPath()
#However, it will not change the position of the optics

def propagateOpticalPath(inputBeam, poxpoy=True):
    '''
    Given an input beam, propagate the beam
    from PRM through the whole interferometer.
    '''
#{{{ init

    #Initialize the beamDict
    beamDict={}
    auxBeamDict={}

#}}}

#{{{ PRC

    #Hit PRM
    beams = PRM.hitFromAR(inputBeam, order=0)
    beamMMTtoPRM = beams['input']
    beamDict['beamMMTtoPRM'] = beamMMTtoPRM
    beamDict['beamPRMs1'] = beams['s1']
    beam_from_PRM = beams['t1']
    beam_from_PRM.optDist = 0
    beam_from_PRM.Gouyx = 0
    beam_from_PRM.Gouyy = 0    

    #Hit PR2
    beams = PR2.hitFromHR(beam_from_PRM, order=0)
    beamPRMtoPR2 = beams['input']
    beamDict['beamPRMtoPR2'] = beamPRMtoPR2
    beam_from_PR2 = beams['r1']

    #Hit PR3
    beams = PR3.hitFromHR(beam_from_PR2, order=0)
    beamPR2toPR3 = beams['input']
    beamDict['beamPR2toPR3'] = beamPR2toPR3
    beam_from_PR3 = beams['r1']

    #Hit BS
    beams = BS.hitFromHR(beam_from_PR3, order=1)
    beamPR3toBS = beams['input']
    beamDict['beamPR3toBS'] = beamPR3toBS
    beamBS_PRs1 = beams['s1']
    beamDict['beamBS_PRs1'] = beamBS_PRs1

    beamBSrefl = beams['r1']
    beamBStrans = beams['t1']

    #BS AR Beams
    # beamBS_PRs2 = beams['s2']
    # auxBeamDict['beamBS_PRs2'] = beamBS_PRs2
    # beamBS_PRr2 = beams['r2']
    # auxBeamDict['beamBS_PRr2'] = beamBS_PRr2
    # beamBS_PRr2.length = 30.0
    
    #Hit ITMX
    beams = ITMX.hitFromAR(beamBStrans, order=2)

    beamBStoITMX = beams['input']
    beamDict['beamBStoITMX'] = beamBStoITMX
    beamITMXs1 = beams['s1']
    beamDict['beamITMXs1'] = beamITMXs1
    beamITMXs2 = beams['s2']
    beamDict['beamITMXs2'] = beamITMXs2
    beamITMXtrans = beams['t1']
    beamITMXtrans.length = Larm
    beamDict['beamITMXtrans'] = beamITMXtrans
    beamDict['beamITMXr2'] = beams['r2']
    

    #Hit ITMY
    beams = ITMY.hitFromAR(beamBSrefl, order=2)

    beamBStoITMY = beams['input']
    beamDict['beamBStoITMY'] = beamBStoITMY
    beamITMYs1 = beams['s1']
    beamDict['beamITMYs1'] = beamITMYs1
    beamITMYtrans = beams['t1']
    beamITMYtrans.length = Larm
    beamDict['beamITMYtrans'] = beamITMYtrans    


#}}}

#{{{ POX

    if poxpoy:
        #POX is taken from the BS AR reflection

        #Hit ITMX
        b=beamITMXtrans.copy()
        b.propagate(1)
        b.flip()
        beams = ITMX.hitFromHR(b, order=1)
        beamPOXs1 = beams['s1']
        beamITMXreturn = beams['t1']

        #Hit BS
        beams = BS.hitFromAR(beamITMXreturn, order=1)
        POX_BSAR_SR3 = beams['r1']

        #Hit SR3
        beams = SR3.hitFromHR(POX_BSAR_SR3, order=1)
        auxBeamDict['POX_BSAR_SR3'] = beams['input']
        POX_SR3_SR2= beams['r1']

        #Hit SR2
        beams = SR2.hitFromHR(POX_SR3_SR2, order=1)
        auxBeamDict['POX_SR3_SR2'] = beams['input']
        auxBeamDict['POX_SR2_SR3'] = beams['r1']


#}}}

#{{{ POY

    if poxpoy:

        b=beamITMYtrans.copy()
        b.propagate(1)
        b.flip()
        beams = ITMY.hitFromHR(b, order=2)
        beamITMYreturn = beams['t1']
        beamPOYs1 = beams['s1']
        auxBeamDict['POYs2'] = beams['s2']
        auxBeamDict['POYs3'] = beams['s3']
        POY_ITMY_BS = beams['t2']

        #Hit BS
        beams = BS.hitFromHR(POY_ITMY_BS, order=1)
        auxBeamDict['POY_ITMY_BS'] = beams['input']
        auxBeamDict['POY_BSs1'] = beams['s1']
        POY_BS_PR3 = beams['r1']
        POY_BS_SR3 = beams['t1']
    
        #Hit PR3
        beams = PR3.hitFromHR(POY_BS_PR3, order=2)
        auxBeamDict['POY_BS_PR3'] = beams['input']
        POY_PR3_PR2= beams['r1']

        #Hit PR2
        beams = PR2.hitFromHR(POY_PR3_PR2, order=2)
        auxBeamDict['POY_PR3_PR2'] = beams['input']
        # auxBeamDict['POY_PR2s1'] = beams['s1']
        # beams['t1'].length = 3.0
        # auxBeamDict['POY_PR2t1'] = beams['t1']    
        POY_PR2_PRM = beams['r1']
        POY_PR2_PRM.length = 15.0
        auxBeamDict['POY_PR2_PRM'] = POY_PR2_PRM

        #Hit PRM
        # beams = PRM.hitFromHR(POY_PR2_PRM)
        # auxBeamDict['POY_PR2_PRM'] = beams['input']
        # auxBeamDict['POY_PRMs1'] = beams['s1']
        # auxBeamDict['POY_PRMt1'] = beams['t1']    


#}}}

#{{{ SRCX

    #Construct SRCX starting from ITMX

    #Hit ITMX
    b=beamITMXtrans.copy()
    b.propagate(1)
    b.flip()
    beams = ITMX.hitFromHR(b, order=1)
    beamPOXs1 = beams['s1']
    beamITMXreturn = beams['t1']

    #Initialize the beam at the HR surface of ITMX
    beamITMXreturn.optDist = beamITMXreturn.optDist - beamPOXs1.optDist
    beamITMXreturn.Gouyx = beamITMXreturn.Gouyx - beamPOXs1.Gouyx
    beamITMXreturn.Gouyy = beamITMXreturn.Gouyy - beamPOXs1.Gouyy

    #Hit the BS
    beams = BS.hitFromAR(beamITMXreturn, order=2)
    beamDict['beamITMXtoBS'] = beams['input']
    beamBStoSR3X = beams['r2']

    beamBS_Xs1 = beams['s1']
    beamDict['beamBS_Xs1'] = beamBS_Xs1
    beamBS_Xs2 = beams['s2']
    beamDict['beamBS_Xs2'] = beamBS_Xs2

    #Hit SR3
    beams = SR3.hitFromHR(beamBStoSR3X)
    beamBStoSR3X = beams['input']
    beamDict['beamBStoSR3X'] = beamBStoSR3X
    beam_from_SR3 = beams['r1']

    #Hit SR2
    beams = SR2.hitFromHR(beam_from_SR3)
    beamSR3toSR2X = beams['input']
    beamDict['beamSR3toSR2X'] = beamSR3toSR2X
    beam_from_SR2 = beams['r1']
    
    #Hit SRM
    beams = SRM.hitFromHR(beam_from_SR2)
    beamSR2toSRMX = beams['input']
    beamDict['beamSR2toSRMX'] = beamSR2toSRMX
    beamSRMs1X = beams['s1']
    beamDict['beamSRMs1X'] = beamSRMs1X
    beamSRMt1X = beams['t1']
    beamDict['beamSRMt1X'] = beamSRMt1X

#}}}

#{{{ SRCY

    #Construct SRCY starting from ITMY

    b=beamITMYtrans.copy()
    b.propagate(1)
    b.flip()
    beams = ITMY.hitFromHR(b, order=2)
    beamITMYreturn = beams['t1']
    beamPOYs1 = beams['s1']
    
    #Initialize the beam at the HR surface of ITMX
    beamITMYreturn.optDist = beamITMYreturn.optDist - beamPOYs1.optDist
    beamITMYreturn.Gouyx = beamITMYreturn.Gouyx - beamPOYs1.Gouyx
    beamITMYreturn.Gouyy = beamITMYreturn.Gouyy - beamPOYs1.Gouyy
    
    #Hit the BS
    beams = BS.hitFromHR(beamITMYreturn, order=2)
    beamDict['beamITMYtoBS'] = beams['input']
    beamBStoSR3Y = beams['t1']

    beamBS_Ys1 = beams['s1']
    beamDict['beamBS_Ys1'] = beamBS_Ys1

    beamBS_Ys2 = beams['s2']
#    auxBeamDict['beamBS_Ys2'] = beamBS_Ys2
    beamBS_Yr2 = beams['r2']
 #   auxBeamDict['beamBS_Yr2'] = beamBS_Yr2
    beamBS_Yr2.length=20.0


    #Hit SR3
    beams = SR3.hitFromHR(beamBStoSR3Y)
    beamBStoSR3Y = beams['input']
    beamDict['beamBStoSR3Y'] = beamBStoSR3Y
    beam_from_SR3 = beams['r1']

    #Hit SR2
    beams = SR2.hitFromHR(beam_from_SR3)
    beamSR3toSR2Y = beams['input']
    beamDict['beamSR3toSR2Y'] = beamSR3toSR2Y
    beam_from_SR2 = beams['r1']

    #Hit SRM
    beams = SRM.hitFromHR(beam_from_SR2)
    beamSR2toSRMY = beams['input']
    beamDict['beamSR2toSRMY'] = beamSR2toSRMY
    beamSRMs1Y = beams['s1']
    beamDict['beamSRMs1Y'] = beamSRMs1Y
    beamSRMt1Y = beams['t1']
    beamDict['beamSRMt1Y'] = beamSRMt1Y
    
#}}}

#{{{ Extract parameters

    v1 = -beamDict['beamPR3toBS'].dirVect
    v2 = BS.normVectHR
    BSIncAngle = np.arccos(np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))

    #Critical parameters
    results = {'ITMXangle': rad2deg(beamITMXs1.dirAngle),
               'ITMYangle': rad2deg(beamITMYs1.dirAngle),
               'ITMXbeamCentering': (ITMX.HRcenter - beamITMXtrans.pos)[1],
               'ITMYbeamCentering': (ITMY.HRcenter - beamITMYtrans.pos)[0],
               'LPRCX': beamITMXtrans.optDist,
               'LPRCY': beamITMYtrans.optDist,
               'LSRCX': beamSRMs1X.optDist,
               'LSRCY': beamSRMs1Y.optDist,
               'BSIncAngle': BSIncAngle}
    
#}}}

    return (results, beamDict, auxBeamDict)

#}}}

#{{{ *** Function to propagate one-way from PRM  ***

def propagateOpticalPathFromPRM(q0=None):

#{{{ init

    #Initialize the beamDict
    beamDict={}
    auxBeamDict={}

    if q0 is None:
        q0 = gauss.Rw2q(ROC=-1/PRM.inv_ROC_HR, w=4*mm)
#}}}

#{{{ PRC

    #First, prepare a beam which matches the ROC of the PRM and a given waist size
    beam_on_PRM = beam.GaussianBeam(q0=q0, pos=PRM.HRcenter, dirAngle=PRM.normAngleHR)
    #Set the starting point for measuring the optical distance    
    beam_on_PRM.optDist = 0.0

    #Hit PR2
    beams = PR2.hitFromHR(beam_on_PRM, order=0)
    beamPRMtoPR2 = beams['input']
    beamDict['beamPRMtoPR2'] = beamPRMtoPR2
    beam_from_PR2 = beams['r1']

    #Hit PR3
    beams = PR3.hitFromHR(beam_from_PR2, order=0)
    beamPR2toPR3 = beams['input']
    beamDict['beamPR2toPR3'] = beamPR2toPR3
    beam_from_PR3 = beams['r1']

    #Hit BS
    beams = BS.hitFromHR(beam_from_PR3, order=1)

    beamPR3toBS = beams['input']
    beamDict['beamPR3toBS'] = beamPR3toBS
    beamBS_PRs1 = beams['s1']
    beamDict['beamBS_PRs1'] = beamBS_PRs1

    beamBSrefl = beams['r1']
    beamBStrans = beams['t1']

    #Hit ITMX
    beams = ITMX.hitFromAR(beamBStrans, order=2)

    beamBStoITMX = beams['input']
    beamDict['beamBStoITMX'] = beamBStoITMX
    beamITMXs1 = beams['s1']
    beamDict['beamITMXs1'] = beamITMXs1
    beamITMXtrans = beams['t1']
    beamDict['beamITMXtrans'] = beamITMXtrans
    
    #Hit ITMY
    beams = ITMY.hitFromAR(beamBSrefl, order=2)

    beamBStoITMY = beams['input']
    beamDict['beamBStoITMY'] = beamBStoITMY
    beamITMYs1 = beams['s1']
    beamDict['beamITMYs1'] = beamITMYs1
    beamITMYtrans = beams['t1']
    beamDict['beamITMYtrans'] = beamITMYtrans    

#}}}

#{{{ Extract parameters

    v1 = -beamDict['beamPR3toBS'].dirVect
    v2 = BS.normVectHR
    BSIncAngle = np.arccos(np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))

    #Critical parameters
    results = {'ITMXangle': rad2deg(beamITMXs1.dirAngle),
               'ITMYangle': rad2deg(beamITMYs1.dirAngle),
               'ITMXbeamCentering': (ITMX.HRcenter - beamITMXtrans.pos)[1],
               'ITMYbeamCentering': (ITMY.HRcenter - beamITMYtrans.pos)[0],
               'LPRCX': beamITMXtrans.optDist,
               'LPRCY': beamITMYtrans.optDist,
               'LPRCavg':(beamITMXtrans.optDist+beamITMYtrans.optDist)/2,
               'Lasym':(beamITMXtrans.optDist-beamITMYtrans.optDist),
               'BSIncAngle': BSIncAngle}
    
    return (results, beamDict, auxBeamDict)

#}}}

#}}}

#{{{ *** Function to propagate one-way from SRM  ***

def propagateOpticalPathFromSRM(q0=None):

#{{{ init

    #Initialize the beamDict
    beamDict={}
    auxBeamDict={}

    if q0 is None:
        q0 = gauss.Rw2q(ROC=-1/SRM.inv_ROC_HR, w=4*mm)
#}}}

#{{{ SRC

    #First, prepare a beam which matches the ROC of the SRM and a given waist size
    beam_on_SRM = beam.GaussianBeam(q0=q0, pos=SRM.HRcenter, dirAngle=SRM.normAngleHR)
    #Set the starting point for measuring the optical distance    
    beam_on_SRM.optDist = 0.0

    #Hit SR2
    beams = SR2.hitFromHR(beam_on_SRM, order=0)
    beamSRMtoSR2 = beams['input']
    beamDict['beamSRMtoSR2'] = beamSRMtoSR2
    beam_from_SR2 = beams['r1']

    #Hit SR3
    beams = SR3.hitFromHR(beam_from_SR2, order=0)
    beamSR2toSR3 = beams['input']
    beamDict['beamSR2toSR3'] = beamSR2toSR3
    beam_from_SR3 = beams['r1']

    #Hit BS
    beams = BS.hitFromAR(beam_from_SR3, order=2)

    beamSR3toBS = beams['input']
    beamDict['beamSR3toBS'] = beamSR3toBS
    beamBS_SRs1 = beams['s1']
    beamDict['beamBS_SRs1'] = beamBS_SRs1
    beamBS_SRs2 = beams['s2']
    beamDict['beamBS_SRs2'] = beamBS_SRs2

    beamBSrefl = beams['r2']
    beamBStrans = beams['t1']

    #Hit ITMX
    beams = ITMX.hitFromAR(beamBSrefl, order=2)

    beamBStoITMX = beams['input']
    beamDict['beamBStoITMX'] = beamBStoITMX
    beamITMXs1 = beams['s1']
    beamDict['beamITMXs1'] = beamITMXs1
    beamITMXtrans = beams['t1']
    beamDict['beamITMXtrans'] = beamITMXtrans
    
    #Hit ITMY
    beams = ITMY.hitFromAR(beamBStrans, order=2)

    beamBStoITMY = beams['input']
    beamDict['beamBStoITMY'] = beamBStoITMY
    beamITMYs1 = beams['s1']
    beamDict['beamITMYs1'] = beamITMYs1
    beamITMYtrans = beams['t1']
    beamDict['beamITMYtrans'] = beamITMYtrans    

#}}}

#{{{ Extract parameters

    v1 = -beamDict['beamSR3toBS'].dirVect
    v2 = -BS.normVectHR
    BSIncAngle = np.arccos(np.dot(v1,v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))

    #Critical parameters
    results = {'ITMXangle': rad2deg(beamITMXs1.dirAngle),
               'ITMYangle': rad2deg(beamITMYs1.dirAngle),
               'ITMXbeamCentering': (ITMX.HRcenter - beamITMXtrans.pos)[1],
               'ITMYbeamCentering': (ITMY.HRcenter - beamITMYtrans.pos)[0],
               'LSRCX': beamITMXtrans.optDist,
               'LSRCY': beamITMYtrans.optDist,
               'LSRCavg':(beamITMXtrans.optDist+beamITMYtrans.optDist)/2,
               'Lasym':(beamITMXtrans.optDist-beamITMYtrans.optDist),
               'BSIncAngle': BSIncAngle}
    
    return (results, beamDict, auxBeamDict)

#}}}

#}}}

#{{{ ** Function to propagate round trip of PRC  **

def propagateRoundTripPRC(q0):

    beamDictX = {}
    beamDictY = {}    

#{{{ Injection part

    #Beam on PRM
    beamOnPRM = beam.GaussianBeam(q0)
    beamOnPRM.pos = PRM.HRcenter
    beamOnPRM.dirVect = PRM.normVectHR
    beamOnPRM.optDist = 0.0
    beamOnPRM.Gouyx = 0.0
    beamOnPRM.Gouyy = 0.0

    #Hit PR2
    beams = PR2.hitFromHR(beamOnPRM, order=0)
    beamPRMtoPR2 = beams['input']
    beamPR2r1 = beams['r1']

    #Hit PR3
    beams = PR3.hitFromHR(beamPR2r1, order=0)
    beamPR2toPR3 = beams['input']
    beamPR3r1 = beams['r1']

    #Hit BS
    beams = BS.hitFromHR(beamPR3r1, order=0)
    beamPR3toBS = beams['input']
    beamBSr1 = beams['r1']
    beamBSt1 = beams['t1']    

#}}}

#{{{ X-ARM

    #Hit ITMX
    beams = ITMX.hitFromAR(beamBSt1, order=2)
    beamITMXr2 = beams['r2']
    beamDictX['beamITMXt1'] = beams['t1']
    a = beams['input']
    a.propagate(a.length)
    beamDictX['beamITMXInput'] = a
    beamDictX['beamITMXs1'] = beams['s1']
    beamDictX['beamITMXs2'] = beams['s2']
    beamDictX['beamITMXr2'] = beams['r2']        
    
    #Return to BS
    beams = BS.hitFromAR(beamITMXr2, order=0)
    beamBSt1Ret = beams['t1']

    #Hit PR3
    beams = PR3.hitFromHR(beamBSt1Ret, order=0)
    beamPR3r1Ret = beams['r1']

    #Hit PR2
    beams = PR2.hitFromHR(beamPR3r1Ret, order=0)
    beamPR2r1Ret = beams['r1']

    #Hit PRM
    beams = PRM.hitFromHR(beamPR2r1Ret, order=0)
    beamPRMr1RetX = beams['r1']
    beamBackToPRM = beams['input']
    beamBackToPRM.propagate(beamBackToPRM.length)
    beamDictX['beamBackToPRM'] = beamBackToPRM
    
    beamDictX['beamPRMr1Ret'] = beamPRMr1RetX
    beamDictX['beamOnPRM'] = beamOnPRM

#}}}

#{{{ Y-ARM

    #Hit ITMY
    beams = ITMY.hitFromAR(beamBSr1, order=2)
    beamITMYr2 = beams['r2']
    beamDictY['beamITMYt1'] = beams['t1']
    a = beams['input']
    a.propagate(a.length)
    beamDictY['beamITMYInput'] = a
    beamDictY['beamITMYs1'] = beams['s1']
    beamDictY['beamITMYs2'] = beams['s2']
    beamDictY['beamITMYr2'] = beams['r2']        
    
    #Return to BS
    beams = BS.hitFromHR(beamITMYr2, order=0)
    beamBSr1Ret = beams['r1']

    #Hit PR3
    beams = PR3.hitFromHR(beamBSr1Ret, order=0)
    beamPR3r1Ret = beams['r1']

    #Hit PR2
    beams = PR2.hitFromHR(beamPR3r1Ret, order=0)
    beamPR2r1Ret = beams['r1']

    #Hit PRM
    beams = PRM.hitFromHR(beamPR2r1Ret, order=0)
    beamPRMr1RetY = beams['r1']
    beamBackToPRM = beams['input']
    beamBackToPRM.propagate(beamBackToPRM.length)
    beamDictY['beamBackToPRM'] = beamBackToPRM    

    beamDictY['beamPRMr1Ret'] = beamPRMr1RetY
    beamDictY['beamOnPRM'] = beamOnPRM

#}}}

#{{{ Check results

    result = {}

    (q1, match1) = gauss.optimalMatching(beamDictX['beamPRMr1Ret'].qx, beamDictX['beamPRMr1Ret'].qy)
    (q2, match2) = gauss.optimalMatching(beamDictY['beamPRMr1Ret'].qx, beamDictY['beamPRMr1Ret'].qy)
    (qr, match0) = gauss.optimalMatching(q1,q2)    

#}}}

    return (qr, beamDictX, beamDictY)

#}}}

#{{{ ** Function to propagate round trip of SRC  **

def propagateRoundTripSRC(q0):

    beamDictX = {}
    beamDictY = {}    

#{{{ Injection part

    #Beam on SRM
    beamOnSRM = beam.GaussianBeam(q0)
    beamOnSRM.pos = SRM.HRcenter
    beamOnSRM.dirVect = SRM.normVectHR
    beamOnSRM.optDist = 0.0
    beamOnSRM.Gouyx = 0.0
    beamOnSRM.Gouyy = 0.0

    #Hit SR2
    beams = SR2.hitFromHR(beamOnSRM, order=0)
    beamSRMtoSR2 = beams['input']
    beamSR2r1 = beams['r1']

    #Hit SR3
    beams = SR3.hitFromHR(beamSR2r1, order=0)
    beamSR2toSR3 = beams['input']
    beamSR3r1 = beams['r1']

    #Hit BS
    beams = BS.hitFromAR(beamSR3r1, order=2)
    beamSR3toBS = beams['input']
    beamBSr2 = beams['r2']
    beamBSt1 = beams['t1']    

#}}}

#{{{ X-ARM

    #Hit ITMX
    beams = ITMX.hitFromAR(beamBSr2, order=1)
    beamITMXr2 = beams['r2']
    beamDictX['beamITMXt1'] = beams['t1']
    a = beams['input']
    a.propagate(a.length)
    beamDictX['beamITMXInput'] = a
    beamDictX['beamITMXs1'] = beams['s1']
    beamDictX['beamITMXs2'] = beams['s2']
    beamDictX['beamITMXr2'] = beams['r2']        
    
    #Return to BS
    beams = BS.hitFromAR(beamITMXr2, order=1)
    beamBSr2Ret = beams['r2']

    #Hit SR3
    beams = SR3.hitFromHR(beamBSr2Ret, order=0)
    beamSR3r1Ret = beams['r1']

    #Hit SR2
    beams = SR2.hitFromHR(beamSR3r1Ret, order=0)
    beamSR2r1Ret = beams['r1']

    #Hit SRM
    beams = SRM.hitFromHR(beamSR2r1Ret, order=0)
    beamSRMr1RetX = beams['r1']
    beamBackToSRM = beams['input']
    beamBackToSRM.propagate(beamBackToSRM.length)
    beamDictX['beamBackToSRM'] = beamBackToSRM
    
    beamDictX['beamSRMr1Ret'] = beamSRMr1RetX
    beamDictX['beamOnSRM'] = beamOnSRM

    
#}}}

#{{{ Y-ARM

    #Hit ITMY
    beams = ITMY.hitFromAR(beamBSt1, order=1)
    beamITMYr2 = beams['r2']
    beamDictY['beamITMYt1'] = beams['t1']
    a = beams['input']
    a.propagate(a.length)
    beamDictY['beamITMYInput'] = a
    beamDictY['beamITMYs1'] = beams['s1']
    beamDictY['beamITMYs2'] = beams['s2']
    beamDictY['beamITMYr2'] = beams['r2']        
    
    #Return to BS
    beams = BS.hitFromHR(beamITMYr2, order=0)
    beamBSt1Ret = beams['t1']

    #Hit SR3
    beams = SR3.hitFromHR(beamBSt1Ret, order=0)
    beamSR3r1Ret = beams['r1']

    #Hit SR2
    beams = SR2.hitFromHR(beamSR3r1Ret, order=0)
    beamSR2r1Ret = beams['r1']

    #Hit SRM
    beams = SRM.hitFromHR(beamSR2r1Ret, order=0)
    beamSRMr1RetY = beams['r1']
    beamBackToSRM = beams['input']
    beamBackToSRM.propagate(beamBackToSRM.length)
    beamDictY['beamBackToSRM'] = beamBackToSRM    

    beamDictY['beamSRMr1Ret'] = beamSRMr1RetY
    beamDictY['beamOnSRM'] = beamOnSRM

#}}}

#{{{ Check results

    result = {}

    (q1, match1) = gauss.optimalMatching(beamDictX['beamSRMr1Ret'].qx, beamDictX['beamSRMr1Ret'].qy)
    (q2, match2) = gauss.optimalMatching(beamDictY['beamSRMr1Ret'].qx, beamDictY['beamSRMr1Ret'].qy)
    (qr, match0) = gauss.optimalMatching(q1,q2)    

#}}}

    return (qr, beamDictX, beamDictY)

#}}}

#{{{ *** Function to draw optical path ***

def drawOpticalPath(opticsDict, beamDict, auxBeamDict, chamberDict, filename='KAGRA_OptLayout.dxf'):

#{x{{ Make copies of beams and optics
    #Copies are necessary to avoid the translation of the
    #objects below from intefering with the iLCGT layout 
    #after this section.
    #To copy the items of the dictionary, iteritems() is
    #used. For some reason, copy.deepcopy() did not work
    #correctly

    beamDictCopy = {}
    for (key, value) in beamDict.iteritems():
        beamDictCopy[key] = value.copy()

    auxBeamDictCopy = {}
    for (key, value) in auxBeamDict.iteritems():
        auxBeamDictCopy[key] = value.copy()

    opticsDictCopy = {}
    for (key, value) in opticsDict.iteritems():
        opticsDictCopy[key] = copy.copy(value)

    chamberDictCopy = {}
    for (key, value) in chamberDict.iteritems():
        chamberDictCopy[key] = copy.copy(value)

    
#{{{ Translate all objects to put the BS at the center

    transAll(beamDictCopy.values(), -BS.HRcenter)
    transAll(auxBeamDictCopy.values(), -BS.HRcenter)
    transAll(opticsDictCopy.values(), -BS.HRcenter)

    for k in chamberDictCopy.keys():
        chamberDictCopy[k] = chamberDictCopy[k] -BS.HRcenter

#}}}

#{{{ ++ Canvas object ++

    d = draw.Canvas()
    d.unit = 'm'
    d.add_layer("main_beam", color=(255,0,0))
    d.add_layer("main_beam_width", color=(255,0,255))    
    d.add_layer("aux_beam", color=(0,255,0))
    d.add_layer("aux_beam_width", color=(0,255,255))    

#}}}

#{{{ ++ Draw Beams ++

    drawAllBeams(d, beamDictCopy.values(), drawWidth=True, sigma=2.7, drawPower=False,
                     drawROC=False, drawGouy=False, drawOptDist=False, layer='main_beam',
                        fontSize=0.01)

    drawAllBeams(d, auxBeamDictCopy.values(), drawWidth=True, sigma=1.0, drawPower=False,
                 drawROC=False, drawGouy=False, drawOptDist=False, layer='aux_beam',
                 fontSize=0.01)

#}}}

#{{{ ++ Draw Optics ++

    drawAllOptics(d, opticsDictCopy.values(), drawName=True)

#}}}

#{{{ ++ Draw Vacuum Tanks ++

    for key in chamberDictCopy.keys():
        d.add_shape(draw.Circle(center=chamberDictCopy[key], radius=1.0), layername='Vacuum')

#}}}

#{{{ Save DXF file 

    renderer.renderDXF(d, filename)

#}}}

#}}}

#{{{ *** Function to revert to bKAGRA ***

def restorebKAGRA():
    for (key, value) in opticsDict_bKAGRA.iteritems():
        globals()[key] = value.copy()

    globals()['opticsDict'] = {'PRM':PRM, 'PR2':PR2, 'PR3':PR3, 'BS':BS, 'ITMX':ITMX,
              'ITMY':ITMY, 'SR3':SR3, 'SR2':SR2, 'SRM':SRM, 'ETMX':ETMX, 'ETMY':ETMY}
    globals()['Larm'] = 3*km
    globals()['beamArmWaistX'] = beamDict_bKAGRA['beamArmWaistX'].copy()
    globals()['beamArmWaistY'] = beamDict_bKAGRA['beamArmWaistY'].copy()
    globals()['beamFromMMT'] = beamDict_bKAGRA['beamFromMMT'].copy()
    globals()['beamOnPRM'] = beamDict_bKAGRA['beamOnPRM'].copy()
    globals()['beamITMXtoETMX'] = beamDict_bKAGRA['beamITMXtoETMX'].copy()
    globals()['beamITMYtoETMY'] = beamDict_bKAGRA['beamITMYtoETMY'].copy()
    globals()['beamOnPRMAR'] = beamDict_bKAGRA['beamOnPRMAR'].copy()
    
#}}}

#{{{ *** Adjust folding length ***

#{{{ *** Change Lp2 ***

def changeLp2(d, d2=0.0):
    '''
    Change the distance between PR2 and PR3 without
    breaking the alignment.
    '''

    #Initial distance between PR2 and PR3
    v = PR3.HRcenter - PR2.HRcenter
    Lp2_0 = np.linalg.norm(v)
    
    #Move PR3 by d2
    inc_vect = PR3.HRcenter - BS.HRcenter
    inc_vect = inc_vect/np.linalg.norm(inc_vect)
    
    PR3.HRcenter = PR3.HRcenter + d2*inc_vect
    
    #Move PR2
    inc_vect = PR2.HRcenter - PRM.HRcenter
    inc_vect = inc_vect/np.linalg.norm(inc_vect)

    PR2.HRcenter = PR2.HRcenter + d*inc_vect

    #Distance between PR2 and PR3
    v = PR3.HRcenter - PR2.HRcenter
    Lp2 = np.linalg.norm(v)
    dLp2 = Lp2 - Lp2_0
    
    #Move PRM
    PRM.HRcenter = PRM.HRcenter + (dLp2+d+d2)*inc_vect
    
    out_vect = PR3.HRcenter - PR2.HRcenter
    out_vect = out_vect/np.linalg.norm(out_vect)
    
    #Rotate PR2
    PR2.normVectHR = (-inc_vect + out_vect)/2

    inc_vect = PR3.HRcenter - PR2.HRcenter
    inc_vect = inc_vect/np.linalg.norm(inc_vect)
    
    out_vect = BS.HRcenter - PR3.HRcenter
    out_vect = out_vect/np.linalg.norm(out_vect)

    #Rotate PR3
    PR3.normVectHR = (-inc_vect + out_vect)/2
    
#}}}

#{{{ *** Change Ls2 ***

def changeLs2(d, d2=0.0, inc_vect_SR3=None):
    '''
    Change the distance between SR2 and SR3 without
    breaking the alignment.
    '''

    if inc_vect_SR3 is None:
        inc_vect_SR3 = SR3.HRcenter - beamDict_bKAGRA['beamBStoSR3X'].pos
        inc_vect_SR3 = out_vect/np.linalg.norm(out_vect)
        
    #Initial distance between SR2 and SR3
    v = SR3.HRcenter - SR2.HRcenter
    Ls2_0 = np.linalg.norm(v)

    #Move SR3
    
    SR3.HRcenter = SR3.HRcenter + d2*inc_vect_SR3

    #Move SR2
    
    inc_vect = SR2.HRcenter - SRM.HRcenter
    inc_vect = inc_vect/np.linalg.norm(inc_vect)

    SR2.HRcenter = SR2.HRcenter + d*inc_vect

    #Initial distance between SR2 and SR3
    v = SR3.HRcenter - SR2.HRcenter
    Ls2 = np.linalg.norm(v)
    dLs2 = Ls2 - Ls2_0
    
    #Move SRM
    SRM.HRcenter = SRM.HRcenter + (dLs2+d+d2)*inc_vect
    
    out_vect = SR3.HRcenter - SR2.HRcenter
    out_vect = out_vect/np.linalg.norm(out_vect)
    
    #Rotate SR2
    SR2.normVectHR = (-inc_vect + out_vect)/2

    inc_vect = SR3.HRcenter - SR2.HRcenter
    inc_vect = inc_vect/np.linalg.norm(inc_vect)
    

    #Rotate SR3
    SR3.normVectHR = (-inc_vect - inc_vect_SR3)/2
        
#}}}

#{{{ *** Revert the changes ***

def revertPRCoptics():
    PRM.HRcenter = opticsDict_bKAGRA['PRM'].HRcenter.copy()
    PR2.HRcenter = opticsDict_bKAGRA['PR2'].HRcenter.copy()
    PR3.HRcenter = opticsDict_bKAGRA['PR3'].HRcenter.copy()

    PRM.normVectHR = opticsDict_bKAGRA['PRM'].normVectHR.copy()
    PR2.normVectHR = opticsDict_bKAGRA['PR2'].normVectHR.copy()
    PR3.normVectHR = opticsDict_bKAGRA['PR3'].normVectHR.copy()

def revertSRCoptics():
    SRM.HRcenter = opticsDict_bKAGRA['SRM'].HRcenter.copy()
    SR2.HRcenter = opticsDict_bKAGRA['SR2'].HRcenter.copy()
    SR3.HRcenter = opticsDict_bKAGRA['SR3'].HRcenter.copy()

    SRM.normVectHR = opticsDict_bKAGRA['SRM'].normVectHR.copy()
    SR2.normVectHR = opticsDict_bKAGRA['SR2'].normVectHR.copy()
    SR3.normVectHR = opticsDict_bKAGRA['SR3'].normVectHR.copy()

def revertiPRCoptics():
    PRM.HRcenter = opticsDict_iKAGRA['PRM'].HRcenter.copy()
    PR2.HRcenter = opticsDict_iKAGRA['PR2'].HRcenter.copy()
    PR3.HRcenter = opticsDict_iKAGRA['PR3'].HRcenter.copy()

    PRM.normVectHR = opticsDict_iKAGRA['PRM'].normVectHR.copy()
    PR2.normVectHR = opticsDict_iKAGRA['PR2'].normVectHR.copy()
    PR3.normVectHR = opticsDict_iKAGRA['PR3'].normVectHR.copy()

def revertiSRCoptics():
    SRM.HRcenter = opticsDict_iKAGRA['SRM'].HRcenter.copy()
    SR2.HRcenter = opticsDict_iKAGRA['SR2'].HRcenter.copy()
    SR3.HRcenter = opticsDict_iKAGRA['SR3'].HRcenter.copy()

    SRM.normVectHR = opticsDict_iKAGRA['SRM'].normVectHR.copy()
    SR2.normVectHR = opticsDict_iKAGRA['SR2'].normVectHR.copy()
    SR3.normVectHR = opticsDict_iKAGRA['SR3'].normVectHR.copy()

#}}}

#}}}

#{{{ PRC Eigenmode

def PRC_Eigenmode():
    '''
    Compute the eigen mode of PRC
    '''

    q0 = gauss.Rw2q(ROC=-1/PRM.inv_ROC_HR, w=4*mm)    
    (qr, b1, b2) = propagateRoundTripPRC(q0)

    M = (b1['beamPRMr1Ret'].Mx + b1['beamPRMr1Ret'].My +\
         b2['beamPRMr1Ret'].Mx+b2['beamPRMr1Ret'].My)/4

    A = M[0,0]
    B = M[0,1]
    C = M[1,0]
    D = M[1,1]

    qPRC = 1.0/((D-A)/(2*B)-1j*sp.sqrt(4-(A+D)**2)/(2*B))

    return qPRC

#}}}

#{{{ PRC_ARM_modematch()

def PRC_ARM_modematch():
    '''
    Compute the mode matching between the PRC and Arms
    '''
    qPRC = PRC_Eigenmode()

    if np.imag(qPRC) == 0:
        #PRC is unstable
        modeMatch = np.nan
        GouyPhase = np.nan
    else:
        #Propagate the eigen mode through PRC
        (results, beamDict, auxBeamDict) = propagateOpticalPathFromPRM(qPRC)

        #Mode matching with the arm cavity eigen modes
        qPRCX = beamDict['beamITMXtrans'].q
        qPRCY = beamDict['beamITMYtrans'].q    
        qARMX = beamITMXtoETMX.q
        qARMY = beamITMYtoETMY.q

        modeMatch = \
              (gauss.modeMatching(qARMX, qPRCX) + gauss.modeMatching(qARMY, qPRCY))/2
        bx = beamDict['beamITMXtrans']
        by = beamDict['beamITMYtrans']
        GouyPhase = (bx.Gouyx + bx.Gouyy + by.Gouyx + by.Gouyy)/4

    return (modeMatch, GouyPhase)

#}}}

#{{{ SRC Eigenmode

def SRC_Eigenmode():
    '''
    Compute the eigen mode of SRC
    '''

    q0 = gauss.Rw2q(ROC=-1/SRM.inv_ROC_HR, w=4*mm)    
    (qr, b1, b2) = propagateRoundTripSRC(q0)

    M = (b1['beamSRMr1Ret'].Mx + b1['beamSRMr1Ret'].My +\
         b2['beamSRMr1Ret'].Mx+b2['beamSRMr1Ret'].My)/4

    A = M[0,0]
    B = M[0,1]
    C = M[1,0]
    D = M[1,1]

    qSRC = 1.0/((D-A)/(2*B)-1j*sp.sqrt(4-(A+D)**2)/(2*B))

    return qSRC

#}}}

#{{{ SRC_ARM_modematch()

def SRC_ARM_modematch():
    '''
    Compute the mode matching between the PRC and Arms
    '''
    qSRC = SRC_Eigenmode()

    if np.imag(qSRC) == 0:
        #SRC is unstable
        modeMatch = np.nan
        GouyPhase = np.nan
    else:
        #Propagate the eigen mode through SRC
        (results, beamDict, auxBeamDict) = propagateOpticalPathFromSRM(qSRC)

        #Mode matching with the arm cavity eigen modes
        qSRCX = beamDict['beamITMXtrans'].q
        qSRCY = beamDict['beamITMYtrans'].q    
        qARMX = beamITMXtoETMX.q
        qARMY = beamITMYtoETMY.q

        modeMatch = \
              (gauss.modeMatching(qARMX, qSRCX) + gauss.modeMatching(qARMY, qSRCY))/2
        bx = beamDict['beamITMXtrans']
        by = beamDict['beamITMYtrans']
        GouyPhase = (bx.Gouyx + bx.Gouyy + by.Gouyx + by.Gouyy)/4

    return (modeMatch, GouyPhase)

#}}}

#{{{ Draw Template Generator

def make_draw_template(opticsDict=None, tube_offset_dict=None):
    if opticsDict is None:
        opticsDict = globals()
        
    dtpl = draw.Canvas()
    dtpl.unit = 'm'
    dtpl.add_layer("main_beam", color=(255,0,0))
    dtpl.add_layer("main_beam_width", color=(255,0,255))    
    dtpl.add_layer("aux_beam", color=(0,255,0))
    dtpl.add_layer("aux_beam_width", color=(0,255,255))    
    dtpl.add_layer("pox_beam", color=(0,0,255))
    dtpl.add_layer("pox_beam_width", color=(0,255,255))    
    dtpl.add_layer("poy_beam", color=(0,0,255))
    dtpl.add_layer("poy_beam_width", color=(0,255,255))    

    small_chamber_dia = 1.5
    bs_chamber_dia = 1.5
    tm_chamber_dia = 2.5
    beam_tube_dia = 0.785

    if tube_offset_dict is None:
        tube_offset_dict = {'PRM':(0.0,0.0), 'PR2':(0,-160*mm), 'PR3':(0,160*mm),
                            'SRM':(0.0,0.0), 'SR2':(-160*mm,0), 'SR3':(0,0)}

    
    #Small chambers
    cornerDict = {}
    s_width = small_chamber_dia +20*cm
    s_height = beam_tube_dia
    for optname in ['PRM','PR2','PR3']:
        center = tuple(opticsDict[optname].center)
        dtpl.add_shape(draw.Circle(center=center, radius=small_chamber_dia/2),
                       layername='Vacuum')

        center = center + np.array(tube_offset_dict[optname])
        corner = (center[0] - s_width/2, center[1] + s_height/2,0)
        dtpl.add_shape(draw.Rectangle(point=corner, width=s_width, height=-s_height),
                       layername='Vacuum')
        cornerDict[optname]=corner


    #Sort the mirrors by the x-coordinate
    mirrorList = ['PRM','PR3','PR2']
    idxs = np.argsort([opticsDict['PRM'].center[0], opticsDict['PR3'].center[0], opticsDict['PR2'].center[0]])
    M1 = mirrorList[idxs[0]]
    M2 = mirrorList[idxs[1]]
    M3 = mirrorList[idxs[2]]    

    #Connect the 1st mirror and the 2nd mirror

    start = (cornerDict[M1][0]+s_width, cornerDict[M1][1])
    end = (cornerDict[M2][0], cornerDict[M2][1])
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')
    start = (cornerDict[M1][0]+s_width, cornerDict[M1][1]-s_height)
    end = (cornerDict[M2][0], cornerDict[M2][1]-s_height)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')        


    #Connect PR3 and PR2
    start = (cornerDict[M2][0]+s_width, cornerDict[M2][1])
    end = (cornerDict[M3][0], cornerDict[M3][1])
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')
    start = (cornerDict[M2][0]+s_width, cornerDict[M2][1]-s_height)
    end = (cornerDict[M3][0], cornerDict[M3][1]-s_height)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')


    #Draw BS Chamber
    bs_width = bs_chamber_dia +20*cm
    bs_height = beam_tube_dia
    center = tuple(opticsDict['BS'].center)
    dtpl.add_shape(draw.Circle(center=center, radius=bs_chamber_dia/2),
                       layername='Vacuum')

    corner = (center[0] - bs_width/2, center[1]+bs_height/2,0)
    dtpl.add_shape(draw.Rectangle(point=corner, width=bs_width, height=-bs_height),
                       layername='Vacuum')
    cornerDict['BS_h']=corner
    corner = (center[0] - bs_height/2 , center[1] + bs_width/2,0)
    dtpl.add_shape(draw.Rectangle(point=corner, width=bs_height, height=-bs_width),
                       layername='Vacuum')
    cornerDict['BS_v']=corner

    #Connect PR2 and BS
    start = (cornerDict[M3][0]+s_width, cornerDict[M3][1])
    end = (cornerDict['BS_h'][0], cornerDict['BS_h'][1])
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')    
    start = (cornerDict[M3][0]+s_width, cornerDict[M3][1]-s_height)
    end = (cornerDict['BS_h'][0], cornerDict['BS_h'][1]-s_height)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')        

    #SRC Mirrors
    for optname in ['SRM','SR2','SR3']:
        center = tuple(opticsDict[optname].center)
        dtpl.add_shape(draw.Circle(center=center, radius=small_chamber_dia/2),
                       layername='Vacuum')

        center = center + np.array(tube_offset_dict[optname])
        corner = (center[0] - s_height/2, center[1] + s_width/2, 0)
        dtpl.add_shape(draw.Rectangle(point=corner, width=s_height, height=-s_width),
                       layername='Vacuum')
        cornerDict[optname]=corner

    #Sort the mirrors by the y-coordinate
    mirrorList = ['SRM','SR3','SR2']
    idxs = np.argsort([opticsDict['SRM'].center[1], opticsDict['SR3'].center[1], opticsDict['SR2'].center[1]])
    M1 = mirrorList[idxs[0]]
    M2 = mirrorList[idxs[1]]
    M3 = mirrorList[idxs[2]]    

    #Connect the 1st mirror and the 2nd mirror


    #Connect SRM and SR3
    start = (cornerDict[M1][0], cornerDict[M1][1])
    end = (cornerDict[M2][0], cornerDict[M2][1]-s_width)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')
    start = (cornerDict[M1][0]+s_height, cornerDict[M1][1])
    end = (cornerDict[M2][0]+s_height, cornerDict[M2][1]-s_width)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')

    #Connect SR3 and SR2
    start = (cornerDict[M2][0], cornerDict[M2][1])
    end = (cornerDict[M3][0], cornerDict[M3][1]-s_width)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')    
    start = (cornerDict[M2][0]+s_height, cornerDict[M2][1])
    end = (cornerDict[M3][0]+s_height, cornerDict[M3][1]-s_width)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')    

    #Connect SR2 and BS
    start = (cornerDict[M3][0], cornerDict[M3][1])
    end = (cornerDict['BS_v'][0], cornerDict['BS_v'][1]-bs_width)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')
    start = (cornerDict[M3][0]+s_height, cornerDict[M3][1])
    end = (cornerDict['BS_v'][0]+s_height, cornerDict['BS_v'][1]-bs_width)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')        


    #Draw ITM Chambers
    tm_width = tm_chamber_dia +20*cm
    tm_height = beam_tube_dia
    center = tuple(opticsDict['ITMX'].center)
    dtpl.add_shape(draw.Circle(center=center, radius=tm_chamber_dia/2),
                       layername='Vacuum')

    corner = (center[0] - tm_width/2, center[1]+tm_height/2,0)
    dtpl.add_shape(draw.Rectangle(point=corner, width=tm_width, height=-tm_height),
                       layername='Vacuum')
    cornerDict['ITMX']=corner

    center = tuple(opticsDict['ITMY'].center)
    dtpl.add_shape(draw.Circle(center=center, radius=tm_chamber_dia/2),
                       layername='Vacuum')

    corner = (center[0] - tm_height/2, center[1]+tm_width/2,0)
    dtpl.add_shape(draw.Rectangle(point=corner, width=tm_height, height=-tm_width),
                       layername='Vacuum')
    cornerDict['ITMY']=corner

    #Connect BS and ITMX
    start = (cornerDict['BS_h'][0]+bs_width, cornerDict['BS_h'][1])
    end = (cornerDict['ITMX'][0], cornerDict['ITMX'][1])
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')    
    start = (cornerDict['BS_h'][0]+bs_width, cornerDict['BS_h'][1]-bs_height)
    end = (cornerDict['ITMX'][0], cornerDict['ITMX'][1]-tm_height)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')

    #Connect BS and ITMY
    start = (cornerDict['BS_v'][0], cornerDict['BS_v'][1])
    end = (cornerDict['ITMY'][0], cornerDict['ITMY'][1]-tm_width)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')    
    start = (cornerDict['BS_v'][0]+bs_height, cornerDict['BS_v'][1])
    end = (cornerDict['ITMY'][0]+tm_height, cornerDict['ITMY'][1]-tm_width)
    dtpl.add_shape(draw.Line(start, end), layername='Vacuum')

    return dtpl

#}}}

#}}}

#{{{ Preparation

#{{{ *** Parameters ***

#{{{ Wedge Angles

BSWedge = -deg2rad(0.08)
ITMXWedge = -deg2rad(0.025)
ITMYWedge = ITMXWedge

#}}}

#{{{ Mirror Dimensions

BS_BeamSize = 3.5*cm
ITM_DIA = 22*cm
ETM_DIA = 22*cm
BS_Thickness = 8*cm

#}}}

#{{{ Length

#Basic lengths
Larm = 3000.
Lprc = 66.591327988354962
Las = 3.329850847567223
Lsrc = 66.591327988354962
L_MIavg = 25.0
Lmc = 26.638806780537788

#PRC

#Distance between the PRM and PR3 required by Vacuum
D_PRM_PR3 = 2.7+1.0

#Distance between the BS and PR2 required by Vacuum
D_BS_PR2 = 2.7+2.0

#In the folding part, beams pass by the sides of the folding mirrors
#The separation between the beams and the mirrors should be
#large enough to avoid clipping.
#(Mirror Dia.)/2+4*sigma

#Distance between the PR3 edge and the beam from PRM to PR2
BeamDist1 = 25./2*cm+20*5*mm

#Distance between the PR2 edge and the beam from PR3 to BS
BeamDist2 = 25./2*cm+4*BS_BeamSize

#Length of the folding part
Lfld = (Lprc - L_MIavg - D_BS_PR2 - D_PRM_PR3)/3

#Folding angle (the incident angle to the folding mirror)
foldingAngle1 = np.arctan(BeamDist1/Lfld)/2
#foldingAngle1 = deg2rad(2.2)/2
foldingAngle2 = np.arctan(BeamDist2/Lfld)/2
#foldingAngle2 = deg2rad(1.686)/2

L_PR3_BS = Lfld + D_BS_PR2
L_PR2_PR3 = Lfld/np.cos(2*foldingAngle1)
L_PRM_PR2 = Lprc - L_MIavg - L_PR2_PR3 - L_PR3_BS

#MICH
L_BS_ITMX = L_MIavg + Las/2
L_BS_ITMY = L_MIavg - Las/2

L_PRC_X = L_PRM_PR2 + L_PR2_PR3 + L_PR3_BS + L_BS_ITMX
L_PRC_Y = L_PRM_PR2 + L_PR2_PR3 + L_PR3_BS + L_BS_ITMY

#SRC
L_SR3_BS = Lfld + D_BS_PR2
L_SR2_SR3 = Lfld/np.cos(2*foldingAngle1)
L_SRM_SR2 = Lsrc - L_MIavg - L_SR2_SR3 - L_SR3_BS

#}}}

#{{{ ROC

ITM_ROC = 1900*m
ETM_ROC = 1900*m

PRM_ROC = 306.426765439*m
PR2_ROC = -2.76
PR3_ROC = 24.58
SRM_ROC = 306.426765439*m
SR2_ROC = -2.76
SR3_ROC = 24.58   
    
#}}}

#{{{ Index of refraction
nsilica = 1.44967
nsilica_green = 1.46071
nsaph = 1.754
nsaph_green = 1.7717
#}}}

#}}}

#{{{ *** Define Mirrors ***

PRM = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=25*cm, thickness=10*cm,
                 wedgeAngle=deg2rad(0.25), inv_ROC_HR=1./PRM_ROC,
                 inv_ROC_AR=0,
                 Refl_HR=0.9, Trans_HR=1-0.9,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsilica, name='PRM', HRtransmissive=True)

PR2 = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=25*cm, thickness=10*cm,
                 wedgeAngle=deg2rad(0.25), inv_ROC_HR=1./PR2_ROC,
                 Refl_HR=1-500*ppm, Trans_HR=500*ppm,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsilica, name='PR2')

PR3 = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=25*cm, thickness=10*cm,
                 wedgeAngle=deg2rad(0.25), inv_ROC_HR=1./PR3_ROC,
                 Refl_HR=1-100*ppm, Trans_HR=100*ppm,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsilica, name='PR3')

BS = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=38*cm, thickness=BS_Thickness,
                 wedgeAngle=BSWedge, inv_ROC_HR=0.,
                 Refl_HR=0.5, Trans_HR=0.5,
                 Refl_AR=100*ppm, Trans_AR=1-100*ppm,
                 n=nsilica, name='BS', HRtransmissive=True)

ITMX = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=ITM_DIA, thickness=15*cm,
                 wedgeAngle=ITMXWedge, inv_ROC_HR=1./ITM_ROC,
                 Refl_HR=0.996, Trans_HR=1-0.996,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsaph, name='ITMX', HRtransmissive=True)

ITMY = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=ITM_DIA, thickness=15*cm,
                 wedgeAngle=ITMYWedge, inv_ROC_HR=1./ITM_ROC,
                 Refl_HR=0.996, Trans_HR=1-0.996,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsaph, name='ITMY', HRtransmissive=True)

SRM = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=25*cm, thickness=10*cm,
                 wedgeAngle=deg2rad(0.25), inv_ROC_HR=1./SRM_ROC,
                 inv_ROC_AR=0,
                 Refl_HR=1-0.1536, Trans_HR=0.1536,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsilica, name='SRM', HRtransmissive=True)

SR2= opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=25*cm, thickness=10*cm,
                 wedgeAngle=deg2rad(0.25), inv_ROC_HR=1./SR2_ROC,
                 Refl_HR=1-500*ppm, Trans_HR=500*ppm,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsilica, name='SR2')

SR3 = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=25*cm, thickness=10*cm,
                 wedgeAngle=deg2rad(0.25), inv_ROC_HR=1./SR3_ROC,
                 Refl_HR=1-100*ppm, Trans_HR=100*ppm,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsilica, name='SR3')

ETMX = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=ETM_DIA, thickness=15*cm,
                 wedgeAngle=deg2rad(0.25), inv_ROC_HR=1./ETM_ROC,
                 #Refl_HR=1-55*ppm, Trans_HR=55*ppm,
                  Refl_HR=0.01, Trans_HR=1-0.01,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsaph, name='ETMX')

ETMY = opt.Mirror(HRcenter=[0,0], normAngleHR=0.0,
                 diameter=ETM_DIA, thickness=15*cm,
                 wedgeAngle=deg2rad(0.25), inv_ROC_HR=1./ETM_ROC,
                 #Refl_HR=1-55*ppm, Trans_HR=55*ppm,
                  Refl_HR=0.01, Trans_HR=1-0.01,
                 Refl_AR=500*ppm, Trans_AR=1-500*ppm,
                 n=nsaph, name='ETMY')


opticsDict = {'PRM':PRM, 'PR2':PR2, 'PR3':PR3, 'BS':BS, 'ITMX':ITMX,
              'ITMY':ITMY, 'SR3':SR3, 'SR2':SR2, 'SRM':SRM, 'ETMX':ETMX, 'ETMY':ETMY}

#}}}

#}}}

#{{{ #### bKAGRA Default ####

#{{{ Parameters

targetGouyPRC = 16.5
targetGouySRC = 17.5
PR2_ROC = -3.08
PR3_ROC = 24.9
SR2_ROC = -2.977
SR3_ROC = 24.785

findStartPoint = False

#}}}

#{{{ Update Mirror ROCs

PR2.inv_ROC_HR = 1/PR2_ROC
PR3.inv_ROC_HR = 1/PR3_ROC

SR2.inv_ROC_HR = 1/SR2_ROC
SR3.inv_ROC_HR = 1/SR3_ROC

#}}}

#{{{ file names

log_file_name = 'bKAGRA_log.txt'
dxf_file_name = 'bKAGRA.dxf'
dxf_file_name_stray = 'bKAGRA_stray_beams.dxf'

#}}}

#{{{ == Optimal ITM incident angle ==

theta_w = ITMX.wedgeAngle
n = ITMX.n

theta_ITMX = np.arcsin(n*np.sin(theta_w))-theta_w

theta_w = ITMY.wedgeAngle
n = ITMY.n

theta_ITMY = np.arcsin(n*np.sin(theta_w))-theta_w

#}}}

#{{{ == Optimal BS incident angle ==

theta_w = BS.wedgeAngle
n = BS.n

def testfun(theta_BS):
    a1 = theta_BS - pi/2 + theta_ITMY
    a2 = np.arcsin(np.sin(a1)/n)
    a3 = a2 - theta_w
    a4 = np.arcsin(n*np.sin(a3))
    a5 = a4+theta_w
    return theta_ITMX - pi + a5 +theta_BS

ans = sopt.newton(testfun, pi/2+pi/4)

theta_BS = ans
theta_in_BS = -(3*pi/2 - 2*theta_BS - theta_ITMY)

#BS optical thickness
a1 = theta_BS - pi/2 + theta_ITMY
a2 = np.arcsin(np.sin(a1)/n)
dBS = BS.n*BS.thickness/np.cos(a2)

#}}}

#{{{ == Put Mirrors ==

#{{{ Prepare source beam

q = gauss.Rw2q(ROC=-1/PRM.inv_ROC_HR, w=4*mm)
srcBeam = beam.GaussianBeam(q0=q, pos=[0,0], dirAngle=0.0)
srcBeam.optDist = 0.0

#}}}

#{{{ PRM to BS

#Position the PRM at [0,0]
PRM.HRcenter = [0,0]
#Rotate the PRM
PRM.normAngleHR = theta_in_BS + 2*(foldingAngle2 - foldingAngle1)
srcBeam.dirAngle = theta_in_BS + 2*(foldingAngle2 - foldingAngle1)

#Put PR2
PR2.normAngleHR = pi+PRM.normAngleHR
PR2.rotate(foldingAngle1)
PR2.HRcenter = PRM.HRcenter + PRM.normVectHR*L_PRM_PR2

#Hit PR2
beams = PR2.hitFromHR(srcBeam, order=1)
beamToPR3 = beams['r1']

#Put PR3
PR3.HRcenter = PR2.HRcenter + L_PR2_PR3*beamToPR3.dirVect
PR3.normVectHR = - beamToPR3.dirVect
PR3.rotate(-foldingAngle2)

#Hit PR3
beams = PR3.hitFromHR(beamToPR3)
beamToBS = beams['r1']

#Put BS
BS.HRcenter = PR3.HRcenter + L_PR3_BS*beamToBS.dirVect
BS.normAngleHR = theta_BS

#}}}

#{{{ Roughly locate ITMs

#Hit BS
beams = BS.hitFromHR(beamToBS)
beamToITMY = beams['r1']
beamToITMX = beams['t1']

#Orient ITMX and ITMY
ITMX.normAngleHR = 0.0
ITMY.normAngleHR = deg2rad(90.0)

#ITM optical thickness
dITM = ITMX.thickness*ITMX.n

#Put ITMX
ITMX.HRcenter = (L_BS_ITMX - dBS - (dITM - ITMX.thickness))*beamToITMX.dirVect + beamToITMX.pos

#Put ITMY
ITMY.HRcenter = (L_BS_ITMY - (dITM - ITMY.thickness))*beamToITMY.dirVect + beamToITMY.pos

#}}}

#{{{ Center the beams on the ITMs

#Hit ITMX
beams = ITMX.hitFromAR(beamToITMX)
beamITMXt1 = beams['t1']

#Hit ITMY
beams = ITMY.hitFromAR(beamToITMY)
beamITMYt1 = beams['t1']

#Move ITMs to center the beams
v1= beamITMXt1.pos - ITMX.HRcenter
ITMX.translate(v1)

v1= beamITMYt1.pos - ITMY.HRcenter
ITMY.translate(v1)

#}}}

#{{{ Adjust the Lprc and Las by moving ITMs

#Hit ITMX again
beams = ITMX.hitFromAR(beamToITMX)
beamITMXt1 = beams['t1']

#Move the ITMX to make the length correct
dx = Lprc + Las/2 - beamITMXt1.optDist
ITMX.translate(dx*beamToITMX.dirVect)

#Hit ITMY again
beams = ITMY.hitFromAR(beamToITMY)
beamITMYt1 = beams['t1']

#Move the ITMY to make the length correct
dy = Lprc - Las/2 - beamITMYt1.optDist
ITMY.translate(dy*beamToITMY.dirVect)

#}}}

#{{{ ETMs

#Hit ITMX again
beams = ITMX.hitFromAR(beamToITMX)
beamITMXt1 = beams['t1']

ETMX.HRcenter = beamITMXt1.pos + beamITMXt1.dirVect*Larm
ETMX.normVectHR = - beamITMXt1.dirVect

#Hit ITMY again
beams = ITMY.hitFromAR(beamToITMY)
beamITMYt1 = beams['t1']

ETMY.HRcenter = beamITMYt1.pos + beamITMYt1.dirVect*Larm
ETMY.normVectHR = - beamITMYt1.dirVect

#}}}

#{{{ SRC

#{{{ SRCX

#Hit ITMX again
beams = ITMX.hitFromAR(beamToITMX, order=1)
beamITMXt1 = beams['t1']
beamITMXr2 = beams['r2']
beamITMXr2.optDist = beamITMXr2.optDist - beams['s2'].optDist

#Hit BS
beams = BS.hitFromAR(beamITMXr2, order=1)
beamBStoSR3X = beams['r2']

#Put SR3
d = L_SR3_BS - (beamBStoSR3X.optDist - L_BS_ITMX)
SR3.HRcenter = beamBStoSR3X.pos + d*beamBStoSR3X.dirVect
SR3.normVectHR = - beamBStoSR3X.dirVect
SR3.rotate(-foldingAngle2)

#Hit SR3
beams = SR3.hitFromHR(beamBStoSR3X)
beamSR3toSR2X = beams['r1']

#Put SR2
SR2.HRcenter = beamSR3toSR2X.pos + L_SR2_SR3*beamSR3toSR2X.dirVect
SR2.normVectHR = - beamSR3toSR2X.dirVect
SR2.rotate(foldingAngle1)

#Hit SR2
beams = SR2.hitFromHR(beamSR3toSR2X)
beamSR2toSRMX = beams['r1']

#Put SRM
SRM.HRcenter = beamSR2toSRMX.pos + L_SRM_SR2*beamSR2toSRMX.dirVect
SRM.normVectHR = - beamSR2toSRMX.dirVect

#Hit SRM
beams = SRM.hitFromHR(beamSR2toSRMX)
beamSRMs1X = beams['s1']

#}}}

#{{{ SRCY

#Hit ITMY again
beams = ITMY.hitFromAR(beamToITMY, order=2)
beamITMYt1 = beams['t1']
beamITMYr2 = beams['r2']
beamITMYr2.optDist = beamITMYr2.optDist - beams['s2'].optDist

#Hit BS
beams = BS.hitFromHR(beamITMYr2, order=1)
beamBStoSR3Y = beams['t1']

#Put SR3
d = L_SR3_BS - (beamBStoSR3Y.optDist - L_BS_ITMY)
SR3.HRcenter = beamBStoSR3Y.pos + d*beamBStoSR3Y.dirVect
SR3.normVectHR = - beamBStoSR3Y.dirVect
SR3.rotate(-foldingAngle2)

#Hit SR3
beams = SR3.hitFromHR(beamBStoSR3Y)
beamSR3toSR2Y = beams['r1']

#Put SR2
SR2.HRcenter = beamSR3toSR2Y.pos + L_SR2_SR3*beamSR3toSR2Y.dirVect
SR2.normVectHR = - beamSR3toSR2Y.dirVect
SR2.rotate(foldingAngle1)

#Hit SR2
beams = SR2.hitFromHR(beamSR3toSR2Y)
beamSR2toSRMY = beams['r1']

#Put SRM
SRM.HRcenter = beamSR2toSRMY.pos + L_SRM_SR2*beamSR2toSRMY.dirVect
SRM.normVectHR = - beamSR2toSRMY.dirVect

#Hit SRM
beams = SRM.hitFromHR(beamSR2toSRMY)
beamSRMs1Y = beams['s1']

#}}}

#}}}

#{{{ Check layout

(results, beamDict, auxBeamDict) = propagateOpticalPathFromPRM(q)

#}}}

#}}}

#{{{ ** Arm Cavity **

ArmCavity = Cavity(r1=ITMX.Refl_HR, r2=ETMX.Refl_HR, L=Larm, R1=-ITM_ROC, R2=ETM_ROC*1, power=True)

(q0arm, d) = ArmCavity.waist()

beamArmWaistX = beam.GaussianBeam(q0=q0arm)
beamArmWaistX.pos = ITMX.HRcenter + ITMX.normVectHR*d
beamArmWaistX.dirVect = - ITMX.normVectHR

beamArmWaistY = beam.GaussianBeam(q0=q0arm)
beamArmWaistY.pos = ITMY.HRcenter + ITMY.normVectHR*d
beamArmWaistY.dirVect = - ITMY.normVectHR

#Arm cavity one-way Gouy phase shift
ArmGouyPhase = np.arctan((Larm-d)/np.imag(q0arm)) - np.arctan(-d/np.imag(q0arm))

#}}}

#{{{ == Optimize ROCs of folding mirrors ==

#{{{ ** Optimize PRC mirrors **

#{{{ Optimization Functions

#A Function to optimize R2 given R3
def testFunc1(R2,R3,target=20.0):
    PR3.inv_ROC_HR = 1.0/R3
    PR2.inv_ROC_HR = 1.0/R2
    (result, beamDictX, beamDictY) = \
             propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
    return rad2deg(result['AvgGouyPRCX'] + result['AvgGouyPRCY'])/2 -target

#A function to optimize R3 to make the beam spot size equal on PR2 and PRM
def testFunc2(R3):
    optR2 = sopt.newton(testFunc1, PR2_ROC, args=(R3, targetGouyPRC))
    (result, beamDictX, beamDictY) = \
             propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
    return (result['PR2 Spot Size'] - result['PRM Spot Size'])*1000.0

#}}}

#{{{ Find the start point for optimization

#This process takes time, so by default, we turn off
#this section.
    
#{{{ Fix R3, scan R2 to see the Gouy Phase

#{{{ Scan

if findStartPoint:
    residue = 10.0
    
    while residue > 8./(1+(deg2rad(targetGouyPRC)-pi/2)**2):
        N = 100
        R2s = np.linspace(-1.5,1.5, N)+PR2_ROC
        print('Scanning %f < R2 < %f with R3 = %f'%(np.min(R2s), np.max(R2s), PR3_ROC))
        
        PR3.inv_ROC_HR = 1.0/PR3_ROC
        GouyArray = np.empty(N)
        SpotArray1 = np.empty(N)
        SpotArray2 = np.empty(N)

        for ii in range(N):
            PR2.inv_ROC_HR = 1.0/R2s[ii]
            (result, beamDictX, beamDictY) = \
                     propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
            GouyArray[ii] = rad2deg(result['AvgGouyPRCX'] + result['AvgGouyPRCY'])/2
            SpotArray1[ii] = result['PR2 Spot Size']*1000
            SpotArray2[ii] = result['PRM Spot Size']    *1000


        minIdx = np.argmin(np.abs(GouyArray - targetGouyPRC))
        residue = np.abs(GouyArray[minIdx] - targetGouyPRC)
        print('Residue = %f'%residue)
        
        #Start Point
        PR2_ROC = R2s[minIdx]
    
#}}}

#{{{ Plot
if findStartPoint:
    if os.environ.has_key('DISPLAY'): 

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(R2s, GouyArray, lw=2, color=(0.7,0.7,1))
        (ymin, ymax) = ax.get_ylim()
        ax.plot([PR2_ROC, PR2_ROC], [ymin, ymax], lw=2, color='red')        

        ax.grid(True, color=(0.6,0.6,0.8),ls='-')
        ax.grid(True, which='minor',color=(0.6,0.6,0.6),ls='--')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(24)
        ax.set_xlabel('R2 [m]', size=24)
        ax.set_ylabel('Gouy Phase [deg]', size=24)
        ax.figure.set_size_inches(9,7, forward=True)
        plt.tight_layout(pad=0.5)

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(R2s, SpotArray1, lw=2)
        ax.plot(R2s, SpotArray2, lw=2)
        (ymin, ymax) = ax.get_ylim()
        ax.plot([PR2_ROC, PR2_ROC], [ymin, ymax], lw=2, color='red')
        
        ax.grid(True, color=(0.6,0.6,0.8),ls='-')
        ax.grid(True, which='minor',color=(0.6,0.6,0.6),ls='--')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(24)
        ax.set_xlabel('R2 [m]', size=24)
        ax.set_ylabel('Spot Size [mm]', size=24)
        ax.figure.set_size_inches(9,7, forward=True)
        plt.tight_layout(pad=0.5)

#}}}

#}}}

#{{{ Scan R3 and optimize R2 at each point

#{{{ Scan

if findStartPoint:

    def workerFun(R2, R3, ns, dR3=0.02):
        for ii in ns:
            R2 = sopt.newton(testFunc1, R2, args=(R3, targetGouyPRC))
            PR2.inv_ROC_HR = 1.0/R2
            PR3.inv_ROC_HR = 1.0/R3
            (result, beamDictX, beamDictY) = \
                     propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)

            GouyArray[ii] = rad2deg(result['AvgGouyPRCX'] + result['AvgGouyPRCY'])/2
            SpotArray1[ii] = result['PR2 Spot Size']*1000
            SpotArray2[ii] = result['PRM Spot Size']    *1000
            R2Array[ii] = R2
            R3Array[ii] = R3

            R3 = R3 + dR3


    residue = 1.0
    N = 50
    GouyArray = shm.empty(2*N)
    SpotArray1 = shm.empty(2*N)
    SpotArray2 = shm.empty(2*N)
    R2Array = shm.empty(2*N)
    R3Array = shm.empty(2*N)

    while residue > 0.1:
        tic = time.time()
        print('Scanning R3 starting from %f'%(PR3_ROC))

        ns = N + np.arange(N)
        p1 = Process(target=workerFun, args=(PR2_ROC, PR3_ROC, ns, 0.02))
        p1.start()
        ns = N-1-np.arange(N)
        p2 = Process(target=workerFun, args=(PR2_ROC, PR3_ROC, ns, -0.02))        
        p2.start()        

        p1.join()
        p2.join()

        minIdx = np.argmin(np.abs(SpotArray1 - SpotArray2))
        residue = np.abs(SpotArray1[minIdx] - SpotArray2[minIdx])

        print('Residue = %f'%residue)
        toc = time.time()
        print('Elapsed time = %f'%(toc - tic))
 
        #Start Point
        PR2_ROC = R2Array[minIdx]
        PR3_ROC = R3Array[minIdx]
        


#}}}

#{{{ Plot
if findStartPoint:
    if os.environ.has_key('DISPLAY'): 

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(R3Array, R2Array, lw=2, color=(0.7,0.7,1))
        (ymin, ymax) = ax.get_ylim()
        ax.plot([PR3_ROC, PR3_ROC], [ymin, ymax], lw=2, color='red')

        ax.grid(True, color=(0.6,0.6,0.8),ls='-')
        ax.grid(True, which='minor',color=(0.6,0.6,0.6),ls='--')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(24)
        ax.set_xlabel('R3 [m]', size=24)
        ax.set_ylabel('R2 [m]', size=24)
        ax.figure.set_size_inches(9,7, forward=True)
        plt.tight_layout(pad=0.5)

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)
        ax.plot(R3Array, SpotArray1, lw=2)
        ax.plot(R3Array, SpotArray2, lw=2)
        (ymin, ymax) = ax.get_ylim()
        ax.plot([PR3_ROC, PR3_ROC], [ymin, ymax], lw=2, color='red')
        
        ax.grid(True, color=(0.6,0.6,0.8),ls='-')
        ax.grid(True, which='minor',color=(0.6,0.6,0.6),ls='--')
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontsize(24)
        ax.set_xlabel('R3 [m]', size=24)
        ax.set_ylabel('Spot Size [mm]', size=24)
        ax.figure.set_size_inches(9,7, forward=True)
        plt.tight_layout(pad=0.5)

#}}}]

#}}}

#}}}

#{{{ Final Optimization


#Optimal R3
optR3 = sopt.newton(testFunc2, PR3_ROC)
PR3_ROC = optR3
PR3.inv_ROC_HR = 1.0/optR3

#Optimal R2
optR2 = sopt.newton(testFunc1, PR2_ROC, args=(optR3, targetGouyPRC))
PR2.inv_ROC_HR = 1.0/optR2
PR2_ROC = optR2

#Optimal PRM ROC
(result, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
PRM_ROC = result['PRM ROC']
PRM.inv_ROC_HR = 1.0/PRM_ROC

#}}}

#}}}

#{{{ ** Optimize SRC mirrors ** 

#We want to make the ROCs of the SRM, SR2 and SR3
#as close as possible to that of the PRC mirrors.

#{{{ Save the current positions of the SRC mirrors

SRM_Position0 = SRM.HRcenter
SR2_Position0 = SR2.HRcenter
SR3_Position0 = SR3.HRcenter

SRM_Orientation0 = SRM.normVectHR
SR2_Orientation0 = SR2.normVectHR
SR3_Orientation0 = SR3.normVectHR

(result, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
inc_vect_SR3 = beamDictX['beamBStoSR3'].dirVect

#}}}

#{{{ Start point for optimization

SR2_ROC = PR2_ROC+9.4*cm
SR3_ROC = PR3_ROC

SR2.inv_ROC_HR = 1/SR2_ROC
SR3.inv_ROC_HR = 1/SR3_ROC

#}}}

#{{{ Optimization by Ls2

#A function to return the difference of the Gouy phase from the target value,
#given the change of Ls2

def testFunc1(dLs2):
    SRM.HRcenter = SRM_Position0
    SR2.HRcenter = SR2_Position0
    SR3.HRcenter = SR3_Position0
    SRM.normVectHR = SRM_Orientation0
    SR2.normVectHR = SR2_Orientation0
    SR3.normVectHR = SR3_Orientation0

    changeLs2(dLs2/2, dLs2/2, inc_vect_SR3=inc_vect_SR3)
    (result, beamDictX, beamDictY) = \
             propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)

    GouySRC = rad2deg((result['AvgGouySRCX']+result['AvgGouySRCY'])/2)
    residualGouy = GouySRC - targetGouySRC
    return residualGouy

#A function to return the difference between the ROC of PRM and SRM
#given the change of the SR2_ROC
def testFunc2(dSR2_ROC):
    SR2_ROC = PR2_ROC+dSR2_ROC
    SR2.inv_ROC_HR = 1/SR2_ROC

    optdLs2= sopt.newton(testFunc1, 3*cm)
    
    (result, beamDictX, beamDictY) = \
             propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
    

    return result['SRM ROC'] - PRM_ROC

#Calculate the optimal SR2_ROC
dSR2= sopt.newton(testFunc2, 9*cm)
SR2_ROC = PR2_ROC+dSR2
SR2.inv_ROC_HR = 1/SR2_ROC

print('dSR2 = %fcm'%(dSR2/cm))

dLs2= sopt.newton(testFunc1, 3*cm)

print('dLs2 = %fcm'%(dLs2/cm))

(result, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
GouySRC = rad2deg((result['AvgGouySRCX']+result['AvgGouySRCY'])/2)

print('SRC Gouy Phase = %f deg'%GouySRC)
print('SRM ROC = %f m'%result['SRM ROC'])
print('PRM ROC = %f m'%PRM_ROC)

#}}}

#}}}

#}}}

#{{{ == Put Mirrors Again ==

#{{{ Prepare source beam

q = gauss.Rw2q(ROC=-1/PRM.inv_ROC_HR, w=4*mm)
srcBeam = beam.GaussianBeam(q0=q, pos=[0,0], dirAngle=0.0)
srcBeam.optDist = 0.0

#}}}

#{{{ PRM to BS

#Position the PRM at [0,0]
PRM.HRcenter = [0,0]
#Rotate the PRM
PRM.normAngleHR = theta_in_BS + 2*(foldingAngle2 - foldingAngle1)
srcBeam.dirAngle = theta_in_BS + 2*(foldingAngle2 - foldingAngle1)

#Put PR2
PR2.normAngleHR = pi+PRM.normAngleHR
PR2.rotate(foldingAngle1)
PR2.HRcenter = PRM.HRcenter + PRM.normVectHR*L_PRM_PR2

#Hit PR2
beams = PR2.hitFromHR(srcBeam, order=1)
beamToPR3 = beams['r1']

#Put PR3
PR3.HRcenter = PR2.HRcenter + L_PR2_PR3*beamToPR3.dirVect
PR3.normVectHR = - beamToPR3.dirVect
PR3.rotate(-foldingAngle2)

#Hit PR3
beams = PR3.hitFromHR(beamToPR3)
beamToBS = beams['r1']

#Put BS
BS.HRcenter = PR3.HRcenter + L_PR3_BS*beamToBS.dirVect
BS.normAngleHR = theta_BS

#}}}

#{{{ Roughly locate ITMs

#Hit BS
beams = BS.hitFromHR(beamToBS)
beamToITMY = beams['r1']
beamToITMX = beams['t1']

#Orient ITMX and ITMY
ITMX.normAngleHR = 0.0
ITMY.normAngleHR = deg2rad(90.0)

#ITM optical thickness
dITM = ITMX.thickness*ITMX.n

#Put ITMX
ITMX.HRcenter = (L_BS_ITMX - dBS - (dITM - ITMX.thickness))*beamToITMX.dirVect + beamToITMX.pos

#Put ITMY
ITMY.HRcenter = (L_BS_ITMY - (dITM - ITMY.thickness))*beamToITMY.dirVect + beamToITMY.pos

#}}}

#{{{ Center the beams on the ITMs

#Hit ITMX
beams = ITMX.hitFromAR(beamToITMX)
beamITMXt1 = beams['t1']

#Hit ITMY
beams = ITMY.hitFromAR(beamToITMY)
beamITMYt1 = beams['t1']

#Move ITMs to center the beams
v1= beamITMXt1.pos - ITMX.HRcenter
ITMX.translate(v1)

v1= beamITMYt1.pos - ITMY.HRcenter
ITMY.translate(v1)

#}}}

#{{{ Adjust the Lprc and Las by moving ITMs

#Hit ITMX again
beams = ITMX.hitFromAR(beamToITMX)
beamITMXt1 = beams['t1']

#Move the ITMX to make the length correct
dx = Lprc + Las/2 - beamITMXt1.optDist
ITMX.translate(dx*beamToITMX.dirVect)

#Hit ITMY again
beams = ITMY.hitFromAR(beamToITMY)
beamITMYt1 = beams['t1']

#Move the ITMY to make the length correct
dy = Lprc - Las/2 - beamITMYt1.optDist
ITMY.translate(dy*beamToITMY.dirVect)

#}}}

#{{{ ETMs

#Hit ITMX again
beams = ITMX.hitFromAR(beamToITMX)
beamITMXt1 = beams['t1']

ETMX.HRcenter = beamITMXt1.pos + beamITMXt1.dirVect*Larm
ETMX.normVectHR = - beamITMXt1.dirVect

#Hit ITMY again
beams = ITMY.hitFromAR(beamToITMY)
beamITMYt1 = beams['t1']

ETMY.HRcenter = beamITMYt1.pos + beamITMYt1.dirVect*Larm
ETMY.normVectHR = - beamITMYt1.dirVect

#}}}

#{{{ SRC

#{{{ SRCX

#Hit ITMX again
beams = ITMX.hitFromAR(beamToITMX, order=1)
beamITMXt1 = beams['t1']
beamITMXr2 = beams['r2']
beamITMXr2.optDist = beamITMXr2.optDist - beams['s2'].optDist

#Hit BS
beams = BS.hitFromAR(beamITMXr2, order=1)
beamBStoSR3X = beams['r2']

#Put SR3
d = L_SR3_BS - (beamBStoSR3X.optDist - L_BS_ITMX) - dLs2/2
SR3.HRcenter = beamBStoSR3X.pos + d*beamBStoSR3X.dirVect
SR3.normVectHR = - beamBStoSR3X.dirVect
SR3.rotate(-foldingAngle2)

#Hit SR3
beams = SR3.hitFromHR(beamBStoSR3X)
beamSR3toSR2X = beams['r1']

#Put SR2
SR2.HRcenter = beamSR3toSR2X.pos + (L_SR2_SR3+dLs2)*beamSR3toSR2X.dirVect
SR2.normVectHR = - beamSR3toSR2X.dirVect
SR2.rotate(foldingAngle1)

#Hit SR2
beams = SR2.hitFromHR(beamSR3toSR2X)
beamSR2toSRMX = beams['r1']

#Put SRM
SRM.HRcenter = beamSR2toSRMX.pos + (L_SRM_SR2-dLs2/2)*beamSR2toSRMX.dirVect
SRM.normVectHR = - beamSR2toSRMX.dirVect

#Hit SRM
beams = SRM.hitFromHR(beamSR2toSRMX)
beamSRMs1X = beams['s1']

#}}}

#{{{ SRCY

#Hit ITMY again
beams = ITMY.hitFromAR(beamToITMY, order=2)
beamITMYt1 = beams['t1']
beamITMYr2 = beams['r2']
beamITMYr2.optDist = beamITMYr2.optDist - beams['s2'].optDist

#Hit BS
beams = BS.hitFromHR(beamITMYr2, order=1)
beamBStoSR3Y = beams['t1']

#Put SR3
d = L_SR3_BS - (beamBStoSR3Y.optDist - L_BS_ITMY) - dLs2/2
SR3.HRcenter = beamBStoSR3Y.pos + d*beamBStoSR3Y.dirVect
SR3.normVectHR = - beamBStoSR3Y.dirVect
SR3.rotate(-foldingAngle2)

#Hit SR3
beams = SR3.hitFromHR(beamBStoSR3Y)
beamSR3toSR2Y = beams['r1']

#Put SR2
SR2.HRcenter = beamSR3toSR2Y.pos + (L_SR2_SR3+dLs2)*beamSR3toSR2Y.dirVect
SR2.normVectHR = - beamSR3toSR2Y.dirVect
SR2.rotate(foldingAngle1)

#Hit SR2
beams = SR2.hitFromHR(beamSR3toSR2Y)
beamSR2toSRMY = beams['r1']

#Put SRM
SRM.HRcenter = beamSR2toSRMY.pos + (L_SRM_SR2-dLs2/2)*beamSR2toSRMY.dirVect
SRM.normVectHR = - beamSR2toSRMY.dirVect

#Hit SRM
beams = SRM.hitFromHR(beamSR2toSRMY)
beamSRMs1Y = beams['s1']

#}}}

#}}}

#{{{ Check layout

(results, beamDict, auxBeamDict) = propagateOpticalPathFromPRM(q)

#}}}

#}}}

#{{{ ** Arm Cavity Again **

ArmCavity = Cavity(r1=ITMX.Refl_HR, r2=ETMX.Refl_HR, L=Larm, R1=-ITM_ROC, R2=ETM_ROC*1, power=True)

(q0arm, d) = ArmCavity.waist()

beamArmWaistX = beam.GaussianBeam(q0=q0arm)
beamArmWaistX.pos = ITMX.HRcenter + ITMX.normVectHR*d
beamArmWaistX.dirVect = - ITMX.normVectHR

beamArmWaistY = beam.GaussianBeam(q0=q0arm)
beamArmWaistY.pos = ITMY.HRcenter + ITMY.normVectHR*d
beamArmWaistY.dirVect = - ITMY.normVectHR


#}}}

#{{{ == Final Optimization of the ROCs of the RC mirrors ==

#{{{ PRC

#{{{ Optimization Functions

#A Function to optimize R2 given R3
def testFunc1(R2,R3,target=20.0):
    PR3.inv_ROC_HR = 1.0/R3
    PR2.inv_ROC_HR = 1.0/R2
    (result, beamDictX, beamDictY) = \
             propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
    return rad2deg(result['AvgGouyPRCX'] + result['AvgGouyPRCY'])/2 -target

#A function to optimize R3 to make the beam spot size equal on PR2 and PRM
def testFunc2(R3):
    optR2 = sopt.newton(testFunc1, PR2_ROC, args=(R3, targetGouyPRC))
    (result, beamDictX, beamDictY) = \
             propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
    return (result['PR2 Spot Size'] - result['PRM Spot Size'])*1000.0

#}}}

#{{{ Do optimization

#Optimal R3
optR3 = sopt.newton(testFunc2, PR3_ROC)
PR3_ROC = optR3
PR3.inv_ROC_HR = 1.0/optR3

#Optimal R2
optR2 = sopt.newton(testFunc1, PR2_ROC, args=(optR3, targetGouyPRC))
PR2.inv_ROC_HR = 1.0/optR2
PR2_ROC = optR2

#Optimal PRM ROC
(result, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
PRM_ROC = result['PRM ROC']
PRM.inv_ROC_HR = 1.0/PRM_ROC

#}}}

#}}}

#{{{ ** Optimize SRC mirrors ** 

#We want to make the ROCs of the SRM, SR2 and SR3
#as close as possible to that of the PRC mirrors.

#{{{ Save the current positions of the SRC mirrors

SRM_Position0 = SRM.HRcenter
SR2_Position0 = SR2.HRcenter
SR3_Position0 = SR3.HRcenter

SRM_Orientation0 = SRM.normVectHR
SR2_Orientation0 = SR2.normVectHR
SR3_Orientation0 = SR3.normVectHR

(result, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
inc_vect_SR3 = beamDictX['beamBStoSR3'].dirVect

#}}}

#{{{ Start point for optimization

SR2_ROC = PR2_ROC+9.4*cm
SR3_ROC = PR3_ROC

SR2.inv_ROC_HR = 1/SR2_ROC
SR3.inv_ROC_HR = 1/SR3_ROC

#}}}

#{{{ Optimization by Ls2

#A function to return the difference of the Gouy phase from the target value,
#given the change of Ls2

def testFunc1(dLs2):
    SRM.HRcenter = SRM_Position0
    SR2.HRcenter = SR2_Position0
    SR3.HRcenter = SR3_Position0
    SRM.normVectHR = SRM_Orientation0
    SR2.normVectHR = SR2_Orientation0
    SR3.normVectHR = SR3_Orientation0

    changeLs2(dLs2/2, dLs2/2, inc_vect_SR3=inc_vect_SR3)
    (result, beamDictX, beamDictY) = \
             propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)

    GouySRC = rad2deg((result['AvgGouySRCX']+result['AvgGouySRCY'])/2)
    residualGouy = GouySRC - targetGouySRC
    return residualGouy

#A function to return the difference between the ROC of PRM and SRM
#given the change of the SR2_ROC
def testFunc2(dSR2_ROC):
    SR2_ROC = PR2_ROC+dSR2_ROC
    SR2.inv_ROC_HR = 1/SR2_ROC

    optdLs2= sopt.newton(testFunc1, 3*cm)
    
    (result, beamDictX, beamDictY) = \
             propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
    

    return result['SRM ROC'] - PRM_ROC

#Calculate the optimal SR2_ROC
dSR2= sopt.newton(testFunc2, 9*cm)
SR2_ROC = PR2_ROC+dSR2
SR2.inv_ROC_HR = 1/SR2_ROC

print('dSR2 = %fcm'%(dSR2/cm))

dLs2= sopt.newton(testFunc1, 3*cm)

print('dLs2 = %fcm'%(dLs2/cm))

(result, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)
GouySRC = rad2deg((result['AvgGouySRCX']+result['AvgGouySRCY'])/2)

print('SRC Gouy Phase = %f deg'%GouySRC)
print('SRM ROC = %f m'%result['SRM ROC'])
print('PRM ROC = %f m'%PRM_ROC)

#}}}

#}}}

#{{{ ** Display Results **

(result, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)

print('=============================')
print('PRC Gouy Phase X = '+str(rad2deg(result['AvgGouyPRCX']))+'deg')
print('PRC Gouy Phase Y = '+str(rad2deg(result['AvgGouyPRCY']))+'deg')
print('SRC Gouy Phase X = '+str(rad2deg(result['AvgGouySRCX']))+'deg')
print('SRC Gouy Phase Y = '+str(rad2deg(result['AvgGouySRCY']))+'deg')
print('-----------------------------------------------------')
print('PRM ROC = '+str(result['PRM ROC'])+'m')
print('SRM ROC = '+str(result['SRM ROC'])+'m')
print('PR2 ROC = '+str(1.0/PR2.inv_ROC_HR)+'m')
print('SR2 ROC = '+str(1.0/SR2.inv_ROC_HR)+'m')
print('PR3 ROC = '+str(1.0/PR3.inv_ROC_HR)+'m')
print('SR3 ROC = '+str(1.0/SR3.inv_ROC_HR)+'m')
print('PRC Mode Matching = '+str(result['PRC Mode matching']))
print('SRC Mode Matching = '+str(result['SRC Mode matching']))
print('-----------------------------------------------------')
print('PRM Spot Size = '+str(result['PRM Spot Size']/mm)+'mm')
print('PR2 Spot Size = '+str(result['PR2 Spot Size']/mm)+'mm')
print('PR3 Spot Size = '+str(result['PR3 Spot Size']/mm)+'mm')
print('SRM Spot Size = '+str(result['SRM Spot Size']/mm)+'mm')
print('SR2 Spot Size = '+str(result['SR2 Spot Size']/mm)+'mm')
print('SR3 Spot Size = '+str(result['SR3 Spot Size']/mm)+'mm')

print('=============================')
#}}}

#}}}

#{{{ Check PRC/SRC Gouy Phase with Astigmatism

(result, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)

PRCGouyX = (beamDictX['beamOnPRM'].Gouyx + beamDictY['beamOnPRM'].Gouyx)/2
PRCGouyY = (beamDictX['beamOnPRM'].Gouyy + beamDictY['beamOnPRM'].Gouyy)/2
SRCGouyX = (beamDictX['beamOnSRM'].Gouyx + beamDictY['beamOnSRM'].Gouyx)/2
SRCGouyY = (beamDictX['beamOnSRM'].Gouyy + beamDictY['beamOnSRM'].Gouyy)/2

print('PRC Gouy (Horizontal): %f'%rad2deg(PRCGouyX))
print('PRC Gouy (Vertical): %f'%rad2deg(PRCGouyY))
print('SRC Gouy (Horizontal): %f'%rad2deg(SRCGouyX))
print('SRC Gouy (Vertical): %f'%rad2deg(SRCGouyY))

#}}}

#{{{ == Input beam from IMMT ==
(result, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)

q0 = result['q-parameter on PRM']
b1 = beam.GaussianBeam(q0)
b1.pos = PRM.HRcenter
b1.dirVect = - PRM.normVectHR

beamOnPRM = b1.copy()
beamOnPRM.flip()

b1.propagate(-1.0)

#Beam from the MMT
beams = PRM.hitFromHR(b1, order=1)
beamFromMMT = beams['t1']
beamFromMMT.flip()
beamOnPRMAR = beamFromMMT.copy()
beamFromMMT.propagate(-1.0)
beamFromMMT.name = 'From MMT'

#Beam from ITM to ETM
beamITMXtoETMX = beamDictX['beamOnITMX'].copy()
beamITMXtoETMX.flip()
beamITMXtoETMX.name = 'ITMXtoETMX'

beamITMYtoETMY = beamDictY['beamOnITMY'].copy()
beamITMYtoETMY.flip()
beamITMXtoETMX.name = 'ETMXtoETMY'

#}}}

#{{{ Write parameters to the log file

#{{{ Propagate beams from ITMs

(result1, beamDictX, beamDictY) = \
         propagateOpticalPathFromITM(beamArmWaistX, beamArmWaistY)

#}}}

#{{{ Propagate the input beam

(result2, beamDict, auxBeamDict) = propagateOpticalPath(beamFromMMT, True)

#}}}

#{{{ Compute optical path lengths

Lp1 = beamDict['beamPR2toPR3'].optDist - beamDict['beamPRMtoPR2'].optDist
Lp2 = beamDict['beamPR3toBS'].optDist - beamDict['beamPR2toPR3'].optDist
Lp3 = beamDict['beamBS_PRs1'].optDist - beamDict['beamPR3toBS'].optDist
Lmx = beamDict['beamITMXtrans'].optDist - beamDict['beamBS_PRs1'].optDist
Lmy = beamDict['beamITMYtrans'].optDist - beamDict['beamBStoITMY'].optDist
Ls3 = beamDict['beamSR3toSR2X'].optDist - beamDict['beamBS_Xs2'].optDist
Ls2 = beamDict['beamSR2toSRMX'].optDist - beamDict['beamSR3toSR2X'].optDist
Ls1 = beamDict['beamSRMs1X'].optDist - beamDict['beamSR2toSRMX'].optDist

dLprc = Lprc - (Lp1+Lp2+Lp3+(Lmx+Lmy)/2)
dLsrc = Lprc - (Ls1+Ls2+Ls3+(Lmx+Lmy)/2)

#}}}

#{{{ BS incident angle

v1 = -beamDict['beamPR3toBS'].dirVect
v2 = BS.normVectHR
BS_inc_angle = rad2deg(np.arccos(np.dot(v1,v2)))

#}}}

#{{{ Folding Angle

v1 = -beamDict['beamPRMtoPR2'].dirVect
v2 = PR2.normVectHR
PR2_inc_angle = rad2deg(np.arccos(np.dot(v1,v2)))

v1 = -beamDict['beamPR2toPR3'].dirVect
v2 = PR3.normVectHR
PR3_inc_angle = rad2deg(np.arccos(np.dot(v1,v2)))

#}}}

#{{{ Write the results to a log file

logfile = open(log_file_name, 'w')

logfile.write('==== bLCGT Layout Information ====\n')
logfile.write('\n')
# logfile.write('------------------ g-factor ------------------------------\n')
# logfile.write('g1 = '+str(g1)+'\n')
# logfile.write('g2 = '+str(g2)+'\n')
# logfile.write('Kopt = '+str(kopt)+'\n')
logfile.write('------------------ ROCs ------------------------------\n')
logfile.write('ITM ROC = '+str(1.0/ITMX.inv_ROC_HR)+'m\n')
logfile.write('ETM ROC = '+str(1.0/ETMX.inv_ROC_HR)+'m\n')
logfile.write('PRM ROC = '+str(result1['PRM ROC'])+'m\n')
logfile.write('SRM ROC = '+str(result1['SRM ROC'])+'m\n')
logfile.write('PR2 ROC = '+str(1.0/PR2.inv_ROC_HR)+'m\n')
logfile.write('SR2 ROC = '+str(1.0/SR2.inv_ROC_HR)+'m\n')
logfile.write('PR3 ROC = '+str(1.0/PR3.inv_ROC_HR)+'m\n')
logfile.write('SR3 ROC = '+str(1.0/SR3.inv_ROC_HR)+'m\n')
logfile.write('PRC Mode Matching = '+str(result1['PRC Mode matching'])+'\n')
logfile.write('SRC Mode Matching = '+str(result1['SRC Mode matching'])+'\n')
logfile.write('---------------- Wedge Angles -----------------\n')
logfile.write('BS wedge = '+str(rad2deg(BS.wedgeAngle))+'deg\n')
logfile.write('ITMX wedge = '+str(rad2deg(ITMX.wedgeAngle))+'deg\n')
logfile.write('ITMY wedge = '+str(rad2deg(ITMY.wedgeAngle))+'deg\n')
logfile.write('---------------- Incident Angles -----------------\n')
logfile.write('PR2 incident angle = '+str(PR2_inc_angle)+'deg\n')
logfile.write('PR3 incident angle = '+str(PR3_inc_angle)+'deg\n')
logfile.write('BS incident angle = '+str(BS_inc_angle)+'deg\n')
logfile.write('---------------- Beam Spot Sizes -----------------\n')
logfile.write('ITM Spot Size = '+str(ArmCavity.spotSize()[0]/mm)+'mm\n')
logfile.write('ETM Spot Size = '+str(ArmCavity.spotSize()[1]/mm)+'mm\n')
logfile.write('PRM Spot Size = '+str(result1['PRM Spot Size']/mm)+'mm\n')
logfile.write('PR2 Spot Size = '+str(result1['PR2 Spot Size']/mm)+'mm\n')
logfile.write('PR3 Spot Size = '+str(result1['PR3 Spot Size']/mm)+'mm\n')
logfile.write('SRM Spot Size = '+str(result1['SRM Spot Size']/mm)+'mm\n')
logfile.write('SR2 Spot Size = '+str(result1['SR2 Spot Size']/mm)+'mm\n')
logfile.write('SR3 Spot Size = '+str(result1['SR3 Spot Size']/mm)+'mm\n')
logfile.write('---------------- Gouy Phases -----------------\n')
logfile.write('PRC Gouy Phase X = '+str(rad2deg(result1['AvgGouyPRCX']))+'deg\n')
logfile.write('PRC Gouy Phase Y = '+str(rad2deg(result1['AvgGouyPRCY']))+'deg\n')
logfile.write('SRC Gouy Phase X = '+str(rad2deg(result1['AvgGouySRCX']))+'deg\n')
logfile.write('SRC Gouy Phase Y = '+str(rad2deg(result1['AvgGouySRCY']))+'deg\n')

logfile.write('\n')
logfile.write('------------------ Optical Length ------------------------------\n')
logfile.write('Lp1 = '+str(Lp1)+'m\n')
logfile.write('Lp2 = '+str(Lp2)+'m\n')
logfile.write('Lp3 = '+str(Lp3)+'m\n')
logfile.write('Lmx = '+str(Lmx)+'m\n')
logfile.write('Lmy = '+str(Lmy)+'m\n')
logfile.write('Ls1 = '+str(Ls1)+'m\n')
logfile.write('Ls2 = '+str(Ls2)+'m\n')
logfile.write('Ls3 = '+str(Ls3)+'m\n')
logfile.write('dLprc = '+str(dLprc)+'m\n')
logfile.write('dLsrc = '+str(dLsrc)+'m\n')

logfile.write('=============================\n\n\n')

logfile.close()

#}}}

#}}}

#{{{ Change layers of POX and POY beams

POX_beam_list = [auxBeamDict[key] for key in auxBeamDict.keys() if key.find('POX') != -1]
for b in POX_beam_list:
    b.layer = 'pox'

POY_beam_list = [auxBeamDict[key] for key in auxBeamDict.keys() if key.find('POY') != -1]
for b in POY_beam_list:
    b.layer = 'poy'
    
#}}}

#{{{ *** Save Mirrors, Optics and Beams

opticsDict_bKAGRA = {}
for (key, value) in opticsDict.iteritems():
    opticsDict_bKAGRA[key] = value.copy()
    
beamDict_bKAGRA = {}
for (key, value) in beamDict.iteritems():
    beamDict_bKAGRA[key] = value.copy()
    
auxBeamDict_bKAGRA = {}
for (key, value) in auxBeamDict.iteritems():
    auxBeamDict_bKAGRA[key] = value.copy()

beamDict_bKAGRA['beamFromMMT'] = beamFromMMT.copy()
beamDict_bKAGRA['beamOnPRM'] = beamOnPRM.copy()
beamDict_bKAGRA['beamOnPRMAR'] = beamOnPRMAR.copy()
beamDict_bKAGRA['beamArmWaistX'] = beamArmWaistX.copy()
beamDict_bKAGRA['beamArmWaistY'] = beamArmWaistY.copy()
beamDict_bKAGRA['beamITMXtoETMX'] = beamITMXtoETMX.copy()
beamDict_bKAGRA['beamITMYtoETMY'] = beamITMYtoETMY.copy()

#}}}

#{{{ Draw the results

#{{{ Make copies of beams and optics
#Copies are necessary to avoid the translation of the
#objects below from intefering with the iLCGT layout 
#after this section.
#To copy the items of the dictionary, iteritems() is
#used. For some reason, copy.deepcopy() did not work
#correctly

beamDictCopy = {}
for (key, value) in beamDict.iteritems():
    beamDictCopy[key] = value.copy()

auxBeamDictCopy = {}
for (key, value) in auxBeamDict.iteritems():
    auxBeamDictCopy[key] = value.copy()

opticsDictCopy = {}
for (key, value) in opticsDict.iteritems():
    opticsDictCopy[key] = copy.copy(value)

# chamberDictCopy = {}
# for (key, value) in chamberDict.iteritems():
#     chamberDictCopy[key] = copy.copy(value)

    
#}}}

#{{{ Translate all objects to put the BS at the center

transAll(beamDictCopy.values(), -BS.HRcenter)
transAll(auxBeamDictCopy.values(), -BS.HRcenter)
transAll(opticsDictCopy.values(), -BS.HRcenter)

# for k in chamberDictCopy.keys():
#     chamberDictCopy[k] = chamberDictCopy[k] -BS.HRcenter

#}}}

#{{{ ++ DXF object ++

tube_offset_dict = {'PRM':(0.0,0.0), 'PR2':(0,-160*mm), 'PR3':(0,160*mm),
                    'SRM':(0.0,0.0), 'SR2':(-160*mm,0), 'SR3':(0,0)}

d = make_draw_template(opticsDictCopy, tube_offset_dict=tube_offset_dict)

#}}}

#{{{ ++ Draw Beams ++

drawAllBeams(d, beamDictCopy.values(), drawWidth=True, sigma=2.7, drawPower=False,
                 drawROC=False, drawGouy=False, drawOptDist=False, layer='main_beam',
                    fontSize=0.01)

drawAllBeams(d, auxBeamDictCopy.values(), drawWidth=True, sigma=2.7, drawPower=False,
             drawROC=False, drawGouy=False, drawOptDist=False, layer='aux_beam',
             fontSize=0.01)

#}}}

#{{{ ++ Draw Optics ++

drawAllOptics(d, opticsDictCopy.values(), drawName=True)

#}}}

#{{{ Save DXF file 

renderer.renderDXF(d, dxf_file_name)

#}}}

#}}}

#}}}

#{{{ *** Non-sequential trace ***

#{{{ Parameters

power_threshold = 10e-3

#}}}

#{{{ Avoid cavity formation

opticsDict_bKAGRA['PRM'].term_on_HR = True
opticsDict_bKAGRA['SRM'].term_on_HR = True
opticsDict_bKAGRA['ETMX'].term_on_HR = True
opticsDict_bKAGRA['ETMY'].term_on_HR = True

#}}}

#{{{ From PRM HR surface


#Input beam
input_beam = beamDict_bKAGRA['beamOnPRM'].copy()
input_beam.P = 500.0

beams_PRM = non_seq_trace(opticsDict_bKAGRA.values(), input_beam, order=30, power_threshold=power_threshold)

#}}}

#{{{ From ITMX

#Input beam
input_beam = beamDict_bKAGRA['beamArmWaistX'].copy()
input_beam.P = 500.0/opticsDict_bKAGRA['ITMX'].Trans_HR

# #Temporarily Increase the PR2/SR2 transmittance to catch the POX beam
# PR2_TR0 = opticsDict_bKAGRA['PR2'].Trans_HR
# opticsDict_bKAGRA['PR2'].Trans_HR = 0.5
# SR2_TR0 = opticsDict_bKAGRA['SR2'].Trans_HR
# opticsDict_bKAGRA['SR2'].Trans_HR = 0.5

beams_ITMX = non_seq_trace(opticsDict_bKAGRA.values(), input_beam, order=30, power_threshold=power_threshold)

# opticsDict_bKAGRA['PR2'].Trans_HR = PR2_TR0
# opticsDict_bKAGRA['SR2'].Trans_HR = SR2_TR0

#}}}

#{{{ From ITMY

#Input beam
input_beam = beamDict_bKAGRA['beamArmWaistY'].copy()
input_beam.P = 500.0/opticsDict_bKAGRA['ITMY'].Trans_HR

# #Temporarily Increase the PR2 transmittance to catch the POX beam
# PR2_TR0 = opticsDict_bKAGRA['PR2'].Trans_HR
# opticsDict_bKAGRA['PR2'].Trans_HR = 0.5
# SR2_TR0 = opticsDict_bKAGRA['SR2'].Trans_HR
# opticsDict_bKAGRA['SR2'].Trans_HR = 0.5

beams_ITMY = non_seq_trace(opticsDict_bKAGRA.values(), input_beam, order=30, power_threshold=power_threshold)

# opticsDict_bKAGRA['PR2'].Trans_HR = PR2_TR0
# opticsDict_bKAGRA['SR2'].Trans_HR = SR2_TR0

#}}}

#{{{ Draw the results

#{{{ Make copies of beams and optics

beamListCopy = []
for b in beams_PRM + beams_ITMX + beams_ITMY:
    beamListCopy.append(b.copy())

POX_POY_beam_list = []
for b in [auxBeamDict_bKAGRA[key] for key in auxBeamDict_bKAGRA.keys()\
          if key.find('POX') != -1 or key.find('POY') != -1]:
    POX_POY_beam_list.append(b.copy())

opticsDictCopy = {}
for (key, value) in opticsDict_bKAGRA.iteritems():
    opticsDictCopy[key] = value.copy()

#}}}

#{{{ Translate all objects to put the BS at the center

transAll(beamListCopy, -opticsDict_bKAGRA['BS'].HRcenter)
transAll(POX_POY_beam_list, -opticsDict_bKAGRA['BS'].HRcenter)
transAll(opticsDictCopy.values(), -opticsDict_bKAGRA['BS'].HRcenter)

#}}}

#{{{ ++ DXF object ++

d = make_draw_template(opticsDictCopy, tube_offset_dict=tube_offset_dict)

d.add_layer("stray_beam", color=(0,255,0))
d.add_layer("stray_beam_width", color=(0,255,255))    
d.add_layer("poxpoy_beam", color=(0,0,255))
d.add_layer("poxpoy_beam_width", color=(0,255,255))    

#}}}

#{{{ ++ Draw Beams ++

for b in beamListCopy:
    if b.stray_order > 0:
        b.layer = 'stray_beam'
        sigma = 1.0
        drawWidth=False
    else:
        b.layer = 'main_beam'
        sigma = 3.0
        drawWidth=True
    b.draw(d, sigma=sigma, drawWidth=drawWidth, drawPower=True,
           drawName=True, fontSize=1*mm)

for b in POX_POY_beam_list:
    b.layer = 'poxpoy_beam'
    sigma = 1.0
    drawWidth=True
    b.draw(d, sigma=sigma, drawWidth=drawWidth, drawPower=True,
           drawName=True, fontSize=1*mm)

#}}}

#{{{ ++ Draw Optics ++

drawAllOptics(d, opticsDictCopy.values(), drawName=True)

#}}}

#{{{ Save DXF file 

renderer.renderDXF(d, dxf_file_name_stray)

#}}}

#}}}

#{{{ POX Only

# #Input beam
# b = beamDict_bKAGRA['beamArmWaistX'].copy()
# b.P = 500.0/opticsDict_bKAGRA['ITMX'].Trans_HR

# beams = opticsDict_bKAGRA['ITMX'].hitFromHR(b, order=2)
# input_beam = beams['t2']
# input_beam.stray_order = 1


# beams_POX = non_seq_trace(opticsDict_bKAGRA.values(), input_beam, order=30, power_threshold=1e-5)

# drawOptSys(opticsDict_bKAGRA.values(), beams_POX, 'POX.dxf', fontSize=1*mm)

#}}}

#{{{ POY Only

# #Input beam
# b = beamDict_bKAGRA['beamArmWaistY'].copy()
# b.P = 500.0/opticsDict_bKAGRA['ITMY'].Trans_HR

# beams = opticsDict_bKAGRA['ITMY'].hitFromHR(b, order=2)
# input_beam = beams['t2']
# input_beam.stray_order = 1


# beams_POY = non_seq_trace(opticsDict_bKAGRA.values(), input_beam, order=30, power_threshold=1e-5)

# drawOptSys(opticsDict_bKAGRA.values(), beams_POY, 'POY.dxf', fontSize=1*mm)

#}}}

#}}}

