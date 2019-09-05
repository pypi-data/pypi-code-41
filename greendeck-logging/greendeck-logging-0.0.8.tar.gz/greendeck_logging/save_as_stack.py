
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from datetime import datetime,timedelta
import time
import os
import sys
from bson.objectid import ObjectId
from .logging_function import message_value


class GdLoggingStack:
	'''
	initializing the gd logging the required variable
	'''
	def __init__(self, LOG_ECS_HOST, service_name, LOG_ECS_INDEX = 'gdlogging', LOG_ECS_TYPE = '_doc', username = None, password = None, ):
		try:
			self.ecs_host = LOG_ECS_HOST
			self.ecs_index = LOG_ECS_INDEX
			self.ecs_type = LOG_ECS_TYPE
			self.service_name = service_name
			self.file_name = sys.argv[0]
			self.username = username
			self.password = password
			self.stack_data = []

			if username==None and password==None:
				try:
					self.es = Elasticsearch(self.ecs_host)
				except Exception as e:
					print("\n Error in connecting to elastic search ")
					raise e
			else:
				try:
					self.es = Elasticsearch(self.ecs_host, http_auth = (self.username, self.password))
				except Exception as e:
					print("\n Authentication Failed ")
					raise e
		except Exception as e:
			print(" Gd logging is not connected to elasticsearch 'CONNECTION FAILED' ")
			pass

	def base_log_info(self,log_type):
		'''
		base data that will for all logging data
		'''
		try:
			user_name = os.getlogin()
		except:
			user_name = ""
		
		try:
			system_name = os.uname()[1]
		except:
			system_name = ""
		
		try:
			os_name = os.uname()[0]
		except:
			os_name = ""
		try:
			file_name = self.file_name
		except:
			file_name = ""

		standard_info = {
			"service_name" : self.service_name,
			"log_type" : log_type,
			"created_at" : datetime.now(),
			"meta" : {
				"file_name" : file_name,
				"user_name" : user_name,
				"system_name" : system_name,
				"os_name": os_name
				}
			}

		return standard_info

	def debug(self, message, info = None, value = int(1)):
		'''
		It save the data for debug info
		'''
		try:
			log_level = 'debug'
			message_counter = message_value(message, info, value)
			data = self.base_log_info(log_level)
			data["debug"] = message_counter
			self.stack_data.append(data)
		except Exception as e:
			pass

		#return r


	def counter_status(self, status_code, info = None, value = int(1)):
		'''
		This is for record the counter status like 200, 404 etc.

		'''
		try:
			log_type =  'info'
			data = self.base_log_info(log_type)
			message_counter = message_value(status_code, info, value)
			message_counter['counter_type'] = 'status'
			data['status'] = message_counter
			self.stack_data.append(data)

		except Exception as e:
			pass
			# raise e


		#return res

	def counter_message(self, message, info = None, value = int(1)):
		'''
		gdl.counter_message({"message":"bert_count","value":bert_count})
		'''
		try:
			log_type =  'info'
			data = self.base_log_info(log_type)
			message_counter = message_value(message, info, value)
			data['counter_message'] = message_counter
			self.stack_data.append(data)
		except Exception as e:
			pass
			# raise e

		#return r

	def error(self,error_message, info = None, value = int(1)):
		try:
			log_type = "error"
			data = self.base_log_info(log_type)
			message_counter = message_value(error_message, info, value)
			data['error'] = message_counter
			self.stack_data.append(data)

		except Exception as e:
			pass
			# raise e

		#return r
	def counter_website(self, website_id, message, info = {}, value = int(1)):
		try:
			log_type = 'info'
			data =  self.base_log_info(log_type)
			message_counter = message_value(message, info, value)
			message_counter['website_id'] = website_id
			data['counter_website'] = message_counter
			self.stack_data.append(data)

		except Exception as e:
			pass
			# raise e


	def gendata(self, posts):
	    for post in posts:
	    	yield {
	            "_index": self.ecs_index,
	            "_type": self.ecs_type,
	            "_source": post,
	        	}

	def push(self):
		if len(self.stack_data) ==0:
			return "nothing to push"
		else:
			helpers.bulk(self.es, self.gendata(self.stack_data))
			try:
				print("Transported documents to ecs_index: %s; Current Count: %d" % (self.ecs_index, self.es.count(index=self.ecs_index)["count"]))
				_ = self.clear()

			except Exception as e:
				print("Error counting documents in ECS: "+ str(e))
				pass

	def clear(self):
		self.stack_data = []
		return  len(self.stack_data)

	def count(self):
		count = len(self.stack_data)
		return count

	def show_one(self):
		count = len(self.stack_data)
		if count==0:
			return "nothing to show"
		else:
			return self.stack_data[0]

	def show(self):
		count = len(self.stack_data)
		if count==0:
			return "nothing to show"
		else:
			return self.stack_data
