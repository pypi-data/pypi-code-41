import sys
import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql import SQLContext
from pyspark.sql import DataFrame
from pyspark.sql.types import *
from pyspark.sql.functions import *

class adevinta_yapo_bi_pySpark_postgresql(object):

    def __init__(self, app_name, connection_db_name, dbname, host, port, user, password ):
        """
        Method    [ __init__ ] is constructor of adevinta_yapo_bi_pySpark_postgresql class.
        Attribute [ app_name ][ String ] is spark application name.
        Attribute [ connection_db_name ][ String ] is connection database name. For example DW_BLOCKETDB.HOST.
        Attribute [ dbname ][ String ] is database name. For example dw_blocketdb_ch.
        Attribute [ host ][ String ] is database host. For example 127.0.0.1.
        Attribute [ host ][ String ] is database port. For example 5432.
        Attribute [ username ][ String ] is database username.
        Attribute [ password ][ String ] is database password.
        Attribute [ url_connection ][ String ] is url connection to database.
        Attribute [ spark_session ][ pyspark.sql ] is sparkSession object.
        Attribute [ spark_context ][ pyspark.sql ] is sparkContext object.
        Attribute [ node ][ String ] is node where must be run spark application.
        Attribute [ db_jar ][ String ] is jar file that allow connection to postgresql database.
        Attribute [ driver ][ String ] is driver class that allow write to postgresql database.
        Attribute [ logger_db ][ logging ] is logging object that allow create log.
        """
        self.app_name = app_name
        self.connection_db_name = connection_db_name
        self.dbname = dbname
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.url_connection = "jdbc:postgresql://" + self.host + ":" + self.port + "/" + self.dbname
        self.spark_session = ""
        self.spark_context = ""
        self.node = "local"
        self.db_jar = "/usr/spark-2.4.1/jars/postgresql-42.2.6.jar"
        self.driver = "org.postgresql.Driver"
        self.logger_db = logging.getLogger('pySpark_database')
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d - %(funcName)20s()] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.INFO)
        self.get_spark_session()

    def get_dbname( self ):
        self.logger_db.info('App Name %s Get database name %s ' % ( self.app_name, self.dbname ) )
        return self.dbname

    def get_user( self ):
        self.logger_db.info('App Name %s Get username %s '% ( self.app_name, self.user) )
        return self.user

    def get_password( self ):
        self.logger_db.info('App Name %s Get password %s ' % ( self.app_name, self.password) )
        return self.password

    def get_host( self ):
        self.logger_db.info('App Name %s Get host %s ' % ( self.app_name, self.host ) )
        return self.host

    def get_port( self ):
        self.logger_db.info('App Name %s Get port %s ' % ( self.port, self.port ) )
        return self.port

    def set_dbname( self, dbname ):
        self.logger_db.info('App Name %s Set database name %s ' % ( self.app_name, dbname ) )
        self.dbname = dbname

    def set_user( self, user ):
        self.logger_db.info('App Name %s Set username %s ' % ( self.app_name, user ) )
        self.user = user

    def set_password( self, password ):
        self.logger_db.info('App Name %s Set password %s ' % ( self.app_name, password ) )
        self.password = password

    def set_host( self, host ):
        self.logger_db.info('App Name %s Set host %s ' % ( self.app_name, host ) )
        self.host = host

    def set_port( self, port ):
        self.logger_db.info('App Name %s Set port %s ' % ( self.app_name, port ) )
        self.port = port

    def get_spark_sql_context( self, query ):
        """
        Method [ get_spark_sql_context ] allow do query to Posgtresql dataBase engine.
        Param  [ query ] : Is the SQL query that we want do.
        Return [ df ]    : Is a DataFramwe that return
        """
        try:
            self.logger_db.info('Generate Spark SQL Context App Name %s DBName %s ' % ( self.app_name, self.connection_db_name ) )
            self.spark_sql_context = SQLContext(self.spark_context)
            self.logger_db.info('App Name %s DBName %s execution query  %s ' % ( self.app_name, self.connection_db_name, query ) )
            df = self.spark_sql_context.read.format("jdbc") \
                                .option('url', self.url_connection ) \
                                .option('dbtable', query ) \
                                .option('user', self.user ) \
                                .option('password', self.password ) \
                                .load()
            return df
        except Exception as e:
            self.logger_db.error('App Name %s ERROR %s' % ( self.app_name,  e ) )
            self.stop_spark_session()
            exit()

    def write_dataFrame_file( self, df, type_file, path_file ):
        """
        Method [ write_dataFrame_file ] allow write a dataframe in parquet or csv file.
        Param  [ df ] : is dataframe object that contains data that we want insert.
        Param  [ type_file ] : is mode type file write. For example [ parquet || csv ]
        Param  [ path_file ] : is path file where must be write data. For example [ /usr/spark-2.4.1/ETL/pyspark/ ]
        """
        try:
            self.logger_db.info('Write DataFrame to %s mode App Name %s ' % (type_file, self.app_name))
            if ( type_file == 'csv' or type_file == 'CSV' ):
                df.write.format('com.databricks.spark.csv').save( path_file )
            elif ( type_file == 'parquet' or type_file == 'PARQUET' ):
                df.write.parquet( path_file )
        except Exception as e:
            self.logger_db.error('%s' % e )

    def write_DataFrame_jdbc( self, df, table_write, mode_write ):
        """
        Method [ write_DataFrame_jdbc ] allow write a dataframe in postgresql database.
        Param  [ df ] : is dataframe object that contains data that we want insert.
        Param  [ table_write ] : is table name that we want insert data.
        Return [ mode_write ] : is mode to write. For example [overwrite || append ]
        """
        try:
            self.logger_db.info('Write DataFrameWriter App Name %s ' % self.app_name )
            self.logger_db.info('Write database %s table %s mode %s ' % (self.connection_db_name, table_write, mode_write ) )
            self.logger_db.info('Create DataFrameWriter ')
            df_writer = df.write

            properties = {
            'user' : self.user
            , 'password' : self.password
            }

            self.logger_db.info('Write data')
            df_writer.jdbc( self.url_connection
                            , table_write
                            , mode_write
                            , properties )
        except Exception as e:
            self.logger_db.error('App Name %s ERROR %s' % ( self.app_name,  e ) )
            self.stop_spark_session()
            exit()

    def get_spark_session( self ):
        """
        Method [ get_spark_session ] allow create sparkSession object.
        """
        try:
            self.logger_db.info('Generate Spark Session App Name %s ' % self.app_name )
            self.logger_db.info('Generate Spark Session JAR Name %s ' % self.db_jar )

            self.spark_session = SparkSession.builder \
                                .master(self.node) \
                                .appName(self.app_name) \
                                .config("spark.driver.extraClassPath", self.db_jar) \
                                .getOrCreate()
            self.logger_db.info('Generate Spark Context App Name %s ' % self.app_name )
            self.spark_context = self.spark_session.sparkContext
            logger = self.spark_context._jvm.org.apache.log4j
            logger.LogManager.getLogger("org"). setLevel( logger.Level.ERROR )
            logger.LogManager.getLogger("akka").setLevel( logger.Level.ERROR )
        except Exception as e:
            self.logger_db.error('App Name %s ERROR %s' % ( self.app_name,  e ) )
            self.stop_spark_session()
            exit()

    def stop_spark_session( self ):
        """
        Method [ stop_spark_session ] allow stop sparkSession object.
        """
        try:
            self.logger_db.info('Stopping SparkSession APP Name %s ' % self.app_name )
            self.spark_session.stop()
        except Exception as e:
            self.logger_db.error('App Name %s ERROR %s' % ( self.app_name,  e ) )
            exit()

    def write_to_parquet( self, df, path_filename, mode_write ):
        try:
            self.logger_db.info('Write parquet to %s' % path_filename  )
            df.write.parquet(path_filename
                            , mode=mode_write )
        except Exception as e:
            self.logger_db.error('App Name %s ERROR %s' % ( self.app_name,  e ) )
            self.stop_spark_session()
            exit()

    def spark_df_sql( self, query ):
        try:
            self.logger_db.info('Spark SQL App Name %s Query %s.' % ( self.app_name, query) )
            result_query = self.spark_session.sql( query )
            return result_query
        except Exception as e:
            self.logger_db.error('App Name %s ERROR %s' % ( self.app_name,  e ) )
            self.stop_spark_session()
            exit()
