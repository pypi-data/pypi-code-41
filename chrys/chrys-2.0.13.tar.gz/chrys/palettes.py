import math
import matplotlib as mpl
import numpy as np

from chrys.data.vega_palettes import VEGA_PALETTES

BOKEH = 'bokeh'
MATPLOTLIB = 'matplotlib'
VEGA = 'vega'

DIVERGING_PALETTES = (
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'blueorange'},
    {BOKEH: 'BrBG', MATPLOTLIB: None, VEGA: 'brownbluegreen'},
    {BOKEH: 'PRGn', MATPLOTLIB: None, VEGA: 'purplegreen'},
    {BOKEH: 'PiYG', MATPLOTLIB: None, VEGA: 'pinkyellowgreen'},
    {BOKEH: 'PuOr', MATPLOTLIB: None, VEGA: 'purpleorange'},
    {BOKEH: 'RdBu', MATPLOTLIB: None, VEGA: 'redblue'},
    {BOKEH: 'RdGy', MATPLOTLIB: None, VEGA: 'redgrey'},
    {BOKEH: 'RdYlBu', MATPLOTLIB: None, VEGA: 'redyellowblue'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'redyellowgreen'},
    {BOKEH: 'Spectral', MATPLOTLIB: None, VEGA: 'spectral'},
)

QUALITATIVE_PALETTES = (
    {BOKEH: 'Accent', MATPLOTLIB: None, VEGA: 'accent'},
    {BOKEH: 'Category10', MATPLOTLIB: None, VEGA: 'category10'},
    {BOKEH: 'Category20', MATPLOTLIB: None, VEGA: 'category20'},
    {BOKEH: 'Category20b', MATPLOTLIB: None, VEGA: 'category20b'},
    {BOKEH: 'Category20c', MATPLOTLIB: None, VEGA: 'category20c'},
    {BOKEH: 'Dark2', MATPLOTLIB: None, VEGA: 'dark2'},
    {BOKEH: 'Paired', MATPLOTLIB: None, VEGA: 'paired'},
    {BOKEH: 'Pastel1', MATPLOTLIB: None, VEGA: 'pastel1'},
    {BOKEH: 'Pastel2', MATPLOTLIB: None, VEGA: 'pastel2'},
    {BOKEH: 'Set1', MATPLOTLIB: None, VEGA: 'set1'},
    {BOKEH: 'Set2', MATPLOTLIB: None, VEGA: 'set2'},
    {BOKEH: 'Set3', MATPLOTLIB: None, VEGA: 'set3'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'tableau10'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'tableau20'},
)

SEQUENTIAL_PALETTES = (
    # Single hue
    {BOKEH: 'Blues', MATPLOTLIB: None, VEGA: 'blues'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'tealblues'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'teals'},
    {BOKEH: 'Greens', MATPLOTLIB: None, VEGA: 'greens'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'browns'},
    {BOKEH: 'Oranges', MATPLOTLIB: None, VEGA: 'oranges'},
    {BOKEH: 'Reds', MATPLOTLIB: None, VEGA: 'reds'},
    {BOKEH: 'Purples', MATPLOTLIB: None, VEGA: 'purples'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'warmgreys'},
    {BOKEH: 'Greys', MATPLOTLIB: None, VEGA: 'greys'},
    # Multiple hues
    {BOKEH: 'Viridis', MATPLOTLIB: None, VEGA: 'viridis'},
    {BOKEH: 'Magma', MATPLOTLIB: None, VEGA: 'magma'},
    {BOKEH: 'Inferno', MATPLOTLIB: None, VEGA: 'inferno'},
    {BOKEH: 'Plasma', MATPLOTLIB: None, VEGA: 'plasma'},
    {BOKEH: 'BuGn', MATPLOTLIB: None, VEGA: 'bluegreen'},
    {BOKEH: 'BuPu', MATPLOTLIB: None, VEGA: 'bluepurple'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'goldgreen'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'goldorange'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'goldred'},
    {BOKEH: 'GnBu', MATPLOTLIB: None, VEGA: 'greenblue'},
    {BOKEH: 'OrRd', MATPLOTLIB: None, VEGA: 'orangered'},
    {BOKEH: 'PuBuGn', MATPLOTLIB: None, VEGA: 'purplebluegreen'},
    {BOKEH: 'PuBu', MATPLOTLIB: None, VEGA: 'purpleblue'},
    {BOKEH: 'PuRd', MATPLOTLIB: None, VEGA: 'purplered'},
    {BOKEH: 'RdPu', MATPLOTLIB: None, VEGA: 'redpurple'},
    {BOKEH: 'YlGnBu', MATPLOTLIB: None, VEGA: 'yellowgreenblue'},
    {BOKEH: 'YlGn', MATPLOTLIB: None, VEGA: 'yellowgreen'},
    {BOKEH: 'YlOrBr', MATPLOTLIB: None, VEGA: 'yelloworangebrown'},
    {BOKEH: 'YlOrRd', MATPLOTLIB: None, VEGA: 'yelloworangered'},
    # For dark backgrounds
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'darkblue'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'darkgold'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'darkgreen'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'darkmulti'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'darkred'},
    # For light backgrounds
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'lightgreyred'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'lightgreyteal'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'lightmulti'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'lightorange'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'lighttealblue'},
)

