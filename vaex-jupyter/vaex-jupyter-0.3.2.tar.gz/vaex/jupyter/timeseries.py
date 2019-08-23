import bqplot
import bqplot.pyplot as plt
import ipywidgets as widgets
import ipyvuetify as v
import matplotlib.cm
import numpy as np
import traitlets

import vaex
from .utils import debounced

_USE_DELAY = False

class TimeSeriesStatistic(traitlets.HasTraits):
    enabled = traitlets.Bool(True)

    def __init__(self, time_series, **kwargs):
        self.time_series = time_series
        super(TimeSeriesStatistic, self).__init__(**kwargs)

    def calculate(self):
        pass

    def add_mark(self):
        pass

class TimeSeriesStatisticScalar(TimeSeriesStatistic):
    def __init__(self, time_series, name='count', **kwargs):
        super(TimeSeriesStatisticScalar, self).__init__(time_series, **kwargs)
        self.name = name

    def calculate(self, progress=None):
        method = getattr(self.time_series.df, self.name)
        shape = self.time_series.shape
        limits = self.time_series.limits
        binby = self.time_series.binby
        # progressbar = vaex.utils.progressbars()
        result = method(self.time_series.y, delay=_USE_DELAY, binby=binby, limits=limits, shape=shape, progress=progress.add('statistic: ' + self.name))
        
        vaex.delayed(self.post_process_result)(result)

    def post_process_result(self, result):
        self.grid = result

class TimeSeriesStatisticOHLC(TimeSeriesStatistic):
    def __init__(self, time_series, name='OHLC', **kwargs):
        super(TimeSeriesStatisticOHLC, self).__init__(time_series, **kwargs)
        self.name = name

    def calculate(self, progress=None):
        shape = self.time_series.shape
        limits = self.time_series.limits
        binby = self.time_series.binby
        
        progress = vaex.utils.progressbars(progress)
        df = self.time_series.df
        t = self.time_series.time
        y = self.time_series.y
        open_result = df.first(y, t.astype('int64'), delay=_USE_DELAY, binby=binby, limits=limits, shape=shape, progress=progress.add('open: ' + self.name))
        close_result = df.first(y, -t.astype('int64'), delay=_USE_DELAY, binby=binby, limits=limits, shape=shape, progress=progress.add('open: ' + self.name))
        min_result = df.min(y, delay=_USE_DELAY, binby=binby, limits=limits, shape=shape, progress=progress.add('minmax: ' + self.name))
        max_result = df.max(y, delay=_USE_DELAY, binby=binby, limits=limits, shape=shape, progress=progress.add('minmax: ' + self.name))
        
        vaex.delayed(self.post_process_result)(open_result, close_result, min_result, max_result)

    def post_process_result(self, o, c, vmin, vmax):
        shape = o.shape + (4,)
        self.grid = np.zeros(shape)
        self.grid[...,0] = o
        self.grid[...,1] = vmin
        self.grid[...,2] = vmax
        self.grid[...,3] = c



