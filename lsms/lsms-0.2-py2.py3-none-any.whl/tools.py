
# -*- coding: utf-8 -*-

import sys
import re
try: # Only python 2
    reload(sys).setdefaultencoding('utf-8')  
except NameError: pass
import pandas as pd
import numpy as np
from pandas.io import stata
from collections import defaultdict
from warnings import warn

def get_food_expenditures(fn,purchased,away,produced,given,itmcd='itmcd',HHID='HHID',units=None,convert_categoricals=False):
    """
    Aggregate expenditures on different goods across sources.

    Takes as input a stata *.dta file fn, organized so that each 'row' corresponds to the
    household's expenditures on a particular good, uniquely identified by a string itmcd.

    Different sources for a given good are =purchased=; consumed =away=
    from home; consumed from what the household =produced=; or might have been =given=.

    If the optional input =units= is supplied (the field name of a
    variable describing the units in which consumed /quantities/ of the
    good were measured), then instead of producing an aggregate for each
    =itmcd=, produce one for =(itmcd,units)=.

    Ethan Ligon                                                                 March 2015
    """

    sources={'purchased':purchased,'away':away,'produced':produced,'given':given}
    return sum_food_expenditures_from_different_sources(fn,sources,itmcd=itmcd,HHID=HHID,units=None,convert_categoricals=convert_categoricals)

def sum_food_expenditures_from_different_sources(fn,sources,itmcd='itmcd',HHID='HHID',units=None,convert_categoricals=False,labels=None):
    """Aggregate expenditures on different goods across sources.

    Takes as input a stata *.dta file fn, organized so that each 'row'
    corresponds to the household's expenditures on a particular good,
    uniquely identified by a string itmcd.

    Different sources and corresponding variable names for a given good
    are specified in a dictionary sources; e.g,
    sources={'purchased':'h01','consumed away':'h02'}.

    If a value in a item in sources is a pair (as for "produced" in
    the example above) then the pair is interpreted as a
    (quantity,unit).

    Ethan Ligon                                           December 2015
    """
    if type(fn)==list:
        files=[f for f in set(fn)]
        df=pd.read_stata(files.pop(), convert_categoricals=convert_categoricals)
        for f in files:
            current_df=pd.read_stata(f, convert_categoricals=convert_categoricals)
            df=pd.merge(df,current_df)
    else:
        df=pd.read_stata(fn, convert_categoricals=convert_categoricals)

    if type(HHID)==list:        
        df['HHID']=df[HHID[0]].apply(lambda x: unicode(x))
        for itm in HHID[1:]:
            df['HHID']=df['HHID']+'-'+df[itm].apply(lambda x: unicode(x))
        HHID = 'HHID'
    values = list(sources.values())
    df[values[0]]=df[values[0]].astype(np.float64)
    varnames = {v: k for k, v in sources.items()}
    varnames.update({HHID:'HHID',itmcd:'itmcd'})

    df.rename(columns=varnames,inplace=True)

    try:
        df['HHID']=df['HHID'].apply(lambda x: '%d' % int(float(x)))
    except ValueError:
        pass
    try:
        df['itmcd']=df['itmcd'].apply(lambda x: float(x))
        originalShape=df.shape
        df=df.loc[~np.isnan(df['itmcd']),:]
        if df.shape!=originalShape:
            warn("Warning: %d missing item codes dropped" % (originalShape[0]-df.shape[0]))
        df['itmcd']=df['itmcd'].apply(lambda x: int(x))
    except ValueError:
        pass

    if convert_categoricals:
        try:
            sr=stata.StataReader(fn)
            itemlabels=sr.value_labels()[itmcd].items()
        except KeyError:
            itemlabels=sr.value_labels()[itmcd.upper()].items()

        itemlabels = list(zip(*itemlabels))
        itemlabels = zip(itemlabels[1],itemlabels[0])

        # Deal with possibly poorly formed labels (e.g., those with unbalanced parentheses).
        e=[]
        for k,v in itemlabels:
            e.append((re.sub('\)|\(','',k),'$x_{%d}$' % v))

        itemlabels=dict(e)


        df.replace({'itmcd':{'\)|\(':''}},inplace=True)
    elif labels is not None:
        itemlabels=labels
        df.replace({'itmcd':itemlabels},inplace=True)
    else: # Use numerical labels
        itemlabels=set(df.itmcd)
        try:
            itemlabels={i:r'$x_{%d}$' % i for i in itemlabels}
            df.replace({'itmcd':itemlabels},inplace=True)
        except TypeError: #case where itmcds are strings
            itemlabels = {i:i for i in itemlabels}

    # Group together consumption from different sources.
    valvars=['HHID','itmcd']+list(sources.keys())

    if units:
        g=df.loc[:,valvars+['units']].groupby(['HHID','units','itmcd'])
        x=g.sum().sum(axis=1)
        x=x.reorder_levels(['itmcd','units','HHID']).unstack().T
    else:
        g=df.loc[:,valvars].groupby(['HHID','itmcd'])
        x=g.sum().sum(axis=1).unstack()


    x.replace(np.NaN,0,inplace=True)

    return x,defaultdict(int,{v:k for k,v in itemlabels.items()})

