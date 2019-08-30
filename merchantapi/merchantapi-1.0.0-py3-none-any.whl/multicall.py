"""
This file is part of the MerchantAPI package.

(c) Miva Inc <https://www.miva.com/>

For the full copyright and license information, please view the LICENSE
file that was distributed with self source code.

$Id: multicall.py 77667 2019-08-29 19:18:13Z gidriss $
"""

from merchantapi.abstract import Request
from merchantapi.abstract import Response
from merchantapi.abstract import Client

""" 
Handles sending multiple Request objects as one request.
:see: https://docs.miva.com/json-api/multicall
"""


class MultiCallRequest(Request):
	def __init__(self, client: Client = None, requests: list = None):
		"""
		MultiCallRequest Constructor.

		:param client: Client
		:param requests: list[Request]
		"""

		super().__init__(client)
		self.requests = []
		self.use_iterations = False

		if isinstance(requests, list):
			self.add_requests(requests)

	def add_request(self, request: Request) -> 'MultiCallRequest':
		"""
		Add a request to be sent.

		:param request: Request
		:returns: MultiCallRequest
		"""

		if isinstance(request, MultiCallRequest):
			for r in request.get_requests():
				r.add_request(r)
		else:
			self.requests.append(request)
		return self

	def get_requests(self) -> list:
		"""
		Get the requests to be sent.

		:returns: list
		"""

		return self.requests

	def set_requests(self, requests: list):
		"""
		Set and override the requests to be sent.

		:param requests: list
		:returns: MultiCallRequest
		"""

		self.requests.clear()
		for r in requests:
			self.add_request(r)
		return self

	def add_requests(self, requests: list):
		"""
		Add requests to be sent.
		
		:param :Array requests
		:returns:MultiCallRequest
		"""

		for r in requests:
			self.add_request(r)
		return self

	def operation(self, request: Request = None, shared_data: dict = None) -> 'MultiCallOperation':
		"""
		Create an operation instance and add it to the request.

		:param request: Request|list[Request]|None
		:param shared_data: dict|None
		:returns:
		"""

		operation = MultiCallOperation(request, shared_data)
		self.add_operation(operation)
		return operation

	def add_operation(self, operation: 'MultiCallOperation') -> 'MultiCallRequest':
		"""
		Add a operation to be sent.

		:param operation: MultiCallOperation
		:returns: MultiCallRequest
		"""

		self.requests.append(operation)
		return self

	def add_operations(self, operations: list) -> 'MultiCallRequest':
		"""
		Add an array of operations.

		:param: list[MultiCallOperation]
		:returns: MultiCallRequest
		"""

		for o in operations:
			self.add_operation(o)
		return self

	def to_dict(self) -> dict:
		"""
		Reduce the request to an Object.

		:returns: dict
		"""

		data = {
			'Operations': []
		}

		for r in self.requests:
			if isinstance(r, MultiCallRequest):
				data['Operations'].append(r.to_dict())
			else:
				merged = r.to_dict()
				merged.update({
					'Function': self.requests[0].get_function()
				})
				data['Operations'].append(merged)
		return data

	def create_response(self, data: dict) -> 'MultiCallResponse':
		"""
		:param data: dict
		"""

		return MultiCallResponse(self, data)

	# noinspection PyTypeChecker
	def send(self) -> 'MultiCallResponse':
		return super().send()


""" 
Handles multicall response.
:see: https://docs.miva.com/json-api/multicall
"""


class MultiCallResponse(Response):
	def __init__(self, request: MultiCallRequest, data: dict):
		"""
		MultiCallResponse constructor.

		:param request: Request
		:param data: dict
		"""

		super().__init__(request, data)

		self.data = data
		self.responses = []

		if not self.is_success():
			return

		for i, r in enumerate(request.get_requests(), 0):
			if isinstance(r, MultiCallOperation):
				for i2, r2 in enumerate(r.get_requests(), 0):
					self.add_response(r2.create_response(self.data[i][i2]))
			else:
				self.add_response(r.create_response(self.data[i]))

	def is_success(self):
		"""
		:returns: bool
		"""

		return isinstance(self.data, list)

	def get_responses(self) -> list:
		"""
		Get the responses.

		:returns: list[Response]
		"""

		return self.responses

	def add_response(self, response: Response) -> 'MultiCallResponse':
		"""
		Add a response.

		:param response: Response
		:returns: MultiCallResponse
		:raises Exception:
		"""

		self.responses.append(response)
		return self

	def set_responses(self, responses: list) -> 'MultiCallResponse':
		"""
		Set and overwrite the responses.

		:param responses: list[Response]
		:returns: MultiCallResponse
		"""

		for response in responses:
			self.add_response(response)
		return self


""" 
Handles creation of an Operation with Iterations.

:see: MultiCallRequest
"""


class MultiCallOperation:
	def __init__(self, request: Request = None, shared_data: dict = None):
		"""
		MultiCallOperation Constructor.

		:param request: Request or list[Request]
		:param shared_data: dict
		"""

		self.requests = []

		if shared_data is not dict:
			shared_data = {}

		self.shared_data = shared_data

		if isinstance(request, Request):
			self.add_request(request)
		elif isinstance(request, list):
			for r in request:
				self.add_request(r)

	def get_function(self):
		if len(self.requests) > 0:
			return self.requests[0].get_function()
		return None

	def add_request(self, request: Request) -> 'MultiCallOperation':
		"""
		Add a request iteration.

		:param request: Request
		:returns: MultiCallOperation
		:raises Exception:
		"""

		if isinstance(request, MultiCallRequest):
			raise Exception('Can\'t nest a MultiCallRequest in a MultiCallOperation')
		self.requests.append(request)
		return self

	def get_requests(self):
		"""
		Get the request iterations.

		:returns: list
		"""

		return self.requests

	def set_requests(self, requests: list) -> 'MultiCallOperation':
		"""
		Set and override the request iterations.

		:param requests: list[Request]
		:returns: MultiCallOperation
		:raises Exception:
		"""

		self.requests = []
		for r in requests:
			self.add_request(r)
		return self

	def add_requests(self, requests: list) -> 'MultiCallOperation':
		"""
		Add an array of requests iterations.

		:param requests: list[Request]
		:returns: MultiCallOperation
		:raises Exception:
		"""

		for r in requests:
			self.add_request(r)
		return self

	def add_shared_data(self, key: str, value) -> 'MultiCallOperation':
		"""
		Add a shared data value for key.

		:param key: str
		:param value: str|dict
		:returns: MultiCallOperation
		"""

		self.shared_data[key] = value
		return self

	def set_shared_data(self, values: dict) -> 'MultiCallOperation':
		"""
		Set the shared data object.

		:param values: dict
		:returns: MultiCallOperation
		"""

		self.shared_data = values
		return self

	def get_shared_data(self) -> dict:
		"""
		Get the shared data between the iterations.

		:returns: dict
		"""

		return self.shared_data

	def to_dict(self) -> dict:
		"""
		Reduce the operation to a dict

		:returns: dict
		"""

		if not len(self.requests):
			return {}

		data = self.shared_data.copy()
		data.update({
			'Function': self.requests[0].get_function(),
			'Iterations': []
		})

		for r in self.requests:
			data['Iterations'].append(r.to_dict())
		return data

