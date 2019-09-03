import pandas as pd
from influxed.ifql.line_protocol.list_to_line import to_lines as list_to_lines 

def to_lines(df, measurement):
    """
        Format a pandas DataFrame into line protocol
    """
    df = df.copy()
    df['time'] = df.index.values.astype(int).astype(str)
    ndf = df.to_dict(orient='records')
    return list_to_lines(ndf, measurement)
    # return dataframe_to_line_protocol(df, measurement) # list to line is faster

def dataframe_to_line_protocol(df, measurement):
    """
        Format a pandas DataFrame into line protocol
    """
    df = df.dropna(how='all')
    tags = df[df.dtypes.index[df.dtypes == pd.np.object]]
    fields = df[df.dtypes.index[df.dtypes != pd.np.object]]

    fields = pd.np.apply_along_axis(dataframe_to_line_protocol_apply, 1, fields, columns=fields.columns)
    tags = pd.np.apply_along_axis(dataframe_to_line_protocol_apply, 1, tags, columns=tags.columns, join_str='', format_str=',"{}"="{}"')

    tags = pd.np.core.defchararray.add(measurement, tags)
    tags = pd.np.core.defchararray.add(tags, ' ')
    fields = pd.np.core.defchararray.add(tags, fields)
    fields = pd.np.core.defchararray.add(fields, ' ')
    fields = pd.np.core.defchararray.add(fields, df.index.values.astype(int).astype(str))

    return fields.tolist()

def dataframe_to_line_protocol_apply(row, columns, join_str=',', format_str='"{}"={}'):
    """
        Helper function for dataframe_to_line_protocol
    """
    return join_str.join(format_str.format(i, v) for i, v in zip(columns, row) if pd.notnull(v))

