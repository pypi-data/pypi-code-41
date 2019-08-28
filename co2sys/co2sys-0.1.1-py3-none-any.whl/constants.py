
import numpy as np

"""
 SUB Constants, version 04.01, 10-13-97, written by Ernie Lewis.
 Inputs: pHScale, WhichKs, WhoseKSO4, Sali, TempCi, Pdbar
 Outputs: K0, K(), T(), fH, FugFac, VPFac
 This finds the Constants of the CO2 system in seawater or freshwater,
 corrects them for pressure, and reports them on the chosen pH scale.
 The process is as follows: the Constants (except KS, KF which stay on the
 free scale - these are only corrected for pressure) are
       1) evaluated as they are given in the literature
       2) converted to the SWS scale in mol/kg-SW or to the NBS scale
       3) corrected for pressure
       4) converted to the SWS pH scale in mol/kg-SW
       5) converted to the chosen pH scale

       PROGRAMMER'S NOTE: all logs are log base e
       PROGRAMMER'S NOTE: all Constants are converted to the pH scale
               pHScale (the chosen one) in units of mol/kg-SW
               except KS and KF are on the free scale
               and KW is in units of (mol/kg-SW)^2

***************************************************************************
CorrectKsForPressureNow:
 Currently: For WhichKs = 1 to 7, all Ks (except KF and KS, which are on
       the free scale) are on the SWS scale.
       For WhichKs = 6, KW set to 0, KP1, KP2, KP3, KSi don't matter.
       For WhichKs = 8, K1, K2, and KW are on the "pH" pH scale
       (the pH scales are the same in this case); the other Ks don't matter.


 No salinity dependence is given for the pressure coefficients here.
 It is assumed that the salinity is at or very near Sali = 35.
 These are valid for the SWS pH scale, but the difference between this and
 the total only yields a difference of .004 pH units at 1000 bars, much
 less than the uncertainties in the values.
****************************************************************************
 The sources used are:
 Millero, 1995:
       Millero, F. J., Thermodynamics of the carbon dioxide system in the
       oceans, Geochemica et Cosmochemica Acta 59:661-677, 1995.
       See table 9 and eqs. 90-92, p. 675.
       TYPO: a factor of 10^3 was left out of the definition of Kappa
       TYPO: the value of R given is incorrect with the wrong units
       TYPO: the values of the a's for H2S and H2O are from the 1983
                values for fresh water
       TYPO: the value of a1 for B(OH)3 should be +.1622
        Table 9 on p. 675 has no values for Si.
       There are a variety of other typos in Table 9 on p. 675.
       There are other typos in the paper, and most of the check values
       given don't check.
 Millero, 1992:
       Millero, Frank J., and Sohn, Mary L., Chemical Oceanography,
       CRC Press, 1992. See chapter 6.
       TYPO: this chapter has numerous typos (eqs. 36, 52, 56, 65, 72,
               79, and 96 have typos).
 Millero, 1983:
       Millero, Frank J., Influence of pressure on chemical processes in
       the sea. Chapter 43 in Chemical Oceanography, eds. Riley, J. P. and
       Chester, R., Academic Press, 1983.
       TYPO: p. 51, eq. 94: the value -26.69 should be -25.59
       TYPO: p. 51, eq. 95: the term .1700t should be .0800t
       these two are necessary to match the values given in Table 43.24
 Millero, 1979:
       Millero, F. J., The thermodynamics of the carbon dioxide system
       in seawater, Geochemica et Cosmochemica Acta 43:1651-1661, 1979.
       See table 5 and eqs. 7, 7a, 7b on pp. 1656-1657.
 Takahashi et al, in GEOSECS Pacific Expedition, v. 3, 1982.
       TYPO: the pressure dependence of K2 should have a 16.4, not 26.4
       This matches the GEOSECS results and is in Edmond and Gieskes.
 Culberson, C. H. and Pytkowicz, R. M., Effect of pressure on carbonic acid,
       boric acid, and the pH of seawater, Limnology and Oceanography
       13:403-417, 1968.
 Edmond, John M. and Gieskes, J. M. T. M., The calculation of the degree of
       seawater with respect to calcium carbonate under in situ conditions,
       Geochemica et Cosmochemica Acta, 34:1261-1291, 1970.
****************************************************************************
 These references often disagree and give different fits for the same thing.
 They are not always just an update either; that is, Millero, 1995 may agree
       with Millero, 1979, but differ from Millero, 1983.
 For WhichKs = 7 (Peng choice) I used the same factors for KW, KP1, KP2,
       KP3, and KSi as for the other cases. Peng et al didn't consider the
       case of P different from 0. GEOSECS did consider pressure, but didn't
       include Phos, Si, or OH, so including the factors here won't matter.
 For WhichKs = 8 (freshwater) the values are from Millero, 1983 (for K1, K2,
       and KW). The other aren't used (TB = TS = TF = TP = TSi = 0.), so
       including the factors won't matter.
****************************************************************************
       deltaVs are in cm3/mole
       Kappas are in cm3/mole/bar
****************************************************************************
"""
def calc_tempK(temp):
    return  temp + 273.15

def RT(temp, RGasConstant=83.1451):
    return RGasConstant * calc_tempK(temp)

def calculate_TB(salt, ver="Uppstrom"):
    """ Calculate Total Borate """
    if "upp" in ver.lower():
        return 0.0004157 * salt / 35 # in mol/kg-SW
    else:
        # Lee, Kim, Byrne, Millero, Feely, Yong-Ming Liu. 2010.	
        # Geochimica Et Cosmochimica Acta 74 (6): 1801?1811.
        return 0.0004326 * salt / 35

