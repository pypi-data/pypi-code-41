# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 14:34:05 2019

@author: TS
"""


from ts_response import response


if __name__ == "__main__":
	print("start getting response")
	while(True):
		try:
			response_value = response()
			print("response_value: ", response_value)
		except Exception as ex:
			print("错误: ", ex)