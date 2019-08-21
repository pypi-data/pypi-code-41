from openhltspirent.base import Base
class MldPortStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/mld-port-statistics resource.
	"""
	YANG_NAME = 'mld-port-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'port-name'
	YANG_PROPERTY_MAP = {"TxV2ChangeToIncludeModeCount": "tx-v2-change-to-include-mode-count", "TxV2QueryCount": "tx-v2-query-count", "RxMldLengthErrorCount": "rx-mld-length-error-count", "RxUnknownTypeCount": "rx-unknown-type-count", "TxFrameCount": "tx-frame-count", "RxGroupAndSourceSpecificQueryCount": "rx-group-and-source-specific-query-count", "TxGroupAndSourceSpecificQueryCount": "tx-group-and-source-specific-query-count", "RxV2QueryCount": "rx-v2-query-count", "RxV2ReportCount": "rx-v2-report-count", "RxGroupSpecificQueryCount": "rx-group-specific-query-count", "TxV2ModeIsExcludeCount": "tx-v2-mode-is-exclude-count", "RxMldChecksumErrorCount": "rx-mld-checksum-error-count", "RxV1ReportCount": "rx-v1-report-count", "TxV2AllowNewSourcesCount": "tx-v2-allow-new-sources-count", "TxV1QueryCount": "tx-v1-query-count", "RxFrameCount": "rx-frame-count", "TxV2ReportCount": "tx-v2-report-count", "TxV1ReportCount": "tx-v1-report-count", "TxV2ModeIsIncludeCount": "tx-v2-mode-is-include-count", "TimeStamp": "time-stamp", "TxV2BlockOldSourcesCount": "tx-v2-block-old-sources-count", "TxGroupSpecificQueryCount": "tx-group-specific-query-count", "TxV2ChangeToExcludeModeCount": "tx-v2-change-to-exclude-mode-count", "TxGeneralQueryCount": "tx-general-query-count", "RxGeneralQueryCount": "rx-general-query-count", "TxStopListenGroupCount": "tx-stop-listen-group-count", "RxV1QueryCount": "rx-v1-query-count", "PortName": "port-name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(MldPortStatistics, self).__init__(parent)

	@property
	def PortName(self):
		"""An abstract test port name

		Getter Returns:
			string
		"""
		return self._get_value('port-name')

	@property
	def RxFrameCount(self):
		"""Total number of MLD frames received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-frame-count')

	@property
	def RxGeneralQueryCount(self):
		"""Total number of multicast general queries received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-general-query-count')

	@property
	def RxGroupAndSourceSpecificQueryCount(self):
		"""Group- and source-specific queries are sent by a multicast router whenever a host leave a specific
		source of a group. This is to make sure that there are no other hosts of that source and group.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-group-and-source-specific-query-count')

	@property
	def RxGroupSpecificQueryCount(self):
		"""Group-Specific Query is used to learn if a particular group has any members on an attached network.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-group-specific-query-count')

	@property
	def RxMldChecksumErrorCount(self):
		"""Total number of MLD messages received with checksum errors.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-mld-checksum-error-count')

	@property
	def RxMldLengthErrorCount(self):
		"""Total number of MLD messages received with length errors.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-mld-length-error-count')

	@property
	def RxUnknownTypeCount(self):
		"""Total number of frames of unknown type received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-unknown-type-count')

	@property
	def RxV1QueryCount(self):
		"""Total number of MLDv1 queries received. Routers use Multicast Listener Query messages to query
		a subnet for multicast listeners.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v1-query-count')

	@property
	def RxV1ReportCount(self):
		"""MLDv1 reports are sent to multicast routers to indicate that hosts have listeners interested in
		joining multicast groups whose multicast address is listed in the router's list.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v1-report-count')

	@property
	def RxV2QueryCount(self):
		"""Total number of MLDv2 queries received. Routers use Multicast Listener Query messages to query
		a subnet for multicast listeners.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v2-query-count')

	@property
	def RxV2ReportCount(self):
		"""MLDv1 are used to report interest in receiving multicast traffic for a specific multicast address
		or to respond to a Multicast Listener Query message..

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v2-report-count')

	@property
	def TimeStamp(self):
		"""Timestamp in seconds of last statistic update.

		Getter Returns:
			uint32
		"""
		return self._get_value('time-stamp')

	@property
	def TxFrameCount(self):
		"""Total number of MLD frames transmitted.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-frame-count')

	@property
	def TxGeneralQueryCount(self):
		"""General Queries are used to learn which multicast addresses have listeners on an attached link.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-general-query-count')

	@property
	def TxGroupAndSourceSpecificQueryCount(self):
		"""Group- and source-specific queries are sent by a multicast router whenever a host leave a specific
		source of a group. This is to make sure that there are no other hosts of that source and group.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-group-and-source-specific-query-count')

	@property
	def TxGroupSpecificQueryCount(self):
		"""Total number of MLD group specific queries transmitted. The Group-Specific Query is used to learn
		if a particular group has any members on an attached network..

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-group-specific-query-count')

	@property
	def TxStopListenGroupCount(self):
		"""Stop listening events occur when the node stops listening to an address on the interface.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-stop-listen-group-count')

	@property
	def TxV1QueryCount(self):
		"""MLDv1 Membership Queries are sent by IP multicast routers to query the multicast reception
		state of neighboring interfaces.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v1-query-count')

	@property
	def TxV1ReportCount(self):
		"""MLDv1 reports are sent to multicast routers to indicate that hosts have listeners interested
		in joining multicast groups whose multicast address is listed in the router's list.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v1-report-count')

	@property
	def TxV2QueryCount(self):
		"""MLDv2 Membership Queries are sent by IP multicast routers to query the multicast reception state
		of neighboring interfaces.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-query-count')

	@property
	def TxV2ReportCount(self):
		"""MLDv2 reports are sent to multicast routers to indicate that hosts have listeners interested in
		joining multicast groups whose multicast address is listed in the router's list.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-report-count')

	@property
	def TxV2AllowNewSourcesCount(self):
		"""A Source-List-Change Record (SLCR) indicating the group's associated sources have changed such
		that data from a new set of sources are to be received

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-allow-new-sources-count')

	@property
	def TxV2BlockOldSourcesCount(self):
		"""A Source-List-Change Record (SLCR) indicating the group's associated sources have changed such
		that data from an existing set of sources are not required..

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-block-old-sources-count')

	@property
	def TxV2ChangeToExcludeModeCount(self):
		"""A Filter-Mode-Change Record (FMCR) indicating the filter-mode of the reception state has changed
		to exclude mode.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-change-to-exclude-mode-count')

	@property
	def TxV2ChangeToIncludeModeCount(self):
		"""A Filter-Mode-Change Record (FMCR) indicating the filter-mode of the reception state has changed
		to include mode

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-change-to-include-mode-count')

	@property
	def TxV2ModeIsExcludeCount(self):
		"""A Current-State Record (CSR) indicating the current reception state with respect to 1 multicast
		group at a given interface. The state contains the exclude filter mode.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-mode-is-exclude-count')

	@property
	def TxV2ModeIsIncludeCount(self):
		"""A Current-State Record (CSR) indicating the current reception state with respect to 1 multicast
		group at a given interface. The state contains the include filter mode.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-mode-is-include-count')

	def read(self, PortName=None):
		"""Get `mld-port-statistics` resource(s). Returns all `mld-port-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(PortName)

