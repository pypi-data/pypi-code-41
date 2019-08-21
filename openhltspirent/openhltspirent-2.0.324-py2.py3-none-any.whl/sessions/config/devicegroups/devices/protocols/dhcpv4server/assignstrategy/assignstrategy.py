from openhltspirent.base import Base
class AssignStrategy(Base):
	"""The strategy that server choose address pools which are used for assign address.
	   GATEWAY	       : If Client IP address is not 0 in DHCP message, assign address from those pools
	                   who has the same network as Client IP address.
	                   Else if Relay Agent IP address is not 0 in DHCP message, assign address from those
	                   pools who has the same network as Relay Agent IP address.
	                   Else if EnablePoolAddrPrefix is true, assign address from the default address pool.
	                   Else assign address from those pools who has the same network as DHCP server IP.
	   CIRCUIT_ID     : Assign address from those pools who match the relay agent circuit ID option received.
	   REMOTE_ID      : Assign address from those pools who match the relay agent remote ID option received.
	   LINK_SELECTION : Assign address from those pools who match the relay agent link selection option received.
	   VPN_ID	       : Assign address from those pools who match the relay agent virtual subnet
	                    selection option received.
	   POOL_BY_POOL   : Assign address from default pool, and then from the first relay agent pool if any when
	                   the default pool is exhausted and so on.
	"""
	YANG_NAME = 'assign-strategy'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"Single": "single", "PatternType": "pattern-type", "PatternFormat": "pattern-format", "ValueList": "value-list"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(AssignStrategy, self).__init__(parent)

	@property
	def PatternFormat(self):
		"""Refine this leaf value with a regex of valid enum choices

		Getter Returns:
			string
		"""
		return self._get_value('pattern-format')

	@property
	def PatternType(self):
		"""TBD

		Getter Returns:
			SINGLE | VALUE_LIST

		Setter Allows:
			SINGLE | VALUE_LIST

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('pattern-type')

	@property
	def Single(self):
		"""TBD

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('single')

	@property
	def ValueList(self):
		"""TBD

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('value-list')

	def update(self, PatternFormat=None, PatternType=None, Single=None, ValueList=None):
		"""Update the current instance of the `assign-strategy` resource

		Args:
			PatternFormat (string): Refine this leaf value with a regex of valid enum choices
			PatternType (enumeration): TBD
			Single (string): TBD
			ValueList (string): TBD
		"""
		return self._update(locals())

