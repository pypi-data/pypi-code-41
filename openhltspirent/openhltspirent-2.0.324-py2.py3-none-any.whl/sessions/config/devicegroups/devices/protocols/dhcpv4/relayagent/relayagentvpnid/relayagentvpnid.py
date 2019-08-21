from openhltspirent.base import Base
class RelayAgentVpnId(Base):
	"""Relay agent virtual subnet selection sub-option in DHCP messages sent from emulated relay agent.
	The virtual subnet selection sub-option is described in RFC 6607.
	"""
	YANG_NAME = 'relay-agent-vpn-id'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(RelayAgentVpnId, self).__init__(parent)

	@property
	def VpnId(self):
		"""VPN ID

		Get an instance of the VpnId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentvpnid.vpnid.vpnid.VpnId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentvpnid.vpnid.vpnid import VpnId
		return VpnId(self)._read()

	@property
	def VpnIdType(self):
		"""VPN ID Type
		NVT_ASCII : Network Virtual Terminal (NVT) ASCII VPN identifier
		RFC_2685  : RFC 2685 VPN-ID

		Get an instance of the VpnIdType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentvpnid.vpnidtype.vpnidtype.VpnIdType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentvpnid.vpnidtype.vpnidtype import VpnIdType
		return VpnIdType(self)._read()

