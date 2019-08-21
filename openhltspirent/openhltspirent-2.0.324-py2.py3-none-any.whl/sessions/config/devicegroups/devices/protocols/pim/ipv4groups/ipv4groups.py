from openhltspirent.base import Base
class Ipv4Groups(Base):
	"""A list of IPv4 Multicast Group block.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/devices/protocols/pim/ipv4-groups resource.
	"""
	YANG_NAME = 'ipv4-groups'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "MulticastGroup": "multicast-group"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv4Groups, self).__init__(parent)

	@property
	def GroupType(self):
		"""Group designation. Notation represents a routing entry.
		STARG	: Default group-specific multicast group set type that is used in
		       Join/Prune messages with (*,G) source list entries.
		SG	    : Group-specific multicast group set type that is used in Join/Prune
		        messages with (S,G) source-specific source list entries.
		STARSTARRP	: Wildcard multicast group set type. This is used in (*,*,RP)
		           Join/Prune messages.

		Get an instance of the GroupType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.grouptype.grouptype.GroupType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.grouptype.grouptype import GroupType
		return GroupType(self)._read()

	@property
	def RpAddress(self):
		"""Rendezvous Point Router (RPR) address = a PIM router configured as the root of a
		multicast distribution tree. Required for (*,*,RP) and (*,G) groups.

		Get an instance of the RpAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.rpaddress.rpaddress.RpAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.rpaddress.rpaddress import RpAddress
		return RpAddress(self)._read()

	@property
	def JoinSourceAddress(self):
		"""The source block (Source Start IP Address and Source Prefix Length)represents the source
		address range from which the (S,G) grouprequests traffic. Each Join/Prune message corresponding
		to this (S,G) groupincludes the specified source address in its Join source list (or inthe
		Prune source list, if the group is being deleted or made inactive).

		Get an instance of the JoinSourceAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.joinsourceaddress.joinsourceaddress.JoinSourceAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.joinsourceaddress.joinsourceaddress import JoinSourceAddress
		return JoinSourceAddress(self)._read()

	@property
	def JoinSourcePrefix(self):
		"""Prefix length of the joined sourceIP address

		Get an instance of the JoinSourcePrefix class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.joinsourceprefix.joinsourceprefix.JoinSourcePrefix)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.joinsourceprefix.joinsourceprefix import JoinSourcePrefix
		return JoinSourcePrefix(self)._read()

	@property
	def EnablingPruning(self):
		"""Enables including the optional Prune source for (*,G) groups.
		TRUE    : Enables Prune source.
		FALSE	: Disables Prune Source.

		Get an instance of the EnablingPruning class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.enablingpruning.enablingpruning.EnablingPruning)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.enablingpruning.enablingpruning import EnablingPruning
		return EnablingPruning(self)._read()

	@property
	def PruneSourceAddress(self):
		"""The Prune source address block (Prune IP Address and Prune Prefix Length)represents the
		source range from which (*,G) groups request thatNO traffic be sent (i.e., do not send traffic
		to this group from this source).

		Get an instance of the PruneSourceAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.prunesourceaddress.prunesourceaddress.PruneSourceAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.prunesourceaddress.prunesourceaddress import PruneSourceAddress
		return PruneSourceAddress(self)._read()

	@property
	def PruneSourcePrefix(self):
		"""Prefix length of the pruned source IP address

		Get an instance of the PruneSourcePrefix class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.prunesourceprefix.prunesourceprefix.PruneSourcePrefix)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4groups.prunesourceprefix.prunesourceprefix import PruneSourcePrefix
		return PruneSourcePrefix(self)._read()

	@property
	def Name(self):
		"""The unique name of the PIM IPv4 group block object.

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
		"""Get `ipv4-groups` resource(s). Returns all `ipv4-groups` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, MulticastGroup=None):
		"""Create an instance of the `ipv4-groups` resource

		Args:
			Name (string): The unique name of the PIM IPv4 group block object.
			MulticastGroup (leafref): Reference to list of global multicast groups.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `ipv4-groups` resource

		"""
		return self._delete()

	def update(self, MulticastGroup=None):
		"""Update the current instance of the `ipv4-groups` resource

		Args:
			MulticastGroup (leafref): Reference to list of global multicast groups.
		"""
		return self._update(locals())

