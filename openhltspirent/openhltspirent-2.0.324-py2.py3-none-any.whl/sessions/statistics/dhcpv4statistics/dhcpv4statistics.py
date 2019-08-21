from openhltspirent.base import Base
class Dhcpv4Statistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/dhcpv4-statistics resource.
	"""
	YANG_NAME = 'dhcpv4-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"TotalRebootedCount": "total-rebooted-count", "TxRenewCount": "tx-renew-count", "RxDnaV4ReplyCount": "rx-dna-v4-reply-count", "DeviceName": "device-name", "RxNakCount": "rx-nak-count", "DnaV4RetryCount": "dna-v4-retry-count", "TxDiscoverCount": "tx-discover-count", "TxDnaV4RequestCount": "tx-dna-v4-request-count", "CurrentAttemptCount": "current-attempt-count", "RxAckCount": "rx-ack-count", "RxForceRenewCount": "rx-force-renew-count", "TxReleaseCount": "tx-release-count", "CurrentBoundCount": "current-bound-count", "AttemptRate": "attempt-rate", "TotalRenewedCount": "total-renewed-count", "BindRate": "bind-rate", "TxRebootCount": "tx-reboot-count", "TotalFailedCount": "total-failed-count", "ElapsedTime": "elapsed-time", "CurrentIdleCount": "current-idle-count", "TxRebindCount": "tx-rebind-count", "TotalAttemptCount": "total-attempt-count", "RxOfferCount": "rx-offer-count", "DnaV4FailedCount": "dna-v4-failed-count", "TotalBoundCount": "total-bound-count", "TotalRetriedCount": "total-retried-count", "TxRequestCount": "tx-request-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv4Statistics, self).__init__(parent)

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
		"""Number of hosts in the block that are in the process of attempting to bind and are sending or receiving DHCP messages.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-attempt-count')

	@property
	def CurrentBoundCount(self):
		"""Number of DHCP sessions that are currently bound. This statistic should match the DUT's Leased-Count statistic.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-bound-count')

	@property
	def CurrentIdleCount(self):
		"""Number of DHCP sessions currently in the Idle state (sessions that have been programmed but are not being attempted).

		Getter Returns:
			uint32
		"""
		return self._get_value('current-idle-count')

	@property
	def DnaV4FailedCount(self):
		"""Number of DNAv4 requests failed.

		Getter Returns:
			uint32
		"""
		return self._get_value('dna-v4-failed-count')

	@property
	def DnaV4RetryCount(self):
		"""Number of DNAv4 requests retried.

		Getter Returns:
			uint32
		"""
		return self._get_value('dna-v4-retry-count')

	@property
	def ElapsedTime(self):
		"""Elapsed time.

		Getter Returns:
			decimal64
		"""
		return self._get_value('elapsed-time')

	@property
	def RxAckCount(self):
		"""Number of DHCPACK messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-ack-count')

	@property
	def RxDnaV4ReplyCount(self):
		"""Number of DNAv4 replies received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-dna-v4-reply-count')

	@property
	def RxForceRenewCount(self):
		"""Number of DHCP Force Renews (unicast DHCPREQUEST messages) received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-force-renew-count')

	@property
	def RxNakCount(self):
		"""Number of DHCPNAK messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-nak-count')

	@property
	def RxOfferCount(self):
		"""Number of DHCPOFFER messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-offer-count')

	@property
	def TotalAttemptCount(self):
		"""Total number of sessions attempted (both past and current).

		Getter Returns:
			uint32
		"""
		return self._get_value('total-attempt-count')

	@property
	def TotalBoundCount(self):
		"""Total number of bound sessions (both past and current).

		Getter Returns:
			uint32
		"""
		return self._get_value('total-bound-count')

	@property
	def TotalFailedCount(self):
		"""Total number of DHCP hosts in the block that have failed to bind (both past and current).
		Failures may be due to DUT overload, a T1 timer expiration, or reaching the number of retries for the session.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-failed-count')

	@property
	def TotalRebootedCount(self):
		"""Number of DHCPv4 reboot commands issued.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-rebooted-count')

	@property
	def TotalRenewedCount(self):
		"""Total number of renewed sessions.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-renewed-count')

	@property
	def TotalRetriedCount(self):
		"""Total number of times DHCPDISCOVER and DHCPREQUEST messages have been retried.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-retried-count')

	@property
	def TxDiscoverCount(self):
		"""Number of DHCPDISCOVER messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-discover-count')

	@property
	def TxDnaV4RequestCount(self):
		"""Number of DNAv4 requests sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-dna-v4-request-count')

	@property
	def TxRebindCount(self):
		"""Number of DHCP Rebinds (broadcast DHCPREQUEST messages).

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-rebind-count')

	@property
	def TxRebootCount(self):
		"""Total number of rebooted sessions.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-reboot-count')

	@property
	def TxReleaseCount(self):
		"""Number of DHCPRELEASE messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-release-count')

	@property
	def TxRenewCount(self):
		"""Number of DHCP Renews (unicast DHCPREQUEST messages).

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-renew-count')

	@property
	def TxRequestCount(self):
		"""Number of DHCPREQUEST messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-request-count')

	def read(self, DeviceName=None):
		"""Get `dhcpv4-statistics` resource(s). Returns all `dhcpv4-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

