import plotly
import plotly.graph_objs as go

def show_barchart(df, col):
    res = df.groupby(col)[col].count() #df[col].value_counts()
    data = go.Bar(x=res.index.values, y=res.values)
    plotly.offline.iplot([data])

def show_multi_barchart(df, cols):
    if not isinstance(cols, list): cols = [cols]    
    data = []
    for col in cols:
        res = df.groupby(col)[col].count()
        data.append( go.Bar(x=res.index.values, y=res.values) )
    plotly.offline.iplot(data)