from openhltspirent.base import Base
class DefaultServerAddressPool(Base):
	"""Default pool configurations.
	"""
	YANG_NAME = 'default-server-address-pool'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(DefaultServerAddressPool, self).__init__(parent)

	@property
	def StartIpv4Address(self):
		"""Pool starting IP address.

		Get an instance of the StartIpv4Address class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.startipv4address.startipv4address.StartIpv4Address)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.startipv4address.startipv4address import StartIpv4Address
		return StartIpv4Address(self)._read()

	@property
	def CustomHostAddressPrefixLength(self):
		"""Customized prefix length value.

		Get an instance of the CustomHostAddressPrefixLength class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.customhostaddressprefixlength.customhostaddressprefixlength.CustomHostAddressPrefixLength)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.customhostaddressprefixlength.customhostaddressprefixlength import CustomHostAddressPrefixLength
		return CustomHostAddressPrefixLength(self)._read()

	@property
	def HostAddressCountLimit(self):
		"""Number of addresses in a pool.

		Get an instance of the HostAddressCountLimit class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.hostaddresscountlimit.hostaddresscountlimit.HostAddressCountLimit)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.hostaddresscountlimit.hostaddresscountlimit import HostAddressCountLimit
		return HostAddressCountLimit(self)._read()

	@property
	def RouterList(self):
		"""Router addresses (option 3).

		Get an instance of the RouterList class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.routerlist.routerlist.RouterList)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.routerlist.routerlist import RouterList
		return RouterList(self)._read()

	@property
	def DomainName(self):
		"""Domain name (option 15).

		Get an instance of the DomainName class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.domainname.domainname.DomainName)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.domainname.domainname import DomainName
		return DomainName(self)._read()

	@property
	def DomainNameServerList(self):
		"""Domain name servers (option 6).

		Get an instance of the DomainNameServerList class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.domainnameserverlist.domainnameserverlist.DomainNameServerList)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.domainnameserverlist.domainnameserverlist import DomainNameServerList
		return DomainNameServerList(self)._read()

	@property
	def RelayAgentCircuitId(self):
		"""Generate a list of circuit ID so that this pool can assign addresses for those
		   DHCP clients who match any of the circuit ID in the list.

		Get an instance of the RelayAgentCircuitId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.relayagentcircuitid.relayagentcircuitid.RelayAgentCircuitId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.relayagentcircuitid.relayagentcircuitid import RelayAgentCircuitId
		return RelayAgentCircuitId(self)._read()

	@property
	def MaxRelayAgentCircuitIdCount(self):
		"""Maximum circuit ID count that can be generated.

		Get an instance of the MaxRelayAgentCircuitIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.maxrelayagentcircuitidcount.maxrelayagentcircuitidcount.MaxRelayAgentCircuitIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.maxrelayagentcircuitidcount.maxrelayagentcircuitidcount import MaxRelayAgentCircuitIdCount
		return MaxRelayAgentCircuitIdCount(self)._read()

	@property
	def RelayAgentRemoteId(self):
		"""Generate a list of remote ID so that this pool can assign addresses for those
		   DHCP clients who match any of the remote ID in the list.

		Get an instance of the RelayAgentRemoteId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.relayagentremoteid.relayagentremoteid.RelayAgentRemoteId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.relayagentremoteid.relayagentremoteid import RelayAgentRemoteId
		return RelayAgentRemoteId(self)._read()

	@property
	def MaxRelayAgentRemoteIdCount(self):
		"""Maximum remote ID count that can be generated.

		Get an instance of the MaxRelayAgentRemoteIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.maxrelayagentremoteidcount.maxrelayagentremoteidcount.MaxRelayAgentRemoteIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.maxrelayagentremoteidcount.maxrelayagentremoteidcount import MaxRelayAgentRemoteIdCount
		return MaxRelayAgentRemoteIdCount(self)._read()

	@property
	def RelayAgentVpnId(self):
		"""Generate a list of VPN ID so that this pool can assign addresses for those DHCP clients who match any of the VPN ID in the list.

		Get an instance of the RelayAgentVpnId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.relayagentvpnid.relayagentvpnid.RelayAgentVpnId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.relayagentvpnid.relayagentvpnid import RelayAgentVpnId
		return RelayAgentVpnId(self)._read()

	@property
	def RelayAgentVpnIdType(self):
		"""VPN ID Type
		NVT_ASCII : Network Virtual Terminal (NVT) ASCII VPN identifier
		RFC_2685  : RFC 2685 VPN-ID

		Get an instance of the RelayAgentVpnIdType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.relayagentvpnidtype.relayagentvpnidtype.RelayAgentVpnIdType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.relayagentvpnidtype.relayagentvpnidtype import RelayAgentVpnIdType
		return RelayAgentVpnIdType(self)._read()

	@property
	def MaxRelayAgentVpnIdCount(self):
		"""Maximum VPN ID count that can be generated.

		Get an instance of the MaxRelayAgentVpnIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.maxrelayagentvpnidcount.maxrelayagentvpnidcount.MaxRelayAgentVpnIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.maxrelayagentvpnidcount.maxrelayagentvpnidcount import MaxRelayAgentVpnIdCount
		return MaxRelayAgentVpnIdCount(self)._read()

