import pyFC
import numpy as np
import matplotlib.pyplot as pl

kmin = 20
nx = 128
ny = nx
nz = nx
sigma = 300
do_rho = True
do_vel = False


if do_rho:
    lnfc = pyFC.LogNormalFractalCube(nx, ny, nz, kmin=kmin)
    lnfc.gen_cube()
    lnfc.write_cube(fname='dens.flt', prec='single')

if do_vel:
    g1fc = pyFC.GaussianFractalCube(nx, ny, nz, kmin=kmin, mean=0, sigma=sigma)
    g2fc = pyFC.GaussianFractalCube(nx, ny, nz, kmin=kmin, mean=0, sigma=sigma)
    g3fc = pyFC.GaussianFractalCube(nx, ny, nz, kmin=kmin, mean=0, sigma=sigma)
    g1fc.gen_cube()
    g2fc.gen_cube()
    g3fc.gen_cube()
    pyFC.write_cube(g1fc, 'vel1.flt', prec='single')
    pyFC.write_cube(g2fc, 'vel2.flt', prec='single')
    pyFC.write_cube(g3fc, 'vel3.flt', prec='single')



# pl.ion()
pyFC.plot_field_stats(lnfc, 'log')
pl.gcf().savefig('lnfc_stats.png', dpi=300, bbox_inches='tight')
