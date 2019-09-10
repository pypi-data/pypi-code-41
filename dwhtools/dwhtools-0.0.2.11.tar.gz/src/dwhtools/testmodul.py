from pyspark.sql.dataframe import DataFrame
from datetime import datetime
def replaceNulls(spark, df:DataFrame, valueForNumbers:int = -99, valueForStrings:str = "-", valueForBool:bool = False) -> DataFrame:
  numberCols = []
  stringCols = []
  boolCols = []
  
  for col in df.dtypes:
    name = col[0]
    typ = col[1]
    if typ == "int" or typ[:7] == "decimal" or typ == "double" or typ == "bigint":
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


# spark = pyspark.sql.SparkSession.builder.appName('someSession').getOrCreate()


def getTestData(spark):
  row1 = Row(MenschName = "Herbert", Stadt = None, Abteilung = "Purchase", PersonalNummer = 1)
  row2 = Row(MenschName = "Gundula", Stadt = "Düsseldorf", Abteilung = "HR", PersonalNummer = None)
  row3 = Row(MenschName = "Petra", Stadt = "Berlin", Abteilung = "Finance", PersonalNummer = 3)
  row4 = Row(MenschName = "Serafina", Stadt = "Berlin", Abteilung = "Finance", PersonalNummer = 4)

  departmentsWithEmployees_Seq = [row1, row2, row3, row4]
  dframe = spark.createDataFrame(departmentsWithEmployees_Seq)
  return dframe

def getTestDataTwo():
  row1 = Row(MenschName = "Herbert", Stadt = None, Abteilung = "Purchase", PersonalNummer = 1)
  row2 = Row(MenschName = "Gundula", Stadt = "Düsseldorf", Abteilung = "HR", PersonalNummer = None)
  row3 = Row(MenschName = "Petra", Stadt = "Berlin", Abteilung = "Finance", PersonalNummer = 3)
  row4 = Row(MenschName = "Serafina", Stadt = "Berlin", Abteilung = "Finance", PersonalNummer = 4)

  departmentsWithEmployees_Seq = [row1, row2, row3, row4]
  dframe = spark.createDataFrame(departmentsWithEmployees_Seq)
  return dframe