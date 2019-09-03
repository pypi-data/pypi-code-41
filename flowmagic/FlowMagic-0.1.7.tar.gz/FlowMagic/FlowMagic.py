import json,traceback,os,logging,glob



logging.basicConfig(format='%(levelname)s - %(asctime)s - %(message)s', level=logging.DEBUG)
#env = os.environ
#logging.info("All Environment Variables")
#logging.info(os.environ)
#try:
#	logging.info('Input Paths %s', json.loads(env['input_path']))
#except Exception as e:
#	logging.error("Input path not found")

FM_ALLOWED_EXTENSION = []
def setExtensions( *args ):
	global FM_ALLOWED_EXTENSION
	for x in args:
		if x not in FM_ALLOWED_EXTENSION:
			FM_ALLOWED_EXTENSION.append(x)

def unsetExtensions( *args ):
	global FM_ALLOWED_EXTENSION
	for x in args:
		FM_ALLOWED_EXTENSION.remove( x )


def allowed_file(filename):
	global FM_ALLOWED_EXTENSION
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in FM_ALLOWED_EXTENSION

def info_log( *args ):
	for info in args:
		logging.info( info  )

def err_log( *args ):
	for err in args:
		logging.error( err )

def debug( *args ):
	for data in args:
		logging.debug( data  )

def custom_input_path( path_regex ):
	return glob.glob(path_regex)


def base_input_path( path=None ):
	try:
		return json.loads(os.environ.get('input_path'))

	except (Exception, IndexError) as e:
		if path!=None:	return [path]
		return traceback.format_exc()
		
def base_output_path( path=None ):

	try:
		output_path= json.loads( os.environ.get('output_path')  ) 
		for x in output_path:
			os.makedirs( x, exist_ok=True )
		return output_path

	except (Exception, IndexError) as e:
		if path!=None:	return [path]
		return traceback.format_exc()


def getSystemValue( key=None ):
	if key==None:	return os.environ
	value = os.environ.get( key )
	if value!=None:	return value
	data = configJsonFile()
	for x in data['config_required']:
		#print(x)
		if str(x['name'])==key:
			return x['value']
	return None



def input_tree_path( obj , prevPath ,k ):

	if obj['type'] == 'dir':
		for x in obj['children']:
			#print(  os.path.join(prevPath,x['name']) )
			input_tree_path( x, os.path.join(prevPath,x['name']),k )  	
	elif obj['type'] == 'file':
		#print(  prevPath+ "."+obj['endsWith'] ) 
		k.append( prevPath+ "."+obj['endsWith']  )

def configJsonFile():
	configFileData={}
	with open( 'config.json' ) as json_file:
		configFileData = json.load(json_file)
	return configFileData


def get_config_required( **kwargs ):
	data = configJsonFile()
	for x in data['config_required']:
		if x['name'] == kwargs['name']:
			return x		


