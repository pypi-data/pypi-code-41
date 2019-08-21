from openhltspirent.base import Base
class IgmpHostGroupStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/igmp-host-group-statistics resource.
	"""
	YANG_NAME = 'igmp-host-group-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"DeviceName": "device-name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IgmpHostGroupStatistics, self).__init__(parent)

	@property
	def IgmpHost(self):
		"""TBD

		Get an instance of the IgmpHost class.

		Returns:
			obj(openhltspirent.sessions.statistics.igmphostgroupstatistics.igmphost.igmphost.IgmpHost)
		"""
		from openhltspirent.sessions.statistics.igmphostgroupstatistics.igmphost.igmphost import IgmpHost
		return IgmpHost(self)

	@property
	def DeviceName(self):
		"""Device Name

		Getter Returns:
			string
		"""
		return self._get_value('device-name')

	def read(self, DeviceName=None):
		"""Get `igmp-host-group-statistics` resource(s). Returns all `igmp-host-group-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

