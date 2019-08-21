from openhltspirent.base import Base
class Pim(Base):
	"""TBD
	"""
	YANG_NAME = 'pim'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Pim, self).__init__(parent)

	@property
	def PimMode(self):
		"""Multicast protocol used to manage multicast group memberships
		           SM	: Router supports all three group types: (S,G), (*,*,RP), and (*,G).
		           SSM	: Router will not send Join/Prune messages for groups that are not (S,G).
		               You cannot add (*,*,RP) or (*,G) groups.

		Get an instance of the PimMode class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.pimmode.pimmode.PimMode)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.pimmode.pimmode import PimMode
		return PimMode(self)._read()

	@property
	def IpVersion(self):
		"""IP version to be used for communication with the neighbor.
		               IPV4	: Uses IP version 4.
		               IPV6	: Uses IP version 6.

		Get an instance of the IpVersion class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipversion.ipversion.IpVersion)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipversion.ipversion import IpVersion
		return IpVersion(self)._read()

	@property
	def GenIdMode(self):
		"""In PIM, routers send the Generation ID as an option in the Hello messages.
		            Every time a router starts up, it selects a random number. The router uses
		            that number as long as it remains operational. If the Generation ID changes,
		            it is an indication to the neighboring routers that this router has gone through
		            a shutdown-restart cycle. This causes the neighboring routers to reset their
		            databases and start fresh. If the generation ID mode is Fixed, it emulates normal
		            PIM router behavior. Incremental or Random means Spirent TestCenter will send
		            different generation IDs in successive Hello messages, causing the DUTs to reset
		            and rebuild their databases often.
		            The interactive menu option, Increment Generation ID, sends one Hello message with
		            incremented Generation ID
		               FIXED	    : Emulates normal PIM router behavior.
		               INCREMENT   : Spirent TestCenter sends different Generation IDs in successive Hello messages,
		                           incrementing by one each time.
		               RANDOM	    : Spirent TestCenter sends different Generation IDs in successive Hello messages,
		                           selecting a random number each time.

		Get an instance of the GenIdMode class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.genidmode.genidmode.GenIdMode)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.genidmode.genidmode import GenIdMode
		return GenIdMode(self)._read()

	@property
	def BiDirOption(self):
		"""Include the BI-DIR option in Hellomessages.
		           TRUE    : Enables sending BI-DIR option in Hello messages.
		           FALSE	: Disables sending BI-DIR option in Hello messages.

		Get an instance of the BiDirOption class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.bidiroption.bidiroption.BiDirOption)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.bidiroption.bidiroption import BiDirOption
		return BiDirOption(self)._read()

	@property
	def BootstrapMessageInterval(self):
		"""Frequency in seconds with which bootstrap messages are transmitted.

		Get an instance of the BootstrapMessageInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.bootstrapmessageinterval.bootstrapmessageinterval.BootstrapMessageInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.bootstrapmessageinterval.bootstrapmessageinterval import BootstrapMessageInterval
		return BootstrapMessageInterval(self)._read()

	@property
	def BsrPriority(self):
		"""8-bit priority of the emulated bootstrap router (BSR).

		Get an instance of the BsrPriority class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.bsrpriority.bsrpriority.BsrPriority)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.bsrpriority.bsrpriority import BsrPriority
		return BsrPriority(self)._read()

	@property
	def DrPriority(self):
		"""Designated Router (DR) priority of this router. This value is sent as an option in the Hello message.

		Get an instance of the DrPriority class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.drpriority.drpriority.DrPriority)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.drpriority.drpriority import DrPriority
		return DrPriority(self)._read()

	@property
	def EnableBsr(self):
		"""PIM routers enabled for bootstrap routing (BSR) functionality generate Bootstrap messages periodically.
		           TRUE    : Enables sending Bootstrap messages.
		           FALSE	: Disables sending Bootstrap messages.

		Get an instance of the EnableBsr class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.enablebsr.enablebsr.EnableBsr)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.enablebsr.enablebsr import EnableBsr
		return EnableBsr(self)._read()

	@property
	def HelloHoldtime(self):
		"""Hold time in seconds to keep neighbor state alive.

		Get an instance of the HelloHoldtime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.helloholdtime.helloholdtime.HelloHoldtime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.helloholdtime.helloholdtime import HelloHoldtime
		return HelloHoldtime(self)._read()

	@property
	def HelloInterval(self):
		"""Periodic interval in seconds for Hello messages.

		Get an instance of the HelloInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.hellointerval.hellointerval.HelloInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.hellointerval.hellointerval import HelloInterval
		return HelloInterval(self)._read()

	@property
	def JoinPruneHoldtime(self):
		"""Hold time in seconds to advertise in Join/Prune messages.

		Get an instance of the JoinPruneHoldtime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.joinpruneholdtime.joinpruneholdtime.JoinPruneHoldtime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.joinpruneholdtime.joinpruneholdtime import JoinPruneHoldtime
		return JoinPruneHoldtime(self)._read()

	@property
	def JoinPruneInterval(self):
		"""Frequency in seconds at which Join/Prune messages are sent.

		Get an instance of the JoinPruneInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.joinpruneinterval.joinpruneinterval.JoinPruneInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.joinpruneinterval.joinpruneinterval import JoinPruneInterval
		return JoinPruneInterval(self)._read()

	@property
	def NullRegisterOnlyMode(self):
		"""Determines whether this PIM router supports full emulation or only NULL register messages.
		   TRUE    : This PIM router only supports NULL register messages.
		   FALSE	: This PIM router supports the full emulation.

		Get an instance of the NullRegisterOnlyMode class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.nullregisteronlymode.nullregisteronlymode.NullRegisterOnlyMode)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.nullregisteronlymode.nullregisteronlymode import NullRegisterOnlyMode
		return NullRegisterOnlyMode(self)._read()

	@property
	def NeighborIpv4Address(self):
		"""IPv4 upstream neighbor address to be used in Join/Prune messages.

		Get an instance of the NeighborIpv4Address class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.neighboripv4address.neighboripv4address.NeighborIpv4Address)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.neighboripv4address.neighboripv4address import NeighborIpv4Address
		return NeighborIpv4Address(self)._read()

	@property
	def NeighborIpv6Address(self):
		"""IPv6 upstream neighbor address to be used in Join/Prune messages.

		Get an instance of the NeighborIpv6Address class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.neighboripv6address.neighboripv6address.NeighborIpv6Address)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.neighboripv6address.neighboripv6address import NeighborIpv6Address
		return NeighborIpv6Address(self)._read()

	@property
	def Ipv4Groups(self):
		"""A list of IPv4 Multicast Group block.

		Get an instance of the Ipv4Groups class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.ipv4groups.Ipv4Groups)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.ipv4groups import Ipv4Groups
		return Ipv4Groups(self)

	@property
	def Ipv6Groups(self):
		"""A list of IPv6 Multicast Group block.

		Get an instance of the Ipv6Groups class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6groups.ipv6groups.Ipv6Groups)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6groups.ipv6groups import Ipv6Groups
		return Ipv6Groups(self)

	@property
	def Ipv4RpMaps(self):
		"""A list of IPv4 Group-RP (Rendezvous Point) mapping.

		Get an instance of the Ipv4RpMaps class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4rpmaps.ipv4rpmaps.Ipv4RpMaps)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4rpmaps.ipv4rpmaps import Ipv4RpMaps
		return Ipv4RpMaps(self)

	@property
	def Ipv6RpMaps(self):
		"""A list of IPv6 Group-RP (Rendezvous Point) mapping.

		Get an instance of the Ipv6RpMaps class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6rpmaps.ipv6rpmaps.Ipv6RpMaps)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6rpmaps.ipv6rpmaps import Ipv6RpMaps
		return Ipv6RpMaps(self)

	@property
	def Ipv4RegisterGroups(self):
		"""A list of IPv4 PIM Registers block.

		Get an instance of the Ipv4RegisterGroups class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4registergroups.ipv4registergroups.Ipv4RegisterGroups)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4registergroups.ipv4registergroups import Ipv4RegisterGroups
		return Ipv4RegisterGroups(self)

	@property
	def Ipv6RegisterGroups(self):
		"""A list of IPv6 PIM Registers block.

		Get an instance of the Ipv6RegisterGroups class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.ipv6registergroups.Ipv6RegisterGroups)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.ipv6registergroups import Ipv6RegisterGroups
		return Ipv6RegisterGroups(self)

