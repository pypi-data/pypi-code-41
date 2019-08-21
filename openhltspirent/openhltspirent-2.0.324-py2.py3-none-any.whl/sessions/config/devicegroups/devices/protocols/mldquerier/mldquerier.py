from openhltspirent.base import Base
class MldQuerier(Base):
	"""TBD
	"""
	YANG_NAME = 'mld-querier'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(MldQuerier, self).__init__(parent)

	@property
	def Version(self):
		"""Multicast protocol used to manage multicast group memberships
		               MLD_V1 :   Initial multicast protocol version for IPv6, similar to IGMPv2. It is specified in RFC 2710.
		               MLD_V2	:  Version of MLD, specified in RFC 3810, that adds the include and exclude filter functionality as in IGMPv3.

		Get an instance of the Version class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.version.version.Version)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.version.version import Version
		return Version(self)._read()

	@property
	def Ipv6TrafficClass(self):
		"""Specifies the value of the Traffic Class field in the IPv6 header.

		Get an instance of the Ipv6TrafficClass class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.ipv6trafficclass.ipv6trafficclass.Ipv6TrafficClass)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.ipv6trafficclass.ipv6trafficclass import Ipv6TrafficClass
		return Ipv6TrafficClass(self)._read()

	@property
	def RobustnessVariable(self):
		"""Robustness Variable, which is used in the calculation of default values for various timers and counters.

		Get an instance of the RobustnessVariable class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.robustnessvariable.robustnessvariable.RobustnessVariable)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.robustnessvariable.robustnessvariable import RobustnessVariable
		return RobustnessVariable(self)._read()

	@property
	def LastMemberQueryCount(self):
		"""Value for the Max Response Time field (in milliseconds) that is inserted into Group-Specific and
		Group-and-Source-Specific Query messages in response to Leave Group messages. This value also specifies
		the interval between transmissions of Group-Specific and Group-and-Source-Specific Query messages.

		Get an instance of the LastMemberQueryCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.lastmemberquerycount.lastmemberquerycount.LastMemberQueryCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.lastmemberquerycount.lastmemberquerycount import LastMemberQueryCount
		return LastMemberQueryCount(self)._read()

	@property
	def LastMemberQueryInterval(self):
		"""Maximum amount of time between group-specific query messages, including those sent in response to leave-group messages..

		Get an instance of the LastMemberQueryInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.lastmemberqueryinterval.lastmemberqueryinterval.LastMemberQueryInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.lastmemberqueryinterval.lastmemberqueryinterval import LastMemberQueryInterval
		return LastMemberQueryInterval(self)._read()

	@property
	def QueryInterval(self):
		"""Duration (in seconds) between transmissions of General Query messages. General Query messages are
		used to learn which multicast groups have members on a connected network.

		Get an instance of the QueryInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.queryinterval.queryinterval.QueryInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.queryinterval.queryinterval import QueryInterval
		return QueryInterval(self)._read()

	@property
	def QueryResponseInterval(self):
		"""Value for the Max Response Time field (in milliseconds) that is inserted into the
		General Query messages. This time is the maximum amount allowed for a host to send a
		responding report to the General Query message. This interval must be less than the
		Query Interval.

		Get an instance of the QueryResponseInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.queryresponseinterval.queryresponseinterval.QueryResponseInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.queryresponseinterval.queryresponseinterval import QueryResponseInterval
		return QueryResponseInterval(self)._read()

	@property
	def StartUpQueryCount(self):
		"""Number of queries sent out on startup, separated by the Startup Query Interval.

		Get an instance of the StartUpQueryCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.startupquerycount.startupquerycount.StartUpQueryCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mldquerier.startupquerycount.startupquerycount import StartUpQueryCount
		return StartUpQueryCount(self)._read()

