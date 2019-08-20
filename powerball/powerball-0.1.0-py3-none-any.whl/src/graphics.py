from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.palettes import viridis
from bokeh.models.widgets import Slider
from bokeh.models import CustomJS, CustomJSFilter, CDSView, ColorBar
from bokeh.layouts import row, column
from bokeh.transform import linear_cmap
import sys


def bokeh_xy_sliders(outputMatrix):
    # outputArray is a 2d array composed of
    # a transposed array of unique group names, competitiveness scores,
    # comp p-values, lottery scores, and lottery p-values.
    # Scatterplot with sliders to filter significance
    output_file("scatterplot.html")

    TOOLS = ("hover,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset, save, tap")

    TOOLTIPS = [  # Displays on hover
        ("group", "@groups"),
        ("Comp P-value", "@compP{0.0000}"),
        ("Lottery P-value", "@lotP{0.0000}"),
        ("(x,y)", "(@x, @y)")
    ]

    # create a new plot with a title and axis labels
    p = figure(tools=TOOLS, title="Scatterplot", x_axis_label='Lottery Score',
               y_axis_label='Competitiveness', tooltips=TOOLTIPS,
               output_backend="webgl", toolbar_location="above")

    # Making sliders
    slider = Slider(start=0., end=1., value=1., step=.01,
                    title="Comp P-value Filter")
    slider2 = Slider(start=0., end=1., value=1., step=.01,
                     title="Lottery P-value Filter")

    try:
        colors = viridis(len(outputMatrix.uniqueGroups))
    except ValueError:
        print("Error: Bokeh can only display 256 colors. You requested ",
              len(outputMatrix.uniqueGroups),
              " Please try chart style 2 instead.")
    for i in range(len(outputMatrix.uniqueGroups)):
        # Assigning data to each point
        dx = [outputMatrix.lotScores[i]]
        dy = [outputMatrix.compScores[i]]
        dcompP = [outputMatrix.compPValues[i]]
        dlotP = [outputMatrix.lotPValues[i]]
        dgroup = [outputMatrix.uniqueGroups[i]]
        dcolor = colors[i]

        source = ColumnDataSource(data=dict(
            x=dx,
            y=dy,
            groups=dgroup,
            compP=dcompP,
            lotP=dlotP,
            size=[15],
            color=[dcolor]
        ))
        # Callback for when the slider is changed
        callback = CustomJS(args=dict(source=source), code="""
            source.change.emit();
        """)
        slider.js_on_change('value', callback)
        slider2.js_on_change('value', callback)

        # Custom Javascript boolean filters
        js_filter = CustomJSFilter(args=dict(slider=slider, source=source),
                                   code="""
            bools = []
            for (i = 0; i < source.data.x.length; i++) {
                if (source.data.compP[i] < slider.value) {
                    bools.push(true);
                }
                else {
                    bools.push(false);
                }
            }

            return bools;
        """)
        js_filter2 = CustomJSFilter(args=dict(slider=slider2, source=source),
                                    code="""
            bools = []
            for (i = 0; i < source.data.x.length; i++) {
                if (source.data.lotP[i] < slider.value) {
                    bools.push(true);
                }
                else {
                    bools.push(false);
                }
            }

            return bools;
        """)

        # Using those filters to change what data is displayed
        view = CDSView(source=source, filters=[js_filter, js_filter2])
        p.circle(x="x", y="y", source=source, size="size",
                 legend="groups", color="color", view=view)

    p.legend.click_policy = "hide"  # Click legend entry to hide that point

    sliders = column(slider, slider2)
    layout = row(p, sliders)

    show(layout)


def bokeh_xy_cmap(outputMatrix):
    # outputArray is a 2d array composed of
    # a transposed array of unique group names, competitiveness scores,
    # comp p-values, lottery scores, and lottery p-values.
    # Scatterplot where comp p-val is shown through size
    # and lot p-val is shown through a color map
    output_file("XY_chart.html")

    TOOLS = ("hover,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset, save, tap")

    TOOLTIPS = [
        ("group", "@groups"),
        ("Comp P-value", "@compP{0.0000}"),
        ("Lottery P-value", "@lotP{0.0000}"),
        ("(x,y)", "(@x, @y)")
    ]

    # create a new plot with a title and axis labels
    p = figure(tools=TOOLS, title="Scatterplot", x_axis_label='Lottery Score',
               y_axis_label='Competitiveness', tooltips=TOOLTIPS,
               output_backend="webgl", toolbar_location="above")

    mapper = linear_cmap(field_name='lotP',  # Color map based on lottery P-val
                         palette=list(reversed((viridis(20)))),
                         low=0.0, high=1.0)
    for i in range(len(outputMatrix.uniqueGroups)):
        dx = [outputMatrix.lotScores[i]]
        dy = [outputMatrix.compScores[i]]
        dcompP = [outputMatrix.compPValues[i]]
        dlotP = [outputMatrix.lotPValues[i]]
        dgroup = [outputMatrix.uniqueGroups[i]]

        source = ColumnDataSource(data=dict(
            x=dx,
            y=dy,
            groups=dgroup,
            compP=dcompP,
            lotP=dlotP,
            size=[size_clamp((1 - dcompP[0]) * 30)]
        ))
        p.circle(x="x", y="y", source=source, size="size",
                 legend="groups", color=mapper)

    p.legend.click_policy = "hide"

    # Bar showing what color corresponds to what
    color_bar = ColorBar(color_mapper=mapper['transform'], width=10,
                         location=(0, 0), title="Lottery P-value")

    p.add_layout(color_bar, 'left')

    show(p)


def bokeh_xy(outputMatrix):
    # outputArray is a 2d array composed of
    # a transposed array of unique group names, competitiveness scores,
    # comp p-values, lottery scores, and lottery p-values.
    # Scatterplot where lot and comp p-values are shown through size of points.
    output_file("XY_chart.html")

    TOOLS = ("hover,pan,wheel_zoom,zoom_in,zoom_out,box_zoom,reset, save, tap")

    TOOLTIPS = [
        ("group", "@groups"),
        ("Comp P-value", "@compP{0.0000}"),
        ("Lottery P-value", "@lotP{0.0000}"),
        ("(x,y)", "(@x, @y)")
    ]

    # create a new plot with a title and axis labels
    p = figure(tools=TOOLS, title="Scatterplot", x_axis_label='Lottery Score',
               y_axis_label='Competitiveness', tooltips=TOOLTIPS,
               output_backend="webgl", toolbar_location="above")

    try:
        colors = viridis(len(outputMatrix.uniqueGroups))
    except ValueError:
        print("Error: Bokeh can only display 256 colors. You requested ",
              len(outputMatrix.uniqueGroups),
              " Please try chart style 2 instead.")
    for i in range(len(outputMatrix.uniqueGroups)):
        dx = [outputMatrix.lotScores[i]]
        dy = [outputMatrix.compScores[i]]
        dcompP = [outputMatrix.compPValues[i]]
        dlotP = [outputMatrix.lotPValues[i]]
        dgroup = [outputMatrix.uniqueGroups[i]]
        dcolor = colors[i]

        source = ColumnDataSource(data=dict(
            x=dx,
            y=dy,
            groups=dgroup,
            compP=dcompP,
            lotP=dlotP,
            size=[size_clamp((1 - dcompP[0]) * (1 - dlotP[0]) * 50)],
            color=[dcolor]
        ))
        p.circle(x="x", y="y", source=source, size="size",
                 legend="groups", color="color")

    p.legend.click_policy = "hide"
    show(p)


def size_clamp(x):
    if x < 5:
        return 5
    if x > 50:
        return 50
    return x