class TimeSeries(traitlets.HasTraits):
    tmin = traitlets.Any()
    tmax = traitlets.Any()
    resolution = traitlets.Any()

    def __init__(self, df, time, y, resolution='W'):
        self.df = df
        self.resolution = resolution
        self.time = time
        self.tmin, self.tmax = self.df[str(self.time)].minmax()
        self.y = y
        self.stats = {}
        self.stats['mean'] = TimeSeriesStatisticScalar(self, name='mean')
        self.stats['min'] = TimeSeriesStatisticScalar(self, name='min', enabled=False)
        self.stats['max'] = TimeSeriesStatisticScalar(self, name='max', enabled=False)
        self.stats['ohlc'] = TimeSeriesStatisticOHLC(self, enabled=False)
        self.signal_compute = vaex.events.Signal()
        self.update_grid(immediate=True)

    def update_grid(self, immediate=False, progress=None, time_change=True):
        if time_change:
            for name, stat in self.stats.items():
                if not stat.enabled:
                    stat.grid = None
        if immediate:
            self._update_grid_immediate(progress=progress)
        else:
            self._update_grid(progress=progress)
    
    @debounced(.5, method=True)
    def _update_grid(self, progress=None):
        self._update_grid_immediate(progress=progress)

    def _update_grid_immediate(self, progress=None):
        self.resolution_type = 'M8[%s]' % self.resolution
        self.mainprogressbar = vaex.utils.progressbars(progress)
        dt = (self.tmax.astype(self.resolution_type) - self.tmin.astype(self.resolution_type))
        N = dt.astype(int).item() + 1
        self.time_centers = np.arange(self.tmin.astype(self.resolution_type), self.tmax.astype(self.resolution_type))
        self.df.add_variable('t_begin', self.tmin.astype(self.resolution_type),)
        self.binby = self.df['%s - t_begin' % self.time.astype(self.resolution_type)].astype('int32')
        self.shape = N
        self.limits = [-0.5, N-0.5]
        for name, stat in self.stats.items():
            if stat.enabled:
                stat.calculate(progress=self.mainprogressbar)
        self.df.execute()
        self.signal_compute.emit()


import cycler
colormap = matplotlib.cm.get_cmap('tab10')
def next_color():
    i = 0
    while True:
        r, g, b, a = [int(k*255) for k in colormap((i % 10)/10)]
        yield '#{:02x}{:02x}{:02x}'.format(r, g, b).upper()
        i += 1
next_color = next_color()
# widgets.trait_types.Color.validate = lambda *x: True
# colors = [colormap(i) for i in range(10)]
# print(colors)
# color_cycler = iter(cycler.cycler(color=colors))

def create_date_picker(initialDate, label, on_change):
    menu1 = v.Menu(v_model=False, offset_y=True, transition="scale-transition", close_on_content_click=False, 
                   children=[
                        v.TextField(v_model=initialDate, label=label, prepend_icon="event", slot="activator"),
                        v.DatePicker(v_model=initialDate)
                   ]
                  )

    def setter(value):
        value = str(value.astype('M8[D]'))
        menu1.children[0].v_model = menu1.children[1].v_model = value

    def on_input(widget, event, data):
        menu1.v_model = False
        menu1.children[0].v_model = menu1.children[1].v_model
        on_change(np.datetime64(menu1.children[1].v_model))
    

    menu1.children[1].on_event('input', on_input)
    return menu1, setter