def calculate_KW(salt, temp, pres=None):
    """Calculate KW"""
    tempK = calc_tempK(temp)
    lnKW = (148.9802 - 13847.26 / tempK - 23.6521 * np.log(tempK) +
            (-5.977 + 118.67 / tempK + 1.0495 * np.log(tempK)) *
            np.sqrt(salt) - 0.01615 * salt)
    KW = np.exp(lnKW) # SWS pH scale in (mol/kg-SW)^2
    if pres is not None:
        Pbar = pres / 10.
        # Millero, 1983 and his programs CO2ROY(T).BAS.
        deltaV  = -20.02 + 0.1119 * temp - 0.001409 * temp**2
        # Millero, 1992 and Millero, 1995 have:
        Kappa   = (-5.13 + 0.0794 * temp) / 1000 # Millero, 1983
        # Millero, 1995 has this too, but Millero, 1992 is different.
        lnKWfac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        # Millero, 1979 does not list values for these.
        KW = KW * np.exp(lnKWfac)
    return KW
              
def calculate_TF(salt):
    """Riley, J. P., Deep-Sea Research 12:219-220, 1965:
    this is .000068.*Sali./35. = .00000195.*Sali
    """
    return (0.000067/18.998) * (salt/1.80655) # mol/kg-SW

def calculate_TS(salt):
    """Morris, A. W., and Riley, J. P., Deep-Sea Research 13:699-705, 1966:
    this is .02824.*Sali./35. = .0008067.*Sali
    """
    return (0.14/96.062) * (salt/1.80655) # mol/kg-SW

def calculate_fH(salt, temp):
    """Takahashi et al, Chapter 3 in GEOSECS Pacific Expedition, 
        v. 3, 1982 (p. 80);
    """
    #Use GEOSECS's value for cases 1,2,3,4,5 (and 6) to convert pH scales.
    tempK = calc_tempK(temp)
    fH = 1.2948 - 0.002036*tempK + (0.0004607 - 0.000001475*tempK) * salt**2
    return fH

def calculate_K0(salt, temp):
    """Weiss, R. F., Marine Chemistry 2:203-215, 1974."""
    TempK100  = calc_tempK(temp) / 100
    lnK0 = (-60.2409 + 93.4517 / TempK100 + 23.3585 * np.log(TempK100) +
            salt * (0.023517 - 0.023656*TempK100 + 0.0047036*TempK100**2))
    return np.exp(lnK0) # mol/kg-SW/atm

def calculate_KB(salt, temp, pres=None, KSver="Dickson"):
    """Calculate KB

    Dickson, A. G., Deep-Sea Research 37:755-766, 1990:
    Pressure effects from: Millero, 1979.
    with parameters from Culberson and Pytkowicz, 1968.
    Millero 1983: deltaV = -28.56 + .1211.*TempCi - .000321.*TempCi.*TempCi
                  Kappa = (-3 + .0427.*TempCi)./1000
                  lnKBfac = (-deltaV + 0.5.*Kappa.*Pbar).*Pbar./RT(temp);
    Millero 1992: deltaV = -29.48 + .1622.*TempCi + .295.*(Sali - 34.8)
                  Kappa + .354.*(Sali - 34.8)./1000
    Millero 1995: deltaV = -29.48 - .1622.*TempCi - .002608.*TempCi.*TempCi
                  Kappa + .354.*(Sali - 34.8)./1000
    Millero 1979: deltaV = deltaV + .295.*(Sali - 34.8); 
                  Kappa  = -2.84./1000; # Millero, 1979
    """
    tempK = calc_tempK(temp)
    lnKBtop = (-8966.9 - 2890.53 * np.sqrt(salt) - 77.942 * salt + 1.728 *
               np.sqrt(salt) * salt - 0.0996 * salt**2)
    lnKB = (lnKBtop/tempK + 148.0248 + 137.1942*np.sqrt(salt) + 1.62142*salt +
            (-24.4344 - 25.085*np.sqrt(salt) - 0.2474 * salt) * np.log(tempK) +
            0.053105 * np.sqrt(salt) * tempK)
    KB = np.exp(lnKB) / calculate_SWStoTOT(salt, temp, KSver=KSver)
    if pres is not None:
        Pbar = pres/10
        deltaV  = -29.48 + 0.1622 * temp - 0.002608 * temp**2
        Kappa   = -2.84 / 1000
        lnKBfac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        KBfac  = np.exp(lnKBfac)
        KB     = KB * KBfac
    return KB

def calculate_IonS(salt):
    """DOE handbook, Chapter 5, p. 13/22, eq. 7.2.4"""
    return 19.924 * salt / (1000 - 1.005 * salt)

def calculate_KF(salt, temp, pres=None):
    """Dickson, A. G. and Riley, J. P., Marine Chemistry 7:89-99, 1979
    Pressure effects from Millero, 1983, 1995
    It is assumed that KF is on the free pH scale.
    """
    # exp(lnKF) is on the free pH scale in mol/kg-H2O
    lnKF = 1590.2/calc_tempK(temp) - 12.641 + 1.525 * calculate_IonS(salt)**0.5
    KF = np.exp(lnKF) * (1 - 0.001005 * salt) # mol/kg-SW
    if pres is not None:
        Pbar = pres / 10
        deltaV  = -9.78 - 0.009 * temp - 0.000942 * temp**2
        Kappa   = (-3.91 + 0.054 * temp) / 1000
        lnKFfac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        KFfac   = np.exp(lnKFfac)
        KF      = KF * KFfac
    return KF
            
def calculate_KF_perez_fraga_1987(salt, temp):
    """Perez and Fraga 1987. 
    Not used here since ill defined for low salinity. 
    (to be used for S: 10-40, T: 9-33)
    Nonetheless, P&F87 might actually be better than the fit of D&R79 above, 
    which is based on only three salinities: [0 26.7 34.6]
    """
    lnKF = 874. / calc_tempK(temp) - 9.68 + 0.111 * salt**0.5 
    return np.exp(lnKF) # the free pH scale in mol/kg-SW

