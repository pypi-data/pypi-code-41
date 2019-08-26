#!/usr/bin/env python
# -*- coding: utf-8 -*-


from pymetrick import version
__author__ = version.__author__
__copyright__ = version.__copyright__
__license__ = version.__license__
__version__ = version.__version__
__date__ = '2012-09-21'
__credits__ = ''
__text__ = 'Tratamiento fiscal, bancos y monedas'
__file__ = 'exchequer.py'

#--- CHANGES ------------------------------------------------------------------
# 2012-09-21 v0.01 PL: - First version

import sys, os, imp
import string
import re
from urllib.request import urlopen

def validate_EORI(iso_country_2='ES',nif=''):

    if iso_country_2=='ES':
        _nif = " ".join(re.findall("[a-zA-Z0-9]+",nif)).upper().replace(' ','')
        ''' NIF 8 digitos + 1 caracter o 1 caracter + 7 digitos + 1 caracter
            CIF 7 digitos + 1 caracter de control
        '''
        ALPHA_NIF = 'TRWAGMYFPDXBNJZSQVHLCKE'
        '''Entidades juridicas con animo de lucro'''
        ALPHA_CIF_a = 'JABCDEFGHI'
        '''Personas juridicas sin animo de lucro '''
        ALPHA_CIF_b = 'NPQRSW'
        '''Personas fisicas extranjeras, menores de 14 o no residentes'''
        ALPHA_CIF_c = 'KLMXYZ'
        '''Comprobar si es un NIF'''
        if len(_nif)>0:
            if _nif[0] in '0123456789':
                _nif_number = ' '.join(re.findall("[0-9]+",_nif))
                ctrl = (int(_nif_number))%23
                __nif = _nif_number+ALPHA_NIF[ctrl]
                if __nif.strip().upper() == _nif:
                    __nif = _nif_number.zfill(8)+ALPHA_NIF[ctrl]
                    return __nif
            else:
                '''Comprobar si es una Persona fisica extranjera, menor de 14 o no residente'''
                if _nif[0] in ALPHA_CIF_c:
                    _nif_number = ' '.join(re.findall("[0-9]+",_nif))
                    '''Si contiene 7 digitos y comienza por X Y Z, sustituir X Y Z por 0 1 2'''
                    ctrl = int(_nif_number)
                    if len(_nif_number) == 7 and len(_nif) == 9:
                        if _nif[0] in 'XYZ':
                            n = {'X':'0','Y':'1','Z':'2'}
                            ctrl = int(n[_nif[0]]+_nif_number)
                    ctrl = ctrl%23
                    __nif = _nif[0]+_nif_number+ALPHA_NIF[ctrl]
                    if __nif.strip().upper() == _nif:
                        __nif = _nif[0]+_nif_number.zfill(7)+ALPHA_NIF[ctrl]
                        return __nif
                '''Comprobar si es una Persona juridica sin animo de lucro'''
                if _nif[0] in ALPHA_CIF_a:
                    if 7<len(_nif)<=9:
                        _nif_number = ' '.join(re.findall("[0-9]+",_nif))
                        '''obtener posicion par e impar'''
                        n = 0
                        n_ctrl = 0
                        for n in range(0,len(_nif_number)-1):
                            if (n+1)%2 == 0:
                                n_ctrl += int(_nif_number[n])
                            else:
                                n_ctrl += (int(_nif_number[n])*2%10)+int(int(_nif_number[n])*2/10)
                        ctrl = n_ctrl%10
                        ctrl = 10 - ctrl
                        if ctrl>9:
                            ctrl = 0
                        __nif = _nif[0]+_nif_number[0:7]+repr(ctrl)
                        if __nif.strip().upper() == _nif:
                            __nif = _nif[0]+_nif_number[0:7].zfill(7)+repr(ctrl)
                            return __nif
                '''Comprobar si es una Persona juridica sin animo de lucro'''
                if _nif[0] in ALPHA_CIF_b:
                    if 7<len(_nif)<=9:
                        _nif_number = ' '.join(re.findall("[0-9]+",_nif))
                        '''obtener posicion par e impar'''
                        n = 0
                        n_ctrl = 0
                        for n in range(0,len(_nif_number)-1):
                            if (n+1)%2 == 0 == 0:
                                n_ctrl += int(_nif_number[n])
                            else:
                                n_ctrl += (int(_nif_number[n])*2%10)+int(int(_nif_number[n])*2/10)
                        ctrl = n_ctrl%10
                        ctrl = 10 - ctrl
                        __nif = _nif[0]+_nif_number[0:7]+chr(ctrl)
                        if __nif.strip().upper() == _nif:
                            __nif = _nif[0]+_nif_number[0:7].zfill(7)+chr(ctrl)
                            return __nif
        # identificacion fiscal ES incorrecta
        return ''.join(['&',_nif])
    else:
        # identificacion fiscal ajena
        return nif




def currencyExchangeEUR(dest=None):
    """Obtiene lista diaria de cambios desde BCE en formato XML
    y extrae informacion de cambio de monedas a partir de 1 EUR
    """
    currencyList = list()
    currencyDict = dict()
    url = "http://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml"
    currency = urlopen(url).read()
    buscar = b"currency\s\'[\w{3}]\s\'?rate=\'(\d{4,7}.)\'/>"
    l_currency = re.findall(b"currency='[\w]{3}'\srate='[\d]{1,5}[.]?[\d]{1,5}'",currency)
    for m in l_currency:
        currencyList = list(m.decode().replace('currency=','').replace(' rate','').replace("'",'').split('='))
        currencyDict[currencyList[0]]=float(currencyList[1])
    if dest is not None and dest in currencyDict:
        return currencyDict[dest]
    else:
        return 0





#esto es un test
if __name__ == '__main__' :
    print ('''copyright {0}'''.format( __copyright__))
    print ('''license {0}'''.format( __license__))
    print ('''version {0}'''.format( __version__))
    if len(sys.argv) < 2:
        sys.stderr.write("for help use -h o --help")
    elif sys.argv[1]=='-h' or sys.argv[1]=='--help':
        print ('''
        Tratamiento de identificaciones fiscales\n\n
        y gestion de monedas                        ''')


