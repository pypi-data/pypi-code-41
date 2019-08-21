from openhltspirent.base import Base
class IgmpPortStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/igmp-port-statistics resource.
	"""
	YANG_NAME = 'igmp-port-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'port-name'
	YANG_PROPERTY_MAP = {"TxV2QueryCount": "tx-v2-query-count", "RxUnknownTypeCount": "rx-unknown-type-count", "TxV3BlockOldSourcesCount": "tx-v3-block-old-sources-count", "TxLeaveGroupCount": "tx-leave-group-count", "TxFrameCount": "tx-frame-count", "TxV3ReportCount": "tx-v3-report-count", "RxV3ReportCount": "rx-v3-report-count", "TxV3ChangeToExcludeModeCount": "tx-v3-change-to-exclude-mode-count", "RxIgmpChecksumErrorCount": "rx-igmp-checksum-error-count", "RxGroupAndSourceSpecificQueryCount": "rx-group-and-source-specific-query-count", "TxGroupAndSourceSpecificQueryCount": "tx-group-and-source-specific-query-count", "PortName": "port-name", "RxV2QueryCount": "rx-v2-query-count", "RxV2ReportCount": "rx-v2-report-count", "RxGroupSpecificQueryCount": "rx-group-specific-query-count", "TxV3ModeIsExcludeCount": "tx-v3-mode-is-exclude-count", "RxV1ReportCount": "rx-v1-report-count", "TxV1QueryCount": "tx-v1-query-count", "RxFrameCount": "rx-frame-count", "TxV2ReportCount": "tx-v2-report-count", "TxV1ReportCount": "tx-v1-report-count", "TimeStamp": "time-stamp", "TxV3QueryCount": "tx-v3-query-count", "TxV3AllowNewSourcesCount": "tx-v3-allow-new-sources-count", "TxV3ChangeToIncludeModeCount": "tx-v3-change-to-include-mode-count", "TxGroupSpecificQueryCount": "tx-group-specific-query-count", "RxIgmpLengthErrorCount": "rx-igmp-length-error-count", "TxGeneralQueryCount": "tx-general-query-count", "TxV3ModeIsIncludeCount": "tx-v3-mode-is-include-count", "RxGeneralQueryCount": "rx-general-query-count", "RxV1QueryCount": "rx-v1-query-count", "RxV3QueryCount": "rx-v3-query-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(IgmpPortStatistics, self).__init__(parent)

	@property
	def PortName(self):
		"""An abstract test port name

		Getter Returns:
			string
		"""
		return self._get_value('port-name')

	@property
	def RxFrameCount(self):
		"""Total number of IGMP frames received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-frame-count')

	@property
	def RxGeneralQueryCount(self):
		"""Total number of IGMP General Queries received. The General Query is used
		to learn which groups have members on an attached network.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-general-query-count')

	@property
	def RxGroupAndSourceSpecificQueryCount(self):
		"""Group- and source-specific queries are sent by a multicast router whenever a
		host leave a specific source of a group. This is to make sure that there are no
		other hosts of that source and group.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-group-and-source-specific-query-count')

	@property
	def RxGroupSpecificQueryCount(self):
		"""Total number of IGMP group-specific queries transmitted. The Group-Specific Query
		is used to learn if a particular group has any members on an attached network..

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-group-specific-query-count')

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
	def RxV1QueryCount(self):
		"""IGMPv1 Host membership query messages are sent to discover which group have members.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v1-query-count')

	@property
	def RxV1ReportCount(self):
		"""IGMPv1 reports are sent to multicast routers to indicate that hosts have listeners
		interested in joining multicast groups whose multicast address is listed in the router's list.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v1-report-count')

	@property
	def RxV2QueryCount(self):
		"""Total number of IGMPv2 queries received. Routers use Multicast Listener Query messages to query
		a subnet for multicast listeners..

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v2-query-count')

	@property
	def RxV2ReportCount(self):
		"""Similar to IGMPv1 reports, IGMPv2 reports are sent by IGMPv2 hosts if they detect an IGMPv2 router.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v2-report-count')

	@property
	def RxV3QueryCount(self):
		"""IGMPv3 Membership Queries are sent by IP multicast routers to query the multicast reception state
		of neighboring interfaces.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v3-query-count')

	@property
	def RxV3ReportCount(self):
		"""While functionally similar to IGMPv2 reports, IGMPv3 reports add support for source filtering.
		This means a host may report interest in receiving packets only from specific addresses.
		Or, from all but specific addresses sent to a multicast address. This information may be used to
		avoid delivering multicast packets from specific sources to networks where there are no interested hosts.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-v3-report-count')

	@property
	def TimeStamp(self):
		"""Timestamp in seconds of last statistic update.

		Getter Returns:
			uint32
		"""
		return self._get_value('time-stamp')

	@property
	def TxFrameCount(self):
		"""Total number of IGMP frames transmitted.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-frame-count')

	@property
	def TxGeneralQueryCount(self):
		"""otal number of IGMP General Queries transmitted. General Query is used to learn which groups have members
		on an attached network.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-general-query-count')

	@property
	def TxGroupAndSourceSpecificQueryCount(self):
		"""Group- and source-specific queries are sent by a multicast router whenever a host leave a specific source
		of a group. This is to make sure that there are no other hosts of that source and group

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-group-and-source-specific-query-count')

	@property
	def TxGroupSpecificQueryCount(self):
		"""Total number of IGMP group-specific queries transmitted. The Group-Specific Query is used to learn
		if a particular group has any members on an attached network.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-group-specific-query-count')

	@property
	def TxLeaveGroupCount(self):
		"""When an IGMP host leaves a multicast group, it may send a Leave Group message to the all-routers multicast group.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-leave-group-count')

	@property
	def TxV1QueryCount(self):
		"""IGMPv1 Membership Queries are sent by IP multicast routers to query the multicast reception state of neighboring interfaces

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v1-query-count')

	@property
	def TxV1ReportCount(self):
		"""IGMPv1 reports are sent to multicast routers to indicate that hosts have listeners interested in joining
		multicast groups whose multicast address is listed in the router's list..

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v1-report-count')

	@property
	def TxV2QueryCount(self):
		"""IGMPv2 Membership Queries are sent by IP multicast routers to query the multicast reception state of neighboring interfaces.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-query-count')

	@property
	def TxV2ReportCount(self):
		"""Similar to IGMPv1 reports, IGMPv2 reports are sent by IGMPv2 hosts if they detect an IGMPv2 router.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v2-report-count')

	@property
	def TxV3QueryCount(self):
		"""IGMPv3 Membership Queries are sent by IP multicast routers to query the multicast reception state of neighboring interfaces.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v3-query-count')

	@property
	def TxV3ReportCount(self):
		"""While functionally similar to IGMPv2 reports, IGMPv3 reports add support for source filtering.
		This means a host may report interest in receiving packets only from specific addresses.
		Or, from all but specific addresses sent to a multicast address. This information may be used to
		avoid delivering multicast packets from specific sources to networks where there are no interested hosts.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v3-report-count')

	@property
	def TxV3AllowNewSourcesCount(self):
		"""A Source-List-Change Record (SLCR) indicating the group's associated sources have changed such that data
		from a new set of sources are to be received..

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v3-allow-new-sources-count')

	@property
	def TxV3BlockOldSourcesCount(self):
		"""A Source-List-Change Record (SLCR) indicating the group's associated sources have changed such that data
		from an existing set of sources are not required.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v3-block-old-sources-count')

	@property
	def TxV3ChangeToExcludeModeCount(self):
		"""A Filter-Mode-Change Record (FMCR) indicating the filter-mode of the reception state has changed to exclude mode.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v3-change-to-exclude-mode-count')

	@property
	def TxV3ChangeToIncludeModeCount(self):
		"""A Filter-Mode-Change Record (FMCR) indicating the filter-mode of the reception state has changed to include mode.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v3-change-to-include-mode-count')

	@property
	def TxV3ModeIsExcludeCount(self):
		"""A Current-State Record (CSR) indicating the current reception state with respect to 1 multicast group at a given interface.
		The state contains the exclude filter mode.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v3-mode-is-exclude-count')

	@property
	def TxV3ModeIsIncludeCount(self):
		"""A Current-State Record (CSR) indicating the current reception state with respect to 1 multicast group at a given interface.
		The state contains the include filter mode.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-v3-mode-is-include-count')

	def read(self, PortName=None):
		"""Get `igmp-port-statistics` resource(s). Returns all `igmp-port-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(PortName)