def get_labor_earnings(fn,sources,itmcd='itmcd',HHID='HHID',units=None,convert_categoricals=False,labels=None):
    """Labor earnings by person across sources.

    Takes as input a stata *.dta file fn, organized so that each 'row'
    corresponds to an individual's labor earnings from a particular job,
    uniquely identified by a string itmcd.

    Different sources and corresponding variable names 
    are specified in a dictionary sources; e.g,
    sources={'cash':'h01','in-kind':'h02'}.

    Ethan Ligon                                           April 2016
    """

    if type(fn)==list:
        files=[f for f in set(fn)]
        df=pd.read_stata(files.pop(), convert_categoricals=convert_categoricals)
        for f in files:
            current_df=pd.read_stata(f, convert_categoricals=convert_categoricals)
            df=pd.merge(df,current_df)
    else:
        sr=stata.StataReader(fn)
        df=pd.read_stata(fn, convert_categoricals=convert_categoricals)

    if type(HHID)==list:        
        df['HHID']=df[HHID[0]].apply(lambda x: unicode(x))
        for itm in HHID[1:]:
            df['HHID']=df['HHID']+'-'+df[itm].apply(lambda x: unicode(x))
        HHID = 'HHID'

    if type(itmcd)==tuple: # 2nd element of tuple is a function to apply
        df[itmcd[0]]=df[itmcd[0]].apply(itmcd[1])
        itmcd=itmcd[0]

    values = list(sources.values())
    df[values[0]]=df[values[0]].astype(np.float64)
    varnames = {v: k for k, v in sources.items()}
    varnames.update({HHID:'HHID',itmcd:'itmcd'})

    df.rename(columns=varnames,inplace=True)

    try:
        df['HHID']=df['HHID'].apply(lambda x: '%d' % int(float(x)))
    except ValueError:
        pass

    df['itmcd']=df['itmcd'].apply(lambda x: float(x))
    originalShape=df.shape
    df=df.loc[~np.isnan(df['itmcd']),:]
    if df.shape!=originalShape:
        warn("Warning: %d missing item codes dropped" % (originalShape[0]-df.shape[0]))
    df['itmcd']=df['itmcd'].apply(lambda x: int(x))
    if convert_categoricals:
        try:
            itemlabels=sr.value_labels()[itmcd].items()
        except KeyError:
            itemlabels=sr.value_labels()[itmcd.upper()].items()

        itemlabels = list(zip(*itemlabels))
        itemlabels = zip(itemlabels[1],itemlabels[0])

        # Deal with possibly poorly formed labels (e.g., those with unbalanced parentheses).
        e=[]
        for k,v in itemlabels:
            e.append((re.sub('\)|\(','',k),'$x_{%d}$' % v))

        itemlabels=dict(e)


        df.replace({'itmcd':{'\)|\(':''}},inplace=True)
    elif labels is not None:
        itemlabels=labels
        df.replace({'itmcd':itemlabels},inplace=True)
    else: # Use numerical labels
        itemlabels=set(df.itmcd)
        itemlabels={i:r'$x_{%d}$' % i for i in itemlabels}
        df.replace({'itmcd':itemlabels},inplace=True)

    # Group together earnings from different sources.
    valvars=['HHID','itmcd']+list(sources.keys())

    if units:
        g=df.loc[:,valvars+['units']].groupby(['HHID','units','itmcd'])
        x=g.sum().sum(axis=1)
        x=x.reorder_levels(['itmcd','units','HHID']).unstack().T
    else:
        g=df.loc[:,valvars].groupby(['HHID','itmcd'])
        x=g.sum().sum(axis=1).unstack()


    x.replace(np.NaN,0,inplace=True)

    return x

