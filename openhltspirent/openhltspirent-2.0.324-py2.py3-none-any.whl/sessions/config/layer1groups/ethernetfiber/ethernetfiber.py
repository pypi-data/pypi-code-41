from openhltspirent.base import Base
class EthernetFiber(Base):
	"""TBD
	"""
	YANG_NAME = 'ethernet-fiber'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"TxGapControl": "tx-gap-control", "CustomFecMode": "custom-fec-mode", "AutoNegotiationEnabled": "auto-negotiation-enabled", "CfpInterface": "cfp-interface", "Mtu": "mtu", "PortSetupMode": "port-setup-mode", "TxMode": "tx-mode", "DataPathMode": "data-path-mode", "MasterSlaveType": "master-slave-type", "CollisionExponent": "collision-exponent", "AutoInstrumentation": "auto-instrumentation", "FlowControlDirectedAddress": "flow-control-directed-address", "CableTypeLength": "cable-type-length", "RxMode": "rx-mode", "FlowControl": "flow-control", "DeficitIdleCount": "deficit-idle-count"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(EthernetFiber, self).__init__(parent)

	@property
	def AutoInstrumentation(self):
		"""TBD

		Getter Returns:
			END_OF_FRAME | FLOATING

		Setter Allows:
			END_OF_FRAME | FLOATING

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('auto-instrumentation')

	@property
	def AutoNegotiationEnabled(self):
		"""If enabled allows for auto negotiation between ports for speed and duplex operation.

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('auto-negotiation-enabled')

	@property
	def MasterSlaveType(self):
		"""When auto negotiation is enabled one of the master slave types can be specified

		Getter Returns:
			MASTER | SLAVE | FAULT

		Setter Allows:
			MASTER | SLAVE | FAULT

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('master-slave-type')

	@property
	def CollisionExponent(self):
		"""TBD

		Getter Returns:
			uint8

		Setter Allows:
			uint8

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('collision-exponent')

	@property
	def CustomFecMode(self):
		"""TBD

		Getter Returns:
			NONE | KR_FEC | RS_FEC

		Setter Allows:
			NONE | KR_FEC | RS_FEC

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('custom-fec-mode')

	@property
	def DataPathMode(self):
		"""TBD

		Getter Returns:
			NORMAL | LOOPBACK | LINE_MONITOR

		Setter Allows:
			NORMAL | LOOPBACK | LINE_MONITOR

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('data-path-mode')

	@property
	def FlowControl(self):
		"""Enables the port's MAC flow control mechanisms to listen for a directed address pause message

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('flow-control')

	@property
	def FlowControlDirectedAddress(self):
		"""The 48-bit MAC address that the port listens on for a directed pause.

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('flow-control-directed-address')

	@property
	def Mtu(self):
		"""TBD

		Getter Returns:
			uint16

		Setter Allows:
			uint16

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('mtu')

	@property
	def PortSetupMode(self):
		"""TBD

		Getter Returns:
			PORTCONFIG_ONLY | REGISTERS_ONLY

		Setter Allows:
			PORTCONFIG_ONLY | REGISTERS_ONLY

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('port-setup-mode')

	@property
	def RxMode(self):
		"""TBD

		Getter Returns:
			CAPTURE | CAPTURE_AND_MEASURE | MEASURE | PACKET_IMPAIRMENT

		Setter Allows:
			CAPTURE | CAPTURE_AND_MEASURE | MEASURE | PACKET_IMPAIRMENT

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('rx-mode')

	@property
	def TxGapControl(self):
		"""TBD

		Getter Returns:
			AVERAGE_MODE | FIXED_MODE

		Setter Allows:
			AVERAGE_MODE | FIXED_MODE

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('tx-gap-control')

	@property
	def TxMode(self):
		"""TBD

		Getter Returns:
			INTERLEAVED | INTERLEAVED_COARSE | PACKET_IMPAIRMENT | SEQUENTIAL | SEQUENTIAL_COARSE

		Setter Allows:
			INTERLEAVED | INTERLEAVED_COARSE | PACKET_IMPAIRMENT | SEQUENTIAL | SEQUENTIAL_COARSE

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('tx-mode')

	@property
	def CableTypeLength(self):
		"""TBD

		Getter Returns:
			OPTICAL | COPPER_OM_2M | COPPER_3M | COPPER_5M | COPPER_7M | COPPER_OM_1M | COPPER_2M | COPPER_5M_ACTIVE | COPPER_7M_ACTIVE

		Setter Allows:
			OPTICAL | COPPER_OM_2M | COPPER_3M | COPPER_5M | COPPER_7M | COPPER_OM_1M | COPPER_2M | COPPER_5M_ACTIVE | COPPER_7M_ACTIVE

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('cable-type-length')

	@property
	def CfpInterface(self):
		"""TBD

		Getter Returns:
			ACC_6068A | ACC_6069A | ACC_6068A_CISCO_100G_SR10 | ACC_6069A_CISCO_40G_SR4 | CISCO_FINISAR_100G_LR4_v1_5 | OTHER_CFP | LR4_100GBASE | SR10_100GBASE | CXP_SR10_100GBASE | CFP4_LR4_100GBASE | CFP4_SR4_100GBASE | CFP4_CR4_100GBASE | QSFP28_LR4_100GBASE | QSFP28_SR4_100GBASE | QSFP28_CR4_100GBASE | QSFP28_AOC_100GBASE

		Setter Allows:
			ACC_6068A | ACC_6069A | ACC_6068A_CISCO_100G_SR10 | ACC_6069A_CISCO_40G_SR4 | CISCO_FINISAR_100G_LR4_v1_5 | OTHER_CFP | LR4_100GBASE | SR10_100GBASE | CXP_SR10_100GBASE | CFP4_LR4_100GBASE | CFP4_SR4_100GBASE | CFP4_CR4_100GBASE | QSFP28_LR4_100GBASE | QSFP28_SR4_100GBASE | QSFP28_CR4_100GBASE | QSFP28_AOC_100GBASE

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('cfp-interface')

	@property
	def DeficitIdleCount(self):
		"""Deficit Idle Count

		Getter Returns:
			boolean

		Setter Allows:
			boolean

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('deficit-idle-count')

	def update(self, AutoInstrumentation=None, AutoNegotiationEnabled=None, MasterSlaveType=None, CollisionExponent=None, CustomFecMode=None, DataPathMode=None, FlowControl=None, FlowControlDirectedAddress=None, Mtu=None, PortSetupMode=None, RxMode=None, TxGapControl=None, TxMode=None, CableTypeLength=None, CfpInterface=None, DeficitIdleCount=None):
		"""Update the current instance of the `ethernet-fiber` resource

		Args:
			AutoInstrumentation (enumeration): TBD
			AutoNegotiationEnabled (boolean): If enabled allows for auto negotiation between ports for speed and duplex operation.
			MasterSlaveType (enumeration): When auto negotiation is enabled one of the master slave types can be specified
			CollisionExponent (uint8): TBD
			CustomFecMode (enumeration): TBD
			DataPathMode (enumeration): TBD
			FlowControl (boolean): Enables the port's MAC flow control mechanisms to listen for a directed address pause message
			FlowControlDirectedAddress (string): The 48-bit MAC address that the port listens on for a directed pause.
			Mtu (uint16): TBD
			PortSetupMode (enumeration): TBD
			RxMode (enumeration): TBD
			TxGapControl (enumeration): TBD
			TxMode (enumeration): TBD
			CableTypeLength (enumeration): TBD
			CfpInterface (enumeration): TBD
			DeficitIdleCount (boolean): Deficit Idle Count
		"""
		return self._update(locals())

