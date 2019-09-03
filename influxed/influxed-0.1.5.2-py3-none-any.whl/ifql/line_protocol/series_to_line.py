import pandas as pd
from influxed.ifql.line_protocol.dataframe_to_line import to_lines as df_to_line

def to_lines(series, measurement):
    """
        Pandas Series to line protocol
    """
    return df_to_line(pd.DataFrame([series]), measurement)
    