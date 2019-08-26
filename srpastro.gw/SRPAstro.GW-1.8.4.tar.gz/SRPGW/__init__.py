""" 

Context : SRP
Module  : GW
Version : 1.3.4
Author  : Stefano Covino
Date    : 26/08/2019
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : to be imported

Remarks :

History : (16/11/2015) First version.
        : (11/12/2015) V. 0.1.1b1.
        : (12/12/2015) V. 0.1.1b2.
        : (14/12/2015) V. 0.1.1b3.
        : (15/03/2015) V. 0.1.1b4.
        : (18/12/2015) V. 0.2.0b1.
        : (21/12/2015) V. 0.2.0b2.
        : (22/12/2015) V. 0.2.0b3.
        : (30/12/2015) V. 0.2.0b4.
        : (02/01/2016) V. 0.2.0b5.
        : (03/01/2016) V. 0.2.0b6.
        : (03/01/2016) V. 0.2.0.
        : (08/01/2016) V. 0.3.0.
        : (13/01/2016) V. 0.4.0b1.
        : (20/01/2016) V. 0.4.0, V. 0.5.0b1.
        : (21/01/2016) V. 0.5.0b2.
        : (22/01/2016) V. 0.5.0b3.
        : (23/01/2016) V. 0.5.0.
        : (26/01/2916) V. 0.6.0b1.
        : (28/01/2016) V. 0.6.0b2.
        : (29/01/2016) V. 0.6.0.
        : (01/02/2016) V. 0.7.0b1.
        : (02/02/2016) V. 0.7.0b2.
        : (03/02/2016) V. 0.7.0b3.
        : (03/02/2016) V. 0.7.0b4.
        : (04/02/2016) V. 0.7.0.
        : (04/02/2016) V. 0.7.1b1.
        : (05/02/2016) V. 0.8.0b1.
        : (06/02/2016) V. 0.8.0b2.
        : (07/02/2016) V. 0.8.0b3.
        : (08/02/2016) V. 0.8.0b4.
        : (09/02/2016) V. 0.8.0b5 and 0.8.0.
        : (09/02/2016) V. 0.8.0, 0.8.1 and 0.8.2.
        : (10/02/2016) V. 0.8.2, 0.8.3 and 0.8.4b1.
        : (11/02/2016) V. 0.8.4, 0.8.5b1, 0.8.5, 0.8.6b1 and 0.8.6b2.
        : (12/02/2016) V. 0.8.6b3 and 0.8.6.
        : (13/02/2016) V. 0.8.7b1 and 0.8.7.
        : (15/02/2016) V. 0.8.8b1 and 0.8.8.
        : (17/02/2016) V. 0.8.9b1 and 0.8.9.
        : (18/02/2016) V. 0.8.10b1.
        : (19/02/2016) V. 0.8.10.
        : (20/02/2016) V. 0.8.11b1.
        : (21/02/2016) V. 0.8.11.
        : (22/02/2016) V. 0.8.12b1.
        : (24/02/2016) V. 0.9.0b1.
        : (25/02/2016) V. 0.9.0b2 and 0.9.0.
        : (26/02/2016) V. 0.9.1.
        : (02/03/2016) V. 0.9.2b1.
        : (03/03/2016) V. 0.9.2b2.
        : (04/03/2016) V. 0.9.2b3.
        : (06/03/2016) V. 0.9.2b4, 0.9.2b5 and 0.9.2.
        : (08/03/2016) V. 0.9.3b1.
        : (14/03/2016) V. 0.9.3.
        : (18/03/2016) V. 0.9.4.
        : (01/04/2016) V. 0.10.0b1 and 0.10.0.
        : (10/05/2016) V. 0.10.1b1.
        : (11/05/2016) V. 0.10.1b2.
        : (16/05/2016) V. 0.10.1b3.
        : (17/05/2016) V. 0.10.1b4.
        : (20/05/2016) V. 0.10.1.
        : (26/05/2016) V. 0.10.2.
        : (31/05/2016) V. 0.10.3b1.
        : (06/06/2016) Correct VST pixel size. V. 0.10.3b2.
        : (07/06/2016) V. 0.10.3b3.
        : (13/06/2016) V. 0.10.3.
        : (14/06/2016) V. 0.10.4.
        : (13/07/2016) V. 0.10.5b1.
        : (15/07/2016) V. 1.0.0.
        : (10/08/2016) V. 1.0.1b1.
        : (24/08/2016) V. 1.0.1b2.
        : (30/08/2016) V. 1.0.1.
        : (29/11/2016) V. 1.1.0b1.
        : (01/12/2016) V. 1.1.0.
        : (05/12/2016) V. 1.1.1b1.
        : (07/12/2016) V. 1.1.1b2, 1.1.1b3.
        : (13/12/2016) V. 1.2.0b1.
        : (14/12/2016) V. 1.2.0b2.
        : (15/12/2016) V. 1.2.0b3.
        : (16/12/2016) V. 1.2.0b4.
        : (18/12/2016) V. 1.2.0b5 and 1.2.0.
        : (21/12/2016) V. 1.2.1b1.
        : (23/12/2016) V. 1.2.1b2.
        : (24/12/2016) V. 1.2.1b3.
        : (05/01/2017) V. 1.3.0b1.
        : (09/01/2017) V. 1.3.0b2.
        : (18/01/2017) V. 1.3.0b3.
        : (22/02/2017) V. 1.3.0.
        : (24/02/2017) V. 1.3.1b1.
        : (25/02/2017) V. 1.4.0b1.
        : (02/03/2017) V. 1.4.0b2.
        : (03/03/2017) V. 1.4.0b3.
        : (03/04/2017) V. 1.4.0.
        : (19/04/2017) V. 1.4.1.
        : (16/05/2017) V. 1.4.2.
        : (15/08/2017) V. 1.4.3.
        : (16/08/2017) V. 1.4.4 and 1.4.5.
        : (22/08/2017) V. 1.4.6.
        : (23/08/2017) V. 1.4.7.
        : (03/10/2017) V. 1.4.8.
        : (06/12/2017) V. 1.4.9 and 1.5.0.
        : (07/12/2017) V. 1.5.1.
        : (19/12/2017) V. 1.6.0.
        : (20/12/2017) V. 1.6.1.
        : (21/12/2017) V. 1.6.2.
        : (19/01/2018) V. 1.6.3.
        : (04/03/2019) V. 1.6.4.
        : (05/03/2019) V. 1.6.5 and 1.6.6.
        : (06/03/2019) V. 1.6.7.
        : (11/03/2018) V. 1.6.8.
        : (14/03/2019) V. 1.6.9 and 1.6.10.
        : (25/03/2019) V. 1.7.0beta.
        : (28/03/2019) V. 1.7.0.
        : (30/03/2019) V. 1.7.1.
        : (05/04/2019) V. 1.7.2.
        : (28/04/2019) V. 1.7.3, 1.7.4, 1.7.5, 1.7.6 and 1.7.7.
        : (30/05/2019) V. 1.7.8.
        : (11/05/2019) V. 1.7.9.
        : (14/05/2019) V. 1.7.10.
        : (24/05/2019) V. 1.7.11.
        : (29/05/2019) V. 1.8.0.
        : (03/06/2019) V. 1.8.1.
        : (31/07/2019) V. 1.8.2.
        : (07/08/2019) V. 1.8.3.
        : (26/08/2019) V. 1.8.4.
"""

