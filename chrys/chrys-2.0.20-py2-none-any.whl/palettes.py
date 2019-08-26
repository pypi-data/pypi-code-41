import math
import matplotlib as mpl
import numpy as np

from chrys.data.bokeh_palettes import BOKEH_PALETTES_DATA, BOKEH_PALETTES, BOKEH_CATEGORY_10, \
    BOKEH_CATEGORY_20, BOKEH_CATEGORY_20_B, BOKEH_CATEGORY_20_C, BOKEH_COLORBLIND, BOKEH_ACCENT, \
    BOKEH_DARK_2, BOKEH_PAIRED, BOKEH_PASTEL_1, BOKEH_PASTEL_2, BOKEH_SET_1, BOKEH_SET_2, \
    BOKEH_SET_3, BOKEH_YL_GN, BOKEH_YL_GN_BU, BOKEH_GN_BU, BOKEH_BU_GN, BOKEH_PU_BU_GN, \
    BOKEH_PU_BU, BOKEH_BU_PU, BOKEH_RD_PU, BOKEH_PU_RD, BOKEH_OR_RD, BOKEH_YL_OR_RD, \
    BOKEH_YL_OR_BR, BOKEH_PURPLES, BOKEH_BLUES, BOKEH_GREENS, BOKEH_ORANGES, BOKEH_REDS, \
    BOKEH_GREYS, BOKEH_PU_OR, BOKEH_BR_BG, BOKEH_PR_GN, BOKEH_PI_YG, BOKEH_RD_BU, BOKEH_RD_GY, \
    BOKEH_RD_YL_BU, BOKEH_SPECTRAL, BOKEH_RD_YL_GN, BOKEH_INFERNO, BOKEH_MAGMA, BOKEH_PLASMA, \
    BOKEH_VIRIDIS
from chrys.data.vega_palettes import VEGA_PALETTES_DATA, VEGA_PALETTES, VEGA_CATEGORY_10, \
    VEGA_CATEGORY_20, VEGA_CATEGORY_20_B, VEGA_CATEGORY_20_C, VEGA_TABLEAU_10, VEGA_TABLEAU_20, \
    VEGA_ACCENT, VEGA_DARK_2, VEGA_PAIRED, VEGA_PASTEL_1, VEGA_PASTEL_2, VEGA_SET_1, VEGA_SET_2, \
    VEGA_SET_3, VEGA_BLUES, VEGA_GREENS, VEGA_GREYS, VEGA_ORANGES, VEGA_PURPLES, VEGA_REDS, \
    VEGA_BLUE_GREEN, VEGA_BLUE_PURPLE, VEGA_GREEN_BLUE, VEGA_ORANGE_RED, VEGA_PURPLE_BLUE, \
    VEGA_PURPLE_BLUE_GREEN, VEGA_PURPLE_RED, VEGA_RED_PURPLE, VEGA_YELLOW_GREEN, \
    VEGA_YELLOW_ORANGE_BROWN, VEGA_YELLOW_ORANGE_RED, VEGA_BLUE_ORANGE, VEGA_BROWN_BLUE_GREEN, \
    VEGA_PURPLE_GREEN, VEGA_PURPLE_ORANGE, VEGA_RED_BLUE, VEGA_RED_GREY, VEGA_YELLOW_GREEN_BLUE, \
    VEGA_RED_YELLOW_BLUE, VEGA_RED_YELLOW_GREEN, VEGA_PINK_YELLOW_GREEN, VEGA_SPECTRAL, \
    VEGA_VIRIDIS, VEGA_MAGMA, VEGA_INFERNO, VEGA_PLASMA, VEGA_RAINBOW, VEGA_SINEBOW, VEGA_BROWNS, \
    VEGA_TEAL_BLUES, VEGA_TEALS, VEGA_WARM_GREYS, VEGA_GOLD_GREEN, VEGA_GOLD_ORANGE, \
    VEGA_GOLD_RED, VEGA_LIGHT_GREY_RED, VEGA_LIGHT_GREY_TEAL, VEGA_LIGHT_MULTI, VEGA_LIGHT_ORANGE, \
    VEGA_LIGHT_TEAL_BLUE, VEGA_DARK_BLUE, VEGA_DARK_GOLD, VEGA_DARK_GREEN, VEGA_DARK_MULTI, \
    VEGA_DARK_RED

