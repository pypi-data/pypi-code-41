import re
from _purpose import purpose
from _method import method
from _basisset import basisset
from _output import output

class gms(purpose, method, basisset, output):
	__data__=''
	__purpose__=' $contrl runtyp=energy $end\n'
	__method__=' $contrl scftyp=rhf $end\n'
	__basis__=' $basis gbasis=sto ngauss=3 $end\n'
	
	def __init__(self, infile='mol.xyz'):
		an={
			'H': '     1.0     ',
			'He': '    2.0     ',
			'Li': '    3.0     ',
			'Be': '    4.0     ',
			'B': '     5.0     ',
			'C': '     6.0     ',
			'N': '     7.0     ',
			'O': '     8.0     ',
			'F': '     9.0     ',
			'Ne': '   10.0     ',
			'Na': '   11.0     ',
			'Mg': '   12.0     ',
			'Al': '   13.0     ',
			'Si': '   14.0     ',
			'P' :'    15.0     ',
			'S' :'    16.0     ',
			'Cl': '   17.0     ',
			'Ar': '   18.0     ',
			'K': '    19.0     ',
			'Ca': '   20.0     ',
			'Sc': '   21.0     ',
			'Ti': '   22.0     ',
			'V' :'    23.0     ',
			'Cr': '   24.0     ',
			'Mn': '   25.0     ',
			'Fe': '   26.0     ',
			'Co': '   27.0     ',
			'Ni': '   28.0     ',
			'Cu': '   29.0     ',
			'Zn': '   30.0     ',
			'Ga': '   31.0     ',
			'Ge': '   32.0     ',
			'As': '   33.0     ',
			'Se': '   34.0     ',
			'Br': '   35.0     ',
			'Kr': '   36.0     ',
			'Rb': '   37.0     ',
			'Sr': '   38.0     ',
			'Y' :'    39.0     ',
			'Zr': '   40.0     ',
			'Nb': '   41.0     ',
			'Mo': '   42.0     ',
			'Tc': '   43.0     ',
			'Ru': '   44.0     ',
			'Rh': '   45.0     ',
			'Pd': '   46.0     ',
			'Ag': '   47.0     ',
			'Cd': '   48.0     ',
			'In': '   49.0     ',
			'Sn': '   50.0     ',
			'Sb': '   51.0     ',
			'Te': '   52.0     ',
			'I' :'    53.0     ',
			'Xe': '   54.0     ',
			'Cs': '   55.0     ',
			'Ba': '   56.0     ',
			'La': '   57.0     ',
			'Hf': '   72.0     ',
			'Ta': '   73.0     ',
			'W' :'    74.0     ',
			'Re': '   75.0     ',
			'Os':'    76.0     ',
			'Ir':'    77.0     ',
			'Pt':'    78.0     ',
			'Au':'    79.0     ',
			'Hg':'    80.0     ',
			'Tl':'    81.0     ',
			'Pb':'    82.0     ',
			'Bi':'    83.0     ',
			'Po':'    84.0     ',
			'At':'    85.0     ',
			'Rn':'    86.0     ',
		}
		self.__data__=''
		header   =' $data\nTitle\nC1\n'
		self.__data__ +=header

		pat=re.compile('\s+')

		f=open(infile, 'r')
		f.readline()
		f.readline()
		for line in f:
			line=line.strip()
			(element,coor)=pat.split(line, 1)
			self.__data__+=element+an[element]+coor+'\n'
		self.__data__+=' $end\n'

		f.close()