__version__ = '1.8.4'


import numpy


# Generic pars
DATADIR     = 'Data'
PICDIR      = 'GWPics'
RESDIR      = 'GWRes'
FITSDIR     = 'GWFits'
LCDIR       = 'GWLC'
PREDEFFILE  = 'Predef_parset.dat'
FNAMECOL    = 'CatFilename'
FNAMECOLF   = 'FITSFilename'
FNAMECOLW   = 'WeightFilename'
WEIGHTCOL   = 'Weight'
WEIGHTACOL  = 'WeightArea'
TESTCOL     = 'TestArea'
IDCOL       = 'Id'
VSTID       = 'VST'
PICCOL      = 'Pics'
SRPMAG      = 'SRPMAG'
eSRPMAG     = 'eSRPMAG'
ORGMAG      = 'MAG_APER_1'
eORGMAG     = 'MAGERR_APER_1'
PSFMAG      = 'PSFMAG'
ePSFMAG     = 'ePSFMAG'
FLUX        = 'FLUX'
eFLUX       = 'eFLUX'
SIMBCOL     = 'Simbad'
GAIACOL     = 'GAIA'
USNOCOL     = 'USNO'
GLADECOL    = 'GLADE'
LEDACOL     = 'LEDA'
SDSSCOL     = 'SDSS'
DATECOL     = 'MJDSTART'
DATEHEAD    = 'MJDSTART'
DATEOBS     = 'DATE-OBS'
MAGCOL      = 'MAG_APER'
eMAGCOL     = 'MAGERR_APER'
RACOL       = 'X_WORLD'
DECCOL      = 'Y_WORLD'
XCOL        = 'X_IMAGE'
YCOL        = 'Y_IMAGE'
FWCOL       = 'FWHM_IMAGE'
FWHEAD      = 'FWHM'
FITSCOL     = 'FITS_STAMP'
VARINDCOL   = 'DSRPMAG'
AVEMAG      = 'ASRPMAG'
MINMAG      = 'MINMAG'
NEICOL      = 'Neighbor'
DNEICOL     = 'DeltaNeighbor'
GDATACOL    = 'GoodData'
MPCOL       = 'MinorPlanet'
SCOCOL      = 'Score'
TELHEAD     = 'TELESCOP'
CHI2        = 'CHI2'
PANSTARRS   = 'PANSTARRS'