def calculate_KS(salt, temp, pres=None, ver="Dickson"):
    """Calculate KSO4 dissociation constants

    Dickson, A. G., J. Chemical Thermodynamics, 22:113-127, 1990
    The goodness of fit is .021. It was given in mol/kg-H2O. I convert it to 
    mol/kg-SW. TYPO on p. 121: the constant e9 should be e8. This is from 
    eqs 22 and 23 on p. 123, and Table 4 on p 121:
    
    Khoo, et al, Analytical Chemistry, 49(1):29-34, 1977
    KS was found by titrations with a hydrogen electrode of artificial seawater
    containing sulfate (but without F) at 3 salinities from 20 to 45 and 
    artificial seawater NOT containing sulfate (nor F) at 16 salinities from 
    15 to 45, both at temperatures from 5 to 40 deg C. KS is on the Free pH 
    scale (inherently so). It was given in mol/kg-H2O. I convert it to 
    mol/kg-SW. He finds log(beta) which = my pKS; his beta is an association 
    constant. The rms error is .0021 in pKS, or about .5in KS. 
    This is equation 20 on p. 33:

    Pressure effects from Millero, 1983, 1995; KS on the free pH scale.
    """
    tempK = calc_tempK(temp)
    IonS = calculate_IonS(salt)
    if "dick" in ver.lower():
        lnKS = (-4276.1/tempK + 141.328 - 23.0930*np.log(tempK) +            
                (-13856/tempK + 324.57  - 47.9860*np.log(tempK)) * IonS**0.5 +
                (35474./tempK - 771.54  + 114.723*np.log(tempK)) * IonS +
                (-2698./tempK) * np.sqrt(IonS) * IonS + (1776/tempK) * IonS**2) 
        KS   = np.exp(lnKS) * (1 - 0.001005 * salt)  # mol/kg-SW
    elif "kho" in ver.lower():
        pKS = 647.59 / tempK - 6.3451 + 0.019085 * tempK - 0.5208 * IonS**0.5
        KS  = 10.^(-pKS) * (1 - 0.001005 * salt) # mol/kg-SW
    if pres is not None:
        Pbar = pres / 10
        deltaV = -18.03 + 0.0466 * temp + 0.000316 * temp**2
        Kappa = (-4.53 + 0.09 * temp)/1000;
        lnKSfac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        KSfac  = np.exp(lnKSfac)
        KS  = KS * KSfac
    return KS
                    
def calculate_SWStoTOT(salt, temp, pres=None, KSver="Dickson"):
    """Calculate conversion factors from SWS pH to TOT"""
    TS = calculate_TS(salt)
    KS = calculate_KS(salt, temp, pres=pres, ver=KSver)
    TF = calculate_TF(salt)
    KF = calculate_KF(salt, temp, pres=pres)
    return (1 + TS/KS) / (1 + TS/KS + TF/KF)

def calculate_FREEtoTOT(salt, temp, pres=None, KSver="Dickson"):
    """Calculate conversion factors from SWS pH to Free"""
    TS = calculate_TS(salt)
    KS = calculate_KS(salt, temp, pres=pres, ver=KSver)
    return 1 + TS / KS
    
def calculate_fugfac(temp):
    """Calculate Fugacity Constants
    
    This assumes that the pressure is at one atmosphere, or close to it.
    Otherwise, the Pres term in the exponent affects the results.
    Weiss, R. F., Marine Chemistry 2:203-215, 1974.
    
    For a mixture of CO2 and air at 1 atm (at low CO2 concentrations)
    Delta and B in cm3/mol
    """
    tempK = calc_tempK(temp)
    Delta = (57.7 - 0.118 * tempK)
    b = (-1636.75 + 12.0408 * tempK - 0.0327957 * tempK**2 +
         3.16528  * 0.00001 * tempK**3)
    P1atm = 1.01325 # in bar
    return np.exp((b + 2 * Delta) * P1atm / RT(temp))

def calculate_VPFac(salt, temp):
    """Calculate VPFac

    Assumes 1 atmosphere, output in atmospheres.

    They fit the data of Goff and Gratch (1946) with the vapor pressure 
    lowering by sea salt as given by Robinson (1954). This fits the more 
    complicated Goff and Gratch, and Robinson equations from 273 to 313 deg K 
    and 0 to 40 Sali with a standard error of .015#, about 5 uatm over this
    range. This may be on IPTS-29 since they didn't mention the temperature 
    scale, and the data of Goff and Gratch came before IPTS-48.
    
    References:
    Weiss, R. F., and Price, B. A., Nitrous oxide solubility in water and
          seawater, Marine Chemistry 8:347-359, 1980.
    Goff, J. A. and Gratch, S., Low pressure properties of water from -160 deg
          to 212 deg F, Transactions of the American Society of Heating and
          Ventilating Engineers 52:95-122, 1946.
    Robinson, Journal of the Marine Biological Association of the U. K.
          33:449-455, 1954. eq. 10 on p. 350.
    """
    tempK    = calc_tempK(temp)
    VPWP = np.exp(24.4543 - 67.4509 * (100/tempK) - 4.8489 * np.log(tempK/100))
    VPCorrWP = np.exp(-0.000544 * salt)
    VPSWWP = VPWP * VPCorrWP
    return 1 - VPSWWP

def generate_constants_dict(salt, temp, pres=None,
                            KBver="Uppstrom", KSver="Dickson"):
    """Agreegate all constants except K1 and K2 into one dictionary."""
    cdict = {"KB"  : calculate_KB(salt, temp, pres, KSver),
             "TB"  : calculate_TB(salt, ver=KBver),
             "TS"  : calculate_TS(salt),
             "TF"  : calculate_TF(salt),
             "KF"  : calculate_KF(salt, temp, pres=pres),
             "KS"  : calculate_KS(salt,  temp, pres, ver=KSver),
             "KW"  : calculate_KW(salt,  temp, pres),
             "KP1" : calculate_KP1(salt, temp, pres),
             "KP2" : calculate_KP2(salt, temp, pres),
             "KP3" : calculate_KP3(salt, temp, pres),
             "KSi" : calculate_KSi(salt, temp, pres),
             "K0"  : calculate_K0(salt, temp),
             "K1"  : salt * np.nan,
             "K2"  : salt * np.nan,
             "FugFac"    : calculate_fugfac(temp),
             "SWStoTOT"  : calculate_SWStoTOT(salt, temp, pres, KSver=KSver),
             "FREEtoTOT" : calculate_FREEtoTOT(salt, temp, pres, KSver=KSver)
             }
    return cdict

