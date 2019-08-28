
import numpy as np

from . import constants

class CarbonateSystem(object):
    
    def __init__(self, salt, temp, pres=None, temp_out=None, pres_out=None,
                 TC=None, TA=None, pH=None, pCO2=None, fCO2=None,
                 PO4=None, Si=None,
                 K1K2="Millero2010", KBver="Uppstrom", KSver="Dickson"):

        if TA is not None:
            TA   = TA   / 1e6 # micromol/kg to mol/kg
        if TC is not None:
            TC   = TC   / 1e6 # micromol/kg to mol/kg
        if pCO2 is not None:
            pCO2 = pCO2 / 1e6 # microatm. to atm.
        if fCO2 is not None:
            fCO2 = fCO2 / 1e6 # microatm. to atm.
            
        cdict = constants.millero_2010(salt, temp, pres)
        for key in cdict:
            setattr(self, key, cdict[key])
        if PO4 is None:
            self.TP = salt * 0
        else:
            self.TP = PO4  / 1e6
        if Si is None:
            self.TSi = salt * 0
        else:
            self.TSi = Si / 1e6
        if "peng" in K1K2.lower():
            self.peng_corr = self.TP * 0
        else:
            self.peng_corr = self.TP
            
        # Calculate missing values for AT,CT,PH,FC:
        if fCO2 is None and pCO2 is not None:
            fCO2 =  pCO2 * self.FugFac
        if TA is not None and TC is not None:
            pH   = self.calc_pH_from_TATC(TA-self.peng_corr, TC)
            fCO2 = self.calc_fCO2_from_TCpH(TC, pH)
            #pH,fCO2 = self.calc_pHfCO2_from_TATC(TA-self.peng_corr, TC);
        elif TA is not None and pH is not None:
            TC   = self.calc_TC_from_TApH(TA-self.peng_corr, pH);
            fCO2 = self.calc_fCO2_from_TCpH(TC, pH);
        elif TA is not None and fCO2 is not None:
            pH   = self.calc_pH_from_TAfCO2(TA-self.peng_corr, fCO2);
            TC   = self.calc_TC_from_TApH  (TA-self.peng_corr, pH);
        elif TC is not None and pH is not None:
            TA   = self.calc_TA_from_TCpH  (TC, pH) + self.peng_corr
            fCO2 = self.calc_fCO2_from_TCpH(TC, pH)
        elif TC is not None and fCO2 is not None:
            pH   = self.calc_pH_from_TCfCO2(TC, fCO2)
            TA   = self.calc_TA_from_TCpH  (TC, pH) + self.peng_corr
        elif pH is not None and fCO2 is not None:
            TC   = self.calc_TC_from_pHfCO2(pH, fCO2)
            TA   = self.calc_TA_from_TCpH  (TC, pH) + self.peng_corr
        else:
            raise (TypeError, "Two carbonate properties must be provided")
        if pCO2 is None and fCO2 is not None:
            pCO2 = fCO2 / self.FugFac
        self.revelle = self.calc_revelle_factor(TA-self.peng_corr, TC)
        self.alkdict = self.calc_all_Alk_parts(pH, TC)
        for key in self.alkdict:
            setattr(self, key, self.alkdict[key])
        self.OmCa,self.OmAr = self.calc_CaSolubility(salt, temp, pres, TC, pH)
        self.CO2  = TC - self.CO3 - self.HCO3
        self.PAlk = self.PAlk + self.peng_corr

        self.salt = salt
        self.temp = temp
        if pres is not None:
            self.pres = pres
        self.TA   = TA   * 1e6
        self.TC   = TC   * 1e6
        self.pCO2 = pCO2 * 1e6
        self.fCO2 = fCO2 * 1e6
        self.pH   = pH

        VPFac = constants.calculate_VPFac(self.salt, self.temp)
        self.xCO2dry = self.pCO2 / VPFac # ' this assumes pTot = 1 atm
        #allpHs = FindpHOnAllScales(pH, scales
        
        if temp_out is not None:
            self.out = CarbonateSystem(salt, temp_out, pres=pres_out,
                                       TC=self.TC, TA=self.TA, PO4=PO4, Si=Si,
                                       K1K2=K1K2, KBver=KBver, KSver=KSver)



        """
        # Calculate the constants for all samples at output conditions
        cdict = Constants(Temp_out, press_out)
        pHout,fCO2out = CalculatepHfCO2fromTATC(TA-self.peng_corr, TC)
        PCoc = FCoc./FugFac;
        TAlk  = CalculateAlkParts(PHoc, TCc);
        PAlkout                 = PAlkout+self.peng_corr;
        CO2out                  = TCc - CO3out - HCO3out;
        Revelleout              = RevelleFactor(TAc, TCc);
        [OmegaCaout OmegaArout] = CaSolubility(Sal, TempCo, Pdbaro, TCc, PHoc);
        xCO2dryout              = PCoc./VPFac; # ' this assumes pTot = 1 atm
        """

    def calc_pHfCO2_from_TATC(self, TA, TC):
        """Calculate pH and fCO2 from TA and TC"""
        pH   = self.calc_pH_from_TATC(TA, TC)
        fCO2 = self.calc_fCO2_from_TCpH(TC, pH)
        return pH,fCO2

    def calc_pH_from_TATC(self, TA, TC):
        """Calculate pH from TA and TC using K1 and K2 by Newton's method

        Try to solve for the pH at which Residual = 0. Starting guess is 
        pH = 8. Though it is coded for H on the total pH scale, for the pH 
        values occuring in seawater (pH > 6) it will be equally valid on any
        pH scale (H terms negligible) as long as the K Constants are on that 
        scale. It will continue iterating until all # values in the vector are 
        "abs(deltapH) < pHTol". SVH2007
        """
        pH      = TA * 0 + 8 # First guess
        pHTol   = 0.0001     # tolerance for iterations end
        ln10    = np.log(10)
        deltapH = pHTol + 1
        while np.any(abs(deltapH) > pHTol):
            H         = 10**(-pH)
            Denom     = (H*H + self.K1*H + self.K1*self.K2)
            CAlk      = TC*self.K1 * (H + 2*self.K2) / Denom
            BAlk      = self.TB * self.KB / (self.KB + H)
            OH        = self.KW / H
            PAlk      = self.calc_PAlk(H)
            SiAlk     = self.TSi*self.KSi / (self.KSi + H)
            Hfree     = H / self.FREEtoTOT # for H on the total scale
            HSO4      = self.TS / (1 + self.KS/Hfree) # KS is on the free scale
            HF        = self.TF / (1 + self.KF/Hfree) # KF is on the free scale
            Residual  = TA-CAlk-BAlk - OH - PAlk-SiAlk + Hfree + HSO4 + HF
            # find dTA/dpH (this is not exact but keeps all important terms)
            Slope     = ln10 * (TC*self.K1*H *
                                (H*H + self.K1*self.K2 + 4*H*self.K2) /
                                Denom/Denom + BAlk*H / (self.KB + H) + OH + H)
            deltapH   = Residual / Slope # this is Newton's method
            # to keep the jump from being too big;
            while np.nanmax(abs(deltapH)) > 1:
                mask = np.abs(deltapH) > 1 
                deltapH[mask] = deltapH[mask] / 2
            pH = pH + deltapH # Same scale as K1 and K2 were calculated.
        return pH
    
    def calc_fCO2_from_TCpH(self, TC, pH):
        """Calculate fCO2 from TC and pH using K0, K1, and K2"""
        H = 10**(-pH)
        return TC*H*H / (H*H + self.K1*H + self.K1*self.K2) / self.K0 # fCO2
                       
    def calc_TC_from_TApH(self, TA, pH):
        """Calculate TC from TA and pH

        Though it is coded for H on the total pH scale, for the pH values 
        occuring in seawater (pH > 6) it will be equally valid on any pH scale 
        (H terms negligible) as long as the K Constants are on that scale.
        """
        H         = 10**(-pH)
        BAlk      = self.TB*self.KB / (self.KB + H)
        OH        = self.KW / H
        PAlk      = self.calc_PAlk(H)
        SiAlk     = self.TSi*self.KSi / (self.KSi + H)
        Hfree     = H /self.FREEtoTOT             # for H on the total scale
        HSO4      = self.TS / (1 + self.KS/Hfree) # KS is on the free scale
        HF        = self.TF / (1 + self.KF/Hfree) # KF is on the free scale
        CAlk      = TA - BAlk - OH - PAlk - SiAlk + Hfree + HSO4 + HF
        TC        = (CAlk * (H*H + self.K1*H + self.K1*self.K2) /
                     (self.K1*(H + 2*self.K2)))
        return TC

    def calc_pH_from_TAfCO2(self, TA, fCO2):
        """Calculates pH from TA and fCO2 using K1 and K2 by Newton's method.

        Tries to solve for the pH at which Residual = 0. The starting guess
        is pH = 8. Though it is coded for H on the total pH scale, for the
        pH values occuring in seawater (pH > 6) it will be equally valid on
        any pH scale (H terms negligible) as long as the K Constants are on 
        that scale.
        """
        try:
            TA[TA<0]     = np.nan
            fCO2[fCO2<0] = np.nan
        except:
            pass
        pH     = TA * 0 + 8 # First guess
        pHTol  = 0.0001     # tolerance
        ln10   = np.log(10)
        deltapH = pHTol + pH
        while np.nanmax(np.abs(deltapH)) > pHTol:
            H         = 10**(-pH)
            HCO3      = self.K0 * self.K1 * fCO2 / H
            CO3       = self.K0 * self.K1 * self.K2 * fCO2 / (H*H)
            CAlk      = HCO3 + 2*CO3
            BAlk      = self.TB*self.KB / (self.KB + H)
            OH        = self.KW / H
            PAlk      = self.calc_PAlk(H)
            SiAlk     = self.TSi*self.KSi / (self.KSi + H)
            Hfree     = H / self.FREEtoTOT          # for H on the total scale
            HSO4      = self.TS/(1 + self.KS/Hfree) # KS is on the free scale
            HF        = self.TF/(1 + self.KF/Hfree);# KF is on the free scale
            Residual  = TA - CAlk - BAlk - OH - PAlk-SiAlk + Hfree + HSO4 + HF
            # find slope dTA/dpH (not exact but keeps all important terms)
            Slope     = ln10 * (HCO3 + 4*CO3 + BAlk*H / (self.KB + H) + OH + H)
            deltapH   = Residual / Slope

            # Newton's method to keep the jump from being too big:
            while np.nanmax(np.abs(deltapH)) > 1:
                mask = np.abs(deltapH) > 1 
                deltapH[mask] = deltapH[mask] / 2
            pH = pH + deltapH # Same scale as K1 and K2 were calculated.
        return pH


    def calc_TA_from_TCpH(self, TC, pH):
        """Calculate TA from TC and pH.

        Though it is coded for H on the total pH scale, for the pH values 
        occuring in seawater (pH > 6) it will be equally valid on any pH
        scale (H terms negligible) as long as the K Constants are on that 
        scale.
        """
        H         = 10**(-pH)
        CAlk      = (TC*self.K1 * (H + 2*self.K2) /
                     (H*H + self.K1*H + self.K1*self.K2))
        BAlk      = self.TB*self.KB / (self.KB + H)     
        OH        = self.KW / H
        PAlk      = self.calc_PAlk(H)
        SiAlk     = self.TSi*self.KSi / (self.KSi + H)
        Hfree     = H / self.FREEtoTOT # for H on the total scale
        HSO4      = self.TS / (1 + self.KS/Hfree) # KS is on the free scale
        HF        = self.TF / (1 + self.KF/Hfree) # KF is on the free scale
        TA        = CAlk + BAlk + OH + PAlk + SiAlk - Hfree - HSO4 - HF
        return TA

    def calc_pH_from_TCfCO2(self, TC, fCO2):
        """Calculate pH from TC and fCO2

        This calculates pH from TC and fCO2 using K0, K1, and K2 by solving the
        quadratic in H: fCO2.*K0 = TC.*H.*H./(K1.*H + H.*H + K1.*K2).
        if there is not a real root, then pH is returned as missingn.
        """
        RR = self.K0 * fCO2 / TC
        Discr = (self.K1*RR) * (self.K1*RR) + 4*(1 - RR) * (self.K1*self.K2*RR)
        H     = 0.5 * (self.K1*RR + np.sqrt(Discr)) / (1 - RR)
        pH    = np.log(H) / np.log(0.1)
        return pH

    def calc_TC_from_pHfCO2(self, pH, fCO2):
        """Calculate TC from pH and fCO2 using K0, K1, and K2"""
        H  = 10**(-pH)
        TC = self.K0*fCO2 * (H*H + self.K1*H + self.K1*self.K2) / (H*H)
        return TC

    def calc_revelle_factor(self, TA, TC):
        """Calculate the Revelle factor (dfCO2/dTC)|TA/(fCO2/TC)

        It only makes sense to talk about it at pTot = 1 atm, but it is
        computed here at the given K(), which may be at pressure <> 1 atm. 
        Care must thus be used to see if there is any validity to the number
        computed.
        """
        dTC = 0.000001 # 1 umol/kg-SW
        pH    = self.calc_pH_from_TATC(TA, TC+dTC)
        fCO2p = self.calc_fCO2_from_TCpH(TC+dTC, pH)
        pH    = self.calc_pH_from_TATC(TA, TC-dTC);
        fCO2n = self.calc_fCO2_from_TCpH(TC-dTC, pH)
        return (fCO2p - fCO2n) / dTC / ((fCO2p+fCO2n) / (TC-dTC))

    def calc_PAlk(self, H):
        top = self.KP1*self.KP2*H + 2*self.KP1*self.KP2*self.KP3 - H**3
        bot = (H**3 + self.KP1*H*H + self.KP1*self.KP2*H +
               self.KP1*self.KP2*self.KP3)
        return self.TP * top / bot

    def calc_all_Alk_parts(self, pH, TC):
        """Calculate the various contributions to alkalinity

        Inputs: pH, TC, K(), T()
        Outputs: HCO3, CO3, BAlk, OH, PAlk, SiAlk, Hfree, HSO4, HF
        Though it is coded for H on the total pH scale, for the pH values 
        occuring in seawater (pH > 6) it will be equally valid on any pH 
        scale (H terms negligible) as long as the K Constants are on the scale.
        """
        H = 10**(-pH)
        TA = {}
        TA["HCO3"]  = TC*self.K1*H  / (self.K1*H + H*H + self.K1*self.K2)
        TA["CO3"]   = TC*self.K1*self.K2 / (self.K1*H + H*H + self.K1*self.K2)
        TA["BAlk"]  = self.TB*self.KB / (self.KB + H)
        TA["OH"]    = self.KW / H
        TA["PAlk"]  = self.calc_PAlk(H)
        # this is good to better than .0006*TP:
        # PAlk = TP*(-H/(KP1+H) + KP2/(KP2+H) + KP3/(KP3+H))
        TA["SiAlk"] = self.TSi*self.KSi / (self.KSi + H)
        TA["Hfree"] = H / self.FREEtoTOT           # for H on the total scale
        TA["HSO4"]  = self.TS / (1 + self.KS/TA["Hfree"])  # KS on free scale
        TA["HF"]    = self.TF / (1 + self.KF/TA["Hfree"])  # KF on free scale
        return TA

    def calc_CaSolubility(self, salt, temp, pres, TC, pH,
                          const_ver="millero1995"):
        """Calculate omega, the solubility ratio, for calcite and aragonite
        global K1 K2 TempK logTempK sqrSal Pbar RT WhichKs ntps
        ***********************************************************************
        Inputs: WhichKs#, Sal, TempCi, Pdbari, TCi, pHi, K1, K2
        Outputs: OmegaCa, OmegaAr
        This calculates omega, the solubility ratio, for calcite and aragonite.
        This is defined by: Omega = [CO3--]*[Ca++]./Ksp,
              where Ksp is the solubility product (either KCa or KAr).
        **********************************************************************
        These are from:
        Mucci, Alphonso, The solubility of calcite and aragonite in seawater
            at various salinities, temperatures, and one atmosphere total
            pressure, American Journal of Science 283:781-799, 1983.
        Ingle, S. E., Solubility of calcite in the ocean,
            Marine Chemistry 3:301-319, 1975,
        Millero, Frank, The thermodynamics of the carbonate system in seawater,
            Geochemica et Cosmochemica Acta 43:1651-1661, 1979.
        Ingle et al, The solubility of calcite in seawater at atmospheric 
            pressure and 35#o salinity, Marine Chemistry 1:295-307, 1973.
        Berner, R. A., The solubility of calcite and aragonite in seawater in
            atmospheric pressure and 34.5#o salinity, American Journal of
            Science 276:713-730, 1976.
        Takahashi et al, in GEOSECS Pacific Expedition, v. 3, 1982.
        Culberson, C. H. and Pytkowicz, R. M., Effect of pressure on carbonic 
            acid, boric acid, and the pHi of seawater, Limnology and 
            Oceanography 13:403-417, 1968.
        Riley, J. P. and Tongudai, M., Chemical Geology 2:263-269, 1967:
            this is .010285.*Sali./35
        Ingle, Marine Chemistry 3:301-319, 1975
            same as in Millero, GCA 43:1651-1661, 1979, but Millero, GCA 1995
            has typos (-.5304, -.3692, and 10^3 for Kappa factor)
        Millero, Geochemica et Cosmochemica Acta 43:1651-1661, 1979,
            same as Millero, GCA 1995 except for typos (-.5304, -.3692,
            and 10^3 for Kappa factor)
        Culkin, F, in Chemical Oceanography, ed. Riley and Skirrow, 1965:
            (quoted in Takahashi et al, GEOSECS Pacific Expedition v. 3, 1982)
            Culkin gives Ca = (.0213./40.078).*(Sal./1.80655) in mol/kg-SW
            which corresponds to Ca = .01030.*Sal./35.
        Ingle et al, Marine Chemistry 1:295-307, 1973 is referenced in
            (quoted in Takahashi et al, GEOSECS Pacific Expedition v. 3, 1982
            the fit is actually from Ingle, Marine Chemistry 3:301-319, 1975)
        Berner, R. A., American Journal of Science 276:713-730, 1976:
            (quoted in Takahashi et al, GEOSECS Pacific Expedition v. 3, 1982)
            Berner (p. 722) states that he uses 1.48.
            It appears that 1.45 was used in the GEOSECS calculations

        # *** CalculatePressureEffectsOnKCaKArGEOSECS:
        # Culberson and Pytkowicz, Limnology and Oceanography 13:403-417, 1968
        # (quoted in Takahashi et al, GEOSECS Pacific Expedition v. 3, 1982
        # but their paper is not even on this topic).
        # The fits appears to be new in the GEOSECS report.
        # I can't find them anywhere else.
        """
        tempK = temp + 273.15
        if pres is not None:
            Pbar  = pres / 10
        RT = constants.RT(temp)
        if ("geos" in const_ver.lower()) or ("peng" in const_ver.lower()):
            # Culkin et al (1965):
            Ca = 0.01026 * salt / 35
            # Calculate KCa for GEOSECS (Ingle et al 1973):
            KCa = (0.0000001 * (-34.452 - 39.866 * salt**(1./3) +
                    110.21*np.log(salt) / np.log(10) - 0.0000075752*tempK**2))
            # (mol/kg-SW)^2
            # Calculate KAr for GEOSECS (Berner et al 1976):
            KAr = 1.45 * KCa # (mol/kg-SW)^2

            if pres is not None:
                # Calculate pressure effects on KCa KAr (Culberson et al 1968):
                KCa = KCa * np.exp((36   - 0.2  * temp) * Pbar / RT)
                KAr = KAr * np.exp((33.3 - 0.22 * temp) * Pbar / RT)        
        else:
            # Riley et al (1967):
            Ca = 0.02128 / 40.087 * (salt / 1.80655) # in mol/kg-SW
            # CalciteSolubility (Mucci 1983):
            logKCa = (-171.9065 - 0.077993 * tempK + 2839.319 / tempK +
                      71.595 * np.log(tempK) / np.log(10) +
                      (-0.77712 + 0.0028426*tempK + 178.34/tempK) *
                      np.sqrt(salt) - 0.07711*salt +
                      0.0041249 * np.sqrt(salt) * salt)
            KCa = 10**(logKCa) # (mol/kg-SW)^2
            # AragoniteSolubility (Mucci 1983):
            logKAr = (-171.945 - 0.077993 * tempK + 2903.293 / tempK +
                      71.595 * np.log(tempK) / np.log(10) +
                      (-0.068393 + 0.0017276*tempK +
                       88.135/tempK) * np.sqrt(salt) -
                      0.10018 * salt + 0.0059415 * np.sqrt(salt) * salt)
            KAr    = 10**(logKAr) # (mol/kg-SW)^2
            if pres is not None:
                # Pressure correction for Calcite (Ingle et al, 1975):
                deltaVKCa = -48.76 + 0.5304 * temp
                KappaKCa  = (-11.76 + 0.3692 * temp) / 1000
                lnKCafac  = (-deltaVKCa + 0.5 * KappaKCa * Pbar) * Pbar / RT
                KCa       = KCa * np.exp(lnKCafac)
                # Pressure correction for Aragonite (Millero 1995):
                deltaVKAr = deltaVKCa + 2.8
                KappaKAr  = KappaKCa
                lnKArfac  = (-deltaVKAr + 0.5 * KappaKAr * Pbar) * Pbar / RT
                KAr       = KAr * np.exp(lnKArfac)
        # Calculate Omega:
        H = 10**(-pH)
        CO3 = TC*self.K1*self.K2 / (self.K1*H + H*H + self.K1*self.K2)
        OmegaCa = CO3 * Ca / KCa # dimensionless
        OmegaAr = CO3 * Ca / KAr # dimensionless
        return OmegaCa, OmegaAr


    def __repr__(self):

        try:
            for ph,ta,tc,pc,fc in zip(self.pH, self.TA, self.TC,
                                    self.pCO2, self.fCO2):
                print (ph,ta,tc,pc,fc)
        except TypeError:
           print ("% 2.2f, % 4.2f, % 4.2f, % 3.2f, % 3.2f" %
                  (self.pH, self.TA, self.TC, self.pCO2, self.fCO2))
        return "Carbonate system"

