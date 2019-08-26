from cycler import cycler
import spectra


def get_theme(mode="light", strong_grid=False, palette="default"):
    """
    Return a matplotlib theme as a dictionary.

    Parameters
    ----------
    mode : 'light', 'grey', dark'
        the theme's mode
    strong_grid : bool, optional
        whether to use strong grid lines
    palette : 'default', 'light', 'dark'
        whether to use the default color palette, or the light/dark
        versions

    Returns
    -------
    theme : dict
        the dictionary holding the theme parameters

    Examples
    --------
    >>> from matplotlib import pyplot as plt
    >>> import numpy as np

    >>> with plt.style.context(get_theme(mode="dark")):
    >>>    plt.plot(np.random.random(size=10))
    """
    assert mode in ["dark", "grey", "light"]
    assert palette in ["default", "light", "dark"]

    if mode == "light":
        BG_COLOR = "#ffffff"
        TEXT_COLOR = "#353d42"
        LABEL_COLOR = "#666666"
        GRID_COLOR = "#666666" if strong_grid else "#d8d8d8"
    elif mode == "grey":
        BG_COLOR = "#353d42"
        TEXT_COLOR = LABEL_COLOR = "#ffffff"
        GRID_COLOR = "#ffffff" if strong_grid else "#4e5254"
    elif mode == "dark":
        BG_COLOR = "#121516"
        TEXT_COLOR = LABEL_COLOR = "#ffffff"
        GRID_COLOR = "#ffffff" if strong_grid else "#4e5254"

    # figure out the palette of colors
    colors = [
        "#2176d2",
        "#58c04d",
        "#f3c613",
        "#f99300",
        "#f40000",
        "#25cef7",
        "#d233ff",
    ]
    if palette == "dark":
        colors = [spectra.html(color).darken(10).hexcode for color in colors]
    if palette == "light":
        colors = [spectra.html(color).brighten(10).hexcode for color in colors]

    theme = {}

    # Axes
    theme["axes.spines.left"] = False
    theme["axes.spines.bottom"] = False
    theme["axes.spines.top"] = False
    theme["axes.spines.right"] = False
    theme["axes.facecolor"] = BG_COLOR
    theme["axes.grid"] = True
    theme["axes.grid.axis"] = "both"
    theme["axes.grid.which"] = "major"
    theme["axes.labelcolor"] = TEXT_COLOR
    theme["axes.labelpad"] = 4.0
    theme["axes.labelsize"] = 12.0
    theme["axes.labelweight"] = "bold"
    theme["axes.linewidth"] = 0.75
    theme["axes.prop_cycle"] = cycler("color", colors)
    theme["axes.titlepad"] = 6.0
    theme["axes.titlesize"] = 18.0
    theme["axes.titleweight"] = "bold"
    theme["axes.unicode_minus"] = True
    theme["axes.xmargin"] = 0.1
    theme["axes.ymargin"] = 0.1

    # Grid
    theme["grid.alpha"] = 1.0
    theme["grid.color"] = GRID_COLOR
    theme["grid.linestyle"] = "-"
    theme["grid.linewidth"] = 0.75

    # Figure
    theme["figure.dpi"] = 300
    theme["figure.frameon"] = True
    theme["figure.facecolor"] = BG_COLOR
    theme["figure.edgecolor"] = BG_COLOR
    theme["figure.figsize"] = [6.4, 4.8]
    theme["figure.subplot.left"] = 0.10
    theme["figure.subplot.right"] = 0.95
    theme["figure.subplot.bottom"] = 0.07

    # Font
    theme["font.size"] = 12.0
    theme["font.family"] = "Open Sans"

    # Legend
    theme["legend.framealpha"] = 1.0
    theme["legend.edgecolor"] = "none"

    # Lines
    theme["lines.linewidth"] = 4.0
    theme["lines.solid_capstyle"] = "round"
    theme["lines.dash_capstyle"] = "round"
    theme["lines.dashed_pattern"] = 3.7, 2.3
    theme["lines.dashdot_pattern"] = 6.4, 2.3, 1.5, 2.3
    theme["lines.dotted_pattern"] = 1, 1.65
    theme["lines.scale_dashes"] = True

    # Patch
    theme["patch.linewidth"] = 0

    # Savefig
    theme["savefig.edgecolor"] = BG_COLOR
    theme["savefig.facecolor"] = BG_COLOR

    # Text
    theme["text.color"] = TEXT_COLOR

    # Xticks
    theme["xtick.alignment"] = "center"
    theme["xtick.bottom"] = True
    theme["xtick.color"] = LABEL_COLOR
    theme["xtick.direction"] = "out"
    theme["xtick.labelbottom"] = True
    theme["xtick.labelsize"] = 12
    theme["xtick.labeltop"] = False
    theme["xtick.major.bottom"] = True
    theme["xtick.major.pad"] = 3.5
    theme["xtick.major.size"] = 0.0
    theme["xtick.major.top"] = True
    theme["xtick.major.width"] = 0.75
    theme["xtick.minor.bottom"] = True
    theme["xtick.minor.pad"] = 3.4
    theme["xtick.minor.size"] = 0.0
    theme["xtick.minor.top"] = True
    theme["xtick.minor.visible"] = False
    theme["xtick.minor.width"] = 0.6
    theme["xtick.top"] = False

    # Yticks
    theme["ytick.alignment"] = "bottom"
    theme["ytick.color"] = LABEL_COLOR
    theme["ytick.direction"] = "in"
    theme["ytick.labelleft"] = True
    theme["ytick.labelright"] = False
    theme["ytick.labelsize"] = 12.0
    theme["ytick.left"] = True
    theme["ytick.major.left"] = True
    theme["ytick.major.pad"] = 3.5
    theme["ytick.major.right"] = True
    theme["ytick.major.size"] = 0.0
    theme["ytick.major.width"] = 0.75
    theme["ytick.minor.left"] = True
    theme["ytick.minor.pad"] = 3.4
    theme["ytick.minor.right"] = True
    theme["ytick.minor.size"] = 0.0
    theme["ytick.minor.visible"] = False
    theme["ytick.minor.width"] = 0.6
    theme["ytick.right"] = False

    return theme