def get_food_prices(fn,farmgate=None,market=None,units=None,itmcd='itmcd',HHID='HHID',convert_categoricals=False):
    """
    Prices for different goods.

    Takes as input a stata *.dta file fn, organized so that each 'row' corresponds to the
    household's expenditures on a particular good, uniquely identified by a string itmcd.

    Different sources for the price of a given good sold in =units= are
    =farmgate= and =market=.  

    Ethan Ligon                                                                 March 2015
    """
    sr=stata.StataReader(fn)
    df=sr.data(convert_categoricals=convert_categoricals)

    df.rename(columns={HHID:'HHID',itmcd:'itmcd',farmgate:'farmgate',
                       market:'market',units:'units'},inplace=True)

    df['HHID']=df['HHID'].apply(lambda x: '%d' % int(float(x)))

    if convert_categoricals:
        try:
            itemlabels=sr.value_labels()[itmcd].items()
        except KeyError:
            itemlabels=sr.value_labels()[itmcd.upper()].items()

        itemlabels = list(zip(*itemlabels))
        itemlabels = zip(itemlabels[1],itemlabels[0])

        # Deal with possibly poorly formed labels (e.g., those with unbalanced parentheses).
        e=[]
        for k,v in itemlabels:
            e.append((re.sub('\)|\(','',k),'$x_{%d}$' % v))

        itemlabels=dict(e)


        df.replace({'itmcd':{'\)|\(':''}},inplace=True)
    else:
        itemlabels=set(df.itmcd)
        itemlabels={i:r'$x_{%d}$' % i for i in itemlabels}
        df.replace({'itmcd':itemlabels},inplace=True)

    # Group together consumption from different sources.
    valvars=['HHID','itmcd','farmgate','market','units']

    x=df.loc[:,valvars].set_index(['HHID','itmcd'])

    return x,defaultdict(int,{v:k for k,v in itemlabels.items()})

def get_asset_values(fn,count,value,itmcd,HHID='HHID',COUNT=False,convert_categoricals=True):
    """Number and value of reported non-durable assets.

    Takes as input a stata *.dta file fn, organized so that each 'row' corresponds to an
    asset type, identified by a string =itmcd=.

    Number of assets owned by anyone in the household is reported in the variable =count=, 
    while *total* value of those assets is reported in =value=.

    Optional argument =convert_categoricals= is passed to StataReader;
    this will obtain asset descriptions if True.  However, if True, a
    possible problem can arise if these labels are not unique.

    Ethan Ligon                                                                 October 2015
    """
    sr=stata.StataReader(fn)
    df=sr.data(convert_categoricals=convert_categoricals)

    df.rename(columns={HHID:'HHID',itmcd:'itmcd',count:'count',value:'value'},inplace=True)

    df['HHID']=df['HHID'].apply(lambda x: '%d' % int(float(x)))

    if convert_categoricals:
        try:
            key=sr.lbllist[sr.varlist.index(itmcd)]
            if len(key):
                itemlabels=sr.value_labels()[key].items()
            else:
                itemlabels=sr.value_labels()[itmcd].items()
        except KeyError:
            key=sr.lbllist[sr.varlist.index(itmcd.upper())]
            if len(key):
                itemlabels=sr.value_labels()[key].items()
            else:
                itemlabels=sr.value_labels()[itmcd.upper()].items()

        itemlabels=zip(list(zip(*itemlabels))[1],list(zip(*itemlabels))[0])

        # Deal with possibly poorly formed labels (e.g., those with unbalanced parentheses).
        e=[]
        for k,v in itemlabels:
            e.append((re.sub('\)|\(','',k),'$x_{%d}$' % v))

        itemlabels=dict(e)

        df.replace({'itmcd':{'\)|\(':''}},inplace=True)
    else:
        itemlabels=set(df.itmcd.dropna())
        itemlabels={i:r'$x_{%d}$' % i for i in itemlabels}
        df.replace({'itmcd':itemlabels},inplace=True)

    # Deal with request for count instead of value
    if COUNT:
        valvars=['HHID','itmcd','count']
    else:
        valvars=['HHID','itmcd','value','count']

    g=df.loc[:,valvars].groupby(['HHID','itmcd'])
    x=g.sum()
    x=x.unstack()

    x.replace(np.NaN,0,inplace=True)

    return x,defaultdict(int,{v:k for k,v in itemlabels.items()})