ColList     = [IDCOL, RACOL, DECCOL, XCOL,  YCOL,  DATECOL, SRPMAG, eSRPMAG, PICCOL, FNAMECOL, FWCOL]
FormList    = ['a50', float, float,  float, float, float,   float,  float,   'a150', 'a150',   float]
InfoCols    = [IDCOL, DATECOL, SRPMAG, eSRPMAG, GAIACOL, SIMBCOL]


# Initial GAIA catalogue access
# Bologna
IGAIAUser   = 'generic'
IGAIAPwd    = 'password'
IGAIAHost   = '192.167.166.201'
IGAIADB     = 'TOCats'
IGAIACol    = 'sourceId'
IGAIAColb   = 'ID'
IGAIABO     = 'BO'
IGAIACatBo  = 'TOCats.igslsource_v3_htm_6'
# Roma
IGAIAUserRM  = 'gwusr'
IGAIAPwdRM   = 'GW2016'
IGAIAHostRM  = '127.0.0.1'
IGAIADBRM    = 'TOCats'
IGAIAColRM   = 'sourceId'
IGAIAColbRM  = 'ID'
IGAIARM      = 'RM'
IGAIACatRM   = 'TOCats.igslv3_mini_htm_6'


# Rome PC
ROMEPC  =   'gravitown'


# Finding-chart tool
ASTLIB  = 'astLib'
APLPY   = 'aplpy'
EXTTL   = 'exttools'


# SExctractor parameters
gauss_3_0_7x7 = numpy.array([[0.004963, 0.021388, 0.051328, 0.068707, 0.051328, 0.021388, 0.004963],
                        [0.021388, 0.092163, 0.221178, 0.296069, 0.221178, 0.092163, 0.021388],
                        [0.051328, 0.221178, 0.530797, 0.710525, 0.530797, 0.221178, 0.051328],
                        [0.068707, 0.296069, 0.710525, 0.951108, 0.710525, 0.296069, 0.068707],
                        [0.051328, 0.221178, 0.530797, 0.710525, 0.530797, 0.221178, 0.051328],
                        [0.021388, 0.092163, 0.221178, 0.296069, 0.221178, 0.092163, 0.021388],
                        [0.004963, 0.021388, 0.051328, 0.068707, 0.051328, 0.021388, 0.004963]])



gauss_4_0_7x7 = numpy.array([[0.047454, 0.109799, 0.181612, 0.214776, 0.181612, 0.109799, 0.047454],
                       [0.109799, 0.254053, 0.420215, 0.496950, 0.420215, 0.254053, 0.109799],
                       [0.181612, 0.420215, 0.695055, 0.821978, 0.695055, 0.420215, 0.181612],
                       [0.214776, 0.496950, 0.821978, 0.972079, 0.821978, 0.496950, 0.214776],
                       [0.181612, 0.420215, 0.695055, 0.821978, 0.695055, 0.420215, 0.181612],
                       [0.109799, 0.254053, 0.420215, 0.496950, 0.420215, 0.254053, 0.109799],
                       [0.047454, 0.109799, 0.181612, 0.214776, 0.181612, 0.109799, 0.047454]])



