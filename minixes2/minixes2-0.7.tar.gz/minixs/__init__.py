"""
Miniature X-ray Spectrometer (miniXS) Tools
"""
import os
import logging
import logging.config
try:
    from configparser import NoSectionError      # Python 3 way
except:
    from ConfigParser import NoSectionError      # Python 2 way

__version__ = '0.7'
LOGGER_NAME="minixs"
METHOD_ENTER_STR = "Enter %s\n-------------------"
METHOD_EXIT_STR = "Exit %s\n---------------------"
LOGGER_DEFAULT = {
    'version' : 1,
    'handlers' : {'consoleHandler' : {'class' : 'logging.StreamHandler',
                               'level' : 'INFO',
                               'formatter' : 'consoleFormat',
                               'stream' : 'ext://sys.stdout'} ,
                  },
    'formatters' : {'consoleFormat' : {'format' : '%(asctime)-15s - %(name)s - %(funcName)s- %(levelname)s - %(message)s'},
                    },
    'loggers' : {'root' :{'level' : 'INFO',
                        'handlers' : ['consoleHandler',],
                      },
               LOGGER_NAME : {'level' : 'INFO',
                            'handlers' : ['consoleHandler',],
                            'qualname' : LOGGER_NAME
                            }
               },
   }

userDir = os.path.expanduser("~")
logConfigFile = os.path.join(userDir, LOGGER_NAME + 'Log.config')
if os.path.exists(logConfigFile):
    print ("logConfigFile " + logConfigFile )
    try:
        logging.config.fileConfig(logConfigFile, disable_existing_loggers=False)
        print("Success Openning logfile")
    except (NoSectionError,TypeError) as ex:
        print ("In Exception to load dictConfig package %s\n %s" % (LOGGER_NAME, ex))
        logging.config.dictConfig(LOGGER_DEFAULT)
    except KeyError as ex:
        print ("logfile %s was missing or had errant sections %s" %(logConfigFile, ex.args))

else:
    logging.config.dictConfig(LOGGER_DEFAULT)

import minixs.calibrate as calibrate, \
       minixs.emission as emission, \
       minixs.exposure, \
       minixs.filter, \
       minixs.misc, \
       minixs.rixs, \
       minixs.scanfile, \
       minixs.spectrometer

from minixs.constants import *

__all__ = [
  'calibrate',
  'emission',
  'exposure',
  'filter',
  'misc',
  'rixs',
  'scanfile',
  'spectrometer',
  ]


