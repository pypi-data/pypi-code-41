from openhltspirent.base import Base
class MldHost(Base):
	"""TBD

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/statistics/mld-host-group-statistics/mld-host resource.
	"""
	YANG_NAME = 'mld-host'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'host-address'
	YANG_PROPERTY_MAP = {"LeaveTimestamp": "leave-timestamp", "LeaveLatency": "leave-latency", "JoinLatency": "join-latency", "JoinTimestamp": "join-timestamp", "State": "state", "StateChangeTimestamp": "state-change-timestamp", "JoinFail": "join-fail", "HostAddress": "host-address", "GroupAddress": "group-address", "DuplicateJoin": "duplicate-join"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(MldHost, self).__init__(parent)

	@property
	def HostAddress(self):
		"""Host IP address.

		Getter Returns:
			string
		"""
		return self._get_value('host-address')

	@property
	def GroupAddress(self):
		"""Group IP multicast address.

		Getter Returns:
			string
		"""
		return self._get_value('group-address')

	@property
	def State(self):
		"""Current state of the MLD group

		Getter Returns:
			UNDEFINED | NON_MEMBER | DELAYING_MEMBER | IDLE_MEMBER | RETRYING_MEMBER | INCLUDE | EXCLUDE
		"""
		return self._get_value('state')

	@property
	def DuplicateJoin(self):
		"""Indicates whether or not the DUT was already forwarding multicast prior to a join being sent.
		TRUE  : DUT was forwarding multicast traffic for this group prior to the join being sent.
		FALSE : No duplicate join report detected

		Getter Returns:
			boolean
		"""
		return self._get_value('duplicate-join')

	@property
	def JoinFail(self):
		"""Indicates whether or not multicast traffic was received.
		TRUE  : Multicast traffic was not received.
		FALSE : Multicast traffic was received

		Getter Returns:
			boolean
		"""
		return self._get_value('join-fail')

	@property
	def JoinLatency(self):
		"""Time between sending an MLD join message, and receiving multicast data from the group specified in the join message.

		Getter Returns:
			uint64
		"""
		return self._get_value('join-latency')

	@property
	def LeaveLatency(self):
		"""Time between sending an MLD leave message to a multicast group, and when the multicast data stopped traffic.

		Getter Returns:
			uint64
		"""
		return self._get_value('leave-latency')

	@property
	def JoinTimestamp(self):
		"""Transmit timestamp of the initial MLD join message.

		Getter Returns:
			string
		"""
		return self._get_value('join-timestamp')

	@property
	def LeaveTimestamp(self):
		"""Transmit timestamp of the MLD leave message.

		Getter Returns:
			string
		"""
		return self._get_value('leave-timestamp')

	@property
	def StateChangeTimestamp(self):
		"""Timestamp of the MLD group membership state change.

		Getter Returns:
			string
		"""
		return self._get_value('state-change-timestamp')

	def read(self, HostAddress=None):
		"""Get `mld-host` resource(s). Returns all `mld-host` resources from the server if no input parameters are specified.

		"""
		return self._read(HostAddress)

