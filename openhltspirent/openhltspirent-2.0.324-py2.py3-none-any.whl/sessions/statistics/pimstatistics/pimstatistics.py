from openhltspirent.base import Base
class PimStatistics(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/pim-statistics resource.
	"""
	YANG_NAME = 'pim-statistics'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'device-name'
	YANG_PROPERTY_MAP = {"TxJoinPruneCount": "tx-join-prune-count", "TxHelloCount": "tx-hello-count", "RxGroupSGCount": "rx-group-s-g-count", "NeighborCount": "neighbor-count", "RxAssertCount": "rx-assert-count", "RxRegisterCount": "rx-register-count", "TxBootstrapCount": "tx-bootstrap-count", "DeviceName": "device-name", "TxRegisterCount": "tx-register-count", "RxGroupRpCount": "rx-group-rp-count", "RxBootstrapCount": "rx-bootstrap-count", "RxGroupStarGCount": "rx-group-star-g-count", "TxCAndRpAdvertCount": "tx-c-and-rp-advert-count", "RxGroupSGRptCount": "rx-group-s-g-rpt-count", "RxJoinPruneCount": "rx-join-prune-count", "TxAssertCount": "tx-assert-count", "TxGroupSGRptCount": "tx-group-s-g-rpt-count", "TxGroupStarGCount": "tx-group-star-g-count", "TxGroupRpCount": "tx-group-rp-count", "RxRegisterStopCount": "rx-register-stop-count", "TxGroupSGCount": "tx-group-s-g-count", "MdtJoinCount": "mdt-join-count", "TxRegisterStopCount": "tx-register-stop-count", "RxCAndRpAdvertCount": "rx-c-and-rp-advert-count", "RxHelloCount": "rx-hello-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(PimStatistics, self).__init__(parent)

	@property
	def DeviceName(self):
		"""Device Name

		Getter Returns:
			string
		"""
		return self._get_value('device-name')

	@property
	def MdtJoinCount(self):
		"""Number of MDT join messages.

		Getter Returns:
			uint64
		"""
		return self._get_value('mdt-join-count')

	@property
	def NeighborCount(self):
		"""Number of PIM neighbors for this router.

		Getter Returns:
			uint64
		"""
		return self._get_value('neighbor-count')

	@property
	def RxAssertCount(self):
		"""Number of Assert messages received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-assert-count')

	@property
	def RxBootstrapCount(self):
		"""Number of Bootstrap messages received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-bootstrap-count')

	@property
	def RxCAndRpAdvertCount(self):
		"""Number of candidate Rendezvous Point (RP) Advertisements received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-c-and-rp-advert-count')

	@property
	def RxGroupRpCount(self):
		"""Number of (*,*,RP) groups received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-group-rp-count')

	@property
	def RxGroupSGCount(self):
		"""Number of (S,G) groups received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-group-s-g-count')

	@property
	def RxGroupSGRptCount(self):
		"""Number of (S,G,rpt) groups received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-group-s-g-rpt-count')

	@property
	def RxGroupStarGCount(self):
		"""Number of (*,G) groups received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-group-star-g-count')

	@property
	def RxHelloCount(self):
		"""Number of Hello messages received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-hello-count')

	@property
	def RxJoinPruneCount(self):
		"""Number of Join/Prune messages received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-join-prune-count')

	@property
	def RxRegisterCount(self):
		"""Number of Register messages received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-register-count')

	@property
	def RxRegisterStopCount(self):
		"""Number of Register Stop messages received.

		Getter Returns:
			uint64
		"""
		return self._get_value('rx-register-stop-count')

	@property
	def TxAssertCount(self):
		"""Number of Assert messages sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-assert-count')

	@property
	def TxBootstrapCount(self):
		"""Number of Bootstrap messages sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-bootstrap-count')

	@property
	def TxCAndRpAdvertCount(self):
		"""Number of candidate Rendezvous Point (RP) Advertisements sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-c-and-rp-advert-count')

	@property
	def TxGroupRpCount(self):
		"""Number of (*,*,RP) groups sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-group-rp-count')

	@property
	def TxGroupSGCount(self):
		"""Number of (S,G) groups sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-group-s-g-count')

	@property
	def TxGroupSGRptCount(self):
		"""Number of (S,G,rpt) groups sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-group-s-g-rpt-count')

	@property
	def TxGroupStarGCount(self):
		"""Number of (*,G) groups sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-group-star-g-count')

	@property
	def TxHelloCount(self):
		"""Number of Hello messages sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-hello-count')

	@property
	def TxJoinPruneCount(self):
		"""Number of Join/Prune messages sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-join-prune-count')

	@property
	def TxRegisterCount(self):
		"""Number of Register messages sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-register-count')

	@property
	def TxRegisterStopCount(self):
		"""Number of Register Stop messages sent.

		Getter Returns:
			uint64
		"""
		return self._get_value('tx-register-stop-count')

	def read(self, DeviceName=None):
		"""Get `pim-statistics` resource(s). Returns all `pim-statistics` resources from the server if no input parameters are specified.

		"""
		return self._read(DeviceName)