def roy_1993(salt, temp):
    """   1 = Roy, 1993											
    T:    0-45  S:  5-45. Total scale. Artificial seawater.
    
    ROY et al, Marine Chemistry, 44:249-267, 1993
       (see also: Erratum, Marine Chemistry 45:337, 1994 and 
                  Erratum, Marine Chemistry 52:183, 1996)
    Typo: in the abstract on p. 249: in the eq. for lnK1* the last term 
    should have S raised to the power 1.5. They claim standard deviations 
    (p. 254) of the fits as .0048 for lnK1 (.5# in K1) and .007 in lnK2 
    (.7# in K2). They also claim (p. 258) 2s precisions of .004 in pK1 and
    .006 in pK2. These are consistent, but Andrew Dickson (personal 
    communication) obtained an rms deviation of about .004 in pK1 and .003 
    in pK2. This would be a 2s precision of about 2# in K1 and 1.5# in K2.
    T:  0-45  S:  5-45. Total Scale. Artificial sewater.
    """
    tempK    = calc_tempK(temp)
    logTempK = logTempK(temp)
    #Eq. 29, p. 254 + abs
    lnK1 = (2.83655 - 2307.1266 / TempK - 1.5529413 * logTempK(temp) +
            (-0.20760841 - 4.0484 / TempK) * np.sqrt(salt) + 0.08468345*salt -
            0.00654208 * np.sqrt(salt) * salt)
    K1 = np.exp(lnK1) * (1 - 0.001005*salt) / SWStoTOT
    #Eq. 30, p. 254 + abs
    lnK2 = (-9.226508 - 3351.6106/-0.2005743 * logTempK +
            (-0.106901773 - 23.9722/TempK) * np.sqrt(salt) +
            0.1130822 * salt - 0.00846934 * np.sqrt(salt) * salt)
    K2 = np.exp(lnK2) * (1 - 0.001005*salt) / SWStoTOT


def goyet_poisson(salt, temp):
    """2 = Goyet & Poisson										
    T:   -1-40  S: 10-50. Seaw. scale. Artificial seawater.

    GOYET AND POISSON, Deep-Sea Research, 36(11):1635-1654, 1989
    The 2s precision in pK1 is .011, or 2.5# in K1.
    The 2s precision in pK2 is .02, or 4.5# in K2.
    """
    tempK = calc_tempK(temp)
    #Table 5 p. 1652 and what they use in the abstract:
    pK1 = (812.270 / tempK + 3.356 - 0.00171 * salt * np.log(tempK) +
           0.000091 * salt**2)
    K1 = 10**(-pK1) # SWS pH scale in mol/kg-SW  
    #Table 5 p. 1652 and what they use in the abstract:
    pK2 = (1450.87 / tempK + 4.604 - 0.00385 * salt * np.log(tempK) +
           0.000182 * salt**2)
    K2 = 10**(-pK2) # SWS pH scale in mol/kg-SW
  
def hansson(salt, temp):
    """3 = HANSSON refit BY DICKSON AND MILLERO	
    T:    2-35  S: 20-40. Seaw. scale. Artificial seawater.

    Dickson and Millero, Deep-Sea Research, 34(10):1733-1743, 1987
    (see also Corrigenda, Deep-Sea Research, 36:983, 1989)
    refit data of Hansson, Deep-Sea Research, 20:461-478, 1973
    and Hansson, Acta Chemica Scandanavia, 27:931-944, 1973.
    on the SWS pH scale in mol/kg-SW.
    Hansson gave his results on the Total scale (he called it
    the seawater scale) and in mol/kg-SW.
    Typo in DM on p. 1739 in Table 4: the equation for pK2*
    for Hansson should have a .000132 *S**2
    instead of a .000116 *S**2.
    The 2s precision in pK1 is .013, or 3# in K1.
    The 2s precision in pK2 is .017, or 4.1# in K2.
    """
    tempK = calc_tempK(temp)
    logTempK = logTempK(temp)
    #Table 4 on p. 1739.
    pK1 = 851.4 / tempK + 3.237 - 0.0106 * salt + 0.000105 * salt**2
    K1 = 10**(-pK1) # SWS pH scale in mol/kg-SW
    #Table 4 on p. 1739.
    pK2 = (-3885.4 / tempK + 125.844 - 18.141 * logTempK -
           0.0192 * salt + 0.000132 * salt**2)
    K2 = 10**(-pK2) # SWS pH scale in mol/kg-SW


def merback(salt, temp):
    """4 = MEHRBACH             refit BY DICKSON AND MILLERO	
    temp: 2-35, salt: 20-40. Seaw. scale. Artificial seawater.
    
    Dickson and Millero, Deep-Sea Research, 34(10):1733-1743, 1987
    (see also Corrigenda, Deep-Sea Research, 36:983, 1989)
    refit data of Mehrbach et al, Limn Oc, 18(6):897-907, 1973
    on the SWS pH scale in mol/kg-SW.
    Mehrbach et al gave results on the NBS scale.
    The 2s precision in pK1 is .011, or 2.6# in K1.
    The 2s precision in pK2 is .020, or 4.6# in K2.
	Valid for salinity 20-40.
    """
    tempK = calc_tempK(temp)
    # Table 4 on p. 1739.
    pK1 = (3670.7 / tempK - 62.008 + 9.7944 * np.log(tempK) -
           0.0118 * salt + 0.000116 * salt**2)
    K1 = 10**(-pK1) # SWS pH scale in mol/kg-SW
    # Table 4 on p. 1739.
    pK2 = 1394.7 / tempK + 4.777 - 0.0184 * salt + 0.000118 * salt**2
    K2 = 10**(-pK2) # SWS pH scale in mol/kg-SW

