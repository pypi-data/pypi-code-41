from openhltspirent.base import Base
class MulticastGroups(Base):
	"""A list of multi-cast groups.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/global-multicast-groups/multicast-groups resource.
	"""
	YANG_NAME = 'multicast-groups'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"GroupType": "group-type", "NumberOfGroups": "number-of-groups", "Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(MulticastGroups, self).__init__(parent)

	@property
	def Ipv4Group(self):
		"""IPV4 multicast group details

		Get an instance of the Ipv4Group class.

		Returns:
			obj(openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv4group.ipv4group.Ipv4Group)
		"""
		from openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv4group.ipv4group import Ipv4Group
		return Ipv4Group(self)._read()

	@property
	def Ipv6Group(self):
		"""IPV6 multicast group details

		Get an instance of the Ipv6Group class.

		Returns:
			obj(openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv6group.ipv6group.Ipv6Group)
		"""
		from openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv6group.ipv6group import Ipv6Group
		return Ipv6Group(self)._read()

	@property
	def Name(self):
		"""The unique name of the multicast group object.

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
	def NumberOfGroups(self):
		""" number of multicast groups in each multicast group block.

		Getter Returns:
			uint32

		Setter Allows:
			uint32

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('number-of-groups')

	@property
	def GroupType(self):
		"""Determines which detailed multicast group is active.

		Getter Returns:
			IPV4 | IPV6

		Setter Allows:
			IPV4 | IPV6

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('group-type')

	def read(self, Name=None):
		"""Get `multicast-groups` resource(s). Returns all `multicast-groups` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, NumberOfGroups=None, GroupType=None):
		"""Create an instance of the `multicast-groups` resource

		Args:
			Name (string): The unique name of the multicast group object.
			NumberOfGroups (uint32):  number of multicast groups in each multicast group block.
			GroupType (enumeration): Determines which detailed multicast group is active.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `multicast-groups` resource

		"""
		return self._delete()

	def update(self, NumberOfGroups=None, GroupType=None):
		"""Update the current instance of the `multicast-groups` resource

		Args:
			NumberOfGroups (uint32):  number of multicast groups in each multicast group block.
			GroupType (enumeration): Determines which detailed multicast group is active.
		"""
		return self._update(locals())

