from openhltspirent.base import Base
class Dhcpv4PortStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/dhcpv4-port-statistics resource.
	"""
	YANG_NAME = 'dhcpv4-port-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'port-name'
	YANG_PROPERTY_MAP = {"TotalRebootedCount": "total-rebooted-count", "TxRenewCount": "tx-renew-count", "MaxSetupTime": "max-setup-time", "MinSetupTime": "min-setup-time", "RxNakCount": "rx-nak-count", "TotalRetriedCount": "total-retried-count", "RxAckCount": "rx-ack-count", "RxForceRenewCount": "rx-force-renew-count", "TxReleaseCount": "tx-release-count", "SuccessPercent": "success-percent", "CurrentBoundCount": "current-bound-count", "AttemptRate": "attempt-rate", "TotalRenewedCount": "total-renewed-count", "BindRate": "bind-rate", "TxRebootCount": "tx-reboot-count", "TotalFailedCount": "total-failed-count", "CurrentIdleCount": "current-idle-count", "TxRebindCount": "tx-rebind-count", "TotalAttemptCount": "total-attempt-count", "RxOfferCount": "rx-offer-count", "AvgSetupTime": "avg-setup-time", "TotalBoundCount": "total-bound-count", "TxDiscoverCount": "tx-discover-count", "TxRequestCount": "tx-request-count", "PortName": "port-name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv4PortStatistics, self).__init__(parent)

	@property
	def PortName(self):
		"""An abstract test port name

		Getter Returns:
			string
		"""
		return self._get_value('port-name')

	@property
	def AttemptRate(self):
		"""Rate of attempts (in sessions/second) for the binding of DHCP client leases for all sessions on the port.

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
		"""Rate of binding (in sessions/second) of DHCP client leases or lease renewals for all sessions on the port.

		Getter Returns:
			decimal64
		"""
		return self._get_value('bind-rate')

	@property
	def CurrentBoundCount(self):
		"""Number of DHCP hosts on the port that are bound (have been assigned an IP address). This statistic corresponds to the DUT's Leased Count statistic.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-bound-count')

	@property
	def CurrentIdleCount(self):
		"""Number of DHCP hosts on the port that are in the Idle state.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-idle-count')

	@property
	def RxAckCount(self):
		"""Number of DHCPACK messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-ack-count')

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
	def SuccessPercent(self):
		"""Percentage of all sessions on the port that have been successfully bound and
		have obtained DHCP client leases or lease renewals.

		Getter Returns:
			decimal64
		"""
		return self._get_value('success-percent')

	@property
	def TotalAttemptCount(self):
		"""Total number of DHCP hosts on the port that have attempted to bind (both past and current).

		Getter Returns:
			uint32
		"""
		return self._get_value('total-attempt-count')

	@property
	def TotalBoundCount(self):
		"""Total number of DHCP hosts on the port that are bound (both past and current).

		Getter Returns:
			uint32
		"""
		return self._get_value('total-bound-count')

	@property
	def TotalFailedCount(self):
		"""Total number of DHCP hosts on the port that have failed to bind (both past and current).
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
		"""Total number of DHCP hosts on the port that renewed a lease.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-renewed-count')

	@property
	def TotalRetriedCount(self):
		"""Total number of DHCP hosts on the port that have retried to bind (both past and current).

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

	def read(self, PortName=None):
		"""Get `dhcpv4-port-statistics` resource(s). Returns all `dhcpv4-port-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(PortName)

