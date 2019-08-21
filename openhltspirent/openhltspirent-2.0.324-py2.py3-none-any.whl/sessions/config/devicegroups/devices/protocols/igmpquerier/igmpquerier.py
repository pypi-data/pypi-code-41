from openhltspirent.base import Base
class IgmpQuerier(Base):
	"""TBD
	"""
	YANG_NAME = 'igmp-querier'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IgmpQuerier, self).__init__(parent)

	@property
	def Version(self):
		"""Multicast protocol used to manage multicast group memberships
		               IGMP_V1 :   Second version (obsoleted IGMPv0) of IGMP, specified in RFC 1112.
		               IGMP_V2	:   IGMP version specified in RFC 2236. Improved IGMP version that adds
		                           leave messages, shortening the amount of time required for a router to
		                           determine that no stations are in a particular group.
		               IGMP_V3	:   Specified in RFC 3376, this major revision of the IGMP protocol adds the
		                           ability to specify the source(s) that a receiver is willing to listen to.

		Get an instance of the Version class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.version.version.Version)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.version.version import Version
		return Version(self)._read()

	@property
	def Ipv4DontFragment(self):
		"""Controls the fragmentation of packets larger than the MTU (Maximum Transmission Unit) size.
		           TRUE    :Packets larger than the allowable MTU are not fragmented.
		           FALSE	:Packets larger than the allowable MTU will be divided into fragments.

		Get an instance of the Ipv4DontFragment class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.ipv4dontfragment.ipv4dontfragment.Ipv4DontFragment)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.ipv4dontfragment.ipv4dontfragment import Ipv4DontFragment
		return Ipv4DontFragment(self)._read()

	@property
	def RouterAlert(self):
		"""Enable/Disable router alert option in the IPV4 header of IGMP packet.
		           TRUE    :force the IPv4 header to add Router Alert Option information in IGMP Query packet.
		           FALSE	:the IPv4 header don't add Router Alert Option information in IGMP Query packet.

		Get an instance of the RouterAlert class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.routeralert.routeralert.RouterAlert)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.routeralert.routeralert import RouterAlert
		return RouterAlert(self)._read()

	@property
	def IgnoreV1Reports(self):
		"""Ignore IGMPv1 Report messages. Only IGMPv2 Reportmessages are accepted by the router.
		           TRUE    : Ignores IGMPv1 messages.
		           FALSE	: Processes IGMPv1 messages

		Get an instance of the IgnoreV1Reports class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.ignorev1reports.ignorev1reports.IgnoreV1Reports)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.ignorev1reports.ignorev1reports import IgnoreV1Reports
		return IgnoreV1Reports(self)._read()

	@property
	def Ipv4Tos(self):
		"""Provides an indication of the quality of service wanted.

		Get an instance of the Ipv4Tos class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.ipv4tos.ipv4tos.Ipv4Tos)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.ipv4tos.ipv4tos import Ipv4Tos
		return Ipv4Tos(self)._read()

	@property
	def RobustnessVariable(self):
		"""Robustness Variable, which is used in the calculation of default values for various timers and counters.

		Get an instance of the RobustnessVariable class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.robustnessvariable.robustnessvariable.RobustnessVariable)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.robustnessvariable.robustnessvariable import RobustnessVariable
		return RobustnessVariable(self)._read()

	@property
	def LastMemberQueryCount(self):
		"""Value for the Max Response Time field (in milliseconds) that is inserted into Group-Specific and
		Group-and-Source-Specific Query messages in response to Leave Group messages. This value also specifies
		the interval between transmissions of Group-Specific and Group-and-Source-Specific Query messages.

		Get an instance of the LastMemberQueryCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.lastmemberquerycount.lastmemberquerycount.LastMemberQueryCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.lastmemberquerycount.lastmemberquerycount import LastMemberQueryCount
		return LastMemberQueryCount(self)._read()

	@property
	def LastMemberQueryInterval(self):
		"""Maximum amount of time between group-specific query messages, including those sent in response to leave-group messages..

		Get an instance of the LastMemberQueryInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.lastmemberqueryinterval.lastmemberqueryinterval.LastMemberQueryInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.lastmemberqueryinterval.lastmemberqueryinterval import LastMemberQueryInterval
		return LastMemberQueryInterval(self)._read()

	@property
	def QueryInterval(self):
		"""Duration (in seconds) between transmissions of General Query messages. General Query messages are
		used to learn which multicast groups have members on a connected network.

		Get an instance of the QueryInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.queryinterval.queryinterval.QueryInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.queryinterval.queryinterval import QueryInterval
		return QueryInterval(self)._read()

	@property
	def QueryResponseInterval(self):
		"""Value for the Max Response Time field (in milliseconds) that is inserted into the
		General Query messages. This time is the maximum amount allowed for a host to send a
		responding report to the General Query message. This interval must be less than the
		Query Interval.

		Get an instance of the QueryResponseInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.queryresponseinterval.queryresponseinterval.QueryResponseInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.queryresponseinterval.queryresponseinterval import QueryResponseInterval
		return QueryResponseInterval(self)._read()

	@property
	def StartUpQueryCount(self):
		"""Number of queries sent out on startup, separated by the Startup Query Interval.

		Get an instance of the StartUpQueryCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.startupquerycount.startupquerycount.StartUpQueryCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmpquerier.startupquerycount.startupquerycount import StartUpQueryCount
		return StartUpQueryCount(self)._read()

