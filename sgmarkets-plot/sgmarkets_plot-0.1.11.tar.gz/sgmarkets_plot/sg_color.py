
import numpy as np
import matplotlib as mpl
import seaborn as sns

from matplotlib.colors import ListedColormap


main_colors = [
    (35, 85, 140),      # main
    (170, 135, 120),    # 2
    (189, 190, 196),    # 3
    (225, 105, 75),     # 4
    (0, 0, 0),          # 5
    (145, 146, 156),    # 6
    (230, 0, 40),       # 7
    (51, 51, 51),       # 8
    (245, 245, 245),    # 9
    (204, 204, 204),    # 10
    (0, 155, 205),      # 11
    (241, 113, 0),      # 12
    (185, 41, 45),      # 13
]

main_colors = np.array(main_colors) / 255
main_colors = [mpl.colors.to_rgba(c) for c in main_colors]

def lighten(c, a):
    """
    turn color (r, g, b, x) to (r, g, b, a)
    """
    return tuple(list(mpl.colors.to_rgb(c)) + [a])


secondary_colors = [lighten(c, 0.6) for c in main_colors]

SG_COLORS_MATPLOTLIB = main_colors + secondary_colors

SG_THEME_HIGHCHARTS = {
    'colors': [mpl.colors.to_hex(e) for e in SG_COLORS_MATPLOTLIB]
}

CMAP_SG_BuRd = sns.diverging_palette(248, 23, s=70.4, l=40,
                                     center='light',
                                     as_cmap=True)
CMAP_SG_RdBu = sns.diverging_palette(23, 248, s=70.4, l=40,
                                     center='light',
                                     as_cmap=True)
CMAP_SG_White = ListedColormap(['white'])