def get_household_roster(fn,sex='sex',sex_converter=None,age='age',months_spent='months_spent',HHID='HHID',months_converter=None, convert_categoricals=True,Age_ints=None):
    if type(fn)==list:
        files=[f for f in set(fn)]
        df=pd.read_stata(files.pop(), convert_categoricals=convert_categoricals)
        for f in files:
            current_df=pd.read_stata(f, convert_categoricals=convert_categoricals)
            df=pd.merge(df,current_df)
    else:
        df=pd.read_stata(fn, convert_categoricals=convert_categoricals)

    if type(HHID)==list:        
        df['HHID']=df[HHID[0]].apply(lambda x: unicode(x))
        for itm in HHID[1:]:
            df['HHID']=df['HHID']+'-'+df[itm].apply(lambda x: unicode(x))
        HHID = 'HHID'

    df=df.loc[:,[HHID, sex, age, months_spent]]      
    df.rename(columns={HHID:'HHID',sex:'sex',age:'age',months_spent:'months_spent'},inplace=True)

    if months_converter is not None:       
        df['months_spent']=df['months_spent'].apply(months_converter)

    if sex_converter is not None:
        df['sex']=df['sex'].apply(sex_converter)
    df['sex']=df['sex'].apply(lambda s: str(s[0]).lower())

    df['boys']=((df['sex']=='m') & (df['age']<18))
    df['girls']=((df['sex']=='f') & (df['age']<18))
    df['men']=((df['sex']=='m') & (df['age']>=18))
    df['women']=((df['sex']=='f') & (df['age']>=18))

    if Age_ints is None:
        Age_ints = ((0,1),(1,5),(5,10),(10,15),(15,20),(20,30),(30,50),(50,60),(60,100))

    for ages in Age_ints:
        df['Males %d-%d' % ages] = ((df['sex']=='m') & (df['age'] < ages[1]) & (df['age'] >= ages[0]))
        df['Females %d-%d' % ages] = ((df['sex']=='f') & (df['age'] < ages[1]) & (df['age'] >= ages[0]))

    try:
        df['HHID']=df['HHID'].apply(lambda x: '%d' % int(float(x)))
    except ValueError:
        pass

    # Aggregate household members
    valvars = ['HHID','girls','boys','men','women']
    valvars += ['Males %d-%d' % ages for ages in Age_ints]
    valvars += ['Females %d-%d' % ages for ages in Age_ints]

    if df['months_spent'].count()>0:
        g=df.loc[df['months_spent']>0,valvars].groupby(['HHID']) # Drop members never resident this year
    else: 
        g=df[valvars].groupby(['HHID']) # Aggregate at hh level.
    x=g.sum()

    return x

