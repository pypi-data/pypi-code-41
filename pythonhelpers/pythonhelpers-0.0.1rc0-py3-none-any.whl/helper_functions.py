import pandas as pd
import os
import datetime
import warnings
import re

import pyspark.sql.functions as F
from pyspark.sql import Window
from pyspark.sql.types import IntegerType, DoubleType

def frequency_counts(df, cols):
  """Get an overview over how many unicates, duplicates etc. this column contains.
  
  Answers the following question: How many entries appear
  exactly one time in the dataset? How many appear twice?
  How many appear X times?
  
  Returns a PySpark Dataframe.
  """
  if type(cols)==str:
    cols = [cols]
  return df.groupBy(cols).count().withColumnRenamed("count", "freq").groupBy("freq").count().withColumnRenamed("count", "counts").orderBy("freq", ascending=True)  
  
def value_counts(df, cols):
  """Count how often each value appears in the column(s)
  
  If multiple column names are passed in cols, each combination 
  of values in a row is treated as a unique value.
  
  This is more or less equivalent to pandas' value_counts().
  
  Returns a PySpark Dataframe.
  """
  if type(cols)==str:
    cols = [cols]
  return (df.groupBy(cols).count()
            .orderBy("count", ascending=False)
            .withColumnRenamed("count", "counts"))
  
def get_entries_with_frequency(df, cols, freq):
  """Return all rows of df where the value in cols appears X times.
  
  E.g. if "cols" contains [1,2,3,3,4,6,5,5] and "freq" is set to 2, 
  all rows containing "3" and "5" would be returned since these
  appear two times in the column.
  
  Use this in conjunction with frequency_counts to find outliers in
  your data.
  
  Returns a pyspark Dataframe.
  """
  if type(cols)==str:
    cols = [cols]
  w = Window.partitionBy(cols)
  return df.select('*', F.count(cols[0]).over(w).alias('dupeCount'))\
           .where("dupeCount = {}".format(freq))\
           .drop('dupeCount')
