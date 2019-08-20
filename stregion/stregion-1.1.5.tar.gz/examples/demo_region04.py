try:
    from astropy.io import fits as pyfits
except ImportError:
    from astropy.io import fits as pyfits

import matplotlib.pyplot as plt
import stregion

import math

if 1:

    reg_name = "test04_img.reg"


    ax = plt.subplot(111)
    ax.set_xlim(600, 1100)
    ax.set_ylim(600, 1100)
    ax.set_aspect(1)

    r = stregion.open(reg_name)

    patch_list, text_list = r.get_mpl_patches_texts()
    for p in patch_list:
        ax.add_patch(p)
    for t in text_list:
        ax.add_artist(t)

    plt.draw()
    plt.show()