def get_household_variables(fn, HHID, variables, names, converters, convert_categoricals):
    # construct one dataframe from multiple files if necessary
    if type(fn)==list:
        files=[f for f in set(fn)]
        df=pd.read_stata(files.pop(), convert_categoricals=convert_categoricals)
        for f in files:
            current_df=pd.read_stata(f, convert_categoricals=convert_categoricals)
            df=pd.merge(df,current_df)
    else:
        df=pd.read_stata(fn, convert_categoricals=convert_categoricals)


    check_vars = lambda x,d: x in d.columns

    #do this so that if we modify variables it is only for this year and doesn't modify the original list
    variables=list(variables)

    for i in range(len(variables)):
        var = variables[i]
        if type(var)==list:
            valid=False
            for x in var:
                if check_vars(x, df):
                    variables[i] = x
                    valid=True
                    break
            if not valid:
                raise ValueError("None of " + str(var) + " is not a valid variable name -CK")
        else:
            if not check_vars(var, df):
                raise ValueError(var + " is not a valid variable name -CK")

    # construct unique household ID if needed
    if type(HHID)==list:        
        df['HHID']=df[HHID[0]].apply(lambda x: unicode(x))
        for itm in HHID[1:]:
            df['HHID']=df['HHID']+'-'+df[itm].apply(lambda x: unicode(x))
        HHID = 'HHID'      

    # rename the columns
    colnames = {HHID:'HHID'}
    for i in range(len(variables)):
        colnames[variables[i]] = names[i]
    df.rename(columns=colnames, inplace=True)

    #perform necessary conversions
    for i in range(len(converters)):
        if converters[i] is not None:
            df[names[i]] = df[names[i]].apply(converters[i])

    try:
        df['HHID']=df['HHID'].apply(lambda x: '%d' % int(float(x)))
    except ValueError:
        pass

    df = df.loc[:, ['HHID']+names]
    df.set_index('HHID', inplace=True)
    return df.loc[:, names] 

def get_household_identification_particulars(fn,HHID='HHID',urban='urban',urban_converter=None,region='region',region_converter=None,convert_categoricals=True,wealth_rank=None,wealth_rank_converter=None,happiness=None):

    if type(fn)==list:
        files=[f for f in set(fn)]
        df=pd.read_stata(files.pop(), convert_categoricals=convert_categoricals)
        for f in files:
            current_df=pd.read_stata(f, convert_categoricals=convert_categoricals)
            df=pd.merge(df,current_df)
    else:
        df=pd.read_stata(fn, convert_categoricals=convert_categoricals)

    if type(HHID)==list:        
        df['HHID']=df[HHID[0]].apply(lambda x: unicode(x))
        for itm in HHID[1:]:
            df['HHID']=df['HHID']+'-'+df[itm].apply(lambda x: unicode(x))
        HHID = 'HHID'

    df.rename(columns={HHID:'HHID',urban:'urban',region:'region'},inplace=True)

    if urban_converter is not None:
        df['urban']=df['urban'].apply(urban_converter)
    if region_converter is not None:
        df['region']=df['region'].apply(region_converter)

    df['region']=df['region'].apply(lambda s: str(s).lower())
    #df['urban']=df['urban'].apply(lambda s: str(s).lower())=='urban'
    df['urban']=df['urban'].apply(lambda x: x==1)

    #df['HHID']=df['HHID'].apply(lambda x: '%d' % int(float(x)))
    try:
        df['HHID']=df['HHID'].apply(lambda x: '%d' % int(float(x)))
    except ValueError:
        pass

    if wealth_rank is not None:
        columns=['urban','region','wealth rank','happiness']
        df['wealth rank']=df[wealth_rank].apply(wealth_rank_converter)
        df['happiness']=df[happiness]
    else:
        columns=['urban','region']

    df=df.loc[:,['HHID']+columns]
    #df=df.drop_duplicates()

    df.set_index('HHID',inplace=True)

    return df.loc[:,columns]

def make_date(day, month, year):
      if np.isnan(month) or np.isnan(year):
          return np.nan
      if np.isnan(day):
          return make_date(15, month, year)
      try:
          return pd.to_datetime(str(int(month)) + "-" + str(int(day)) + "-" + str(int(year)))
      except ValueError:
          return make_date(15, month, year)
