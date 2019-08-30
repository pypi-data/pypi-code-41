"""
This file is part of the MerchantAPI package.

(c) Miva Inc <https://www.miva.com/>

For the full copyright and license information, please view the LICENSE
file that was distributed with this source code.

$Id: abstract.py 77675 2019-08-29 21:03:50Z gidriss $
"""

import abc


'''
Client - Abstract client class
'''


class Client(object):
	@abc.abstractmethod
	def get_endpoint(self):
		"""
		Get the API endpoint URL.

		:returns: str
		"""

		pass

	@abc.abstractmethod
	def get_api_token(self):
		"""
		Get the api token used to authenticate the request.

		:returns: str
		"""

		pass

	@abc.abstractmethod
	def get_signing_key(self):
		"""
		Get the signing key used to sign requests. Base64 encoded.

		:returns: str
		"""

		pass

	@abc.abstractmethod
	def send(self, request: 'Request') -> 'Response':
		"""
		Send a Request object with callback.

		:param request: Request
		:raises Exception:
		:returns: Response
		"""

		pass

	@abc.abstractmethod
	def generate_auth_header(self, data: str) -> str:
		"""
		Generates the authentication header value.

		:param data: str
		:returns: str
		"""

		pass


'''
Model - Abstract model class
'''


class Model(dict):
	def __init__(self, data: dict = None):
		"""
		Model Constructor.

		:param data:  dict|None
		"""

		super().__init__()
		if data is None:
			data = {}
		self.update(data)

	def get_field(self, name: str, default=None):
		"""
		Get a field value.

		:param name: str
		:param default: mixed
		:return: mixed
		"""

		if not self.has_field(name):
			return default
		return self[name]

	def has_field(self, name: str):
		"""
		Check if a field is defined.

		:param name: str
		:return: bool
		"""

		return name in self

	def set_field(self, name: str, value):
		"""
		Set a field value.

		:param name: str
		:param value: mixed
		:return: Model
		"""

		self[name] = value
		return self

	def to_dict(self):
		"""
		Reduce the model to a dict.
		"""

		return self


'''
Request - Abstract request class
'''


class Request(object):
	SCOPE_STORE = 1
	SCOPE_DOMAIN = 2

	def __init__(self, client: Client = None):
		"""
		Request Constructor.

		:param client: Client
		"""

		self.client = client
		self.store_code = ""
		self.scope = Request.SCOPE_STORE

	def get_function(self):
		"""
		Get the function of the request.

		:returns: str
		"""

		return type(self).__name__

	def get_store_code(self):
		"""
		Get the store code set for the request.

		:returns: str
		"""

		return self.store_code

	def set_store_code(self, store_code):
		"""
		Set the store code for the request.

		:param store_code: str
		:returns: Request
		"""

		self.store_code = store_code
		return self

	def get_scope(self):
		"""
		Get the scope of request.

		:returns: str
		"""

		return self.scope

	def get_client(self) -> 'Client':
		"""
		Return the assigned client.

		:returns: Client
		"""

		return self.client

	def set_client(self, client: 'Client') -> 'Request':
		"""
		Set the Client used for the request.

		:param client: Client
		:returns: Request
		"""

		self.client = client
		return self
	
	def send(self) -> 'Response':
		"""
		Send this object via the assigned client.

		:returns: Response
		:raises Exception: when no client assigned
		"""

		if self.client is None:
			raise Exception('No client assigned to Request')
		return self.client.send(self)

	def to_dict(self) -> dict:
		"""
		Reduce the request to a dict

		:returns: dict
		"""

		data = {}

		if self.scope == Request.SCOPE_STORE and self.store_code is not None:
			data['Store_Code'] = self.store_code

		return data

	def create_response(self, data) -> 'Response':
		"""
		Override this method to create a response for this request.

		:param data: dict
		:returns: Response
		"""

		return Response(self, data)


'''
Response - Abstract response class
'''


class Response(object):
	def __init__(self, request, data: dict):
		"""
		Response constructor.

		:param request: Request
		:param data: dict
		"""

		self.request = request
		self.data = data

	def is_success(self):
		"""
		Check if the response was a success.

		:returns: bool
		"""

		return True if 'success' in self.data and self.data['success'] in (1, True) else False

	def is_error(self):
		"""
		Check if the response was a error.

		:returns: bool
		"""

		return not self.is_success()

	def get_error_message(self):
		"""
		Get the error message.

		:returns: str|None
		"""

		return self.data['error_message'] if 'error_message' in self.data else None

	def get_error_code(self):
		"""
		Get the error code.

		:returns: str|None
		"""

		return self.data['error_code'] if 'error_code' in self.data else None

	def get_error_input_count(self):
		"""
		Get the number of input errors.

		:returns: int
		"""

		return self.data['input_errors'] if 'input_errors' in self.data else 0

	def get_error_fields(self):
		"""
		Get the fields which encountered a validation error.

		:returns: list
		"""

		return self.data['error_fields'] if 'error_fields' in self.data else []

	def get_error_field(self):
		"""
		Get the field which triggered the error.

		:returns: str|None
		"""

		return self.data['error_field'] if 'error_field' in self.data else None

	def get_error_field_message(self):
		"""
		Get the error message associated with the error field that cause the error.
		:returns: str|None
		"""

		return self.data['error_field_message'] if 'error_field_message' in self.data else None

	def is_list_error(self):
		"""
		Check if the error response is a list error.

		:returns: bool
		"""

		return self.data['list_error'] if 'list_error' in self.data else False

	def is_validation_error(self):
		"""
		Check if the error response is a validation error.

		:returns: bool
		"""

		return self.data['validation_error'] if 'validation_error' in self.data else False

	def is_input_error(self):
		"""
		Check if the error response is a input error.

		:returns: bool
		"""

		return self.data['input_errors'] if 'input_errors' in self.data else False

	def get_errors(self):
		"""
		Get the error messages associated with the response.

		:returns: list
		"""

		return self.data['errors'] if 'errors' in self.data else []

	def get_data(self):
		"""
		Get the underlying data object.

		:returns: dict
		"""

		return self.data

	def get_request(self):
		"""
		Get the initiating Request object.

		:returns: Request
		"""

		return self.request
