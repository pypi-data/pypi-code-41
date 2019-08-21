from openhltspirent.base import Base
class PacketPayload(Base):
	"""TBD
	"""
	YANG_NAME = 'packet-payload'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"PayloadType": "payload-type"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(PacketPayload, self).__init__(parent)

	@property
	def Payload(self):
		"""TBD

		Get an instance of the Payload class.

		Returns:
			obj(openhltspirent.sessions.config.devicetraffic.packetpayload.payload.payload.Payload)
		"""
		from openhltspirent.sessions.config.devicetraffic.packetpayload.payload.payload import Payload
		return Payload(self)._read()

	@property
	def PayloadType(self):
		"""TBD

		Getter Returns:
			INCREMENT_BYTE | DECREMENT_BYTE | INCREMENT_WORD | DECREMENT_WORD | CUSTOM

		Setter Allows:
			INCREMENT_BYTE | DECREMENT_BYTE | INCREMENT_WORD | DECREMENT_WORD | CUSTOM

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('payload-type')

	def update(self, PayloadType=None):
		"""Update the current instance of the `packet-payload` resource

		Args:
			PayloadType (enumeration): TBD
		"""
		return self._update(locals())

