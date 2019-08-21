from openhltspirent.base import Base
class Igmpv2Query(Base):
	"""IGMPv2 Query message
	"""
	YANG_NAME = 'igmpv2-query'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Igmpv2Query, self).__init__(parent)

	@property
	def GroupAddress(self):
		"""Group IPv4 Address

		Get an instance of the GroupAddress class.

		Returns:
			obj(openhltspirent.sessions.config.porttraffic.frames.igmpv2query.groupaddress.groupaddress.GroupAddress)
		"""
		from openhltspirent.sessions.config.porttraffic.frames.igmpv2query.groupaddress.groupaddress import GroupAddress
		return GroupAddress(self)._read()

	@property
	def Checksum(self):
		"""Checksum value.

		Get an instance of the Checksum class.

		Returns:
			obj(openhltspirent.sessions.config.porttraffic.frames.igmpv2query.checksum.checksum.Checksum)
		"""
		from openhltspirent.sessions.config.porttraffic.frames.igmpv2query.checksum.checksum import Checksum
		return Checksum(self)._read()

	@property
	def MaxResponseTime(self):
		"""Maximum response Time.

		Get an instance of the MaxResponseTime class.

		Returns:
			obj(openhltspirent.sessions.config.porttraffic.frames.igmpv2query.maxresponsetime.maxresponsetime.MaxResponseTime)
		"""
		from openhltspirent.sessions.config.porttraffic.frames.igmpv2query.maxresponsetime.maxresponsetime import MaxResponseTime
		return MaxResponseTime(self)._read()