BOKEH = 'bokeh'
MATPLOTLIB = 'matplotlib'
VEGA = 'vega'

DIVERGING_PALETTE_VENDORS = (
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_BLUE_ORANGE},
    {BOKEH: BOKEH_BR_BG, MATPLOTLIB: None, VEGA: VEGA_BROWN_BLUE_GREEN},
    {BOKEH: BOKEH_PR_GN, MATPLOTLIB: None, VEGA: VEGA_PURPLE_GREEN},
    {BOKEH: BOKEH_PI_YG, MATPLOTLIB: None, VEGA: VEGA_PINK_YELLOW_GREEN},
    {BOKEH: BOKEH_PU_OR, MATPLOTLIB: None, VEGA: VEGA_PURPLE_ORANGE},
    {BOKEH: BOKEH_RD_BU, MATPLOTLIB: None, VEGA: VEGA_RED_BLUE},
    {BOKEH: BOKEH_RD_GY, MATPLOTLIB: None, VEGA: VEGA_RED_GREY},
    {BOKEH: BOKEH_RD_YL_BU, MATPLOTLIB: None, VEGA: VEGA_RED_YELLOW_BLUE},
    {BOKEH: BOKEH_RD_YL_GN, MATPLOTLIB: None, VEGA: VEGA_RED_YELLOW_GREEN},
    {BOKEH: BOKEH_SPECTRAL, MATPLOTLIB: None, VEGA: VEGA_SPECTRAL},
)

QUALITATIVE_PALETTE_VENDORS = (
    {BOKEH: BOKEH_ACCENT, MATPLOTLIB: None, VEGA: VEGA_ACCENT},
    {BOKEH: BOKEH_CATEGORY_10, MATPLOTLIB: None, VEGA: VEGA_CATEGORY_10},
    {BOKEH: BOKEH_CATEGORY_20, MATPLOTLIB: None, VEGA: VEGA_CATEGORY_20},
    {BOKEH: BOKEH_CATEGORY_20_B, MATPLOTLIB: None, VEGA: VEGA_CATEGORY_20_B},
    {BOKEH: BOKEH_CATEGORY_20_C, MATPLOTLIB: None, VEGA: VEGA_CATEGORY_20_C},
    {BOKEH: BOKEH_DARK_2, MATPLOTLIB: None, VEGA: VEGA_DARK_2},
    {BOKEH: BOKEH_PAIRED, MATPLOTLIB: None, VEGA: VEGA_PAIRED},
    {BOKEH: BOKEH_PASTEL_1, MATPLOTLIB: None, VEGA: VEGA_PASTEL_1},
    {BOKEH: BOKEH_PASTEL_2, MATPLOTLIB: None, VEGA: VEGA_PASTEL_2},
    {BOKEH: BOKEH_SET_1, MATPLOTLIB: None, VEGA: VEGA_SET_1},
    {BOKEH: BOKEH_SET_2, MATPLOTLIB: None, VEGA: VEGA_SET_2},
    {BOKEH: BOKEH_SET_3, MATPLOTLIB: None, VEGA: VEGA_SET_3},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_TABLEAU_10},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_TABLEAU_20},
    {BOKEH: BOKEH_COLORBLIND, MATPLOTLIB: None, VEGA: None},
)

