from openhltspirent.base import Base
class CustomOptions(Base):
	"""DHCPv6 Server custom options

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/devices/protocols/dhcpv6-server/custom-options resource.
	"""
	YANG_NAME = 'custom-options'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(CustomOptions, self).__init__(parent)

	@property
	def OptionType(self):
		"""Option Identifier

		Get an instance of the OptionType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.customoptions.optiontype.optiontype.OptionType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.customoptions.optiontype.optiontype import OptionType
		return OptionType(self)._read()

	@property
	def MessageType(self):
		"""Includes the message option in OFFER, ACK and NAK.
		ADVERTISE   : Include option in the ADVERTISE message.
		REPLY       : Include option in the REPLY message.
		RECONFIGURE	: Include option in the RECONFIGURE message.
		RELAY_REPLY  : Include option in the RELAY_REPLY message.

		Get an instance of the MessageType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.customoptions.messagetype.messagetype.MessageType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.customoptions.messagetype.messagetype import MessageType
		return MessageType(self)._read()

	@property
	def OptionPayload(self):
		"""Option Payload

		Get an instance of the OptionPayload class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.customoptions.optionpayload.optionpayload.OptionPayload)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.customoptions.optionpayload.optionpayload import OptionPayload
		return OptionPayload(self)._read()

	@property
	def Name(self):
		"""The unique name of the DHCPv6 Server custom object.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	def read(self, Name=None):
		"""Get `custom-options` resource(s). Returns all `custom-options` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `custom-options` resource

		Args:
			Name (string): The unique name of the DHCPv6 Server custom object.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `custom-options` resource

		"""
		return self._delete()