gauss_5_0_9x9 = numpy.array([[0.030531, 0.065238, 0.112208, 0.155356, 0.173152, 0.155356, 0.112208, 0.065238, 0.030531],
                              [0.065238, 0.139399, 0.239763, 0.331961, 0.369987, 0.331961, 0.239763, 0.139399, 0.065238],
                              [0.112208, 0.239763, 0.412386, 0.570963, 0.636368, 0.570963, 0.412386, 0.239763, 0.112208],
                              [0.155356, 0.331961, 0.570963, 0.790520, 0.881075, 0.790520, 0.570963, 0.331961, 0.155356],
                              [0.173152, 0.369987, 0.636368, 0.881075, 0.982004, 0.881075, 0.636368, 0.369987, 0.173152],
                              [0.155356, 0.331961, 0.570963, 0.790520, 0.881075, 0.790520, 0.570963, 0.331961, 0.155356],
                              [0.112208, 0.239763, 0.412386, 0.570963, 0.636368, 0.570963, 0.412386, 0.239763, 0.112208],
                              [0.065238, 0.139399, 0.239763, 0.331961, 0.369987, 0.331961, 0.239763, 0.139399, 0.065238],
                              [0.030531, 0.065238, 0.112208, 0.155356, 0.173152, 0.155356, 0.112208, 0.065238, 0.030531]])


minarea = 5
deblend_nthresh = 32
deblend_cont = 0.005
clean = True
clean_param = 1.0



# VST
VSTgain     = 2.5
VSTron      = 5.5
VSTpixsize  = 0.21
VSTName     = 'ESO-VST'


# CNEOST
CNName      = 'CNEOST'
CNpixsize   = 1.0291


# Campo Imperatore
CNName      = 'Schmidt'
CNpixsize   = 1.012



# Byte order
little  =   'little'
big     =   'big'
native  =   '='
lendian =   '<'
bendian =   '>'
nknown  =   '|'


#Meta data
MAGLIMS = 'MAGLIMS'
SCOLIMS = 'SCOLIMS'



# Generic constants
arcsec2deg = 1./3600.
JD2MJD = 2400000.5


# Variability indices
fedescr = [{'name':'Amplitude', 'nmin':0, 'tnk':[]},
           #{'name':'AndersonDarling', 'nmin':0, 'tnk':[]},
           #{'name':'Beyond1Std', 'nmin':1, 'tnk':[]},
           {'name':'Eta_e', 'nmin':0, 'tnk':[]},
           #{'name':'Gskew', 'nmin':1, 'tnk':[]},
           #{'name':'LinearTrend', 'nmin':1, 'tnk':[]},
           {'name':'MaxSlope', 'nmin':1, 'tnk':[]},
           #{'name':'Mean', 'nmin':0, 'tnk':[]},
           {'name':'Meanvariance', 'nmin':0, 'tnk':[]},
           {'name':'MedianAbsDev', 'nmin':0, 'tnk':[]},
           #{'name':'MedianBRP', 'nmin':0, 'tnk':[]},
           {'name':'PercentAmplitude', 'nmin':0, 'tnk':[]},
           {'name':'Q31', 'nmin':1, 'tnk':[]},
           #{'name':'Rcs', 'nmin':1, 'tnk':[]},
           #{'name':'Skew', 'nmin':0, 'tnk':[]},
           {'name':'SmallKurtosis', 'nmin':3, 'tnk':[]},
           {'name':'Std', 'nmin':1, 'tnk':[]}]



__all__ =  ['ApyPhot', 'ApyPSFPhot', 'CheckMagDiff', 'Chi2', 'DaoPhot', 'DaoPSFPhot', 'FindPathes',
                'FindSubPathes', 'Flux2Mag', 'GetApPhot', 'GetCommandStr', 'GetFITS', 'GetGAIAxMatch',
                'GetGLADExMatch', 'GetHeadVal', 'GetIGAIA', 'GetIGAIAxMatch', 'GetLEDAxMatch',
                'GetPanSTARSS', 'GetPics', 'GetPixVal', 'GetPixXY', 'GetPSFPhot', 'GetSDSSxMatch', 'GetSkyBot',
                'GetSkyBotMatch', 'GetSimbad', 'GetSimbadxMatch', 'GetTest', 'GetUSNOxMatch',
                'GetWeights', 'IsCoordIn', 'MyPhot', 'Score', 'SexPhot']





