# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 05:12:01 2019

@author: jittima
"""

import os
from IPython.display import Image
import wget
from cirpy import resolve
from jcamp import JCAMP_reader
import pandas as pd
import requests
from astroquery.nist import Nist
import astropy.units as u

def get_jdx(nistid, stype='IR'):
    """Download jdx file for the specified NIST ID, unless already downloaded."""
    NIST_URL = 'http://webbook.nist.gov/cgi/cbook.cgi'
    filepath = os.path.join(f'{nistid}-{stype}.jdx')
    if os.path.isfile(filepath):
        print(f'{nistid} {stype}: Already exists at {filepath}')
        return
    print(f'{nistid} {stype}: Downloading')
    response = requests.get(NIST_URL, params={'JCAMP': nistid, 'Type': stype, 'Index': 0})
    if response.text == '##TITLE=Spectrum not found.\n##END=\n':
        print(f'{nistid} {stype}: Spectrum not found')
        return
    #print('Saving %s' % filepath)
    with open(filepath, 'w') as file:
        file.write(response.text)
    return filepath


def get_cas(name):
    result = resolve(name,'cas')
    if result == None:
        print('nothing find, name of molecule must be Systematic IUPAC name')
        return 
    else:
        if isinstance(result,list):
            nb_char = 99999
            cas_name = ''
            for cas in result:
                if len(cas)<nb_char:
                    nb_char = len(cas)
                    cas_name = cas
            return cas_name
        else:        
            return result

def get_spectrum(cas,spectrum_type='IR'):
    #other type : 'UVVis'
    if spectrum_type != 'IR':
        spectrum_type = 'UVVis'
    cas0 = cas.replace('-','')
    nist = 'C'+cas0
    namefile = get_jdx(nist,stype=spectrum_type)
    if namefile == None:
        return 
    jcamp_dict = JCAMP_reader(namefile)
    if not 'xunits' in jcamp_dict:
        os.remove(namefile)
        print(f"\nresolve cas = {cas} failled")
        return
    result = pd.DataFrame({jcamp_dict['xunits']:jcamp_dict['x'],jcamp_dict['yunits']:jcamp_dict['y']})
    result.info = f'IR|{cas}'
    z = os.path.getsize(namefile)
    os.remove(namefile)
    if z>1024:
        print(f"\n{80*'='}\ncas={cas}\ncolumns names={result.columns}\n{80*'='}")
        return result
    else:
        print(f"\nresolve cas = {cas} failled")
        return

def mol_display(cas):
    cas0 = cas.replace('-','')
    name=f"Dcas{cas0}.jpg"
    url = f"https://webbook.nist.gov/cgi/cbook.cgi?Struct=C{cas0}&Type=Color"
    wget.download(url,name)
    z = os.path.getsize(name)
    if z>1024:
        return Image(name)
        os.remove(name)
    else:
        print(f"resolve cas = {cas} failled")
        os.remove(name)
        return

def get_element_stectrum(element,lower=400,upper=800,definition=0.01,rel_min=2):
    element = element.strip()
    if ' ' not in element:
        element += ' I'
    table = Nist.query(lower*u.nm,upper*u.nm,linename=element)
    A = pd.DataFrame({'lamb':table['Observed'],'rel':table['Rel.']})
    A['rel']=pd.to_numeric(A['rel'], errors='coerce')
    A.dropna(inplace=True)
    A['rel'] = A['rel'].astype(float)
    A['rel']=A['rel']*100/A['rel'].max()
    A.drop_duplicates(inplace=True)
    A['Dl']=A['lamb'].shift(-1)-A['lamb']
    A['Dl'].fillna(definition*1.1,inplace=True)
    A = A[A['Dl']>definition]
    A.drop(columns=['Dl'],inplace=True)
    A = A[A['rel']>rel_min]
    A.reset_index(inplace=True)
    A.drop(columns=['index'],inplace=True)
    A.info = f"spectrum: {element}"
    return A