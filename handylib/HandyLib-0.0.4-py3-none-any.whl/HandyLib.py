import file_operator
import logging.handlers
import logging
import sys

def get_logger(level = logging.INFO,test_flag = False,
				filename = '',
				maxsize = 1024*1024*3,
				backup_num = 5
				):
	'''
	logger
	'''
	
	if filename == '':
		filename = sys.argv[0].split('.')[0] +'.log'

	logger = logging.getLogger()
	format = logging.Formatter(
	"%(levelname)s - line:%(lineno)d - %(filename)s = %(asctime)s \n\n[ %(message)s ]")    # output format
	
	handler = logging.handlers.RotatingFileHandler(
			  'StockLoader.log', maxBytes=maxsize, backupCount=backup_num)
	handler.setFormatter(format)
	logger.addHandler(handler)
	if test_flag or level==logging.DEBUG:
		sh = logging.StreamHandler(stream = sys.stdout)    # output to standard output
		sh.setFormatter(format)
		logger.addHandler(sh)
	logger.setLevel(level)
	return logger
def hello_world():
	print ('hello world')
