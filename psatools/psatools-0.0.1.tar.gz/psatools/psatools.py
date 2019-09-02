""" Useful tools for electrical power engineering
List of tools:
calci
calcp
calcs
calcc
calcir
calcpf
 """
import math
import numpy

       
def calci(MVA, kV):
    """ Calculates three phase I in amps from MVA and kV"""
    return round(MVA / (kV * 3**0.5) * 1000, 2)
    
def calcpf(MW, kA, kV):
    """ Calculates three phase pf from MW, kV and kA"""
    round(MW / (kV * kA * 3**0.5),2)

    
#@unit    
def calcp(kA, kV, cosphi = 1.0):
    """ Calculates three phase P in MW from kA and kV
    takes an optional input power factor""" 
    return 3**(0.5) * kV * kA * cosphi    
    
def calcs(MW,Mvar):
    """ Calculates S from MW and Mvar"""
    return (MW**2 + Mvar**2)**0.5
    
def calcc(I,V):
    """Returns capacitance based on charging current."""
    return (3**(1/2) * I) / (V * 2* math.pi * 50)
    
def calcir(init,final,startyear,endyear):
    """Calculates growth rate based on a start value and end value and a start
    year and end year.  Assumed annual compounding."""
    return (math.exp(math.log(final/init)/(endyear-startyear))-1)
    
def main():
    pass
    
    
if __name__ == '__main__':
    main()    
    
    