def hansson_merbach(salt, temp):
    """5 = HANSSON and MEHRBACH refit BY DICKSON AND MILLERO	
    T:    2-35  S: 20-40. Seaw. scale. Artificial seawater.

    Dickson and Millero, Deep-Sea Research,34(10):1733-1743, 1987
    (see also Corrigenda, Deep-Sea Research, 36:983, 1989)
    refit data of Hansson, Deep-Sea Research, 20:461-478, 1973,
    Hansson, Acta Chemica Scandanavia, 27:931-944, 1973,
    and Mehrbach et al, Limnol. Oceanogr.,18(6):897-907, 1973
    on the SWS pH scale in mol/kg-SW.
    Typo in DM on p. 1740 in Table 5: the second equation
    should be pK2* =, not pK1* =.
    The 2s precision in pK1 is .017, or 4# in K1.
    The 2s precision in pK2 is .026, or 6# in K2.
	Valid for salinity 20-40.
    """
    tempK = calc_tempK(temp)
    # tbl 5, p. 1740.
    pK1 = 845 / tempK + 3.248 - 0.0098 * salt + 0.000087 * salt**2
    K1 = 10**(-pK1) # SWS pH scale in mol/kg-SW
    # Table 5 on p. 1740.
    pK2 = 1377.3 / tempK + 4.824 - 0.0185 * salt + 0.000122 * salt**2
    K2 = 10**(-pK2) # SWS pH scale in mol/kg-SW

def GEOSECS(salt, temp):
    """6 = GEOSECS (i.e., original Mehrbach)				
	T:    2-35  S: 19-43. NBS scale.   Real seawater.

    # this is .00001173.*Sali
    # this is about 1# lower than Uppstrom's value
    # Culkin, F., in Chemical Oceanography,
    # ed. Riley and Skirrow, 1965:
    # GEOSECS references this, but this value is not explicitly
    # given here

    # This is for GEOSECS and Peng et al.
    # Lyman, John, UCLA Thesis, 1957
    # fit by Li et al, JGR 74:5507-5525, 1969:

    # Neither the GEOSECS choice nor the freshwater choice
    # include contributions from phosphate or silicate.

    # GEOSECS and Peng et al use K1, K2 from Mehrbach et al,
    # Limnology and Oceanography, 18(6):897-907, 1973.
	# I.e., these are the original Mehrbach dissociation constants.
    # The 2s precision in pK1 is .005, or 1.2# in K1.
    # The 2s precision in pK2 is .008, or 2# in K2.

    # pK2 is not defined for Sal=0, since log10(0)=-inf
    """
    tempK = calc_tempK(temp)
    logKB = -9.26 + 0.00886 * salt + 0.01 * temp
    KB  = 10**(logKB) / fH # SWS scale
    TB  = 0.0004106 * salt / 35. # mol/kg-SW
    KW  = 0     # GEOSECS doesn't include OH effects
    KP1 = 0
    KP2 = 0
    KP3 = 0
    KSi = 0

    pK1 = (- 13.7201 + 0.031334 * tempK + 3235.76 / tempK +
           1.3e-5 * salt * tempK - 0.1032 * salt**0.5)
    K1 = 10.**(-pK1) / fH # SWS scale
    pK2 = (5371.9645 + 1.671221 * tempK + 0.22913 * salt +
           18.3802 * np.log10(salt) - 128375.28 / tempK -
           2194.3055 * np.log10(tempK) - 8.0944e-4 * salt * tempK -
           5617.11 * np.log10(salt) / tempK + 2.136 * salt / tempK)
    K2 = 10.**(-pK2) /fH # SWS scale

    #GEOSECS Pressure Effects On K1, K2, KB (on the NBS scale)
    #Takahashi et al, GEOSECS Pacific Expedition v. 3, 1982 quotes
    #Culberson and Pytkowicz, L and O 13:403-417, 1968:
    #but the fits are the same as those in
    #Edmond and Gieskes, GCA, 34:1261-1291, 1970
    #who in turn quote Li, personal communication
    lnK1fac = (24.2 - 0.085 * temp) * Pbar / RT(temp)
    lnK2fac = (16.4 - 0.04  * temp) * Pbar / RT(temp)
    #Takahashi et al had 26.4, but 16.4 is from Edmond and Gieskes
    #and matches the GEOSECS results
    lnKBfac = (27.5 - 0.095 * temp) * Pbar / RT(temp)
    # GEOSECS and Peng assume pCO2 = fCO2, or FugFac = 1
    FugFac = 1
    if pres is not None:
        pass
                
