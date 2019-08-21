from openhltspirent.base import Base
class Dhcpv6ServerStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/dhcpv6-server-statistics resource.
	"""
	YANG_NAME = 'dhcpv6-server-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"RxReleaseCount": "rx-release-count", "DeviceName": "device-name", "RxSolicitCount": "rx-solicit-count", "RxDeclineCount": "rx-decline-count", "TotalBoundCount": "total-bound-count", "TotalReleasedCount": "total-released-count", "TotalRenewedCount": "total-renewed-count", "TxReplyCount": "tx-reply-count", "TxReconfigureRebindCount": "tx-reconfigure-rebind-count", "TotalExpiredCount": "total-expired-count", "RxInfoRequestCount": "rx-info-request-count", "RxRebindCount": "rx-rebind-count", "RxRequestCount": "rx-request-count", "RxRenewCount": "rx-renew-count", "TxReconfigureRenewCount": "tx-reconfigure-renew-count", "PortName": "port-name", "TxReconfigureCount": "tx-reconfigure-count", "TxAdvertiseCount": "tx-advertise-count", "RxConfirmCount": "rx-confirm-count", "CurrentBoundCount": "current-bound-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv6ServerStatistics, self).__init__(parent)

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
	def CurrentBoundCount(self):
		"""Number of sessions that are currently bound.

		Getter Returns:
			uint32
		"""
		return self._get_value('current-bound-count')

	@property
	def RxConfirmCount(self):
		"""Number of Confirm messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-confirm-count')

	@property
	def RxDeclineCount(self):
		"""Number of Decline messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-decline-count')

	@property
	def RxInfoRequestCount(self):
		"""Number of Information-Request messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-info-request-count')

	@property
	def RxRebindCount(self):
		"""Number of Rebind messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-rebind-count')

	@property
	def RxReleaseCount(self):
		"""Number of Release messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-release-count')

	@property
	def RxRenewCount(self):
		"""Number of Renew messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-renew-count')

	@property
	def RxRequestCount(self):
		"""Number of Request messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-request-count')

	@property
	def RxSolicitCount(self):
		"""Number of Solicit messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-solicit-count')

	@property
	def TotalBoundCount(self):
		"""Total number of times a bound event occurred including renew events.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-bound-count')

	@property
	def TotalExpiredCount(self):
		"""Total number of times an expired event occurred.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-expired-count')

	@property
	def TotalReleasedCount(self):
		"""Total number of times a release event occurred.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-released-count')

	@property
	def TotalRenewedCount(self):
		"""Total number of times a renew event occurred.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-renewed-count')

	@property
	def TxAdvertiseCount(self):
		"""Number of Advertise messages transmitted.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-advertise-count')

	@property
	def TxReconfigureCount(self):
		"""Number of Reconfigure messages transmitted.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-reconfigure-count')

	@property
	def TxReconfigureRebindCount(self):
		"""Number of Reconfigure Rebind messages transmitted.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-reconfigure-rebind-count')

	@property
	def TxReconfigureRenewCount(self):
		"""Number of Reconfigure Renew messages transmitted.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-reconfigure-renew-count')

	@property
	def TxReplyCount(self):
		"""Number of Reply messages transmitted.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-reply-count')

	def read(self, DeviceName=None):
		"""Get `dhcpv6-server-statistics` resource(s). Returns all `dhcpv6-server-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

