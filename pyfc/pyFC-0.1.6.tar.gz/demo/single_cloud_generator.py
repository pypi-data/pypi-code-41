import pyFC
import numpy as np
import matplotlib.pyplot as pl

pl.ion()

ndir = 128

kmin = 1.
low_ini = 1.
low_lim = 6.

# Fractal cube object
fc = pyFC.LogNormalFractalCube(ni=ndir, nj=ndir, nk=ndir,
                               kmin=kmin, mean=1, sigma=np.sqrt(5.))

# 1) Generate cube, center, and extract cloud.
#    Only accept if the lower threshold, low,
#    for the minimum value of low, for which
#    cloud doesn't touch boundary domain walls,
#    did not exceed low_lim.

low = 1.e30
while not low < low_lim:
    fc.gen_cube()

    pyFC.center(fc, mode='max', out='inplace')

    low = low_ini
    fc_ex = pyFC.extract_feature(fc, low=low)
    while pyFC.touches_boundary(fc_ex, bgv=1.e-5) and low < low_lim:
        low += 0.1
        fc_ex = pyFC.extract_feature(fc, low=low)

print('low1 = ' + str(low))


# 2) Improve centering

# Doesn't work well with mode='average' (maybe still a bug in there)
# but seems to work well with mode='av_max'
fc_ex, point = pyFC.center(fc_ex, mode='av_max', return_point=True, out='inplace')
pyFC.center(fc, mode='point', point=point, out='inplace')


# 3) Re-extract from improved centering fractal cube with improved centering

low = low_ini
fc_ex = pyFC.extract_feature(fc, low=low)
while pyFC.touches_boundary(fc_ex, bgv=1.e-5) and low < low_lim:
    low += 0.1
    fc_ex = pyFC.extract_feature(fc, low=low)

print('low2 = ' + str(low))


# 4) raytrace final extracted cube

pyFC.plot_raytrace(fc_ex, ax=0)
pyFC.plot_raytrace(fc_ex, ax=1)
pyFC.plot_raytrace(fc_ex, ax=2)


# 5) Save cube if good

accept = ''
while accept not in ['y', 'n']:
    accept = raw_input('Accept cloud? [y/n] ')

if accept == 'y':
    fc_ex.write_cube(fname='cloud.dbl')