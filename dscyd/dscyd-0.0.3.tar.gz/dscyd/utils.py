import random
import datetime


def now_():
	return datetime.datetime.now()


def now_str_():
	return now_().strftime('%Y%m%d%H%M%S')


def random_name_():
	'''
	   返回一个随机数字字符串
	   可用作唯一id, 订单号之类的
	'''
	return now_str() + str(random.random()).replace('.', '')




