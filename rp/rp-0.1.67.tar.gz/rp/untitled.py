#region Hashing functions

def handy_hash(value,fallback=None):
	#This function is really handy!
	#Meant for hashing things that can't normally be hashed, like lists and dicts and numpy arrays. It pretends they're immutable.
	#This function can hash all sorts of values. Anything mutable should be frozen, we're not just returning an ID.
	#For example, lists are turned into tuples, and dicts like {"A":"B","C":"D"} are turned into ((""))
	#If it can't hash something, it will just use fallback to hash it. By default, though, fallback is 
	def default_fallback(value):
		fansi_print('Warning: fallback_hash was called on value where repr(value)=='+repr(value),'yellow')
		return id(value)
	fallback=fallback or default_fallback
	value_type=type(value)
	try:return hash(value)
	except:pass#This is probably going to happen a lot in this function lol (that's kinda the whole point)
	hasher=__hashers[value_type] if value_type in __hashers else fallback
	return hasher(value)

#region Type-specific hashers
__secret_number=71852436691752251090#Used for hashing things. Don't use this value anywhere! It's not generated dynamically (aka it doesnt use randint) because we want consistent hash values across python processes.
__hashers={}#Used by handy_hash

try:#Attempt to add numpy arrays to the hashers used by handy_hash
	def numpy_hash(x):
		assert isinstance(x,np.ndarray)
		return hash((__secret_number,'numpy_hash',x.tobytes()))#Strings such as 'numpy_hash' are put in here to distinguish this function's output from some other hasher which, by some strange coincidence, generate a (__secret_number,‹same bytestring›) but isnt a numpy array. This same technique is also used in the other hasher functions near this one.
	__hashers[np.ndarray]=numpy_hash
except ImportError:pass

def set_hash(x):
	assert isinstance(x,set)
	return hash((__secret_number,frozenset(x)))
__hashers[set]=set_hash

def dict_hash(x,value_hasher=handy_hash):
	assert isinstance(x,dict)
	set_to_hash=set()
	for key,value in x.items():
		set_to_hash.add(hash((__secret_number,'dict_hash_pair',key,value_hasher(value))))
	return hash((__secret_number,frozenset(set_to_hash)))
__hashers[dict]=dict_hash

def list_hash(x,value_hasher=handy_hash):
	assert isinstance(x,list)
	return hash((__secret_number,'list_hash',tuple(map(value_hasher,x))))
__hashers[list]=list_hash
#endregion


def input_hash(function,*args,**kwargs):
	#Return the hashed input that would be passed to 'function', using handy_hash. This function is used for memoizers. function must be provided for context so that arguments passed that can be passed as either kwargs or args both return the same hash.
	assert callable(function),'Cant hash the inputs of function because function isnt callable and therefore doesnt receive arguments. repr(function)=='+repr(function)
	args=list(args)
	try:
		#Whenever we can, we take things from args and put them in kwargs instead...
		from inspect import getfullargspec
		arg_names=list(getfullargspec(function).args)#This often doesn't work, particularly for built-in functions. TODO this is possible to fix, given that rp can complete argument names of even opencv functions. But for the most part, memoization is used in loops where the function is called with the same signature over and over again, so I'm going to push off improving this till later.
	except:
		#...but it's not a necessity, I GUESS...(if the function is always called the same way)
		arg_names=[]
		pass
	while arg_names and args:
		#Take things from args and put them in kwargs instead, for as many args as we know the names of...
		kwargs[arg_names.pop(0)]=args.pop(0)
	hashes=set()
	for index,arg in enumerate(args):
		hashes.add(hash(('arg',index,handy_hash(arg))))
	for kw   ,arg in kwargs.items() :
		hashes.add(hash(('kwarg',kw ,handy_hash(arg))))
	return hash(frozenset(hashes))


def memoized(function):
	#TODO: when trying to @memoize fibbonacci, and calling fibbonacci(4000), python crashes with SIGABRT. I have no idea why. This function really doesn't use any non-vanilla python code.
	#Uses input_hash to hash function inputs...
	#This is meant to be a permanent cache (as opposed to a LRU aka 'Least Recently Used' cache, which deletes cached values if they haven't been used in a while)
	#If you wish to temporarily memoize a function (let's call if F), you can create a new function cached(F), and put it in a scope that will run out eventually so that there are no memory leaks.
	#Some things can't be hashed by default, I.E. lists etc. But all lists can be converted to tuples, which CAN be hashed. This is where hashers come in. Hashers are meant to help you memoize functions that might have non-hashable arguments, such as numpy arrays.
	cache=dict()
	assert callable(function),'You can\'t memoize something that isn\'t a function (you tried to memoize '+repr(function)+', which isn\'t callable)'
	def output(*args,**kwargs):
		key=input_hash(function,*args,**kwargs)
		if not key in cache:
			cache[key]=function(*args,**kwargs)
		return cache[key]
	return output

#endregion