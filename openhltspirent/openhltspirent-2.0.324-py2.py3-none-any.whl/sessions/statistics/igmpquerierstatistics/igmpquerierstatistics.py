from openhltspirent.base import Base
class IgmpQuerierStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/igmp-querier-statistics resource.
	"""
	YANG_NAME = 'igmp-querier-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"DeviceName": "device-name", "IgmpQuerierVersion": "igmp-querier-version", "RouterState": "router-state", "TimeStamp": "time-stamp", "RxUnknownTypeCount": "rx-unknown-type-count", "TxFrameCount": "tx-frame-count", "RxFrameCount": "rx-frame-count", "RxIgmpChecksumErrorCount": "rx-igmp-checksum-error-count", "HostState": "host-state", "PortName": "port-name", "RxIgmpLengthErrorCount": "rx-igmp-length-error-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IgmpQuerierStatistics, self).__init__(parent)

	@property
	def DeviceName(self):
		"""Device Name

		Getter Returns:
			string
		"""
		return self._get_value('device-name')

	@property
	def PortName(self):
		"""An abstract test port name

		Getter Returns:
			string
		"""
		return self._get_value('port-name')

	@property
	def HostState(self):
		"""State of the IGMP Querier block

		Getter Returns:
			UNDEFINED | NON_MEMBER | JOINING | MEMBER | LEAVING
		"""
		return self._get_value('host-state')

	@property
	def IgmpQuerierVersion(self):
		"""IGMP version the device block is currently operating as

		Getter Returns:
			V1 | V2 | V3
		"""
		return self._get_value('igmp-querier-version')

	@property
	def RouterState(self):
		"""State of the IGMP Host

		Getter Returns:
			UNDEFINED | NOT_STARTED | UP
		"""
		return self._get_value('router-state')

	@property
	def RxFrameCount(self):
		"""Total number of IGMP frames received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-frame-count')

	@property
	def TxFrameCount(self):
		"""Total number of IGMP frames transmitted.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-frame-count')

	@property
	def RxIgmpChecksumErrorCount(self):
		"""Total number of IGMP messages received with checksum errors.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-igmp-checksum-error-count')

	@property
	def RxIgmpLengthErrorCount(self):
		"""Total number of IGMP messages received with length errors.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-igmp-length-error-count')

	@property
	def RxUnknownTypeCount(self):
		"""Total number of frames of unknown type received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-unknown-type-count')

	@property
	def TimeStamp(self):
		"""Timestamp in seconds of last statistic update.

		Getter Returns:
			uint32
		"""
		return self._get_value('time-stamp')

	def read(self, DeviceName=None):
		"""Get `igmp-querier-statistics` resource(s). Returns all `igmp-querier-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

