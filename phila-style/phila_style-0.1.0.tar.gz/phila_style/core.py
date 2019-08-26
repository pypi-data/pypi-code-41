import spectra


def get_digital_standards():
    """
    Return a dictionary holding the City of Philadelphia's
    color palette as defined in the Digital Standards.

    Notes
    -----
    See https://standards.phila.gov/guidelines/design-development/brand-elements/color-palette/
    """
    palette = {}
    palette["dark-ben-franklin"] = "#0f4d90"
    palette["ben-franklin-blue"] = "#2176d2"
    palette["light-ben-franklin"] = "#96c9ff"
    palette["electric-blue"] = "#25cef7"
    palette["bell-yellow"] = "#f3c613"
    palette["flyers-orange"] = "#f99300"
    palette["kelly-drive-green"] = "#58c04d"
    palette["light-bell"] = "#ffefa2"
    palette["light-red"] = "#fed0d0"
    palette["light-kelly-drive"] = "#b9f2b1"
    palette["light-blue"] = "#DAEDFE"
    palette["phanatic-green"] = "#3a833c"
    palette["love-park-red"] = "#cc3000"
    palette["pride-purple"] = "#9400c6"
    palette["black"] = "#000000"
    palette["dark-gray"] = "#444444"
    palette["medium-gray"] = "#a1a1a1"
    palette["sidewalk"] = "#cfcfcf"
    palette["ghost-gray"] = "#f0f0f0"

    return palette


def get_default_palette():
    """
    Return the default color palette, which slightly 
    tweaks the Digital Standards for better flexibility on 
    light/dark backgrounds.
    """
    palette = {}

    # the standard set of colors
    palette["blue"] = "#2176d2"
    palette["green"] = "#58c04d"
    palette["yellow"] = "#f3c613"
    palette["orange"] = "#f99300"
    palette["red"] = "#f40000"
    palette["electric-blue"] = "#25cef7"
    palette["purple"] = "#d233ff"

    # greys
    palette["almost-grey"] = "#353d42"
    palette["dark-grey"] = "#2a3135"
    palette["medium-grey"] = "#666666"
    palette["light-grey"] = "#868b8e"

    # black/white
    palette["black"] = "#000000"
    palette["white"] = "#ffffff"
    palette["almost-black"] = "#121516"
    palette["almost-white"] = "#f5f5f5"

    return palette


def get_light_palette():
    """
    Return the default light color palette.
    """
    palette = get_default_palette()
    for color in [
        "blue",
        "green",
        "yellow",
        "orange",
        "red",
        "electric-blue",
        "purple",
    ]:
        palette[color] = spectra.html(palette[color]).brighten(10).hexcode

    return palette


def get_dark_palette():
    """
    Return the default dark color palette.
    """
    palette = get_default_palette()
    for color in [
        "blue",
        "green",
        "yellow",
        "orange",
        "red",
        "electric-blue",
        "purple",
    ]:
        palette[color] = spectra.html(palette[color]).darken(10).hexcode

    return palette


def get_color_ramp(midpoint, palette="default", N=9, as_cmap=False):
    """
    Return a color ramp with the specified midpoint color and 
    number of colors.

    Color maps were generated using the chroma.js tool.

    Notes
    -----
    This can return either a list of hex strings, or a 
    `matplotlib.colors.ListedColorMap` object if `as_cmap` is True.

    Parameters
    ----------
    midpoint : str
        the name of a color in the specified palette, e.g., 'purple', 
        'blue', 'electric-blue'
    palette : 'default', 'light', 'dark', optional
        the color palette to use if midpoint is specified as a color name
    N : int, optional
        the number of colors in the returned ramp
    as_cmap : bool, optional
        whether to return a `matplotlib.colors.ListedColorMap` object
    
    Returns
    -------
    ramp : list of str, or `matplotlib.colors.ListedColorMap` object
        the color ramp, either as a list of hex code strings, or 
        a `matplotlib.colors.ListedColorMap` object
    """
    # default color palette
    assert palette in ["default", "light", "dark"]

    # The mid/end points of the color ramp
    colors = {
        "blue": {
            "default": ["#253757", "#6584c0", "#d3daef"],
            "dark": ["#242d4e", "#6c7ab6", "#d2d4e9"],
            "light": ["#363f61", "#7989c9", "#dddff4"],
        },
        "green": {
            "default": ["#30512a", "#65a25a", "#d8ebd3"],
            "dark": ["#234821", "#569b51", "#d1e6cd"],
            "light": ["#365b32", "#66ab60", "#dcf1d8"],
        },
        "yellow": {
            "default": ["#64531f", "#b99a3a", "#faebce"],
            "dark": ["#574a1a", "#ac933b", "#f2e6ca"],
            "light": ["#685d27", "#b7a443", "#fbf1d3"],
        },
        "orange": {
            "default": ["#674119", "#ca843a", "#fde1c9"],
            "dark": ["#5a3917", "#bd7e3f", "#f5dcc7"],
            "light": ["#694b22", "#c69044", "#fde7cf"],
        },
        "red": {
            "default": ["#672013", "#de5b3f", "#ffd1c4"],
            "dark": ["#5a1d11", "#cd5d43", "#f9cdc2"],
            "light": ["#6a291b", "#de644a", "#ffd5ca"],
        },
        "electric-blue": {
            "default": ["#2a5664", "#52a4bd", "#d8edf6"],
            "dark": ["#274c5a", "#569bb5", "#d5e7f0"],
            "light": ["#395f66", "#66abb8", "#dff3f7"],
        },
        "purple": {
            "default": ["#592767", "#bf63d8", "#f2d4f8"],
            "dark": ["#521f5d", "#b95ccc", "#eecff3"],
            "light": ["#662e67", "#cf66d0", "#fad8f8"],
        },
    }

    # make the midpoint is specified
    allowed = list(colors)
    if midpoint not in allowed:
        raise ValueError(
            f"If specified as as color name, allowed values are: {allowed}"
        )

    # Create the ramp
    ramp = [
        color.hexcode for color in spectra.Scale(colors[midpoint][palette]).range(N)
    ]

    if as_cmap:
        from matplotlib.colors import ListedColormap

        ramp = ListedColormap(ramp, name=f"custom-{midpoint}")

    return ramp

