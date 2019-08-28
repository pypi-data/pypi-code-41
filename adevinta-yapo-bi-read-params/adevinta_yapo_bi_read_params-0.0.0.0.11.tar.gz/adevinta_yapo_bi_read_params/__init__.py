import sys
import logging
import datetime
from datetime import timedelta

class read_params(object):
    #Constructor
    def __init__(self, str_parse_params ):
        """
        Method    [ __init__ ] is constructor of read_params class.
        Attribute [ str_parse_params ][ String Array ] is array string that contains params of execution . For example, python mypyhton.py -d1=2019-08-02 -d2=2019-08-02 -env=dev -app_name=mypython
        Attribute [ date1 ][ String ] is date1 variable. For example DW_BLOCKETDB.HOST.
        Attribute [ date2 ][ String ] is date2 variable. For example dw_blocketdb_ch.
        Attribute [ env ][ String ] is enviroment type. For example [ dev | qa | prod ].
        Attribute [ app_name ][ String ] is a app_name for sparkSession. For example mypython.
        Attribute [ current_year ][ String ] is current year of execution. For example 2019.
        Attribute [ last_year ][ String ] is last year of execution. For example 2018.
        Attribute [ logger ][ logging ] is logging object that allow create log.
        """
        self.str_parse_params = str_parse_params
        self.date1 = ""
        self.date2 = ""
        self.env = ""
        self.app_name = ""
        self.current_year = ""
        self.last_year = ""
        self.logger =  logging.getLogger('read_params')
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d - %(funcName)20s()] %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S',
        level=logging.INFO)
        self.load_params()
        self.validate_params()

    #Getter and Setter attributes
    def get_date1(self):
        return self.date1

    def get_date2(self):
        return self.date2

    def get_env(self):
        return self.env

    def get_app_name(self):
        return self.app_name

    def get_current_year(self):
        return self.current_year

    def get_last_year(self):
        return self.last_year

    def set_date1( self, date1 ):
        self.date1 = date1

    def set_date2( self, date2 ):
        self.date2 = date2

    def set_env( self, env ):
        self.env = env

    def set_app_name( self, app_name ):
        self.app_name = app_name

    def set_current_year( self, current_year ):
        self.current_year = current_year

    def set_last_year( self, last_year ):
        self.last_year = last_year

    def load_params( self ):
        """
        Method [ load_params ] is method that load params into each attribute.
        """
        try:
            self.logger.info( 'Python name : %s ' % self.str_parse_params[0] )
            for i in range(1, len(self.str_parse_params ) ):
                self.logger.info( 'Param[%s] : %s ' % ( i, self.str_parse_params[ i ] ) )
                param = self.str_parse_params[ i ].split("=")
                self.mapping_params( param[0], param[1] )
        except Exception as e:
            self.logger.error('%s' % e )
            exit()

    def mapping_params(self, key, value ):
        """
        Method [ mapping_params ] is method that join attribute with key.
        Param  [ key ] is the key that be compare with params define for assign to attribute.
        Param  [ value ] is value that will be assign to attribute.
        """
        try:
            if ( key == '-d1' ):
                self.date1 = value
                self.current_year = value[0:4]
                year_int = int( self.current_year )
                year_int = year_int - 1
                self.last_year = year_int
            elif ( key == '-d2' ):
                self.date2 = value
            elif ( key == '-env' ):
                self.env = value
            elif ( key == '-app_name' ):
                self.app_name = value
        except Exception as e:
            self.logger.error('%s' % e )
            exit()

    def validate_params(self):
        """
        Method [ validate_params ] is method validate that each attribute have assign a value.
        """
        try:
            self.logger.info('Validate params.')
            current_date = datetime.datetime.now()
            if ( self.date1 == '' ):
                temp_date = current_date + timedelta(days=-1)
                current_year = temp_date.year
                last_year = temp_date.year - 1
                self.current_year = str( current_year )
                self.last_year = str( last_year )
                self.date1 = temp_date.strftime('%Y-%m-%d')
            if ( self.date2 == '' ):
                temp_date = current_date + timedelta(days=-1)
                self.date2 = temp_date.strftime('%Y-%m-%d')
            if ( self.env == '' ):
                self.env = 'prod'
            if( self.app_name == '' ):
                path_app_name = self.str_parse_params[ 0 ].split("/")
                app_name = path_app_name[len(path_app_name)-1].split(".")
                self.app_name = app_name[0]

            self.logger.info('App Name     : %s' % self.app_name)
            self.logger.info('Date 1       : %s' % self.date1)
            self.logger.info('Date 2       : %s' % self.date2)
            self.logger.info('Env          : %s' % self.env)
            self.logger.info('Current Year : %s' % self.current_year)
            self.logger.info('Last    Year : %s' % self.last_year)

        except Exception as e:
            self.logger.error('%s' % e)
            exit()
