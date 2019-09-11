import pandas as pd
import numpy as np
import biogeme.results as res

structResults = res.bioResults(pickleFile='02oneLatentOrdered.pickle')
structBetas = structResults.getBetaValues()

for k,v in structBetas.items():
    print(f"{k} = Beta('{k}',{v},None,None,0 )")


SIGMA_STAR_Envir02 = Beta('SIGMA_STAR_Envir02',0.7670519646409621,None,None,0 )
SIGMA_STAR_Envir03 = Beta('SIGMA_STAR_Envir03',0.7177819009863683,None,None,0 )
SIGMA_STAR_Mobil11 = Beta('SIGMA_STAR_Mobil11',0.7833224122337571,None,None,0 )
SIGMA_STAR_Mobil14 = Beta('SIGMA_STAR_Mobil14',0.6882826546409856,None,None,0 )
SIGMA_STAR_Mobil16 = Beta('SIGMA_STAR_Mobil16',0.7544205820581054,None,None,0 )
SIGMA_STAR_Mobil17 = Beta('SIGMA_STAR_Mobil17',0.7600628538416172,None,None,0 )
coef_ContIncome_0_4000 = Beta('coef_ContIncome_0_4000',0.08954209471304636,None,None,0 )
coef_ContIncome_10000_more = Beta('coef_ContIncome_10000_more',0.08430692986645968,None,None,0 )
coef_ContIncome_4000_6000 = Beta('coef_ContIncome_4000_6000',-0.2209233080453265,None,None,0 )
coef_ContIncome_6000_8000 = Beta('coef_ContIncome_6000_8000',0.2591889240542216,None,None,0 )
coef_ContIncome_8000_10000 = Beta('coef_ContIncome_8000_10000',-0.5227805784067027,None,None,0 )
delta_1 = Beta('delta_1',0.25196349820243613,None,None,0 )
delta_2 = Beta('delta_2',0.759172317380935,None,None,0 )

