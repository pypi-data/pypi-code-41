from openhltspirent.base import Base
class AsNumber2Byte(Base):
	"""TBD
	"""
	YANG_NAME = 'as-number-2-byte'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(AsNumber2Byte, self).__init__(parent)

	@property
	def AsNumber(self):
		"""2-Byte Autonomous system number

		Get an instance of the AsNumber class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv6.asnumber2byte.asnumber.asnumber.AsNumber)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv6.asnumber2byte.asnumber.asnumber import AsNumber
		return AsNumber(self)._read()

	@property
	def DutAsNumber(self):
		"""2-Byte Autonomous system number configured for the DUT.

		Get an instance of the DutAsNumber class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv6.asnumber2byte.dutasnumber.dutasnumber.DutAsNumber)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv6.asnumber2byte.dutasnumber.dutasnumber import DutAsNumber
		return DutAsNumber(self)._read()

	def create(self):
		"""Create an instance of the `as-number-2-byte` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `as-number-2-byte` resource

		"""
		return self._delete()

