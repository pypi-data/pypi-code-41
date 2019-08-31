from pyasp import *
from clyngor.as_pyasp import TermSet, Atom

elem = 'plop'
weight = 2
cofactors_pyasp = Term('cofactor', ["\""+elem+"\"",+weight])
cofactors_clyngor = Atom('cofactor', ["\""+elem+"\"",+weight])

print(cofactors_pyasp)
print(cofactors_clyngor)