def peng(salt, temp):
    """7 = Peng	(i.e., originam Mehrbach but without XXX)	
    T:    2-35  S: 19-43. NBS scale.   Real seawater.

    this is .00001173.*Sali this is about 1% lower than Uppstrom's value
    Culkin, F., in Chemical Oceanography, ed. Riley and Skirrow, 1965:
    GEOSECS references this, but this value is not explicitly given here

    This is for GEOSECS and Peng et al. Lyman, John, UCLA Thesis, 1957
    fit by Li et al, JGR 74:5507-5525, 1969:

    Peng et al don't include the contribution from this term, but it is so 
    small it doesn't contribute. It needs to be kept so that the routines 
    work ok. KP2, KP3 from Kester, D. R., and Pytkowicz, R. M., Limnology and 
    Oceanography 12:243-252, 1967: these are only for sals 33 to 36 and are on 
    the NBS scale Sillen, Martell, and Bjerrum,  Stability Constants of 
    metal-ion complexes 
    KSi: The Chemical Society (London), Special Publ. 17:751, 1964
     
    GEOSECS and Peng et al use K1, K2 from Mehrbach et al, Limnology and 
    Oceanography, 18(6):897-907, 1973. I.e., these are the original Mehrbach 
    dissociation constants. The 2s precision in pK1 is .005, or 1.2# in K1.
    The 2s precision in pK2 is .008, or 2# in K2.
    pK2 is not defined for Sal=0, since log10(0)=-inf
    """
    tempK = calc_tempK(temp)
    logTempK = np.log(tempK)
    
    fH = 1.29 - 0.00204 * tempK + (0.00046 - 0.00000148 * tempK) * salt * salt
    logKB = -9.26 + 0.00886*salt + 0.01*temp
    KB  = 10**(logKB) / fH # SWS scale
    TB  = 0.0004106 * salt / 35 # in mol/kg-SW
    KW  = 0  # GEOSECS doesn't include OH effects
    KP1 = 0.02
    KP2 = np.exp(-9.039 - 1450 / tempK) / fH # SWS scale
    KP3 = np.exp(4.4660 - 7276 / tempK) / fH # SWS scale
    KSi = 0.0000000004 / fH                  # SWS scale

    # Peng et al, Tellus 39B:439-458, 1987:
    # They reference the GEOSECS report, but round the value
    # given there off so that it is about .008 (1#) lower. It
    # doesn't agree with the check value they give on p. 456.

    # Millero, Geochemica et Cosmochemica Acta 43:1651-1661, 1979
    lnKW = (148.9802 - 13847.26 / tempK - 23.6521 * logTempK +
            (-79.2447 + 3298.72 / tempK + 12.0408 * logTempK) *
            np.sqrt(salt) - 0.019813 * salt)

    pK1 = (-13.7201 + 0.031334 * tempK + 3235.76 / tempK +
           1.3e-5 * salt * tempK - 0.1032 * salt**0.5)
    K1 = 10.**(-pK1) / fH # SWS scale
    pK2 = (5371.9645 + 1.671221 * tempK + 0.22913 * salt +
           18.3802   * np.log10(salt)  - 128375.28 / tempK -
           2194.3055 * np.log10(tempK) - 8.0944e-4 * salt * tempK -
           5617.11   * np.log10(salt) / tempK + 2.136 * salt / tempK) 
    K2 = 10.**(-pK2) / fH # SWS scale

    # GEOSECS Pressure Effects On K1, K2, KB (on the NBS scale)
    # Takahashi et al, GEOSECS Pacific Expedition v. 3, 1982 quotes
    # Culberson and Pytkowicz, L and O 13:403-417, 1968:
    # but the fits are the same as those in
    # Edmond and Gieskes, GCA, 34:1261-1291, 1970
    # who in turn quote Li, personal communication
    lnK1fac = (24.2 - 0.085 * tempC) * Pbar / RT(temp)
    lnK2fac = (16.4 - 0.04  * tempC) * Pbar / RT(temp)
    # Takahashi et al had 26.4, but 16.4 is from Edmond and Gieskes
    # and matches the GEOSECS results
    lnKBfac = (27.5 - 0.095 * tempC) * Pbar / RT(temp)
    # GEOSECS and Peng assume pCO2 = fCO2, or FugFac = 1
    FugFac = 1;

    """F=(WhichKs==7);
    if any(F)
    # Millero, Geochemica et Cosmochemica Acta 43:1651-1661, 1979
    lnKW(F) = 148.9802 - 13847.26./TempK(F) - 23.6521.*logTempK(F) +...
        (-79.2447 + 3298.72./TempK(F) + 12.0408.*logTempK(F)).*...
        sqrSal(F) - 0.019813.*Sal(F);
    end
    """
    
def millero_1979(temp, salt, pres=None):
    """ 8 = Millero, 1979, FOR PURE WATER ONLY (i.e., Sal=0)	
    T:    0-50  S:     0. 

    Neither the GEOSECS choice nor the freshwater choice
    include contributions from pho

	PURE WATER CASE
    Millero, F. J., Geochemica et Cosmochemica Acta 43:1651-1661, 1979:
    K1 from refit data from Harned and Davis,
    J American Chemical Society, 65:2030-2037, 1943.
    K2 from refit data from Harned and Scholes,
    J American Chemical Society, 43:1706-1709, 1941.
	This is only to be used for Sal=0 water (note the absence of S in the
    below formulations)
    Millero, Geochemica et Cosmochemica Acta 43:1651-1661, 1979
    refit data of Harned and Owen, The Physical Chemistry of
    Electrolyte Solutions, 1958
    """
    tempK = calc_tempK(temp)
    cdict = {"TB" : 0, "KB" : 0, "KP1" : 0, "KP2" : 0, "KP3" : 0, "KSi" : 0,
             "fH" : 1, "KB2" : 0}
    lnKW = 148.9802 - 13847.26 / tempK - 23.6521 * np.log(tempK)
    KW   = np.exp(lnKW)
    lnK1 = 290.9097 - 14554.21 / tempK - 45.0575 * np.log(tempK)
    K1   = np.exp(lnK1)
    lnK2 = 207.6548 - 11843.79 / tempK - 33.6485 * np.log(tempK)
    K2   = np.exp(lnK2)
    if pres is not None:
        # Millero, 1983.
        Pbar = pres / 10
        deltaV  = -30.54 + 0.1849 * temp - 0.0023366 * temp**2;
        Kappa   = (-6.22 + 0.1368 * temp - 0.001233  * temp**2) / 1000
        lnK1fac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        K1 = K1 * np.exp(lnK1fac)
        deltaV  = -29.81 + 0.115 * temp - 0.001816 * Temp**2
        Kappa   = (-5.74 + 0.093 * temp - 0.001896 * Temp**2) / 1000
        lnK2fac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        K2 = K2 * np.exp(lnK2fac)
        deltaV  =  -25.6 + 0.2324 * temp - 0.0036246 * temp**2;
        Kappa   = (-7.33 + 0.1368 * temp - 0.001233  * temp**2) / 1000
        lnKWfac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        KW = KW * np.exp(lnKWfac)


