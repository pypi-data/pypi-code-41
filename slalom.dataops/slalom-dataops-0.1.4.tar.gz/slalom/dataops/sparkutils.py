import logging
import os
from os import sys

import pyspark
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DateType, TimestampType
from pyspark.sql.types import Row as SparkRow
from pyspark.sql.functions import (
    unix_timestamp,
    from_unixtime,
    to_date,
    input_file_name,
    lit,
)


SUPPORT_CLUSTER_BY = False
SPARK_DRIVER_MEMORY = "4g"
SPARK_EXECUTOR_MEMORY = "4g"
SPARK_WAREHOUSE_ROOT = "/tmp/spark-sql/warehouse"
SPARK_S3_PREFIX = "s3a://"
SPARK_LOG_LEVEL = "ERROR"  # ALL, DEBUG, ERROR, FATAL, INFO, OFF, TRACE, WARN
HADOOP_HOME = os.environ.get("HADOOP_HOME", "/usr/local/hdp")
SPARK_HOME = os.environ["SPARK_HOME"]
SPARK_CLASS_PATH = os.path.join(os.environ["SPARK_HOME"], "jars/*")
SPARK_EXTRA_JARS = [
    # Hadoop 2.7.7:
    os.path.join(HADOOP_HOME, "share/hadoop/tools/lib/aws-java-sdk-1.7.4.jar"),
    os.path.join(HADOOP_HOME, "share/hadoop/tools/lib/hadoop-aws-2.7.7.jar")
    # # Hadoop 3.1.2:
    # os.path.join(HADOOP_HOME, "share/hadoop/tools/lib/aws-java-sdk-bundle-1.11.271.jar"),
    # os.path.join(HADOOP_HOME, "share/hadoop/tools/lib/hadoop-aws-3.1.2.jar")
    # os.path.join(HADOOP_HOME, "share/hadoop/tools/lib/aws-java-sdk-core-1.10.6.jar")
    # os.path.join(HADOOP_HOME, "share/hadoop/tools/lib/aws-java-sdk-kms-1.10.6.jar")
    # os.path.join(HADOOP_HOME, "share/hadoop/tools/lib/aws-java-sdk-s3-1.10.6"),
]
# for jar_path in SPARK_EXTRA_JARS:
#     logging.info("Copying '{}' to '{}'".format(jar_path, SPARK_CLASS_PATH))
#     copyfile(jar_path, SPARK_CLASS_PATH)

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["HADOOP_OPTS"] = (
    os.environ.get("HADOOP_OPTS", "")
    + " -Djava.net.preferIPv4Stack=true -Dcom.amazonaws.services.s3.enableV4=true"
)
HADOOP_CONFIG = {
    "fs.s3a.access.key": os.environ["AWS_ACCESS_KEY_ID"],
    "fs.s3a.secret.key": os.environ["AWS_SECRET_ACCESS_KEY"],
    "fs.s3a.endpoint": "s3.us-east-2.amazonaws.com",
    "fs.s3a.impl": "org.apache.hadoop.fs.s3a.S3AFileSystem",
    "com.amazonaws.services.s3.enableV4": "true",
    "spark.executor.memory": SPARK_EXECUTOR_MEMORY,
    "spark.driver.memory": SPARK_DRIVER_MEMORY,
    "spark.sql.warehouse.dir": SPARK_WAREHOUSE_ROOT,
    "spark.jars": ",".join(SPARK_EXTRA_JARS),
    "derby.system.home": "/tmp/derby.log",
    "derby.stream.error.file": "/tmp/derby",
    "driver-java-options": "-Dderby.stream.error.file=/tmp/derby.log -Dderby.system.home=/tmp/derby",
    "spark.driver.extraJavaOptions": "-Dderby.stream.error.file=/tmp/derby.log -Dderby.system.home=/tmp/derby",
    "spark.executor.extraJavaOptions": "-Dderby.stream.error.file=/tmp/derby.log -Dderby.system.home=/tmp/derby",
    "spark.logConf": "true",
    "spark.ui.showConsoleProgress": "false",  # suppress printing stage updates e.g. 'Stage 2=====>'
}

conf = SparkConf()
for k, v in HADOOP_CONFIG.items():
    SparkContext.setSystemProperty(k, v)
    conf.set(k, v)
context = SparkContext(conf=conf)
for k, v in HADOOP_CONFIG.items():
    context.setSystemProperty(k, v)
logging.info("Creating spark session...")
spark = (
    SparkSession.builder.config(conf=conf)
    .master("local")
    .appName("Python Spark")
    .enableHiveSupport()
    .getOrCreate()
)
spark.sparkContext.setLogLevel(SPARK_LOG_LEVEL)
sc = spark.sparkContext
for jar_path in SPARK_EXTRA_JARS:
    sc.addPyFile(jar_path)
