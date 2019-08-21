from openhltspirent.base import Base
class Dhcpv6PortStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/dhcpv6-port-statistics resource.
	"""
	YANG_NAME = 'dhcpv6-port-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'port-name'
	YANG_PROPERTY_MAP = {"TxRenewCount": "tx-renew-count", "TotalRenewRetriedCount": "total-renew-retried-count", "RxReconfigureCount": "rx-reconfigure-count", "RxRelayReplyCount": "rx-relay-reply-count", "MaxSetupTime": "max-setup-time", "MinSetupTime": "min-setup-time", "ReleaseRate": "release-rate", "TxInfoRequestCount": "tx-info-request-count", "TxConfirmCount": "tx-confirm-count", "CurrentAttemptCount": "current-attempt-count", "TotalReboundCount": "total-rebound-count", "TotalReleasedCount": "total-released-count", "TxSolicitCount": "tx-solicit-count", "SuccessPercent": "success-percent", "CurrentBoundCount": "current-bound-count", "AttemptRate": "attempt-rate", "TxReleaseCount": "tx-release-count", "TotalRenewedCount": "total-renewed-count", "BindRate": "bind-rate", "RxReplyCount": "rx-reply-count", "TotalFailedCount": "total-failed-count", "RxAdvertiseCount": "rx-advertise-count", "CurrentIdleCount": "current-idle-count", "TxRebindCount": "tx-rebind-count", "TotalAttemptCount": "total-attempt-count", "AvgSetupTime": "avg-setup-time", "TotalBoundCount": "total-bound-count", "TxDeclineCount": "tx-decline-count", "TxRelayForwardCount": "tx-relay-forward-count", "TotalRetriedCount": "total-retried-count", "TxRequestCount": "tx-request-count", "PortName": "port-name", "TotalReleaseRetriedCount": "total-release-retried-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv6PortStatistics, self).__init__(parent)

	@property
	def PortName(self):
		"""An abstract test port name

		Getter Returns:
			string
		"""
		return self._get_value('port-name')

	@property
	def AttemptRate(self):
		"""Attempt rate in sessions per second.

		Getter Returns:
			decimal64
		"""
		return self._get_value('attempt-rate')

	@property
	def AvgSetupTime(self):
		"""Average setup time that was required to bind a session (in milliseconds).

		Getter Returns:
			decimal64
		"""
		return self._get_value('avg-setup-time')

	@property
	def MaxSetupTime(self):
		"""Maximum setup time that was required to bind a session (in milliseconds).

		Getter Returns:
			decimal64
		"""
		return self._get_value('max-setup-time')

	@property
	def MinSetupTime(self):
		"""Minimum setup time that was required to bind a session (in milliseconds).

		Getter Returns:
			decimal64
		"""
		return self._get_value('min-setup-time')

	@property
	def BindRate(self):
		"""Binding rate in sessions per second.

		Getter Returns:
			decimal64
		"""
		return self._get_value('bind-rate')

	@property
	def CurrentBoundCount(self):
		"""Number of DHCP hosts on the port that are bound (have been assigned an IP address).
		This statistic corresponds to the DUT's Leased Count statistic.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-bound-count')

	@property
	def CurrentIdleCount(self):
		"""Number of sessions currently in the idle state.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-idle-count')

	@property
	def CurrentAttemptCount(self):
		"""Number of sessions currently being attempted.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-attempt-count')

	@property
	def ReleaseRate(self):
		"""Rate at which all sessions on the ports were released by initiating RELEASE messages.

		Getter Returns:
			decimal64
		"""
		return self._get_value('release-rate')

	@property
	def RxAdvertiseCount(self):
		"""Number of ADVERTISE messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-advertise-count')

	@property
	def RxReconfigureCount(self):
		"""Number of RECONFIGURE messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-reconfigure-count')

	@property
	def RxRelayReplyCount(self):
		"""Number of RELAY-REPLY messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-relay-reply-count')

	@property
	def RxReplyCount(self):
		"""Number of REPLY messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-reply-count')

	@property
	def SuccessPercent(self):
		"""Percentage of sessions that have successfully bound.

		Getter Returns:
			decimal64
		"""
		return self._get_value('success-percent')

	@property
	def TotalAttemptCount(self):
		"""Total number of sessions that were attempted.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-attempt-count')

	@property
	def TotalBoundCount(self):
		"""Total number of bound sessions.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-bound-count')

	@property
	def TotalFailedCount(self):
		"""Number of hosts on the port that failed to bind.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-failed-count')

	@property
	def TotalReboundCount(self):
		"""Total number of sessions that were rebound.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-rebound-count')

	@property
	def TotalReleasedCount(self):
		"""Total number of released sessions.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-released-count')

	@property
	def TotalReleaseRetriedCount(self):
		"""Total number of RENEW messages resent.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-release-retried-count')

	@property
	def TotalRenewedCount(self):
		"""Total number of renewed sessions.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-renewed-count')

	@property
	def TotalRenewRetriedCount(self):
		"""Number of RELEASE messages resent when no REPLY message was received by the associated timeout.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-renew-retried-count')

	@property
	def TotalRetriedCount(self):
		"""Number of SOLICIT and REQUEST messages resent for all hosts on the port.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-retried-count')

	@property
	def TxConfirmCount(self):
		"""Number of CONFIRM messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-confirm-count')

	@property
	def TxDeclineCount(self):
		"""Number of DECLINE messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-decline-count')

	@property
	def TxInfoRequestCount(self):
		"""Number of INFO-REQUEST messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-info-request-count')

	@property
	def TxRebindCount(self):
		"""Number of REBIND messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-rebind-count')

	@property
	def TxRelayForwardCount(self):
		"""Number of RELAY-FORWARD messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-relay-forward-count')

	@property
	def TxReleaseCount(self):
		"""Number of RELEASE messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-release-count')

	@property
	def TxRenewCount(self):
		"""Number of RENEW messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-renew-count')

	@property
	def TxRequestCount(self):
		"""Number of REQUEST messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-request-count')

	@property
	def TxSolicitCount(self):
		"""Number of SOLICIT messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-solicit-count')

	def read(self, PortName=None):
		"""Get `dhcpv6-port-statistics` resource(s). Returns all `dhcpv6-port-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(PortName)

