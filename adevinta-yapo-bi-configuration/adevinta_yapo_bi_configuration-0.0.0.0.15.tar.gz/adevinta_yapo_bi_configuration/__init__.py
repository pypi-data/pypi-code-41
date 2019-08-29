import sys
import logging

class conf(object):
    # Construtor
    def __init__(self, env ):
        self.logger =  logging.getLogger('conf')
        logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d - %(funcName)20s()] %(message)s',
            datefmt='%Y-%m-%d:%H:%M:%S',
            level=logging.INFO)
        self.validate_enviroment( env )
        self.conf = {}
        self.load_conf()

    # Validate enviroment I/O
    def validate_enviroment( self, env ):
        try:
            if( env == 'dev' ):
                self.conf_file = '/usr/spark-2.4.1/ETL/pyspark/Configuration/env/kettle_dev.properties'
            elif ( env == 'prod' ):
                self.conf_file = '/usr/spark-2.4.1/ETL/pyspark/Configuration/env/kettle_prod.properties'
            elif ( env == 'local' ):
                self.conf_file = 'ETL/pyspark/Configuration/env/kettle_dev.properties'
                # TODO: elif enviroment test
        except Exception as e:
            self.logger.error( '%s' % e )
            exit()

    def get_specific(self, key):
        return self.conf.get(key)

    def get_all(self):
        return self.conf

    def get_logger( self ):
        return self.logger

    def load_conf(self):
        try:
            self.logger.info('Load configuration. Read file %s .' % self.conf_file )
            with open(self.conf_file, 'r') as f:
                for line in f.readlines():
                    if line.strip() and not line.startswith('#'):
                        k, v = line.strip().split('=', 1)
                        self.conf[k] = v
                        self.logger.info('%s : %s' % ( k , v ) )
        except Exception as e:
            self.logger.error('%s' % e )
            sys.exit()
