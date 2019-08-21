from openhltspirent.base import Base
class MldHostGroupStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/mld-host-group-statistics resource.
	"""
	YANG_NAME = 'mld-host-group-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"DeviceName": "device-name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(MldHostGroupStatistics, self).__init__(parent)

	@property
	def MldHost(self):
		"""TBD

		Get an instance of the MldHost class.

		Returns:
			obj(openhltspirent.sessions.statistics.mldhostgroupstatistics.mldhost.mldhost.MldHost)
		"""
		from openhltspirent.sessions.statistics.mldhostgroupstatistics.mldhost.mldhost import MldHost
		return MldHost(self)

	@property
	def DeviceName(self):
		"""Device Name

		Getter Returns:
			string
		"""
		return self._get_value('device-name')

	def read(self, DeviceName=None):
		"""Get `mld-host-group-statistics` resource(s). Returns all `mld-host-group-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