def calc_pH_on_all_scales(pH, scale):
    """Convert pH on a given scale to pH on all scales"""
    scale = str(scale)
    if   "1" in scale or "tot" in scale.lower():    # pHtot
        factor = 0
    elif "2" in scale or "sws" in scale.lower():    # pHsws
        factor = -np.log(self.SWStoTOT) / np.log(0.1)
    elif "3" in scale or "free" in scale.lower():   # pHsws
        factor = -np.log(self.FREEtoTOT) / log(0.1)
    elif "4" in scale or "nbs" in scale.lower():    # pHNBS
        factor = -np.log(self.SWStoTOT) / log(0.1) + np.log(fH) / log(0.1)
    else:
        raise (ValueError, "Wrong scale definition")
    pH  = pH - factor
    return {"tot" :pH,
            "NBS" :pH - np.log(SWStoTOT)/np.log(0.1) + np.log(fH)/np.log(0.1),
            "free":pH - np.log(FREEtoTOT)/np.log(0.1),
            "sws" :pH - np.log(SWStoTOT)/np.log(0.1)}


"""
calc_pH_from_TAfCO2, version 04.01, 10-13-97, written by Ernie Lewis.
calc_pH_from_TATC, version 04.01, 10-13-96, written by Ernie Lewis.
calc_fCO2_from_TCpH, version 02.02, 12-13-96, written by Ernie Lewis.
calc_TC_from_TApH, version 02.03, 10-10-97, written by Ernie Lewis.
calc_TA_from_TCpH, version 02.02, 10-10-97, written by Ernie Lewis.
calc_pH_from_TCfCO2, version 02.02, 11-12-96, written by Ernie Lewis.
calc_TC_from_pHfCO2, version 01.02, 12-13-96, written by Ernie Lewis.
calc_AlkParts, version 01.03, 10-10-97, written by Ernie Lewis.
RevelleFactor, version 01.03, 01-07-97, written by Ernie Lewis.
CaSolubility, version 01.05, 05-23-97, written by Ernie Lewis.
FindpHOnAllScales, version 01.02, 01-08-97, written by Ernie Lewis.
FindpHfCO2_from_TATC, version 01.02, 10-10-97, written by Ernie Lewis.
"""
