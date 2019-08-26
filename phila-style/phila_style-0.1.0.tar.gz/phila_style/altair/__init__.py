# Color schemes and defaults
palette = dict(
    black="#000000",
    white="#ffffff",
    grey="#353d42",
    default="#2176d2",
    accent="#f40000",
    highlight="#f3c613",
    schemes={
        "category-7": [
            "#2176d2",
            "#58c04d",
            "#f3c613",
            "#f99300",
            "#f40000",
            "#25cef7",
            "#d233ff",
        ],
        "sequential-7": [
            "#ffffb2",
            "#fed976",
            "#feb24c",
            "#fd8d3c",
            "#fc4e2a",
            "#e31a1c",
            "#b10026",
        ],
        "diverging-7": [
            "#b2182b",
            "#ef8a62",
            "#fddbc7",
            "#f7f7f7",
            "#d1e5f0",
            "#67a9cf",
            "#2166ac",
        ],
    },
)


def get_theme():
    """
    A theme for Altair that uses the City of Philadelphia Digital Standards.

    Inspired by the La Times Altair theme.

    Example
    -------
    >>> from phila_style.altair as get_theme, palette
    >>> import altair as alt
    >>> alt.themes.register('phila', get_theme)
    >>> alt.themes.enable('phila')
    """
    # Headline stuff
    headlineFontSize = 22
    headlineFontWeight = "normal"
    headlineFont = "Open Sans"

    # Titles for axes and legends and such
    titleFont = "Open Sans"
    titleFontWeight = "normal"
    titleFontSize = 14

    # Labels for ticks and legend entries and such
    labelFont = "Open Sans"
    labelFontSize = 12
    labelFontWeight = "normal"

    return dict(
        config=dict(
            view=dict(width=800, height=450),
            background=palette["white"],
            title=dict(
                anchor="start",
                font=headlineFont,
                fontColor=palette["grey"],
                fontSize=headlineFontSize,
                fontWeight=headlineFontWeight,
            ),
            arc=dict(fill=palette["default"]),
            area=dict(fill=palette["default"]),
            line=dict(stroke=palette["default"], strokeWidth=3),
            path=dict(stroke=palette["default"]),
            rect=dict(fill=palette["default"]),
            shape=dict(stroke=palette["default"]),
            bar=dict(fill=palette["default"]),
            point=dict(stroke=palette["default"]),
            symbol=dict(fill=palette["default"], size=30),
            axis=dict(
                titleFont=titleFont,
                titleFontSize=titleFontSize,
                titleFontWeight=titleFontWeight,
                labelFont=labelFont,
                labelFontSize=labelFontSize,
                labelFontWeight=labelFontWeight,
            ),
            axisX=dict(labelAngle=0, labelPadding=4, tickSize=3),
            axisY=dict(
                labelBaseline="middle",
                maxExtent=45,
                minExtent=45,
                tickSize=2,
                titleAlign="left",
                titleAngle=0,
                titleX=-45,
                titleY=-11,
            ),
            legend=dict(
                titleFont=titleFont,
                titleFontSize=titleFontSize,
                titleFontWeight=titleFontWeight,
                symbolType="square",
                labelFont=labelFont,
                labelFontSize=labelFontSize + 1,
            ),
            range=dict(
                category=palette["schemes"]["category-7"],
                diverging=palette["schemes"]["diverging-7"],
                heatmap=palette["schemes"]["sequential-7"],
                ordinal=palette["schemes"]["sequential-7"],
                ramp=palette["schemes"]["sequential-7"],
            ),
        )
    )
