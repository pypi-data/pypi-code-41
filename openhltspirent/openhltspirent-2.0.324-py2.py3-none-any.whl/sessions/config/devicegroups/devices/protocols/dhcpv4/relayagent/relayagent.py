from openhltspirent.base import Base
class RelayAgent(Base):
	"""TBD
	"""
	YANG_NAME = 'relay-agent'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(RelayAgent, self).__init__(parent)

	@property
	def RelayAgentCircuitId(self):
		"""Relay Agent Circuit Identifier.

		Get an instance of the RelayAgentCircuitId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentcircuitid.relayagentcircuitid.RelayAgentCircuitId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentcircuitid.relayagentcircuitid import RelayAgentCircuitId
		return RelayAgentCircuitId(self)._read()

	@property
	def RelayAgentLinkSelection(self):
		"""Relay agent link selection sub-option in DHCP messages sent from emulated relay agent.
		The link selection sub-option is described in RFC 3527.

		Get an instance of the RelayAgentLinkSelection class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentlinkselection.relayagentlinkselection.RelayAgentLinkSelection)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentlinkselection.relayagentlinkselection import RelayAgentLinkSelection
		return RelayAgentLinkSelection(self)._read()

	@property
	def RelayAgentServerIdOverride(self):
		"""Relay agent server identifier override sub-option in DHCP messages sent from emulated relay agent.
		The server identifier override sub-option is described in RFC 5107.

		Get an instance of the RelayAgentServerIdOverride class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentserveridoverride.relayagentserveridoverride.RelayAgentServerIdOverride)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentserveridoverride.relayagentserveridoverride import RelayAgentServerIdOverride
		return RelayAgentServerIdOverride(self)._read()

	@property
	def RelayAgentVpnId(self):
		"""Relay agent virtual subnet selection sub-option in DHCP messages sent from emulated relay agent.
		The virtual subnet selection sub-option is described in RFC 6607.

		Get an instance of the RelayAgentVpnId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentvpnid.relayagentvpnid.RelayAgentVpnId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentvpnid.relayagentvpnid import RelayAgentVpnId
		return RelayAgentVpnId(self)._read()

	@property
	def RelayAgentRemoteId(self):
		"""Remote ID sub-option in the DHCP messages that are sent from the emulated relay agent.
		The remote ID sub-option is described in RFC 3046.

		Get an instance of the RelayAgentRemoteId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentremoteid.relayagentremoteid.RelayAgentRemoteId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentremoteid.relayagentremoteid import RelayAgentRemoteId
		return RelayAgentRemoteId(self)._read()

	@property
	def RelayAgentIpv4Address(self):
		"""Source IP address of the relay agent message.

		Get an instance of the RelayAgentIpv4Address class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentipv4address.relayagentipv4address.RelayAgentIpv4Address)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentipv4address.relayagentipv4address import RelayAgentIpv4Address
		return RelayAgentIpv4Address(self)._read()

	@property
	def RelayAgentMacAddress(self):
		"""MAC address of the relay agent message.

		Get an instance of the RelayAgentMacAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentmacaddress.relayagentmacaddress.RelayAgentMacAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentmacaddress.relayagentmacaddress import RelayAgentMacAddress
		return RelayAgentMacAddress(self)._read()

	@property
	def RelayAgentPoolIpv4Address(self):
		"""IP address of the interface on the relay agent that is connectedto the DHCP hosts.

		Get an instance of the RelayAgentPoolIpv4Address class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentpoolipv4address.relayagentpoolipv4address.RelayAgentPoolIpv4Address)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentpoolipv4address.relayagentpoolipv4address import RelayAgentPoolIpv4Address
		return RelayAgentPoolIpv4Address(self)._read()

	@property
	def RelayAgentServerIpv4Address(self):
		"""Destination IP address for the relay agent message.

		Get an instance of the RelayAgentServerIpv4Address class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentserveripv4address.relayagentserveripv4address.RelayAgentServerIpv4Address)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagentserveripv4address.relayagentserveripv4address import RelayAgentServerIpv4Address
		return RelayAgentServerIpv4Address(self)._read()

