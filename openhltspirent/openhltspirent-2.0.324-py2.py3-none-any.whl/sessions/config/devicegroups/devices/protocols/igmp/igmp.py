from openhltspirent.base import Base
class Igmp(Base):
	"""TBD
	"""
	YANG_NAME = 'igmp'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"MulticastGroup": "multicast-group"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Igmp, self).__init__(parent)

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
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.version.version.Version)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.version.version import Version
		return Version(self)._read()

	@property
	def ForceLeave(self):
		"""Affects all hosts except the last one, which is always required to send an IGMPv2 leave report.
		           IGMPv2 hosts leaving a multicast group may optionally send a leave report to the all-routers multicast group.
		           The force-leave flag controls whether or not all hosts are required to send leave reports when leaving the multicast group.
		           TRUE    : Force the IGMPv2 host(s) to send a Leave Group message when leaving a multicast group.
		           FALSE	: Do not force the IGMPv2 host(s) to send a Leave Group message when leaving a multicast group.

		Get an instance of the ForceLeave class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.forceleave.forceleave.ForceLeave)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.forceleave.forceleave import ForceLeave
		return ForceLeave(self)._read()

	@property
	def ForceSimpleJoin(self):
		"""Forces the IGMP host(s) to send a single join report per group.
		           Enabling this option effectively bypasses the RFC defined behavior of
		           sending (Robustness Variable - 1) reports. Otherwise, IGMP host(s) will
		           behave according to RFC specification.
		           TRUE    :Force IGMP host(s) to send a single join report per group.
		           FALSE	:Default behavior that is compliant to RFC specification. IGMP host(s) will send (Robustness Variable - 1) reports.

		Get an instance of the ForceSimpleJoin class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.forcesimplejoin.forcesimplejoin.ForceSimpleJoin)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.forcesimplejoin.forcesimplejoin import ForceSimpleJoin
		return ForceSimpleJoin(self)._read()

	@property
	def InsertChecksumErrors(self):
		"""Controls the insertion of checksum errors into IGMP messages by the hardware.
		           TRUE    :IGMP checksum of the transmitted packet is flipped by the protocol stack.
		           FALSE	:IGMP checksum of the transmitted packet is not modified.

		Get an instance of the InsertChecksumErrors class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.insertchecksumerrors.insertchecksumerrors.InsertChecksumErrors)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.insertchecksumerrors.insertchecksumerrors import InsertChecksumErrors
		return InsertChecksumErrors(self)._read()

	@property
	def InsertLengthErrors(self):
		"""Controls the insertion of message length errors into the IGMP messages by the IGMP stack.
		           TRUE    :Every IGMP packet transmitted by the host will be 2 bytes shorter than normal.
		           FALSE	:IGMP packet lengths will not be modified.

		Get an instance of the InsertLengthErrors class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.insertlengtherrors.insertlengtherrors.InsertLengthErrors)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.insertlengtherrors.insertlengtherrors import InsertLengthErrors
		return InsertLengthErrors(self)._read()

	@property
	def Ipv4DontFragment(self):
		"""Controls the fragmentation of packets larger than the MTU (Maximum Transmission Unit) size.
		           TRUE    :Packets larger than the allowable MTU are not fragmented.
		           FALSE	:Packets larger than the allowable MTU will be divided into fragments.

		Get an instance of the Ipv4DontFragment class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.ipv4dontfragment.ipv4dontfragment.Ipv4DontFragment)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.ipv4dontfragment.ipv4dontfragment import Ipv4DontFragment
		return Ipv4DontFragment(self)._read()

	@property
	def PackReports(self):
		"""Allows IGMPv3 host(s) to send reports that contain multiple group records,
		           to allow reporting of full current state using fewer packets..
		           TRUE    :Reports will contain multiple group records.
		           FALSE	:An individual report will be sent for each group record.

		Get an instance of the PackReports class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.packreports.packreports.PackReports)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.packreports.packreports import PackReports
		return PackReports(self)._read()

	@property
	def RouterAlert(self):
		"""Enable/Disable router alert option in the IPV4 header of IGMP packet.
		           TRUE    :Reports will contain multiple group records.
		           FALSE	:An individual report will be sent for each group record.

		Get an instance of the RouterAlert class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.routeralert.routeralert.RouterAlert)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.routeralert.routeralert import RouterAlert
		return RouterAlert(self)._read()

	@property
	def Ipv4Tos(self):
		"""Provides an indication of the quality of service wanted.

		Get an instance of the Ipv4Tos class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.ipv4tos.ipv4tos.Ipv4Tos)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.ipv4tos.ipv4tos import Ipv4Tos
		return Ipv4Tos(self)._read()

	@property
	def ForceRobustJoin(self):
		"""When an IGMPv1/IGMPv2 host joins a multicast group, it immediately transmits an initial unsolicited
		           membership report for that group, in case it is the first member of that group on the network.
		           In case the initial report gets damaged or lost, a second unsolicited report is recommended be sent out.
		           The force-robust-join flag controls whether or not a second report is transmitted.
		           TRUE    :Forces the host to send a second IGMPv1/IGMPv2 join report.
		           FALSE	:Does not force the host to send a second IGMPv1/IGMPv2 join report.

		Get an instance of the ForceRobustJoin class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.forcerobustjoin.forcerobustjoin.ForceRobustJoin)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.forcerobustjoin.forcerobustjoin import ForceRobustJoin
		return ForceRobustJoin(self)._read()

	@property
	def RobustnessVariable(self):
		"""Robustness Variable, which is used in the calculationof default values for various timers and counters.

		Get an instance of the RobustnessVariable class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.robustnessvariable.robustnessvariable.RobustnessVariable)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.robustnessvariable.robustnessvariable import RobustnessVariable
		return RobustnessVariable(self)._read()

	@property
	def UnsolicitedReportInterval(self):
		"""Time between repetitions of a host's initial report of membership in a group.

		Get an instance of the UnsolicitedReportInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.unsolicitedreportinterval.unsolicitedreportinterval.UnsolicitedReportInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.unsolicitedreportinterval.unsolicitedreportinterval import UnsolicitedReportInterval
		return UnsolicitedReportInterval(self)._read()

	@property
	def V1RouterPresentTimeout(self):
		"""Amount of time a host must wait after hearing a Version 1 Query before it may send any IGMPv2 messages.

		Get an instance of the V1RouterPresentTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.v1routerpresenttimeout.v1routerpresenttimeout.V1RouterPresentTimeout)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.igmp.v1routerpresenttimeout.v1routerpresenttimeout import V1RouterPresentTimeout
		return V1RouterPresentTimeout(self)._read()

	@property
	def MulticastGroup(self):
		"""Reference to list of global multicast groups.

		Getter Returns:
			list(OpenHLTest.Sessions.Config.GlobalMulticastGroups.MulticastGroups.Name)

		Setter Allows:
			obj(OpenHLTest.Sessions.Config.GlobalMulticastGroups.MulticastGroups) | list(OpenHLTest.Sessions.Config.GlobalMulticastGroups.MulticastGroups.Name)

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('multicast-group')

	def update(self, MulticastGroup=None):
		"""Update the current instance of the `igmp` resource

		Args:
			MulticastGroup (leafref): Reference to list of global multicast groups.
		"""
		return self._update(locals())

