import logging.handlers as log_handlers
from timeit import default_timer as timer
import functools
from box import Box
from colorlog import ColoredFormatter
import logging
from python_log_indenter import IndentedLoggerAdapter

colored_log_format=f"%(log_color)s%(asctime)s %(processName)18.18s %(levelname)5.5s || %(message)s"
base_log_indent_settings=dict(indent_char='| ',spaces=1)
date_fmt="%m-%d %H:%M:%S"
wrapper_log_level=logging.INFO
default_log_level=logging.INFO
default_log_format=colored_log_format.replace(r'%(log_color)s','')
log_func_mapper=Box()
log_func_mapper[logging.DEBUG]=lambda logger:logger.debug
log_func_mapper[logging.INFO]=lambda logger:logger.info
log_func_mapper[logging.WARNING]=lambda logger:logger.warning
log_func_mapper[logging.CRITICAL]=lambda logger:logger.critical
log_func_mapper[logging.ERROR]=lambda logger:logger.error

log_sayer=lambda logger,log_level:log_func_mapper[log_level](logger)

class TheLogger2(IndentedLoggerAdapter):

	def __init__(self,name,extra=None,auto_add=True,log_level=None,log_format='',**kwargs):
		logger=setup_logger(name,log_level,log_format)
		logger.propagate=False
		super(TheLogger2,self).__init__(logger,extra,auto_add,**dict(base_log_indent_settings,**kwargs))
		self.current_handlers=[]

	def add_file_handler(self,log_filepath,log_level=logging.DEBUG):
		log_handler=logging.FileHandler(log_filepath)
		log_handler.setFormatter(logging.Formatter(default_log_format))
		log_handler.setLevel(log_level)
		self.logger.addHandler(log_handler)
		self.current_handlers.append(log_handler)
		return self

	def add_rotating_handler(self,log_filepath,log_level=None,maxBytes=1.99e6,backupCount=14,**other_opts):
		log_level=log_level or default_log_level
		log_handler=log_handlers.RotatingFileHandler(maxBytes=int(maxBytes),filename=log_filepath,backupCount=backupCount,**other_opts)
		log_handler=self.logger.addHandler(log_handler,level=log_level,log_format=default_log_format)
		self.current_handlers.append(log_handler)
		return self

	def wrap(self,log_level=None,skimpy=False):
		def second_wrapper(func):
			@functools.wraps(func)
			def wrapper(*args,**kwargs):
				log_say=log_sayer(self,log_level or wrapper_log_level)
				if skimpy: log_say('Performing "%s"...',func.__name__)
				else: log_say('Running "%s":',func.__name__)
				start=timer()
				self.add()
				result=func(*args,**kwargs)
				if not skimpy: log_say('Done "%s". Duration: %.3f sec.',func.__name__,timer()-start)
				self.sub()
				return result

			return wrapper

		return second_wrapper

	def remove_active_handler(self):
		target_handler=self.current_handlers.pop()
		self.logger.handlers.remove(target_handler)
		return self

class TheLogger(IndentedLoggerAdapter):
	def __init__(self,logger_name,level=logging.DEBUG,extra=None,auto_add=True,**kwargs):
		_logger=logging.getLogger(logger_name)
		_logger.setLevel(level)
		super(TheLogger,self).__init__(_logger,extra=extra,auto_add=auto_add,**dict(base_log_indent_settings,**kwargs))

	def create_handler(self,handler: logging.Handler,level=logging.DEBUG,log_formatter=None):
		if log_formatter is None:
			if type(handler) is logging.StreamHandler:
				log_formatter=ColoredFormatter(colored_log_format,date_fmt)
			else:
				log_formatter=logging.Formatter(default_log_format,date_fmt)
		handler.setLevel(level=level)
		handler.setFormatter(log_formatter)
		self.logger.addHandler(handler)
		return self

	@classmethod
	def streamed_logger(cls,logger_name,level=logging.DEBUG):
		the_logger=cls(logger_name).create_handler(logging.StreamHandler(),level=level)
		return the_logger

	def add_rotating_handler(self,log_filepath,log_level=None,maxBytes=2e6,backupCount=14,**other_opts):
		log_level=log_level or default_log_level
		log_handler=log_handlers.RotatingFileHandler(maxBytes=int(maxBytes),filename=log_filepath,backupCount=backupCount,**other_opts)
		log_handler.setFormatter(logging.Formatter(default_log_format))
		log_handler.setLevel(log_level)
		self.logger.addHandler(log_handler)
		return self

	def wrap(self,log_level=None,skimpy=False):
		def second_wrapper(func):
			@functools.wraps(func)
			def wrapper(*args,**kwargs):
				log_say=log_sayer(self,log_level or wrapper_log_level)
				if skimpy: log_say('Performing "%s"...',func.__name__)
				else: log_say('Running "%s":',func.__name__)
				start=timer()
				self.add()
				result=func(*args,**kwargs)
				if not skimpy: log_say('Done "%s". Duration: %.3f sec.',func.__name__,timer()-start)
				self.sub()
				return result

			return wrapper

		return second_wrapper

	def add_file_handler(self,log_filepath,log_level=logging.DEBUG):
		log_handler=logging.FileHandler(log_filepath)
		log_handler.setFormatter(logging.Formatter(default_log_format))
		log_handler.setLevel(log_level)
		self.logger.addHandler(log_handler)
		# self.current_handlers.append(log_handler)
		return self

def setup_logger(name,log_level=None,log_format=''):
	log_level=log_level or default_log_level
	new_logger=logging.getLogger(name)
	new_logger.setLevel(log_level)
	log_handler=logging.StreamHandler()
	log_format=log_format or colored_log_format
	log_handler.setFormatter(ColoredFormatter(log_format,date_fmt))
	new_logger.addHandler(log_handler)
	# new_logger.info(f'Root logger initialized with level {logging._levelToName[log_level]}.')
	return new_logger

# root_logger=setup_logger(log_level=logging.DEBUG)

simple_logger=TheLogger.streamed_logger('lgblkb_logger')
# log_wrapper=lambda log_level=logging.DEBUG,skimpy=False:simple_logger.wrap(log_level=log_level,skimpy=skimpy)
log_wrapper=simple_logger.wrap

# @simple_logger.wrap(log_level=logging.DEBUG)
@log_wrapper()
def main():
	x=[1,2,3]
	simple_logger.info('x: %s',x)

	pass

if __name__=='__main__':
	main()
