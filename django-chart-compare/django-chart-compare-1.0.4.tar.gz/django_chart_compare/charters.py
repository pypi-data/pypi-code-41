import pandas as pd
from bokeh.plotting import figure
from bokeh.palettes import Spectral11 as pallette
from bokeh.models import Range1d
from bokeh.embed import components
from django.template.defaulttags import register
import numpy as np
import time


class Compare(object):

    df = None
    select_dict = None
    name_dict = None
    col_dict = None

    def __init__(self, model, request, **kwargs):
        assert hasattr(model, 'Name'), "Model must have a Name attribute."
        assert hasattr(model, 'df'), "Model must have a df associated with it. This should return a Pandas DataFrame."
        self.model = model
        self.get_comp_df(request, kwargs)
        self.get_comp_dicts(request, kwargs['pk'], kwargs['slug'])

    @staticmethod
    def name_col(schedule_name, column_name):
        return "{schedule_name} - {column_name}".format(schedule_name=schedule_name, column_name=column_name)

    def process_request(self, request, kwargs):
        self.get_comp_dicts(request, kwargs['pk'], kwargs['slug'])
        self.make_data_chart()

    def get_comp_df(self, request, kwargs):
        df = pd.DataFrame()
        pk_list = [kwargs['pk']] + kwargs['slug'].split('-')
        for pk in pk_list:
            other_df = self.model.objects.get(pk=pk).df
            schedule_name = self.model.objects.get(pk=pk).Name
            if not other_df.columns.empty:
                # if has columns, else supply None and name column empty
                if str(pk) in request.GET.keys():
                    # if this schedule in get request, use col specifics, else use first col
                    # TODO: create error handling
                    assert (request.GET.get(str(pk)).isnumeric()), 'Columns must be specified by a number'
                    col_name = other_df.columns[int(request.GET.get(str(pk)))]
                else:
                    col_name = other_df.columns[0]
                df[self.name_col(schedule_name, col_name)] = other_df[col_name]
            else:
                df[self.name_col(schedule_name, 'Empty')] = None
        self.df = df

    def get_comp_dicts(self, request, main_pk, slug):
        pk_list = [main_pk] + slug.split('-')
        name_dict = {}
        select_dict = {}
        for pk in pk_list:
            matrix = self.model.objects.get(pk=pk)
            name_dict[pk] = matrix.Name
            select_dict[pk] = 0
            if request.GET.get(str(pk)) is not None:
                select_dict[pk] = request.GET.get(str(pk))
            else:
                select_dict[pk] = 0
        self.select_dict = select_dict
        self.name_dict = name_dict
        self.make_col_dict()

    def make_col_dict(self):
        col_dict = {}
        for pk in self.select_dict.keys():
            matrix = self.model.objects.get(pk=pk)
            col_dict[pk] = dict(zip(range(len(matrix.df.columns)), matrix.df.columns))
        self.col_dict = col_dict

    def make_col_name(self, col_name, columns):
        if col_name in columns:
            # TODO: use .format
            if col_name[-1:] == ')':
                return self.make_col_name(col_name[:-2] + str(int(col_name[-2])+1) + ')', columns)
            else:
                return self.make_col_name(col_name + " (0)", columns)
        else:
            return col_name

    def make_data_chart(self):
        df = pd.DataFrame()
        col_dict = {}
        cols = []
        t0 = time.time()
        for pk in self.select_dict.keys():
            matrix = self.model.objects.get(pk=pk)
            lane = matrix.df[matrix.df.columns[self.select_dict[pk]]]
            col_name = self.make_col_name(str(lane.name) + ' - ' + self.name_dict[pk], df.columns)
            cols.append(col_name)
            lane = lane.rename(col_name)
            lane.index = pd.to_numeric(lane.index)
            df = pd.concat([df, lane], axis=1, sort=True)
            col_dict[pk] = dict(zip(range(len(matrix.df.columns)), matrix.df.columns))
        self.df = df[cols].sort_index()
        self.col_dict = col_dict
        print("Made chart in "+str(time.time()-t0)+" seconds")

    def lane_comp_plotter(self):
        # TODO: Handle non-unique column headings
        p = figure(width=800, height=480, title='Lane Comparison Plotter')
        p.left[0].formatter.use_scientific = False
        numlines = len(self.df.columns)
        mypalette = pallette[0:numlines]
        running_max = 0
        count = 0
        for name in self.df:
            y = self.df[name].astype('float')
            y = y.loc[~pd.isnull(y)]
            running_max = max(running_max, y.max())
            p.line(y.index, y.values, line_color=mypalette[count], line_width=5, legend=name)
            count += 1
        p.y_range = Range1d(0, running_max * 1.1)  # Not sure why turn into string...
        p.legend.location = "bottom_right"
        script, div = components(p)
        return script, div

    @staticmethod
    def highlight_cols():
        color = '#007FFF'
        return 'background-color: %s' % color

    def format_df(self):
        d = {}
        # df = self.df.replace(to_replace='None', value=np.nan).astype('float')
        for col in self.df.columns:
            d[col] = lambda x: '' if pd.isnull(x) else '${:,.2f}'.format(x)
        class_string = 'class="dataframe table table-hover table-bordered dataTable" '
        return self.df.style.applymap(self.highlight_cols, subset=pd.IndexSlice[:, [self.df.columns[0]]]
                                      ).set_table_attributes(class_string).format(d)

    class Settings(object):
        plot_width = 800
        plot_height = 480
        plot_title = "Lane Comparison"


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


class Single(object):

    @staticmethod
    def format_df(df, lane_labels):
        # TODO: add lane column headers here
        d = {}
        df = df.replace(to_replace='None', value=np.nan).astype('float')
        for col in df.columns:
            d[col] = lambda x: '' if pd.isnull(x) else '${:,.2f}'.format(x)
        class_string = 'class="dataframe table table-hover table-bordered dataTable" '
        return df.style.set_table_attributes(class_string).format(d)


