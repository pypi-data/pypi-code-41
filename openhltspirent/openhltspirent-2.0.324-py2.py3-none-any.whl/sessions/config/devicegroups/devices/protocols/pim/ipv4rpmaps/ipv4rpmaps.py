from openhltspirent.base import Base
class Ipv4RpMaps(Base):
	"""A list of IPv4 Group-RP (Rendezvous Point) mapping.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/devices/protocols/pim/ipv4-rp-maps resource.
	"""
	YANG_NAME = 'ipv4-rp-maps'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "MulticastGroup": "multicast-group"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv4RpMaps, self).__init__(parent)

	@property
	def RpAddress(self):
		"""IP address of the RP router, a PIM-SM router configured as the root of a multicast distribution tree.

		Get an instance of the RpAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4rpmaps.rpaddress.rpaddress.RpAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4rpmaps.rpaddress.rpaddress import RpAddress
		return RpAddress(self)._read()

	@property
	def RpHoldTime(self):
		"""Hold time specified by the candidate Rendezvous Point (RP) router.

		Get an instance of the RpHoldTime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4rpmaps.rpholdtime.rpholdtime.RpHoldTime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4rpmaps.rpholdtime.rpholdtime import RpHoldTime
		return RpHoldTime(self)._read()

	@property
	def RpPriority(self):
		"""Priority specified by the candidate Rendezvous Point (RP) router.

		Get an instance of the RpPriority class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4rpmaps.rppriority.rppriority.RpPriority)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.pim.ipv4rpmaps.rppriority.rppriority import RpPriority
		return RpPriority(self)._read()

	@property
	def Name(self):
		"""The unique name of the IPv4 Group-RP (Rendezvous Point) object.

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
		"""Get `ipv4-rp-maps` resource(s). Returns all `ipv4-rp-maps` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, MulticastGroup=None):
		"""Create an instance of the `ipv4-rp-maps` resource

		Args:
			Name (string): The unique name of the IPv4 Group-RP (Rendezvous Point) object.
			MulticastGroup (leafref): Reference to list of global multicast groups.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `ipv4-rp-maps` resource

		"""
		return self._delete()

	def update(self, MulticastGroup=None):
		"""Update the current instance of the `ipv4-rp-maps` resource

		Args:
			MulticastGroup (leafref): Reference to list of global multicast groups.
		"""
		return self._update(locals())