class BqplotTimeSeries(traitlets.HasTraits):
    def __init__(self, time_series, figure=None, figure_key=None):
        self.time_series = time_series

        self._dirty = False
        self.figure_key = figure_key
        self.figure = figure
        self.signal_limits = vaex.events.Signal()
        self._cleanups = []
        self.lines = []
        self.lines_min = []
        self.lines_max = []
        self.lines_ohlc = []
        self.lines_map = {
            'mean': self.lines,
            'min': self.lines_min,
            'max': self.lines_max,
            'ohlc': self.lines_ohlc
        }
        self.create_widget()
        self.time_series.observe(self._on_datetime_changed, ['tmin', 'tmax'])
        self.time_series.observe(self._on_change_resolution, 'resolution')
        self._set_line_visibilities()
        self.time_series.signal_compute.connect(self._after_compute)
        for name, stat in self.time_series.stats.items():
            def _check(change, stat=stat):
                if stat.enabled and stat.grid is None:
                    self.time_series.update_grid(immediate=False, progress=self._progress_callback, time_change=False)
            stat.observe(_check, 'enabled')
    
    def _on_change_resolution(self, change):
        self.time_series.update_grid(immediate=False, progress=self._progress_callback)

    def _on_datetime_changed(self, *ignore):
        self.time_series.update_grid(immediate=False, progress=self._progress_callback)

    def _set_line_visibilities(self):
        for i, (name, stat) in enumerate(self.time_series.stats.items()):
            for j, line in enumerate(self.lines_map[name]):
                line.visible = stat.enabled and self.widget_switches_lines[j].v_model #j in self.widget_which_lines.v_model

    
    def _after_compute(self):
        for i, y in enumerate(self.time_series.y):
            stat = self.time_series.stats['mean']
            if stat.enabled:
                line = self.lines[i]
                line.x = self.time_series.time_centers
                line.y = stat.grid[i]
            stat = self.time_series.stats['mean']
            if stat.enabled:
                line = self.lines_max[i]
                line.x = self.time_series.time_centers
                line.y = stat.grid[i]
            stat = self.time_series.stats['min']
            if stat.enabled:
                line = self.lines_min[i]
                line.x = self.time_series.time_centers
                line.y = stat.grid[i]
            stat = self.time_series.stats['ohlc']
            if stat.enabled:
                line = self.lines_ohlc[i]
                line.x = self.time_series.time_centers
                line.y = stat.grid[i]
        self.start_date_setter(self.time_series.tmin)
        self.end_date_setter(self.time_series.tmax)
        self.scales['x'].min = self.time_series.tmin
        self.scales['x'].max = self.time_series.tmax

    def update_image(self, rgb_image):
        src = vaex.image.rgba_to_url(rgb_image)
        self.image.src = src
        # self.scale_x.min, self.scale_x.max = self.limits[0]
        # self.scale_y.min, self.scale_y.max = self.limits[1]
        self.image.x = self.scale_x.min
        self.image.y = self.scale_y.max
        self.image.width = self.scale_x.max - self.scale_x.min
        self.image.height = -(self.scale_y.max - self.scale_y.min)

    def create_lines(self):
        for i, y in enumerate(self.time_series.y):
            color = next(next_color)
            y_values = self.time_series.stats['mean'].grid[i]
            line = plt.plot(self.time_series.time_centers, y_values, colors=[color],
            display_legend=True, labels=[str(y)])
            # traitlets.link((self.time_series.stats['mean'], 'enabled'), (line, 'visible'))
            self.lines.append(line)

            stat = self.time_series.stats['min']
            line = bqplot.Lines(x=self.time_series.time_centers, colors=[color], scales=self.scales)
            if stat.enabled:
                line.y = stat.grid[i]
            self.lines_min.append(line)

            stat = self.time_series.stats['max']
            line = bqplot.Lines(x=self.time_series.time_centers, colors=[color], scales=self.scales)
            if stat.enabled:
                line.y = stat.grid[i]
            self.lines_max.append(line)

            stat = self.time_series.stats['ohlc']
            line = bqplot.OHLC(x=self.time_series.time_centers, stroke=color, scales=self.scales)
            if stat.enabled:
                line.y = stat.grid[i]
            self.lines_ohlc.append(line)

            # y_values = self.time_series.stats['ohlc'].grid[i]
            # line = bqplot.OHLC(x=self.time_series.time_centers, y=y_values.tolist(),
            #  scales=self.scales,
            #  stroke=color)
            # # traitlets.link((self.time_series.stats['mean'], 'enabled'), (line, 'visible'))
            # self.lines_ohlc.append(line)
        self.figure.marks = self.lines + self.lines_min + self.lines_max + self.lines_ohlc

    def create_widget(self):#, output, plot, dataset, limits):
        # self.plot = plot
        # self.output = output
        # self.dataset = dataset
        # self.limits = self.
        self.scale_x = bqplot.DateScale(min=self.time_series.tmin, max=self.time_series.tmax)
        self.scale_y = bqplot.LinearScale() #min=limits[1][0], max=limits[1][1])
        # self.scale_rotation = bqplot.LinearScale(min=0, max=1)
        # self.scale_size = bqplot.LinearScale(min=0, max=1)
        # self.scale_opacity = bqplot.LinearScale(min=0, max=1)
        self.scales = {'x': self.scale_x, 'y': self.scale_y}
        
        # , 'rotation': self.scale_rotation,
        #                'size': self.scale_size, 'opacity': self.scale_opacity}

        margin = {'bottom': 30, 'left': 60, 'right': 0, 'top': 0}
        self.figure = plt.figure(self.figure_key, fig=self.figure, scales=self.scales, fig_margin=margin)
        self.figure.layout.min_width = '900px'
        plt.figure(fig=self.figure)
        self.create_lines()


        # self.figure.padding_y = 0
        # # x = np.arange(0, 10)
        # # y = x ** 2
        # # self._fix_scatter = s = plt.scatter(x, y, visible=False, rotation=x, scales=self.scales)
        # # self._fix_scatter.visible = False
        # # self.scale_rotation = self.scales['rotation']
        # src = ""  # vaex.image.rgba_to_url(self._create_rgb_grid())
        # # self.scale_x.min, self.scale_x.max = self.limits[0]
        # # self.scale_y.min, self.scale_y.max = self.limits[1]
        # self.image = bqplot_image.Image(scales=self.scales, src=src, x=self.scale_x.min, y=self.scale_y.max,
        #                                    width=self.scale_x.max - self.scale_x.min, height=-(self.scale_y.max - self.scale_y.min))
        # self.figure.marks = self.figure.marks + [self.image]
        # # self.figure.animation_duration = 500
        # self.figure.layout.width = '100%'
        # self.figure.layout.max_width = '500px'
        # self.scatter = s = plt.scatter(x, y, visible=False, rotation=x, scales=self.scales, size=x, marker="arrow")
        # self.panzoom = bqplot.PanZoom(scales={'x': [self.scale_x], 'y': [self.scale_y]})
        # self.figure.interaction = self.panzoom
        # # self.figure.axes[0].label = self.x
        # # self.figure.axes[1].label = self.y

        # self.scale_x.observe(self._update_limits, "min")
        # self.scale_x.observe(self._update_limits, "max")
        # self.scale_y.observe(self._update_limits, "min")
        # self.scale_y.observe(self._update_limits, "max")
        # self.observe(self._update_scales, "limits")

        # self.image.observe(self._on_view_count_change, 'view_count')
        self.control_widget = widgets.VBox()

        self.brush_interval_selector = bqplot.interacts.BrushIntervalSelector(scale=self.scales['x'])
        def sync_ui_to_model(*ignore):
            if self.brush_interval_selector.selected is not None and\
               len(self.brush_interval_selector.selected) and\
               self.brush_interval_selector.brushing is False:
                selected = self.brush_interval_selector.selected
                self.brush_interval_selector.selected = []
                self.figure.interaction = None
                self.figure.interaction = self.brush_interval_selector
                with self.time_series.hold_trait_notifications():
                    self.time_series.tmin, self.time_series.tmax = selected
        self.brush_interval_selector.observe(sync_ui_to_model, 'brushing')
        self.figure.interaction = self.brush_interval_selector


        def on_date_change_begin(date):
            self.time_series.tmin = date
        def on_date_change_end(date):
            self.time_series.tmax = date
        self.start_date, self.start_date_setter = create_date_picker("2018-08-22", "Start date", on_date_change_begin)
        self.end_date, self.end_date_setter = create_date_picker("2019-08-22", "End date", on_date_change_end)
        self.start_date_setter(self.time_series.tmin)
        self.end_date_setter(self.time_series.tmax)

        self.button_datetime_reset = v.Btn(flat=True, children=[v.Icon(children=['home'])])
        self.tmin0, self.tmax0 = self.time_series.tmin, self.time_series.tmax
        def reset_datetime(*ignore):
            with self.time_series.hold_trait_notifications():
                self.time_series.tmin, self.time_series.tmax = self.tmin0, self.tmax0
        self.button_datetime_reset.on_event('click', reset_datetime)


        self.widget_which_resolution = v.BtnToggle(v_model=1, multiple=False, children=[
            v.Btn(children=["Day"]),
            v.Btn(children=["Week"]),
            v.Btn(children=["Month"]),
            v.Btn(children=["Year"])])
        def _on_resolution_change(*ignore):
            resolutions = ['D', 'W', 'M', 'Y']
            self.time_series.resolution = resolutions[self.widget_which_resolution.v_model]
        for btn in self.widget_which_resolution.children:
            btn.vstyle = 'text-transform: none;'
        self.widget_which_resolution.observe(_on_resolution_change, 'v_model')


        self.widget_which_stat = v.BtnToggle(v_model=[0], multiple=True, children=[
            v.Btn(children=["Mean"]),
            v.Btn(children=["Min"]),
            v.Btn(children=["Max"]),
            v.Btn(children=["OLHC"])])
        for i, (name, stat) in enumerate(self.time_series.stats.items()):
            stat.enabled = i in self.widget_which_stat.v_model
        def _on_stat_change(*ignore):
            for i, (name, stat) in enumerate(self.time_series.stats.items()):
                stat.enabled = i in self.widget_which_stat.v_model
            self._set_line_visibilities()
        for btn in self.widget_which_stat.children:
            btn.vstyle = 'text-transform: none;'
        self.widget_which_stat.observe(_on_stat_change, 'v_model')

        # self.widget_which_lines = v.BtnToggle(v_model=list(range(len(self.time_series.y))), multiple=True, children=[
        #     v.Switch(children=[str(expr)]) for expr in self.time_series.y])
        self.widget_switches_lines = [
            v.Switch(label=str(expr).title(), v_model=True,
                color=self.lines[i].colors[0]
            ) for i, expr in enumerate(self.time_series.y)
        ]
        
        def _on_which_lines_change(*ignore):
            self._set_line_visibilities()
        for switch in self.widget_switches_lines:
            switch.observe(_on_which_lines_change, 'v_model')
        # for btn in self.widget_which_lines.children:
        #     btn.vstyle = 'text-transform: none;'
        # self.widget_which_lines.observe(_on_which_lines_change, 'v_model')


        # self.widget_which_lines = v.BtnToggle(v_model=list(range(len(self.time_series.y))), multiple=True, children=[
        #     v.Btn(children=[str(expr)]) for expr in self.time_series.y])
        # def _on_which_lines_change(*ignore):
        #     self._set_line_visibilities()
        # for btn in self.widget_which_lines.children:
        #     btn.vstyle = 'text-transform: none;'
        # self.widget_which_lines.observe(_on_which_lines_change, 'v_model')

        # self.widget_progress = v.ProgressLinear(v_model=0)
        self.widget_progress = widgets.FloatProgress(value=0)


        self.control_widget.children = [
            v.Layout(column=True, children=[
                    v.Layout(pa_2=True, column=False, children=[
                        v.Html(tag="div", vstyle="margin-right: 10px", children=[self.widget_which_stat]),
                        self.widget_which_resolution,
                        # self.widget_which_lines,
                        ]
                    ),
                    v.Layout(pa_2=True, children=self.widget_switches_lines)
                ]
            )
        ]


        self.date_tools = v.Layout(align_center=True, children=[self.start_date, self.end_date, self.button_datetime_reset])

        self.widget = widgets.VBox(children=[self.control_widget, self.date_tools, self.figure, self.widget_progress])

        self.widget_progress.layout.width = '99%'
        self.figure.layout.width = '95%'
        # self.create_tools()

    def _progress_callback(self, fraction):
        # print(fraction)
        if fraction == 1.0:
            self.widget_progress.value = 0
        else:
            self.widget_progress.value = 100*fraction
        return True

    def _update_limits(self, *args):
        with self.output:
            limits = copy.deepcopy(self.limits)
            limits[0:2] = [[scale.min, scale.max] for scale in [self.scale_x, self.scale_y]]
            self.limits = limits

    def _update_scales(self, *args):
        with self.scale_x.hold_trait_notifications():
            self.scale_x.min = self.limits[0][0]
            self.scale_x.max = self.limits[0][1]
        with self.scale_y.hold_trait_notifications():
            self.scale_y.min = self.limits[1][0]
            self.scale_y.max = self.limits[1][1]
        # self.update_grid()

    def create_tools(self):
        self.tools = []
        tool_actions = []
        tool_actions_map = {u"pan/zoom": self.panzoom}
        tool_actions.append(u"pan/zoom")

        # self.control_widget.set_title(0, "Main")
        self._main_widget = widgets.VBox()
        self._main_widget_1 = widgets.HBox()
        self._main_widget_2 = widgets.HBox()
        if 1:  # tool_select:
            self.brush = bqplot.interacts.BrushSelector(x_scale=self.scale_x, y_scale=self.scale_y, color="green")
            tool_actions_map["select"] = self.brush
            tool_actions.append("select")

            self.brush.observe(self.update_brush, ["selected", "selected_x"])
            # fig.interaction = brush
            # callback = self.dataset.signal_selection_changed.connect(lambda dataset: update_image())
            # callback = self.dataset.signal_selection_changed.connect(lambda *x: self.update_grid())

            # def cleanup(callback=callback):
            #    self.dataset.signal_selection_changed.disconnect(callback=callback)
            # self._cleanups.append(cleanup)

            self.button_select_nothing = widgets.Button(description="", icon="trash-o")
            self.button_reset = widgets.Button(description="", icon="refresh")
            import copy
            self.start_limits = copy.deepcopy(self.limits)

            def reset(*args):
                self.limits = copy.deepcopy(self.start_limits)
                with self.scale_y.hold_trait_notifications():
                    self.scale_y.min, self.scale_y.max = self.limits[1]
                with self.scale_x.hold_trait_notifications():
                    self.scale_x.min, self.scale_x.max = self.limits[0]
                self.plot.update_grid()
            self.button_reset.on_click(reset)

            self.button_select_nothing.on_click(lambda *ignore: self.plot.select_nothing())
            self.tools.append(self.button_select_nothing)
            self.modes_names = "replace and or xor subtract".split()
            self.modes_labels = "replace and or xor subtract".split()
            self.button_selection_mode = widgets.Dropdown(description='select', options=self.modes_labels)
            self.tools.append(self.button_selection_mode)

            def change_interact(*args):
                # print "change", args
                self.figure.interaction = tool_actions_map[self.button_action.value]

            tool_actions = ["pan/zoom", "select"]
            # tool_actions = [("m", "m"), ("b", "b")]
            self.button_action = widgets.ToggleButtons(description='', options=[(action, action) for action in tool_actions],
                                                       icons=["arrows", "pencil-square-o"])
            self.button_action.observe(change_interact, "value")
            self.tools.insert(0, self.button_action)
            self.button_action.value = "pan/zoom"  # tool_actions[-1]
            if len(self.tools) == 1:
                tools = []
            # self._main_widget_1.children += (self.button_reset,)
            self._main_widget_1.children += (self.button_action,)
            self._main_widget_1.children += (self.button_select_nothing,)
            # self._main_widget_2.children += (self.button_selection_mode,)
        self._main_widget.children = [self._main_widget_1, self._main_widget_2]
        self.control_widget.children += (self._main_widget,)
        self._update_grid_counter = 0  # keep track of t
        self._update_grid_counter_scheduled = 0  # keep track of t

    def _on_view_count_change(self, *args):
        with self.output:
            logger.debug("views: %d", self.image.view_count)
            if self._dirty and self.image.view_count > 0:
                try:
                    logger.debug("was dirty, and needs an update")
                    self.update()
                finally:
                    self._dirty = False

    # @debounced(0.5, method=True)
    # def update_brush(self, *args):
    #     with self.output:
    #         if not self.brush.brushing:  # if we ended brushing, reset it
    #             self.figure.interaction = None
    #         if self.brush.selected is not None:
    #             (x1, y1), (x2, y2) = self.brush.selected
    #             mode = self.modes_names[self.modes_labels.index(self.button_selection_mode.value)]
    #             self.plot.select_rectangle(x1, y1, x2, y2, mode=mode)
    #         else:
    #             self.dataset.select_nothing()
    #         if not self.brush.brushing:  # but then put it back again so the rectangle is gone,
    #             self.figure.interaction = self.brush
import IPython.display
def plot(df, time, y, display=True):
    time_series = TimeSeries(df, df[str(time)], [df[str(k)] for k in y])
    plot = BqplotTimeSeries(time_series)
    if display:
        IPython.display.display(plot.widget)
    return plot
