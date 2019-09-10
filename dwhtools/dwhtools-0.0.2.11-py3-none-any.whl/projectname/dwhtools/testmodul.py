from pyspark.sql.dataframe import DataFrame
from datetime import datetime
def replaceNulls(df:DataFrame, valueForNumbers:int = -99, valueForStrings:str = "-", valueForBool:bool = False) -> DataFrame:
  numberCols = []
  stringCols = []
  boolCols = []
  
  for col in df.dtypes:
    name = col[0]
    typ = col[1]
    if typ == "int" or typ[:7] == "decimal" or typ == "double":
      numberCols.append(name)
    elif typ == "string":
      stringCols.append(name)
    elif typ == "boolean":
      boolCols.append(name)

      
  if len(numberCols) > 0:
    df = df.fillna(valueForNumbers, subset = numberCols)
  if len(stringCols) > 0:
    df = df.fillna(valueForStrings, subset = stringCols)
  if len(boolCols) > 0:
    df = df.fillna(valueForBool, subset = boolCols)
  return df

from pyspark.sql import Row
import pyspark


spark = pyspark.sql.SparkSession.builder.appName('someSession').getOrCreate()


def getTestData():
  row1 = Row(MenschName = "Herbert", Stadt = "Gladbach", Abteilung = "Purchase")
  row2 = Row(MenschName = "Gundula", Stadt = "Düsseldorf", Abteilung = "HR")
  row3 = Row(MenschName = "Petra", Stadt = "Berlin", Abteilung = "Finance")
  row4 = Row(MenschName = "Serafina", Stadt = "Berlin", Abteilung = "Finance")

  departmentsWithEmployees_Seq = [row1, row2, row3, row4]
  dframe = spark.createDataFrame(departmentsWithEmployees_Seq)
  return dframe