from openhltspirent.base import Base
class DuplicateAddrDetection(Base):
	"""Duplicate address detection. Note that the session will not go bound until the duplicate
	address detection is complete. If duplicate address detection fails, the address will be
	declined and the session will go idle.
	"""
	YANG_NAME = 'duplicate-addr-detection'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(DuplicateAddrDetection, self).__init__(parent)

	@property
	def DadTimeout(self):
		"""Length of time in seconds that must elapse before the Neighbor Solicit times out.

		Get an instance of the DadTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duplicateaddrdetection.dadtimeout.dadtimeout.DadTimeout)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duplicateaddrdetection.dadtimeout.dadtimeout import DadTimeout
		return DadTimeout(self)._read()

	@property
	def DadTransmits(self):
		"""Number of Neighbor Solicit messages to send out per session during duplicate address detection.

		Get an instance of the DadTransmits class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duplicateaddrdetection.dadtransmits.dadtransmits.DadTransmits)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duplicateaddrdetection.dadtransmits.dadtransmits import DadTransmits
		return DadTransmits(self)._read()

	def create(self):
		"""Create an instance of the `duplicate-addr-detection` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `duplicate-addr-detection` resource

		"""
		return self._delete()

