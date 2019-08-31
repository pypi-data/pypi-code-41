
__all__ = [
    'BarChart',
    'Chart',
    'LineChart',
    'PieChart'
]


class Chart:
    """
    A generic chart.
    """

    def __init__(self, chart_type, **kwargs):

        # The chart arguments
        self._chart_args = {
            'chart_type': chart_type,
            **kwargs
        }

    def __getattr__(self, name):

        if '_chart_args' in self.__dict__:
            return self.__dict__['_chart_args'].get(name, None)

        raise AttributeError(
            f"'{self.__class__.__name__}' has no attribute '{name}'"
        )

    def __getitem__(self, name):
        return self.__dict__['_chart_args'][name]

    def __contains__(self, name):
        return name in self.__dict__['_chart_args']

    def get(self, name, default=None):
        return self.__dict__['_chart_args'].get(name, default)

    def to_json_type(self):
        return {k: v for k, v in self._chart_args.items() if v is not None}


class BarChart(Chart):

    def __init__(
        self,
        data,
        labels,
        font_size=None,
        orientation='vertical',
        show_legend=False,
        size=None,
        spacing=0.1,
        x_axis_label=None,
        y_axis_label=None,
        x_axis_formatter=None,
        y_axis_formatter=None,
        **kwargs
    ):

        super().__init__(
            'bar',
            data=data,
            labels=labels,
            font_size=font_size,
            orientation=orientation,
            show_legend=show_legend,
            size=size,
            spacing=spacing,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            x_axis_formatter=x_axis_formatter,
            y_axis_formatter=y_axis_formatter,
            **kwargs
        )


class LineChart(Chart):

    def __init__(
        self,
        data,
        labels,
        font_size=None,
        show_legend=False,
        size=None,
        x_axis_label=None,
        y_axis_label=None,
        x_axis_formatter=None,
        y_axis_formatter=None,
        **kwargs
    ):

        super().__init__(
            'line',
            data=data,
            labels=labels,
            font_size=font_size,
            show_legend=show_legend,
            size=size,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            x_axis_formatter=x_axis_formatter,
            y_axis_formatter=y_axis_formatter,
            **kwargs
        )


class PieChart(Chart):

    def __init__(
        self,
        data,
        doughnut=False,
        font_size=None,
        inner_radius=0,
        show_labels=True,
        show_legend=False,
        size=None,
        value_color=None,
        **kwargs
    ):

        super().__init__(
            'pie',
            data=data,
            doughnut=doughnut,
            font_size=font_size,
            inner_radius=inner_radius,
            show_labels=show_labels,
            show_legend=show_legend,
            size=size,
            value_color=value_color,
            **kwargs
        )