def cai_wang_1998():
    """9 = Cai and Wang, 1998									
    T:    2-35  S:  0-49. NBS scale.   Real and artificial seawater.

    From Cai and Wang 1998, for estuarine use.
	Data used in this work is from:
	K1: Merhback (1973) for S>15, for S<15: Mook and Keone (1975)
	K2: Merhback (1973) for S>20, for S<20: Edmond and Gieskes (1970)
	Sigma of residuals between fits and above data: +-0.015, +0.040 for 
    K1 and K2, respectively.
	Sal 0-40, Temp 0.2-30
    Limnol. Oceanogr. 43(4) (1998) 657-668
	On the NBS scale
	Their check values for F1 don't work out, not sure if this was correctly 
    published...
    """
    tempK = calc_tempK(temp)
    F1  = 200.1 / tempK + 0.3220
    pK1 = (3404.71 / tempK + 0.032786 * tempK - 14.8435 -
           0.071692 * F1 * salt**0.5 + 0.0021487 * salt)
    K1  = 10**-pK1 / fH # SWS scale (uncertain at low Sal: junction potential)
    F2  = -129.24 / tempK + 1.4381
    pK2 = (2902.39 / tempK + 0.023790 * tempK - 6.49800 -
           0.319100 * F2 * salt**0.5 + 0.0198000 * salt)
    K2  = 10**-pK2 / fH # SWS scale (uncertain at low Sal: junction potential)

def lueker_2000():
    """10 = Lueker et al, 2000									
    T:    2-35  S: 19-43. Total scale. Real seawater.

    From Lueker, Dickson, Keeling, 2000
	This is Mehrbach's data refit after conversion to the total scale, 
    for comparison with their equilibrator work. 
    Mar. Chem. 70 (2000) 105-119
    Total scale and kg-sw
    """
    tempK = calc_tempK(temp)
    pK1 = (3633.86 / tempK - 61.2172 + 9.67770 * np.log(tempK) -
           0.011555 * salt + 0.0001152 * salt**2)
    K1  = 10**-pK1 / SWStoTOT # SWS pH scale
    pK2 = (471.780 / tempK + 25.929  - 3.16967 * np.log(tempK) -
           0.017810 * salt + 0.0001122 * salt**2)
    K2  = 10**-pK2 / SWStoTOT # SWS pH scale
    
def mojica_2002():
    """11 = Mojica Prieto and Millero, 2002.					
    T:    0-45  S:  5-42. Seaw. scale. Real seawater

    Mojica et al 2002. Geochim. et Cosmochim. Acta. 66(14) 2529-2540.
	Abstract and pages 2536-2537.
	sigma for pK1 is reported to be 0.0056
	sigma for pK2 is reported to be 0.010
    """
    tempK = calc_tempK(temp)
    pK1 = (-43.6977 - 0.01290370 * salt + 1.364e-4 * salt**2 +
           2885.378 / tempK +  7.045159 * np.log(tempK))
    pK2 = (-452.0940 + 13.142162 * salt - 8.101e-4 * salt**2 +
           21263.61 / tempK  + 68.483143 * np.log(tempK) +
           (-581.4428 * salt + 0.259601 * salt**2) / tempK -
           1.967035 * salt * np.log(tempK))
    K1 = 10**-pK1 # this is on the SWS pH scale in mol/kg-SW
    K2 = 10**-pK2 # this is on the SWS pH scale in mol/kg-SW


def millero_2002(salt, temp):
    """12 = Millero et al, 2002									
    T: -1.6-35  S: 34-37. Seaw. scale. Field measurements.

	Millero et al., 2002. Deep-Sea Res. I (49) 1705-1723.
	Calculated from overdetermined WOCE-era field measurements 
	sigma for pK1 is reported to be 0.005
	sigma for pK2 is reported to be 0.008
    """
	# Page 1715
    pK1 =  6.359 - 0.00664 * salt - 0.01322 * temp + 4.989e-5 * temp**2
    pK2 =  9.867 - 0.01314 * salt - 0.01904 * temp + 2.448e-5 * temp**2
    K1 = 10**-pK1 # SWS pH scale in mol/kg-SW
    K2 = 10**-pK2 # SWS pH scale in mol/kg-SW


def millero_2006(salt, temp):
    """13 = Millero et al, 2006									
    T:    0-50  S:  1-50. Seaw. scale. Real seawater.

    From Millero 2006 work on pK1 and pK2 from titrations
	Millero, Graham, Huang, Bustos-Serrano, Pierrot. Mar.Chem. 100 (2006)
    80-94.
    S=1 to 50, T=0 to 50. On seawater scale (SWS).
    From titrations in Gulf Stream seawater.
    """
    tempK = calc_tempK(temp)
    pK1_0 = -126.34048 + 6320.813/tempK + 19.568224*np.log(tempK)
    A_1   = 13.4191 * salt**0.5 + 0.0331 * salt - 5.33e-5 * salt**2
    B_1   = -530.123 * salt**0.5 - 6.103 * salt
    C_1   = -2.06950 * salt**0.5
    pK1   = A_1 + B_1/tempK + C_1*np.log(tempK) + pK1_0 # pK1 sigma = 0.0054
    K1    = 10**-(pK1)
    pK2_0 = -90.18333 + 5143.692/tempK + 14.613358*np.log(tempK)	
    A_2   = 21.0894  * salt**0.5 + 0.1248 * salt - 3.687e-4 * salt**2
    B_2   = -772.483 * salt**0.5 - 20.051 * salt
    C_2   = -3.3336  * salt**0.5
    pK2   = A_2 + B_2/tempK + C_2*np.log(tempK) + pK2_0 #pK2 sigma = 0.011
    K2    = 10**-(pK2)

