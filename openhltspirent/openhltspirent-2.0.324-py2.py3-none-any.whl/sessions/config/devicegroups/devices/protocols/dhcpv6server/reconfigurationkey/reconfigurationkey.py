from openhltspirent.base import Base
class ReconfigurationKey(Base):
	"""Specify reconfiguration keys
	"""
	YANG_NAME = 'reconfiguration-key'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(ReconfigurationKey, self).__init__(parent)

	@property
	def KeyValue(self):
		"""Key used for reconfigure key authentication.

		Get an instance of the KeyValue class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.reconfigurationkey.keyvalue.keyvalue.KeyValue)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.reconfigurationkey.keyvalue.keyvalue import KeyValue
		return KeyValue(self)._read()

	@property
	def KeyValueType(self):
		"""Reconfigure key value type.
		ASCII : Reconfigure key value is specified in ASCII.
		HEX	  : Reconfigure key value is specified in hexadecimal.

		Get an instance of the KeyValueType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.reconfigurationkey.keyvaluetype.keyvaluetype.KeyValueType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.reconfigurationkey.keyvaluetype.keyvaluetype import KeyValueType
		return KeyValueType(self)._read()

	def create(self):
		"""Create an instance of the `reconfiguration-key` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `reconfiguration-key` resource

		"""
		return self._delete()