CYCLICAL_PALETTES = (
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'rainbow'},
    {BOKEH: None, MATPLOTLIB: None, VEGA: 'sinebow'},
)

VEGA_DIVERGING_PALETTES = map(lambda x: x[VEGA], filter(lambda x: x[VEGA], DIVERGING_PALETTES))
VEGA_QUALITATIVE_PALETTES = map(lambda x: x[VEGA], filter(lambda x: x[VEGA], QUALITATIVE_PALETTES))
VEGA_SEQUENTIAL_PALETTES = map(lambda x: x[VEGA], filter(lambda x: x[VEGA], SEQUENTIAL_PALETTES))
VEGA_CYCLICAL_PALETTES = map(lambda x: x[VEGA], filter(lambda x: x[VEGA], CYCLICAL_PALETTES))
VEGA_CONTINUOUS_PALETTES = [name for name, palette in VEGA_PALETTES.iteritems()
                            if filter(lambda x: x == 256, palette.keys())]


def to_discrete_palette(palette, n=6, as_rgb=False):
    """
    Generate a list of discrete colours.

    Parameters
    ----------
    palette: list[str]
        A list of RGB hex colour strings.
    n: int
        The size of the output palette to generate.
    as_rgb: bool
        Whether to return an RGB tuple `(r, g, b)`.

    Returns
    -------
    list[str]
        A list of RGB hex colour strings or RGB tuples.
    """
    n_clamped = min(len(palette), max(1, n))
    result = palette[n_clamped][:n]

    if as_rgb:
        result = [mpl.colours.to_rgb(colour) for colour in result]

    return result


def to_continuous_palette(palette, n=6, as_rgb=False):
    """
    Generate a list of continuous colours.

    Parameters
    ----------
    palette: list[str]
        A list of RGB hex colour strings.
    n: int
        The size of the output palette to generate.
    as_rgb: bool
        Whether to return an RGB tuple `(r, g, b)`.

    Returns
    -------
    list[str]
        A list of RGB hex colour strings or RGB tuples.

    Adapted from Bokeh 1.3.4 https://bokeh.org (BSD-3-Clause)
    """
    if n > len(palette):
        raise ValueError(
            "Requested %(r)s colours, function can only return colours up to the base palette's"
            "length (%(l)s)" % dict(r=n, l=len(palette)))

    result = [palette[int(math.floor(i))] for i in np.linspace(0, len(palette)-1, num=n)]

    if as_rgb:
        result = [mpl.colors.to_rgb(colour) for colour in result]

    return result


def discrete_palette(provider, name, n=6, as_rgb=False):
    if provider == VEGA:
        palettes = VEGA_PALETTES
    else:
        raise ValueError('Provider {} not recognised'.format(provider))

    return to_discrete_palette(palettes[name], n=n, as_rgb=as_rgb)


def continuous_palette(provider, name, n=6, as_rgb=False):
    if provider == VEGA:
        palettes = VEGA_PALETTES
        continuous_palettes = VEGA_CONTINUOUS_PALETTES
    else:
        raise ValueError('Provider {} not recognised'.format(provider))

    if name not in continuous_palettes:
        raise ValueError('Generating continuous palettes of "{}" is not supported'.format(name))

    return to_continuous_palette(palettes[name][256], n=n, as_rgb=as_rgb)
