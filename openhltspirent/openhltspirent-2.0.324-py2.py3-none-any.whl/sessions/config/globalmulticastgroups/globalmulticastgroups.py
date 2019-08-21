from openhltspirent.base import Base
class GlobalMulticastGroups(Base):
	"""A list of multi-cast groups.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/global-multicast-groups resource.
	"""
	YANG_NAME = 'global-multicast-groups'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(GlobalMulticastGroups, self).__init__(parent)

	@property
	def MulticastGroups(self):
		"""A list of multi-cast groups.

		Get an instance of the MulticastGroups class.

		Returns:
			obj(openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.multicastgroups.MulticastGroups)
		"""
		from openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.multicastgroups import MulticastGroups
		return MulticastGroups(self)

	@property
	def Name(self):
		"""The unique name of the group of multicast groups object.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	def read(self, Name=None):
		"""Get `global-multicast-groups` resource(s). Returns all `global-multicast-groups` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `global-multicast-groups` resource

		Args:
			Name (string): The unique name of the group of multicast groups object.
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `global-multicast-groups` resource

		"""
		return self._delete()

