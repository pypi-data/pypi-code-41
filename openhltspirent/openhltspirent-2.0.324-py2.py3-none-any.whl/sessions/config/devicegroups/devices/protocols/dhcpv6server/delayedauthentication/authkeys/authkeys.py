from openhltspirent.base import Base
class AuthKeys(Base):
	"""A list of Authentication Keys.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/devices/protocols/dhcpv6-server/delayed-authentication/auth-keys resource.
	"""
	YANG_NAME = 'auth-keys'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"KeyValueType": "key-value-type", "KeyId": "key-id", "KeyValue": "key-value", "Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(AuthKeys, self).__init__(parent)

	@property
	def Name(self):
		"""The unique name of authentication key.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	@property
	def KeyId(self):
		"""Key identifier that identified the key used to generate the HMAC-MD5 value.

		Getter Returns:
			int32

		Setter Allows:
			int32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('key-id')

	@property
	def KeyValueType(self):
		"""Key used to generate the HMAC-MD5 value.

		Getter Returns:
			ASCII | HEX

		Setter Allows:
			ASCII | HEX

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('key-value-type')

	@property
	def KeyValue(self):
		"""Key used to generate the HMAC-MD5 value.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('key-value')

	def read(self, Name=None):
		"""Get `auth-keys` resource(s). Returns all `auth-keys` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, KeyId=None, KeyValueType=None, KeyValue=None):
		"""Create an instance of the `auth-keys` resource

		Args:
			Name (string): The unique name of authentication key.
			KeyId (int32): Key identifier that identified the key used to generate the HMAC-MD5 value.
			KeyValueType (enumeration): Key used to generate the HMAC-MD5 value.
			KeyValue (string): Key used to generate the HMAC-MD5 value.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `auth-keys` resource

		"""
		return self._delete()

	def update(self, KeyId=None, KeyValueType=None, KeyValue=None):
		"""Update the current instance of the `auth-keys` resource

		Args:
			KeyId (int32): Key identifier that identified the key used to generate the HMAC-MD5 value.
			KeyValueType (enumeration): Key used to generate the HMAC-MD5 value.
			KeyValue (string): Key used to generate the HMAC-MD5 value.
		"""
		return self._update(locals())

