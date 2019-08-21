from openhltspirent.base import Base
class Ipv6RegisterGroups(Base):
	"""A list of IPv6 PIM Registers block.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/devices/protocols/pim/ipv6-register-groups resource.
	"""
	YANG_NAME = 'ipv6-register-groups'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "MulticastGroup": "multicast-group"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv6RegisterGroups, self).__init__(parent)

	@property
	def RpAddress(self):
		"""IP address of the RP router, a PIM-SM router configured as the root of a multicast distribution tree.

		Get an instance of the RpAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.rpaddress.rpaddress.RpAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.rpaddress.rpaddress import RpAddress
		return RpAddress(self)._read()

	@property
	def FixedModeCount(self):
		"""Number of PIM null register messages to send.

		Get an instance of the FixedModeCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.fixedmodecount.fixedmodecount.FixedModeCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.fixedmodecount.fixedmodecount import FixedModeCount
		return FixedModeCount(self)._read()

	@property
	def RegisterTransmitInterval(self):
		"""Number of seconds to wait between sending Register messages.

		Get an instance of the RegisterTransmitInterval class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.registertransmitinterval.registertransmitinterval.RegisterTransmitInterval)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.registertransmitinterval.registertransmitinterval import RegisterTransmitInterval
		return RegisterTransmitInterval(self)._read()

	@property
	def MulticastGroupToSourceDistribution(self):
		"""PIM Multicast Group to Source Distribution.
		PAIR    : One source is paired with one multicast group
		BACKBONE : Each source is meshed with all the multicast group addresses

		Get an instance of the MulticastGroupToSourceDistribution class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.multicastgrouptosourcedistribution.multicastgrouptosourcedistribution.MulticastGroupToSourceDistribution)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.multicastgrouptosourcedistribution.multicastgrouptosourcedistribution import MulticastGroupToSourceDistribution
		return MulticastGroupToSourceDistribution(self)._read()

	@property
	def RegisterTransmitMode(self):
		"""PIM will send a fixed number of register messages or send messages continuously..
		FIXED	    : PIM will send a fixed number of register messages
		CONTINUOUS	: PIM will send a register messages continuously

		Get an instance of the RegisterTransmitMode class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.registertransmitmode.registertransmitmode.RegisterTransmitMode)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.registertransmitmode.registertransmitmode import RegisterTransmitMode
		return RegisterTransmitMode(self)._read()

	@property
	def MulticastSourceAddress(self):
		"""Address of the first multicast source.

		Get an instance of the MulticastSourceAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.multicastsourceaddress.multicastsourceaddress.MulticastSourceAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.multicastsourceaddress.multicastsourceaddress import MulticastSourceAddress
		return MulticastSourceAddress(self)._read()

	@property
	def MulticastSourcePrefix(self):
		"""Length of the prefix of the address of the multicast source

		Get an instance of the MulticastSourcePrefix class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.multicastsourceprefix.multicastsourceprefix.MulticastSourcePrefix)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv6registergroups.multicastsourceprefix.multicastsourceprefix import MulticastSourcePrefix
		return MulticastSourcePrefix(self)._read()

	@property
	def Name(self):
		"""The unique name of the IPv6 PIM Registers block object.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

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

	def read(self, Name=None):
		"""Get `ipv6-register-groups` resource(s). Returns all `ipv6-register-groups` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, MulticastGroup=None):
		"""Create an instance of the `ipv6-register-groups` resource

		Args:
			Name (string): The unique name of the IPv6 PIM Registers block object.
			MulticastGroup (leafref): Reference to list of global multicast groups.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `ipv6-register-groups` resource

		"""
		return self._delete()

	def update(self, MulticastGroup=None):
		"""Update the current instance of the `ipv6-register-groups` resource

		Args:
			MulticastGroup (leafref): Reference to list of global multicast groups.
		"""
		return self._update(locals())