SEQUENTIAL_PALETTE_VENDORS = (
    # Single hue
    {BOKEH: BOKEH_BLUES, MATPLOTLIB: None, VEGA: VEGA_BLUES},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_TEAL_BLUES},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_TEALS},
    {BOKEH: BOKEH_GREENS, MATPLOTLIB: None, VEGA: VEGA_GREENS},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_BROWNS},
    {BOKEH: BOKEH_ORANGES, MATPLOTLIB: None, VEGA: VEGA_ORANGES},
    {BOKEH: BOKEH_REDS, MATPLOTLIB: None, VEGA: VEGA_REDS},
    {BOKEH: BOKEH_PURPLES, MATPLOTLIB: None, VEGA: VEGA_PURPLES},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_WARM_GREYS},
    {BOKEH: BOKEH_GREYS, MATPLOTLIB: None, VEGA: VEGA_GREYS},
    # Multiple hues
    {BOKEH: BOKEH_VIRIDIS, MATPLOTLIB: None, VEGA: VEGA_VIRIDIS},
    {BOKEH: BOKEH_MAGMA, MATPLOTLIB: None, VEGA: VEGA_MAGMA},
    {BOKEH: BOKEH_INFERNO, MATPLOTLIB: None, VEGA: VEGA_INFERNO},
    {BOKEH: BOKEH_PLASMA, MATPLOTLIB: None, VEGA: VEGA_PLASMA},
    {BOKEH: BOKEH_BU_GN, MATPLOTLIB: None, VEGA: VEGA_BLUE_GREEN},
    {BOKEH: BOKEH_BU_PU, MATPLOTLIB: None, VEGA: VEGA_BLUE_PURPLE},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_GOLD_GREEN},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_GOLD_ORANGE},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_GOLD_RED},
    {BOKEH: BOKEH_GN_BU, MATPLOTLIB: None, VEGA: VEGA_GREEN_BLUE},
    {BOKEH: BOKEH_OR_RD, MATPLOTLIB: None, VEGA: VEGA_ORANGE_RED},
    {BOKEH: BOKEH_PU_BU_GN, MATPLOTLIB: None, VEGA: VEGA_PURPLE_BLUE_GREEN},
    {BOKEH: BOKEH_PU_BU, MATPLOTLIB: None, VEGA: VEGA_PURPLE_BLUE},
    {BOKEH: BOKEH_PU_RD, MATPLOTLIB: None, VEGA: VEGA_PURPLE_RED},
    {BOKEH: BOKEH_RD_PU, MATPLOTLIB: None, VEGA: VEGA_RED_PURPLE},
    {BOKEH: BOKEH_YL_GN_BU, MATPLOTLIB: None, VEGA: VEGA_YELLOW_GREEN_BLUE},
    {BOKEH: BOKEH_YL_GN, MATPLOTLIB: None, VEGA: VEGA_YELLOW_GREEN},
    {BOKEH: BOKEH_YL_OR_BR, MATPLOTLIB: None, VEGA: VEGA_YELLOW_ORANGE_BROWN},
    {BOKEH: BOKEH_YL_OR_RD, MATPLOTLIB: None, VEGA: VEGA_YELLOW_ORANGE_RED},
    # For dark backgrounds
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_DARK_BLUE},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_DARK_GOLD},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_DARK_GREEN},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_DARK_MULTI},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_DARK_RED},
    # For light backgrounds
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_LIGHT_GREY_RED},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_LIGHT_GREY_TEAL},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_LIGHT_MULTI},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_LIGHT_ORANGE},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_LIGHT_TEAL_BLUE},
)

CYCLICAL_PALETTE_VENDORS = (
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_RAINBOW},
    {BOKEH: None, MATPLOTLIB: None, VEGA: VEGA_SINEBOW},
)

PALETTE_TO_VENDOR_MAP = {}
mappings = (DIVERGING_PALETTE_VENDORS, QUALITATIVE_PALETTE_VENDORS,
            SEQUENTIAL_PALETTE_VENDORS, CYCLICAL_PALETTE_VENDORS)
for mapping in mappings:
    for palette in mapping:
        for vendor, name in palette.iteritems():
            if name:
                PALETTE_TO_VENDOR_MAP[name] = vendor

# BOKEH_DIVERGING_PALETTE_NAMES = map(
#     lambda x: x[BOKEH], filter(lambda x: x[BOKEH], DIVERGING_PALETTE_VENDORS))
# BOKEH_QUALITATIVE_PALETTE_NAMES = map(
#     lambda x: x[BOKEH], filter(lambda x: x[BOKEH], QUALITATIVE_PALETTE_VENDORS))
# BOKEH_SEQUENTIAL_PALETTE_NAMES = map(
#     lambda x: x[BOKEH], filter(lambda x: x[BOKEH], SEQUENTIAL_PALETTE_VENDORS))
# BOKEH_CYCLICAL_PALETTE_NAMES = map(
#     lambda x: x[BOKEH], filter(lambda x: x[BOKEH], CYCLICAL_PALETTE_VENDORS))
BOKEH_CONTINUOUS_PALETTE_NAMES = [name for name, palette in BOKEH_PALETTES_DATA.iteritems()
                                  if filter(lambda x: x == 256, palette.keys())]

