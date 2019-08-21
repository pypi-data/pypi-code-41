from openhltspirent.base import Base
class Dhcpv6Statistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/dhcpv6-statistics resource.
	"""
	YANG_NAME = 'dhcpv6-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"AvgReleaseReplyTime": "avg-release-reply-time", "TxConfirmCount": "tx-confirm-count", "MinReleaseReplyTime": "min-release-reply-time", "AvgRenewReplyTime": "avg-renew-reply-time", "TxRenewCount": "tx-renew-count", "MaxRenewReplyTime": "max-renew-reply-time", "TxReleaseCount": "tx-release-count", "TotalRenewRetriedCount": "total-renew-retried-count", "RxReconfigureCount": "rx-reconfigure-count", "RxRelayReplyCount": "rx-relay-reply-count", "RebindRate": "rebind-rate", "MinRebindReplyTime": "min-rebind-reply-time", "AvgRequestReplyTime": "avg-request-reply-time", "ReleaseRate": "release-rate", "DeviceName": "device-name", "AvgRebindReplyTime": "avg-rebind-reply-time", "TotalDeclinedCount": "total-declined-count", "TxInfoRequestCount": "tx-info-request-count", "AvgSolicitReplyTime": "avg-solicit-reply-time", "CurrentAttemptCount": "current-attempt-count", "TotalReboundCount": "total-rebound-count", "MaxRequestReplyTime": "max-request-reply-time", "TotalReleasedCount": "total-released-count", "AvgSolicitAdvertiseTime": "avg-solicit-advertise-time", "TxSolicitCount": "tx-solicit-count", "CurrentBoundCount": "current-bound-count", "AttemptRate": "attempt-rate", "MaxReleaseReplyTime": "max-release-reply-time", "TotalRetriedCount": "total-retried-count", "TotalRenewedCount": "total-renewed-count", "BindRate": "bind-rate", "MaxRebindReplyTime": "max-rebind-reply-time", "RxReplyCount": "rx-reply-count", "MaxSolicitReplyTime": "max-solicit-reply-time", "RxAdvertiseCount": "rx-advertise-count", "ElapsedTime": "elapsed-time", "TotalFailedCount": "total-failed-count", "CurrentIdleCount": "current-idle-count", "TotalBoundCount": "total-bound-count", "TxRebindCount": "tx-rebind-count", "TotalAttemptCount": "total-attempt-count", "MinSolicitReplyTime": "min-solicit-reply-time", "RenewRate": "renew-rate", "MaxSolicitAdvertiseTime": "max-solicit-advertise-time", "TxDeclineCount": "tx-decline-count", "PrefixCount": "prefix-count", "MinRenewReplyTime": "min-renew-reply-time", "TxRelayForwardCount": "tx-relay-forward-count", "MinRequestReplyTime": "min-request-reply-time", "TxRequestCount": "tx-request-count", "MinSolicitAdvertiseTime": "min-solicit-advertise-time", "TotalReleaseRetriedCount": "total-release-retried-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv6Statistics, self).__init__(parent)

	@property
	def DeviceName(self):
		"""Device Name

		Getter Returns:
			string
		"""
		return self._get_value('device-name')

	@property
	def AttemptRate(self):
		"""Attempt rate in sessions per second.

		Getter Returns:
			decimal64
		"""
		return self._get_value('attempt-rate')

	@property
	def BindRate(self):
		"""Binding  rate in sessions per second.

		Getter Returns:
			decimal64
		"""
		return self._get_value('bind-rate')

	@property
	def CurrentAttemptCount(self):
		"""Number of DHCPv6 sessions currently being attempted.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-attempt-count')

	@property
	def CurrentBoundCount(self):
		"""Number of DHCPv6 sessions that are currently bound.
		This statistic should match the DUT's Leased Count statistic.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-bound-count')

	@property
	def CurrentIdleCount(self):
		"""Number of DHCPv6 sessions currently in the Idle state
		(sessions that have been programmed but are not being attempted).

		Getter Returns:
			uint32
		"""
		return self._get_value('current-idle-count')

	@property
	def AvgRebindReplyTime(self):
		"""Average amount of time (in milliseconds) that elapsed between when a
		REBIND message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('avg-rebind-reply-time')

	@property
	def AvgReleaseReplyTime(self):
		"""Average amount of time (in milliseconds) that elapsed between when a
		RELEASE message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('avg-release-reply-time')

	@property
	def AvgRenewReplyTime(self):
		"""Average amount of time (in milliseconds) that elapsed between when a
		RENEW message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('avg-renew-reply-time')

	@property
	def AvgRequestReplyTime(self):
		"""Average amount of time (in milliseconds) that elapsed between when a
		REQUEST message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('avg-request-reply-time')

	@property
	def AvgSolicitAdvertiseTime(self):
		"""Average amount of time (in milliseconds) that elapsed between when a
		SOLICIT message was sent by a host and an ADVERTISE message was received
		from the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('avg-solicit-advertise-time')

	@property
	def AvgSolicitReplyTime(self):
		"""Average amount of time (in milliseconds) that elapsed between when a
		SOLICIT message was sent by a host and a REPLY message was received
		from the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('avg-solicit-reply-time')

	@property
	def MaxRebindReplyTime(self):
		"""Maximum amount of time (in milliseconds) that elapsed between when a
		REBIND message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('max-rebind-reply-time')

	@property
	def MaxReleaseReplyTime(self):
		"""Maximum amount of time (in milliseconds) that elapsed between when a
		RELEASE message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('max-release-reply-time')

	@property
	def MaxRenewReplyTime(self):
		"""Maximum amount of time (in milliseconds) that elapsed between when a
		RENEW message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('max-renew-reply-time')

	@property
	def MaxRequestReplyTime(self):
		"""Maximum amount of time (in milliseconds) that elapsed between when a
		REQUEST message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('max-request-reply-time')

	@property
	def MaxSolicitAdvertiseTime(self):
		"""Maximum amount of time (in milliseconds) that elapsed between when a
		SOLICIT message was sent by a host and an ADVERTISE message was received
		from the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('max-solicit-advertise-time')

	@property
	def MaxSolicitReplyTime(self):
		"""Maximum amount of time (in milliseconds) that elapsed between when a
		SOLICIT message was sent by a host and a REPLY message was received
		from the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('max-solicit-reply-time')

	@property
	def MinRebindReplyTime(self):
		"""Minimum amount of time (in milliseconds) that elapsed between when a
		REBIND message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('min-rebind-reply-time')

	@property
	def MinReleaseReplyTime(self):
		"""Minimum amount of time (in milliseconds) that elapsed between when a
		RELEASE message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('min-release-reply-time')

	@property
	def MinRenewReplyTime(self):
		"""Minimum amount of time (in milliseconds) that elapsed between when a
		RENEW message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('min-renew-reply-time')

	@property
	def MinRequestReplyTime(self):
		"""Minimum amount of time (in milliseconds) that elapsed between when a
		REQUEST message was sent by a host and a REPLY message was received from
		the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('min-request-reply-time')

	@property
	def MinSolicitAdvertiseTime(self):
		"""Minimum amount of time (in milliseconds) that elapsed between when a
		SOLICIT message was sent by a host and an ADVERTISE message was received
		from the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('min-solicit-advertise-time')

	@property
	def MinSolicitReplyTime(self):
		"""Minimum amount of time (in milliseconds) that elapsed between when a
		SOLICIT message was sent by a host and a REPLY message was received
		from the delegating server.

		Getter Returns:
			decimal64
		"""
		return self._get_value('min-solicit-reply-time')

	@property
	def ElapsedTime(self):
		"""Elapsed time.

		Getter Returns:
			decimal64
		"""
		return self._get_value('elapsed-time')

	@property
	def PrefixCount(self):
		"""Number of prefixes allocated to the block.

		Getter Returns:
			uint32
		"""
		return self._get_value('prefix-count')

	@property
	def RebindRate(self):
		"""Rebind rate in sessions per second.

		Getter Returns:
			uint32
		"""
		return self._get_value('rebind-rate')

	@property
	def ReleaseRate(self):
		"""Release rate in sessions per second.

		Getter Returns:
			uint32
		"""
		return self._get_value('release-rate')

	@property
	def RenewRate(self):
		"""Renew rate in sessions per second.

		Getter Returns:
			uint32
		"""
		return self._get_value('renew-rate')

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
		"""Number of RELAY-REPLY messages received

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
	def TotalAttemptCount(self):
		"""Total number of sessions attempted.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-attempt-count')

	@property
	def TotalBoundCount(self):
		"""Total number of sessions bound.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-bound-count')

	@property
	def TotalDeclinedCount(self):
		"""Total number of session declined..

		Getter Returns:
			uint32
		"""
		return self._get_value('total-declined-count')

	@property
	def TotalFailedCount(self):
		"""Number of hosts in the block that failed to bind.
		Failures may be due to DUT overload, a T1 or T2 timer expiration,
		or reaching the number of retries for the session.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-failed-count')

	@property
	def TotalReboundCount(self):
		"""Total number of sessions rebound.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-rebound-count')

	@property
	def TotalReleasedCount(self):
		"""Total number of sessions released.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-released-count')

	@property
	def TotalReleaseRetriedCount(self):
		"""Number of RELEASE messages resent when no REPLY message was
		received by the associated timeout.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-release-retried-count')

	@property
	def TotalRenewedCount(self):
		"""Total number of sessions renewed.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-renewed-count')

	@property
	def TotalRenewRetriedCount(self):
		"""Total number of RENEW messages resent.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-renew-retried-count')

	@property
	def TotalRetriedCount(self):
		"""Number of SOLICIT and REQUEST messages resent for all hosts in the block.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-retried-count')

	@property
	def TxConfirmCount(self):
		"""Number of CONFIRM messages sent..

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
		"""Number of RELEASE  messages sent.

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

	def read(self, DeviceName=None):
		"""Get `dhcpv6-statistics` resource(s). Returns all `dhcpv6-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

