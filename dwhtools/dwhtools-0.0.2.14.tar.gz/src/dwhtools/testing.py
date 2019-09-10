from pyspark.sql.dataframe import DataFrame
from datetime import datetime
from pyspark.sql import Row
import pyspark

#sparkSession aufmachen
spark = pyspark.sql.SparkSession.builder.getOrCreate()


def getTestData() -> DataFrame:
  row1 = Row(MenschName = "Herbert", Stadt = None, Abteilung = "Purchase", PersonalNummer = 1)
  row2 = Row(MenschName = "Gundula", Stadt = "Düsseldorf", Abteilung = "HR", PersonalNummer = None)
  row3 = Row(MenschName = "Petra", Stadt = "Berlin", Abteilung = "Finance", PersonalNummer = 3)
  row4 = Row(MenschName = "Serafina", Stadt = "Berlin", Abteilung = "Finance", PersonalNummer = 4)

  departmentsWithEmployees_Seq = [row1, row2, row3, row4]
  dframe = spark.createDataFrame(departmentsWithEmployees_Seq)
  return dframe