# VEGA_DIVERGING_PALETTE_NAMES = map(
#     lambda x: x[VEGA], filter(lambda x: x[VEGA], DIVERGING_PALETTE_VENDORS))
# VEGA_QUALITATIVE_PALETTE_NAMES = map(
#     lambda x: x[VEGA], filter(lambda x: x[VEGA], QUALITATIVE_PALETTE_VENDORS))
# VEGA_SEQUENTIAL_PALETTE_NAMES = map(
#     lambda x: x[VEGA], filter(lambda x: x[VEGA], SEQUENTIAL_PALETTE_VENDORS))
# VEGA_CYCLICAL_PALETTE_NAMES = map(
#     lambda x: x[VEGA], filter(lambda x: x[VEGA], CYCLICAL_PALETTE_VENDORS))
VEGA_CONTINUOUS_PALETTE_NAMES = [name for name, palette in VEGA_PALETTES_DATA.iteritems()
                                 if filter(lambda x: x == 256, palette.keys())]


def parse_palette_name(name):
    if name not in PALETTE_TO_VENDOR_MAP:
        raise ValueError('Palette name "{}" not recognized'.format(name))

    vendor = PALETTE_TO_VENDOR_MAP[name]
    palette = name[len(vendor)+1:]

    return (vendor, palette)


def _get_palette(name):
    vendor, _ = parse_palette_name(name)

    if vendor == BOKEH:
        return BOKEH_PALETTES_DATA[name]
    elif vendor == VEGA:
        return VEGA_PALETTES_DATA[name]
    else:
        raise ValueError('Vendor "{}" not recognized'.format(vendor))


def _is_continuous(name):
    vendor, _ = parse_palette_name(name)

    if vendor == BOKEH:
        return name in BOKEH_CONTINUOUS_PALETTE_NAMES
    elif vendor == VEGA:
        return name in VEGA_CONTINUOUS_PALETTE_NAMES
    else:
        raise ValueError('Vendor "{}" not recognized'.format(vendor))


def to_discrete_palette(palette, n=6, as_rgb=False):
    """
    Generate a list of discrete colors.

    Parameters
    ----------
    palette: list[str]
        A list of RGB hex color strings.
    n: int
        The size of the output palette to generate.
    as_rgb: bool
        Whether to return an RGB tuple `(r, g, b)`.

    Returns
    -------
    list[str]
        A list of RGB hex color strings or RGB tuples.
    """
    n_clamped = min(len(palette), max(1, n))
    result = palette[n_clamped][:n]

    if as_rgb:
        result = [mpl.colors.to_rgb(color) for color in result]

    return result


def to_continuous_palette(palette, n=6, as_rgb=False):
    """
    Generate a list of continuous colors.

    Parameters
    ----------
    palette: list[str]
        A list of RGB hex color strings.
    n: int
        The size of the output palette to generate.
    as_rgb: bool
        Whether to return an RGB tuple `(r, g, b)`.

    Returns
    -------
    list[str]
        A list of RGB hex color strings or RGB tuples.

    Adapted from Bokeh 1.3.4 https://bokeh.org (BSD-3-Clause)
    """
    if n > len(palette):
        raise ValueError(
            "Requested %(r)s colors, function can only return colors up to the base palette's"
            "length (%(l)s)" % dict(r=n, l=len(palette)))

    result = [palette[int(math.floor(i))] for i in np.linspace(0, len(palette)-1, num=n)]

    if as_rgb:
        result = [mpl.colors.to_rgb(color) for color in result]

    return result


def discrete_palette(name, n=6, as_rgb=False):
    return to_discrete_palette(_get_palette(name), n=n, as_rgb=as_rgb)


def continuous_palette(name, n=6, as_rgb=False):
    if not _is_continuous(name):
        raise ValueError('Generating continuous palettes of "{}" is not supported'.format(name))

    return to_continuous_palette(_get_palette(name)[256], n=n, as_rgb=as_rgb)
