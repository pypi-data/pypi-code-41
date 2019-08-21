from openhltspirent.base import Base
class Dhcpv4ServerStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/dhcpv4-server-statistics resource.
	"""
	YANG_NAME = 'dhcpv4-server-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"RxReleaseCount": "rx-release-count", "DeviceName": "device-name", "RxDeclineCount": "rx-decline-count", "TotalBoundCount": "total-bound-count", "TxAckCount": "tx-ack-count", "TotalRenewedCount": "total-renewed-count", "RxInformCount": "rx-inform-count", "RxDiscoverCount": "rx-discover-count", "TotalExpiredCount": "total-expired-count", "TxNakCount": "tx-nak-count", "RxRequestCount": "rx-request-count", "TotalReleasedCount": "total-released-count", "TxOfferCount": "tx-offer-count", "PortName": "port-name", "TxForceRenewCount": "tx-force-renew-count", "CurrentBoundCount": "current-bound-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv4ServerStatistics, self).__init__(parent)

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
	def RxDeclineCount(self):
		"""Number of DHCPDECLINE messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-decline-count')

	@property
	def RxDiscoverCount(self):
		"""Number of DHCPDISCOVER messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-discover-count')

	@property
	def RxInformCount(self):
		"""Number of DHCPINFORM messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-inform-count')

	@property
	def RxReleaseCount(self):
		"""Number of DHCPRELEASE messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-release-count')

	@property
	def RxRequestCount(self):
		"""Number of DHCPRELEASE messages received.

		Getter Returns:
			uint32
		"""
		return self._get_value('rx-request-count')

	@property
	def TotalBoundCount(self):
		"""Total number of bound sessions.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-bound-count')

	@property
	def TotalExpiredCount(self):
		"""Total number of expired offers or sessions.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-expired-count')

	@property
	def TotalReleasedCount(self):
		"""Total number of sessions released by clients.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-released-count')

	@property
	def TotalRenewedCount(self):
		"""Total number of renewed sessions.

		Getter Returns:
			uint32
		"""
		return self._get_value('total-renewed-count')

	@property
	def TxAckCount(self):
		"""Number of ACK messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-ack-count')

	@property
	def TxForceRenewCount(self):
		"""Number of DHCP Force Renews (unicast DHCPREQUEST messages) transmitted.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-force-renew-count')

	@property
	def TxNakCount(self):
		"""Number of NAK messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-nak-count')

	@property
	def TxOfferCount(self):
		"""Number of OFFER messages sent.

		Getter Returns:
			uint32
		"""
		return self._get_value('tx-offer-count')

	def read(self, DeviceName=None):
		"""Get `dhcpv4-server-statistics` resource(s). Returns all `dhcpv4-server-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