def millero_2010(salt, temp, pres=None):
    """14 = Millero et al, 2010									
    T:    0-50  S:  1-50. Seaw. scale. Real seawater.

    # From Millero, 2010, also for estuarine use.
	# Marine and Freshwater Research, v. 61, p. 139?142.
	# Fits through compilation of real seawater titration results:
	# Mehrbach et al. (1973), Mojica-Prieto & Millero (2002),
    Millero et al. (2006)
	# Constants for K's on the SWS;
    """
    cdict = generate_constants_dict(salt, temp, pres)
    tempK = calc_tempK(temp)
	# Page 141
    pK10 = -126.34048 + 6320.813 / tempK + 19.568224 * np.log(tempK)
	# Table 2, page 140.
    A1   = 13.4038  * salt**0.5 + 0.03206 * salt - 5.242e-5 * salt**2
    B1   = -530.659 * salt**0.5 - 5.82100 * salt
    C1   = -2.0664  * salt**0.5
    pK1  = pK10 + A1 + B1/tempK + C1*np.log(tempK)
    K1   = 10**-pK1
	# Page 141
    pK20 =  -90.18333 + 5143.692/tempK + 14.613358*np.log(tempK)
	# Table 3, page 140.
    A2   = 21.3728  * salt**0.5 + 0.1218 * salt - 3.688e-4 * salt**2
    B2   = -788.289 * salt**0.5 - 19.189 * salt
    C2   = -3.374   * salt**0.5
    pK2  = pK20 + A2 + B2/tempK + C2*np.log(tempK)
    K2   = 10**-pK2
    K1,K2 = calculate_press_effects_on_K1_K2(K1, K2, temp, pres)
    cdict['K1'] = K1
    cdict['K2'] = K2
    return cdict

def calculate_press_effects_on_K1_K2(K1, K2, temp, pres):
    """Calculate pressure effects on K1 and K2
    Millero, 1995 (same as Millero, 1979 and Millero, 1992)
    From data of Culberson and Pytkowicz, 1968.
    """
    if pres is not None:
        Pbar = pres / 10
        deltaV  = -25.5 + 0.1271 * temp
        Kappa   = (-3.08 + 0.0877 * temp) / 1000
        lnK1fac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        K1 = K1 * np.exp(lnK1fac)
        deltaV  = -15.82 - 0.0219 * temp
        Kappa   = (1.13 - 0.1475 * temp) / 1000
        lnK2fac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        K2 = K2 * np.exp(lnK2fac)
    return K1,K2

def calculate_KP1(salt, temp, pres=None):
    """Yao and Millero, Aquatic Geochemistry 1:53-88, 1995
    KSi was given on the SWS pH scale in molal units.
    """
    tempK = calc_tempK(temp)
    lnKP1 = (-4576.752 / tempK + 115.54 - 18.453 * np.log(tempK) +
             (-106.736 / tempK + 0.69171) * np.sqrt(salt) +
             (-0.65643 / tempK - 0.01844) * salt)
    KP1 = np.exp(lnKP1)
    if pres is not None:
        Pbar = pres / 10
        deltaV = -14.51 + 0.1211 * temp - 0.000321 * temp**2
        Kappa  = (-2.67 + 0.0427 * temp) / 1000
        lnKP1fac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        KP1 = KP1 * np.exp(lnKP1fac)
    return KP1 # SWS pH scale in mol/kg-SW.

def calculate_KP2(salt, temp, pres=None):    
    """Millero, Geochemica et Cosmochemica Acta 59:661-677, 1995.
    His check value of 1.6 umol/kg-SW should be 6.2
    """
    tempK = calc_tempK(temp)
    lnKP2 = (-8814.715 / tempK + 172.1033 - 27.927 * np.log(tempK) +
             (-160.34 / tempK + 1.35660) * np.sqrt(salt) +
             (0.37335 / tempK - 0.05778) * salt)
    KP2 = np.exp(lnKP2)
    if pres is not None:
        Pbar = pres / 10        
        deltaV = -23.12 + 0.1758 * temp - 0.002647 * temp**2
        Kappa  = (-5.15 + 0.09   * temp) / 1000
        lnKP2fac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        KP2 = KP2 * np.exp(lnKP2fac)
    return KP2 # SWS pH scale in mol/kg-SW.

def calculate_KP3(salt, temp, pres=None):    
    """Millero, Geochemica et Cosmochemica Acta 59:661-677, 1995."""
    tempK = calc_tempK(temp)
    lnKP3 = (-3070.7500 / tempK - 18.126 +
             (17.270390 / tempK + 2.81197) * np.sqrt(salt) +
             (-44.99486 / tempK - 0.09984) * salt)
    KP3 = np.exp(lnKP3)
    if pres is not None:
        Pbar = pres / 10
        deltaV = -26.57 + 0.202  * temp - 0.003042 * temp**2
        Kappa  = (-4.08 + 0.0714 * temp) / 1000
        lnKP3fac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        KP3 = KP3 * np.exp(lnKP3fac)
    return KP3 # SWS pH scale in mol/kg-SW.

def calculate_KSi(salt, temp, pres=None):
    tempK = calc_tempK(temp)
    IonS  = calculate_IonS(salt)
    lnKSi = (-8904.20  / tempK + 117.4 - 19.334 * np.log(tempK) +
             (-458.79  / tempK + 3.5913) * np.sqrt(IonS) +
             (188.740  / tempK - 1.5998) * IonS +
             (-12.1652 / tempK + 0.07871) * IonS**2)
    KSi = np.exp(lnKSi) * (1 - 0.001005 * salt) # mol/kg-SW
    if pres is not None:
        Pbar = pres / 10
        deltaV = -29.48 + 0.1622 * temp - 0.002608 * temp**2
        Kappa  = -2.84 / 1000
        lnKSifac = (-deltaV + 0.5 * Kappa * Pbar) * Pbar / RT(temp)
        KSi = KSi * np.exp(lnKSifac)
    return KSi # SWS pH scale in mol/kg-SW

def convert_pH_scale(cdict):
    "Convert cdict to other pHscale"""
    if pHscale==1: #Total
        pHfactor = cdict["SWStoTOT"]
    elif pHScale==2: #SWS, they are all on this now
        pHfactor = 1
    elif pHScale==3: #pHfree
        pHfactor = cdict['SWStoTOT'] / cdict['FREEtoTOT']
    elif pHScale==4: #pHNBS
        pHfactor = fH
    for key in ["K1", "K2", "KW", "KB", "KP1", "KP2", "KP3", "KSi"]:
        cdict[key] = cdict[key] * pHfactor
    return cdict
