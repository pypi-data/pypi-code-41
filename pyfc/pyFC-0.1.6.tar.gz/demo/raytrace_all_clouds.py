import pyFC
import numpy as np
import matplotlib.pyplot as pl
import glob
from mpl_toolkits.axes_grid1 import ImageGrid

pl.ion()

ndir = 128
clouds_per_fig = 10
clouds_per_row = 2
fbasenm = 'cloud_1.0_128x128x128'

# Fractal cube object
fc = pyFC.LogNormalFractalCube(ni=ndir, nj=ndir, nk=ndir,
                               kmin=1., mean=1., sigma=np.sqrt(5.))

all_cubes = glob.glob(fbasenm+'-*.dbl')
ncubes = len(all_cubes)
nfigs = np.float(ncubes)/clouds_per_fig
all_cubes = np.array(all_cubes).reshape(nfigs, clouds_per_fig)

for ifig, figcubes in enumerate(all_cubes):

    panels_per_row = np.float(clouds_per_fig)/clouds_per_row
    fig = pl.figure(figsize=(6., panels_per_row))
    grid = ImageGrid(fig, 111,
                    nrows_ncols=(int(np.round(panels_per_row)), 6),
                    axes_pad=0.03,
                    )

    for icube, cube_name in enumerate(figcubes):
        fc.read_cube(cube_name)

        for ipanel in range(3):
            gr = grid[icube*3 + ipanel]
            pyFC.paint_raytrace(fc, gr, ax=ipanel)
            gr.set_yticks([]), gr.set_xticks([])
            gr.set_ylabel(''), gr.set_xlabel('')
            if ipanel == 0:
                pl.text(0.05, 0.9, cube_name, color='w',
                        fontsize=3, transform=gr.transAxes)

    #fig.savefig(fbasenm+'-'+str(ifig)+'.png', dpi=300, bbox_inches='tight')
    fig.savefig(fbasenm+'-'+str(ifig)+'.pdf', dpi=300, bbox_inches='tight')

