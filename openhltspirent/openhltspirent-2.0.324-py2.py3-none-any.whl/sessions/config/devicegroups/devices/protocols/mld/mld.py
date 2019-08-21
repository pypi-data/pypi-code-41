from openhltspirent.base import Base
class Mld(Base):
	"""TBD
	"""
	YANG_NAME = 'mld'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"MulticastGroup": "multicast-group"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Mld, self).__init__(parent)

	@property
	def Version(self):
		"""Multicast protocol used to manage multicast group memberships
		               MLD_V1  :   Initial multicast protocol version for IPv6, similar to IGMPv2. It is specified in RFC 2710.
		               MLD_V2  :   Version of MLD, specified in RFC 3810, that adds the include and exclude filter functionality as in IGMPv3.

		Get an instance of the Version class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.version.version.Version)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.version.version import Version
		return Version(self)._read()

	@property
	def ForceLeave(self):
		"""Affects all hosts except the last one, which is always required to send an MLDv1 leave report.
		           MLDv1 hosts leaving a multicast group may optionally send a leave report to the all-routers
		           multicast group. This option controls whether or not all hosts are required to send leave reports
		           when leaving the multicast group..
		           TRUE    : Force the MLDv1 host(s) to send a Leave Group message when leaving a multicast group.
		           FALSE	: Do not force the MLDv1 host(s) to send a Leave Group message when leaving a multicast group.

		Get an instance of the ForceLeave class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.forceleave.forceleave.ForceLeave)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.forceleave.forceleave import ForceLeave
		return ForceLeave(self)._read()

	@property
	def ForceRobustJoin(self):
		"""When an MLDv1 host joins a multicast group, it immediately transmits an initial unsolicited membership
		            report for that group, in case it is the first member of that group on the network. In case the initial
		            report gets damaged or lost, a second unsolicited report is recommended be sent out. This option controls
		            whether or not a second report is transmitted.
		           TRUE    : Forces the host to send a second MLDv1 join report.
		           FALSE	: Does not force the host to send a second MLDv1 join report.

		Get an instance of the ForceRobustJoin class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.forcerobustjoin.forcerobustjoin.ForceRobustJoin)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.forcerobustjoin.forcerobustjoin import ForceRobustJoin
		return ForceRobustJoin(self)._read()

	@property
	def ForceSimpleJoin(self):
		"""Forces the MLD host(s) to send a single join report per group. Enabling this option effectively bypasses
		            the RFC defined behavior of sending (Robustness Variable - 1) reports. Otherwise, MLD host(s) will behave
		            according to RFC specification.
		           TRUE    : Force MLD host(s) to send a single join report per group.
		           FALSE	: Default behavior that is compliant to RFC specification. MLD host(s) will send (Robustness Variable - 1) reports.

		Get an instance of the ForceSimpleJoin class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.forcesimplejoin.forcesimplejoin.ForceSimpleJoin)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.forcesimplejoin.forcesimplejoin import ForceSimpleJoin
		return ForceSimpleJoin(self)._read()

	@property
	def InsertChecksumErrors(self):
		"""Controls the insertion of checksum errors into MLD messages by the hardware.
		           TRUE    : MLD checksum of the transmitted packet is flipped by the protocol stack.
		           FALSE	: MLD checksum of the transmitted packet is not modified.

		Get an instance of the InsertChecksumErrors class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.insertchecksumerrors.insertchecksumerrors.InsertChecksumErrors)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.insertchecksumerrors.insertchecksumerrors import InsertChecksumErrors
		return InsertChecksumErrors(self)._read()

	@property
	def InsertLengthErrors(self):
		"""Controls the insertion of message length errors into the MLD messages by the MLD stack.
		           TRUE    : Every MLD packet transmitted by the host will be 2 bytes shorter than normal.
		           FALSE	: MLD packet lengths will not be modified.

		Get an instance of the InsertLengthErrors class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.insertlengtherrors.insertlengtherrors.InsertLengthErrors)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.insertlengtherrors.insertlengtherrors import InsertLengthErrors
		return InsertLengthErrors(self)._read()

	@property
	def PackReports(self):
		"""Allows MLDv2 host(s) to send reports that contain multiple group records,
		           to allow reporting of full current state using fewer packets.
		           TRUE    : Reports will contain multiple group records.
		           FALSE	: An individual report will be sent for each group record.

		Get an instance of the PackReports class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.packreports.packreports.PackReports)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.packreports.packreports import PackReports
		return PackReports(self)._read()

	@property
	def Ipv6TrafficClass(self):
		"""Specifies the value of the Traffic Class field in the IPv6 header.

		Get an instance of the Ipv6TrafficClass class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.ipv6trafficclass.ipv6trafficclass.Ipv6TrafficClass)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.ipv6trafficclass.ipv6trafficclass import Ipv6TrafficClass
		return Ipv6TrafficClass(self)._read()

	@property
	def RobustnessVariable(self):
		"""Robustness Variable, which is used in the calculationof default values for various timers and counters.

		Get an instance of the RobustnessVariable class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.robustnessvariable.robustnessvariable.RobustnessVariable)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.robustnessvariable.robustnessvariable import RobustnessVariable
		return RobustnessVariable(self)._read()

	@property
	def UnsolicitedReportInterval(self):
		"""Time between repetitions of a host's initial report of membership in a group.

		Get an instance of the UnsolicitedReportInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.mld.unsolicitedreportinterval.unsolicitedreportinterval.UnsolicitedReportInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.mld.unsolicitedreportinterval.unsolicitedreportinterval import UnsolicitedReportInterval
		return UnsolicitedReportInterval(self)._read()

	@property
	def MulticastGroup(self):
		"""Reference to list of global multicast groups.

		Getter Returns:
			list(OpenHLTest.Sessions.Config.GlobalMulticastGroups.Name)

		Setter Allows:
			obj(OpenHLTest.Sessions.Config.GlobalMulticastGroups) | list(OpenHLTest.Sessions.Config.GlobalMulticastGroups.Name)

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('multicast-group')

	def update(self, MulticastGroup=None):
		"""Update the current instance of the `mld` resource

		Args:
			MulticastGroup (leafref): Reference to list of global multicast groups.
		"""
		return self._update(locals())

