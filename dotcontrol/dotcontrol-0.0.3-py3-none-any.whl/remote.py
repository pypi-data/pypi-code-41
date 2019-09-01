from importlib import import_module


def get_remote(name):
	if name == 'local':
		return None
	
	try:
		return import_module('.' + name, 'dotcontrol.remotes')
	except:
		raise Exception('Unsupported remote: "{}"'.format(name))
