#coding:utf8
from flask import request
from mongoengine.queryset.visitor import Q
import traceback

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def queryset(model):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):
			request.queryset = model.objects.all()
			return func(*args, **kwargs)
		return wrapper2
	return wrapper1


def get_query_string():

	params = request.environ['QUERY_STRING'].split("&")

	l = []

	if params != ['']:
		l = [
			{
				p.split('=')[0]:p.split('=')[1]
			} for p in params
		]
	else:
		l = []
	d = {}
	for ll in l:
		d.update(ll)

	return d

def get_queryset(model):
	if not hasattr(request,'queryset'):
		request.queryset = model.objects()



def ordering(model,key='ordering',fields=[]):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):

			d = get_query_string()

			get_queryset(model)

			if d.get(key) in fields:
					request.queryset = request.queryset.order_by(d.get(key))
			return func(*args, **kwargs)
		return wrapper2
	return wrapper1



def searching(model,key='searching',fields=[]):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):

			get_queryset(model)

			keys = [v+'__contains' for v in fields]

			_dict = {}
			_list = [{k:request.args.get(key)} for k in keys]
			arg = [
				Q(**_dict) for _dict in _list
			]

			_arg = None
			for a in arg:
				if _arg == None:
					_arg = a
				else:
					_arg = _arg|a

			if request.args.get(key):
				request.queryset = request.queryset.filter(_arg)

			return func(*args, **kwargs)
		return wrapper2
	return wrapper1



def paginating(model,page_field='page',page_size_field='page_size',force=False):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):

			get_queryset(model)

			page = int(request.args.get(page_field,1))

			page_size = int(request.args.get(page_size_field,5))	

			request.page_count = len(request.queryset)

			try:
				pass
				#request.queryset.paginating(page=page, per_page=page_size)
				request.queryset = request.queryset[(page-1)*page_size:page*page_size]
			except Exception as e:
				raise e
				logger.error(e)
				if force is False:
					request.queryset = []

			return func(*args, **kwargs)
		return wrapper2
	return wrapper1



def retrieve(model,force=True,code=-200):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):
			if force == True:
				try:
					request.retrieve = model.objects.get(id=kwargs.get('id'))
				except:
					return {
						'code':code,
						'msg':'retrieve fail! id: {}'.format(kwargs.get('id'))
					}
			else:
				retrieveequest.retrieve = None
			return func(*args, **kwargs)
		return wrapper2
	return wrapper1



from mongoengine.fields import ReferenceField,ListField,EmbeddedDocumentField
from bson.objectid import ObjectId
def update(model,parser,fields=[]):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):
			kwargs_ = parser.parse_args()
			_kwargs = {}
			for index,field in enumerate(fields):
				if issubclass(model._fields.get(field).__class__, ReferenceField):
					logger.error('is ReferenceField')
					value = ObjectId(kwargs_.get(field))
				elif issubclass(model._fields.get(field).__class__, ListField):
					value = [ObjectId(kwargs_.get(f)) for f in field]
				else:
					value = kwargs_.get(field)
				_kwargs[field]=value
			request._kwargs = _kwargs
			return func(*args, **kwargs)
		return wrapper2
	return wrapper1



from mongoengine.fields import ReferenceField,ListField,EmbeddedDocumentField
from bson.objectid import ObjectId
def create(model,parser,fields=[],code=-100):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):
			kwargs_ = parser.parse_args()
			_kwargs = {}
			for index,field in enumerate(fields):
				if issubclass(model._fields.get(field).__class__, ReferenceField):
					if kwargs_.get(field):
						try:
							value = ObjectId(kwargs_.get(field))
						except:
							return {'code':code,'msg':traceback.format_exc().split('\n')[-2:-1][0],}
					else:
						value = None
				elif issubclass(model._fields.get(field).__class__, ListField) and \
					issubclass(model._fields.get(field).field.__class__,ReferenceField):
					if kwargs_.get(field):
						value = [ObjectId(kwargs_.get(f)) for f in kwargs_.get(field)]
					else:
						value = None
				else:
					value = kwargs_.get(field)

				if value:
					_kwargs[field]=value
			request._kwargs = _kwargs
			return func(*args, **kwargs)
		return wrapper2
	return wrapper1


from mongoengine.fields import ReferenceField,ListField
from bson.objectid import ObjectId
def get_kwargs(model,parser,fields=[]):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):
			kwargs_ = parser.parse_args()
			_kwargs = {}
			for index,field in enumerate(fields):
				if issubclass(model._fields.get(field).__class__, ReferenceField):
					if kwargs_.get(field):
						value = ObjectId(kwargs_.get(field))
					else:
						value = None
				elif issubclass(model._fields.get(field).__class__, ListField):
					logger.error(kwargs_.get(field))
					if kwargs_.get(field):
						value = [ObjectId(kwargs_.get(f)) for f in kwargs_.get(field)]
					else:
						value = None
				else:
					value = kwargs_.get(field)

				if value:
					_kwargs[field]=value
			request._kwargs = _kwargs
			return func(*args, **kwargs)
		return wrapper2
	return wrapper1



def filting(model,f):
	def wrapper1(func):
		def wrapper2(*args, **kwargs):
			get_queryset(model)
			f()
			return func(*args, **kwargs)
		return wrapper2
	return wrapper1


from mongoengine.queryset.visitor import Q
def filting2(domains):

	options = {
		'!=':'ne',
		'<':'lt',
		'<=':'lte',
		'>':'gt',
		'>=':'gte',
		#'not':'not',
		'in':'in',
		'nin':'nin',
		#'mod':'mod',
		#'v':'all',
		#'size':'size',
		#'exist':'exist',

		'like':'contain',
	}


	q = None
	for index,domain in enumerate(domains):

		if index % 2 != 1:

			#
			# 2层及以上
			#
			if type(domains[index][0]) == tuple:
				_q = filting2(domains[index])

			#
			# 1层
			#
			if type(domain[0]) == str:
				key = str(domain[0]) + '__' + options.get(domain[1])
				value = domain[2]
				_q = Q(**{key:value})

			if q == None:
				q = _q
			else:
				if domains[index-1] == '|':
					q = (q|_q)
				else:
					q = (q&_q)

	return q


#
# example of filting2
#

# input
domains = (
	(
		(
			('create_ts','>','2019-01-01 00:00:00'),
			'|',
			('category','in',[2,]),
		),
		'&',
		('create_ts','>','2018-01-01 00:00:00'),
	),
	'|',
	('text','like','hahaha'),
)

# output
(
	(
		(
			Q(**{'create_ts__gt': '2019-01-01 00:00:00'}) 
			| 
			Q(**{'category__in': [2]})
		) 
		& 
		Q(**{'create_ts__gt': '2018-01-01 00:00:00'})
	) 
	| 
	Q(**{'text__contain': 'hahaha'})
)

#print(filting2(domains))