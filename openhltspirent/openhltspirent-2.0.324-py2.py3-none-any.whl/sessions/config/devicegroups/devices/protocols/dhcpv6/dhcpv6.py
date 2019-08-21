from openhltspirent.base import Base
class Dhcpv6(Base):
	"""TBD
	"""
	YANG_NAME = 'dhcpv6'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv6, self).__init__(parent)

	@property
	def Dhcpv6ClientMode(self):
		"""The type of client to emulate.
		DHCPV6      : The client emulates DHCPv6.
		DHCPPD      : The client emulates DHCP PD.
		DHCPV6ANDPD	: The client emulates DHCPv6 and DHCP PD.

		Get an instance of the Dhcpv6ClientMode class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.dhcpv6clientmode.dhcpv6clientmode.Dhcpv6ClientMode)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.dhcpv6clientmode.dhcpv6clientmode import Dhcpv6ClientMode
		return Dhcpv6ClientMode(self)._read()

	@property
	def AuthProtocol(self):
		"""Specifies whether to use the DHCP message authentication option used to reliably
		identify the source of a DHCP message and to confirm that the contents of the DHCP
		message have not been tampered with.
		Protocol used to generate the authentication information carried in the option.
		DELAYED_AUTH : Use the delayed authentication protocol.
		RECONFIG_KEY : Use the reconfigure key authentication protocol.

		Get an instance of the AuthProtocol class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.authprotocol.authprotocol.AuthProtocol)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.authprotocol.authprotocol import AuthProtocol
		return AuthProtocol(self)._read()

	@property
	def AuthKeys(self):
		"""A list of Authentication Keys.

		Get an instance of the AuthKeys class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.authkeys.authkeys.AuthKeys)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.authkeys.authkeys import AuthKeys
		return AuthKeys(self)

	@property
	def ClientMacAddrStart(self):
		"""DHCPv6 client starting MAC address.

		Get an instance of the ClientMacAddrStart class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.clientmacaddrstart.clientmacaddrstart.ClientMacAddrStart)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.clientmacaddrstart.clientmacaddrstart import ClientMacAddrStart
		return ClientMacAddrStart(self)._read()

	@property
	def ControlPlanePrefix(self):
		"""Control plane source for the IPv6 address prefix.
		LINKLOCAL           : Use the Link-Local address.
		ROUTERADVERTISEMENT	: Use the router advertisement.

		Get an instance of the ControlPlanePrefix class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.controlplaneprefix.controlplaneprefix.ControlPlanePrefix)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.controlplaneprefix.controlplaneprefix import ControlPlanePrefix
		return ControlPlanePrefix(self)._read()

	@property
	def DuplicateAddrDetection(self):
		"""Duplicate address detection. Note that the session will not go bound until the duplicate
		address detection is complete. If duplicate address detection fails, the address will be
		declined and the session will go idle.

		Get an instance of the DuplicateAddrDetection class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duplicateaddrdetection.duplicateaddrdetection.DuplicateAddrDetection)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duplicateaddrdetection.duplicateaddrdetection import DuplicateAddrDetection
		return DuplicateAddrDetection(self)

	@property
	def DhcpRealm(self):
		"""DHCP realm that identifies the key used to generate the HMAC-MD5 value when using delayed authentication.

		Get an instance of the DhcpRealm class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.dhcprealm.dhcprealm.DhcpRealm)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.dhcprealm.dhcprealm import DhcpRealm
		return DhcpRealm(self)._read()

	@property
	def DstAddrType(self):
		"""Determines the DHCP control plane multicast address used as destination ip address.
		ALL_DHCP_RELAY_AGENTS_AND_SERVERS : (FF02::1:2) A link-scoped multicast address used by a
		                                   client to communicate with neighboring relay agents and servers.
		ALL_DHCP_SERVERS : (FF05::1:3) A site-scoped multicast address used by a relay agent to communicate
		                   with servers.

		Get an instance of the DstAddrType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.dstaddrtype.dstaddrtype.DstAddrType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.dstaddrtype.dstaddrtype import DstAddrType
		return DstAddrType(self)._read()

	@property
	def DuidType(self):
		"""DHCPv6 unique identifier type.
		LLT    : Link-layer address plus time.
		EN     : Vendor-assigned unique ID based on enterprise number.
		LL     : Link-layer address.
		CUSTOM : Custom type.

		Get an instance of the DuidType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duidtype.duidtype.DuidType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duidtype.duidtype import DuidType
		return DuidType(self)._read()

	@property
	def DuidEnterprise(self):
		"""Enterprise number to be used in the DUID.

		Get an instance of the DuidEnterprise class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duidenterprise.duidenterprise.DuidEnterprise)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duidenterprise.duidenterprise import DuidEnterprise
		return DuidEnterprise(self)._read()

	@property
	def DuidValue(self):
		"""DHCPv6/PD Unique Identifier Value.

		Get an instance of the DuidValue class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duidvalue.duidvalue.DuidValue)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duidvalue.duidvalue import DuidValue
		return DuidValue(self)._read()

	@property
	def DuidCustomValue(self):
		"""Custom DHCPv6/PD Unique Identifier Value.

		Get an instance of the DuidCustomValue class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duidcustomvalue.duidcustomvalue.DuidCustomValue)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.duidcustomvalue.duidcustomvalue import DuidCustomValue
		return DuidCustomValue(self)._read()

	@property
	def EnableRelayAgent(self):
		"""Relay Agent emulation
		           TRUE  : Enable relay agent emulation.
		           FALSE : Disable relay agent emulation.

		Get an instance of the EnableRelayAgent class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enablerelayagent.enablerelayagent.EnableRelayAgent)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enablerelayagent.enablerelayagent import EnableRelayAgent
		return EnableRelayAgent(self)._read()

	@property
	def EnableLdra(self):
		"""Enable or disable a Lightweight DHCPv6 Relay Agent(LDRA).
		           TRUE  : Enable a Lightweight DHCPv6 Relay Agent(LDRA).
		           FALSE : Disable a Lightweight DHCPv6 Relay Agent(LDRA).

		Get an instance of the EnableLdra class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enableldra.enableldra.EnableLdra)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enableldra.enableldra import EnableLdra
		return EnableLdra(self)._read()

	@property
	def RelayServerIpv6Addr(self):
		"""Relay server IPv6 address.

		Get an instance of the RelayServerIpv6Addr class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.relayserveripv6addr.relayserveripv6addr.RelayServerIpv6Addr)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.relayserveripv6addr.relayserveripv6addr import RelayServerIpv6Addr
		return RelayServerIpv6Addr(self)._read()

	@property
	def UseRelayAgentMacForDataplane(self):
		"""Use the relay agent MAC address (forward-facing device) for traffic
		instead of the emulated session blocks MAC address.
		TRUE  : Use the relay agent's MAC address for the data plane.
		FALSE : Use the linked session block MAC address for the data plane.

		Get an instance of the UseRelayAgentMacForDataplane class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.userelayagentmacfordataplane.userelayagentmacfordataplane.UseRelayAgentMacForDataplane)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.userelayagentmacfordataplane.userelayagentmacfordataplane import UseRelayAgentMacForDataplane
		return UseRelayAgentMacForDataplane(self)._read()

	@property
	def RequestedPrefixLength(self):
		"""Specify the requested length (in bits) of the IPv6 prefix.
		A value of 0 allows the server to specify this value.

		Get an instance of the RequestedPrefixLength class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.requestedprefixlength.requestedprefixlength.RequestedPrefixLength)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.requestedprefixlength.requestedprefixlength import RequestedPrefixLength
		return RequestedPrefixLength(self)._read()

	@property
	def RequestedPrefixStartAddress(self):
		"""Specify the requested IPv6 prefix. A value of 0 allows the server
		to specify this value.

		Get an instance of the RequestedPrefixStartAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.requestedprefixstartaddress.requestedprefixstartaddress.RequestedPrefixStartAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.requestedprefixstartaddress.requestedprefixstartaddress import RequestedPrefixStartAddress
		return RequestedPrefixStartAddress(self)._read()

	@property
	def IaidStartValue(self):
		"""Start value of IAID of each device.

		Get an instance of the IaidStartValue class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.iaidstartvalue.iaidstartvalue.IaidStartValue)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.iaidstartvalue.iaidstartvalue import IaidStartValue
		return IaidStartValue(self)._read()

	@property
	def HomeGatewayStartAddr(self):
		"""Home Gateway starting MAC address.

		Get an instance of the HomeGatewayStartAddr class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.homegatewaystartaddr.homegatewaystartaddr.HomeGatewayStartAddr)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.homegatewaystartaddr.homegatewaystartaddr import HomeGatewayStartAddr
		return HomeGatewayStartAddr(self)._read()

	@property
	def InterfaceId(self):
		"""Identifies the interface on which the client message was received.

		Get an instance of the InterfaceId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.interfaceid.interfaceid.InterfaceId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.interfaceid.interfaceid import InterfaceId
		return InterfaceId(self)._read()

	@property
	def RemoteId(self):
		"""This option may be added by DHCPv6 relay agents that terminate switched or permanent circuits
		and have mechanisms to identify the remote host end of the circuit.

		Get an instance of the RemoteId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.remoteid.remoteid.RemoteId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.remoteid.remoteid import RemoteId
		return RemoteId(self)._read()

	@property
	def RemoteIdEnterprise(self):
		"""For DHCPv6 LDRA or DHCPv6 Relay Agent to identify the vendor's registered Enterprise
		Number as registered with IANA.

		Get an instance of the RemoteIdEnterprise class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.remoteidenterprise.remoteidenterprise.RemoteIdEnterprise)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.remoteidenterprise.remoteidenterprise import RemoteIdEnterprise
		return RemoteIdEnterprise(self)._read()

	@property
	def Dhcpv6ClientRequestedAddr(self):
		"""DHCPv6 client requested starting address.

		Get an instance of the Dhcpv6ClientRequestedAddr class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.dhcpv6clientrequestedaddr.dhcpv6clientrequestedaddr.Dhcpv6ClientRequestedAddr)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.dhcpv6clientrequestedaddr.dhcpv6clientrequestedaddr import Dhcpv6ClientRequestedAddr
		return Dhcpv6ClientRequestedAddr(self)._read()

	@property
	def PreferredLifetime(self):
		"""Preferred lifetime in seconds for the addresses.

		Get an instance of the PreferredLifetime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.preferredlifetime.preferredlifetime.PreferredLifetime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.preferredlifetime.preferredlifetime import PreferredLifetime
		return PreferredLifetime(self)._read()

	@property
	def ValidLifetime(self):
		"""Valid lifetime in seconds for the addresses.

		Get an instance of the ValidLifetime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.validlifetime.validlifetime.ValidLifetime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.validlifetime.validlifetime import ValidLifetime
		return ValidLifetime(self)._read()

	@property
	def T1Timer(self):
		"""Time in seconds at which the client contacts the server from which the addresses
		were obtained to extend the lifetimes of the assigned addresses.

		Get an instance of the T1Timer class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.t1timer.t1timer.T1Timer)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.t1timer.t1timer import T1Timer
		return T1Timer(self)._read()

	@property
	def T2Timer(self):
		"""Time in seconds at which the client contacts any available server to extend the
		lifetimes of the assigned addresses.

		Get an instance of the T2Timer class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.t2timer.t2timer.T2Timer)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.t2timer.t2timer import T2Timer
		return T2Timer(self)._read()

	@property
	def EnableRenew(self):
		"""Specifies whether the host sends a RENEW message to the delegating
		           router when the DHCPv6/PD session's T1 time has expired. The host
		           enters the Renewing state when the elapsed lease lifetime is between
		           T1 and T2, but the State field does not change accordingly.
		           TRUE  : Specifies that host will send a RENEW message when T1 expires.
		           FALSE : Specifies that host will not send a RENEW message when T1 expires.

		Get an instance of the EnableRenew class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enablerenew.enablerenew.EnableRenew)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enablerenew.enablerenew import EnableRenew
		return EnableRenew(self)._read()

	@property
	def EnableRebind(self):
		"""Specifies whether the host sends a REBIND message to the delegating router when
		           the DHCPv6/PD session's T2 time has expired. The lifetime of the prefixes (DHCPv6-PD)
		           or addresses (DHCPv6 client) continues until the Valid Lifetime value is reached.
		           TRUE  : Specifies that the host will send a REBIND message when T2 expires.
		           FALSE : Specifies that the host will not send a REBIND message when T2 expires.

		Get an instance of the EnableRebind class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enablerebind.enablerebind.EnableRebind)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enablerebind.enablerebind import EnableRebind
		return EnableRebind(self)._read()

	@property
	def EnableReconfigAccept(self):
		"""Specifies whether the client is willing to accept Reconfigure messages
		           from the server. The default behavior, in the absence of this option,
		           means unwillingness to accept Reconfigure messages.
		           TRUE  : Specifies that the client is willing to accept Reconfigure messages from the server.
		           FALSE : Specifies that the client is unwilling to accept Reconfigure messages from the server.

		Get an instance of the EnableReconfigAccept class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enablereconfigaccept.enablereconfigaccept.EnableReconfigAccept)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.enablereconfigaccept.enablereconfigaccept import EnableReconfigAccept
		return EnableReconfigAccept(self)._read()

	@property
	def RequestRate(self):
		"""The the rate (in sessions per second) for a host block at whichSOLICIT or REBIND
		messages are sent or at which REQUEST messages aresent after an ADVERTISE message
		is received. For example, if this rateis 100 sessions per second and there are three
		host blocks, the ratefor the entire port is 300 sessions per second. The messages
		apply toDHCPv6/PD prefixes.

		Get an instance of the RequestRate class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.requestrate.requestrate.RequestRate)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.requestrate.requestrate import RequestRate
		return RequestRate(self)._read()

	@property
	def ReleaseRate(self):
		"""The rate (in sessions per second) at which RELEASE messages aresent for a host block.
		For example, if this rate is 100 sessions per secondand there are three host blocks,
		the rate for the entire port is 300 sessionsper second. The messages apply to DHCPv6/PD
		prefixes.

		Get an instance of the ReleaseRate class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.releaserate.releaserate.ReleaseRate)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.releaserate.releaserate import ReleaseRate
		return ReleaseRate(self)._read()

	@property
	def RenewRate(self):
		"""The rate (in sessions per second) at which RENEW messages are sentfor a host block.
		For example, if this rate is 100 sessions per secondand there are three host blocks,
		the rate for the entire port is 300 sessionsper second. The messages apply to DHCPv6/PD
		prefixes.

		Get an instance of the RenewRate class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.renewrate.renewrate.RenewRate)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.renewrate.renewrate import RenewRate
		return RenewRate(self)._read()

	@property
	def Ipv6TrafficClass(self):
		"""Traffic Class Value in IP Header.

		Get an instance of the Ipv6TrafficClass class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.ipv6trafficclass.ipv6trafficclass.Ipv6TrafficClass)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.ipv6trafficclass.ipv6trafficclass import Ipv6TrafficClass
		return Ipv6TrafficClass(self)._read()

	@property
	def RapidCommitMode(self):
		"""Rapid commit operation mode.
		DISABLE : Disable rapid commit mode.
		ENABLE  : Enable rapid commit mode and only honor replies with the Rapid Commit option.
		SERVER  : Enable rapid commit mode and continue binding process whether or not the server
		       responds with a Rapid Commit option. The Rapid Commit option isincluded in the
		       ADVERTISE message. If the Rapid Commit option isenabled on the DUT, the two-message
		       exchanged is used. If the RapidCommit option is disabled on the DUT, the four-message
		       exchange is used

		Get an instance of the RapidCommitMode class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.rapidcommitmode.rapidcommitmode.RapidCommitMode)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6.rapidcommitmode.rapidcommitmode import RapidCommitMode
		return RapidCommitMode(self)._read()

