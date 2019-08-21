from openhltspirent.base import Base
class RelayAgentAddressPools(Base):
	"""Default pool configurations.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/devices/protocols/dhcpv4-server/relay-agent-address-pools resource.
	"""
	YANG_NAME = 'relay-agent-address-pools'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(RelayAgentAddressPools, self).__init__(parent)

	@property
	def StartIpv4Address(self):
		"""Pool starting IP address.

		Get an instance of the StartIpv4Address class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.startipv4address.startipv4address.StartIpv4Address)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.startipv4address.startipv4address import StartIpv4Address
		return StartIpv4Address(self)._read()

	@property
	def CustomHostAddressPrefixLength(self):
		"""Customized prefix length value.

		Get an instance of the CustomHostAddressPrefixLength class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.customhostaddressprefixlength.customhostaddressprefixlength.CustomHostAddressPrefixLength)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.customhostaddressprefixlength.customhostaddressprefixlength import CustomHostAddressPrefixLength
		return CustomHostAddressPrefixLength(self)._read()

	@property
	def HostAddressCountLimit(self):
		"""Number of addresses in a pool.

		Get an instance of the HostAddressCountLimit class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.hostaddresscountlimit.hostaddresscountlimit.HostAddressCountLimit)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.hostaddresscountlimit.hostaddresscountlimit import HostAddressCountLimit
		return HostAddressCountLimit(self)._read()

	@property
	def RouterList(self):
		"""Router addresses (option 3).

		Get an instance of the RouterList class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.routerlist.routerlist.RouterList)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.routerlist.routerlist import RouterList
		return RouterList(self)._read()

	@property
	def DomainName(self):
		"""Domain name (option 15).

		Get an instance of the DomainName class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.domainname.domainname.DomainName)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.domainname.domainname import DomainName
		return DomainName(self)._read()

	@property
	def DomainNameServerList(self):
		"""Domain name servers (option 6).

		Get an instance of the DomainNameServerList class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.domainnameserverlist.domainnameserverlist.DomainNameServerList)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.domainnameserverlist.domainnameserverlist import DomainNameServerList
		return DomainNameServerList(self)._read()

	@property
	def RelayAgentCircuitId(self):
		"""Generate a list of circuit ID so that this pool can assign addresses for those
		   DHCP clients who match any of the circuit ID in the list.

		Get an instance of the RelayAgentCircuitId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentcircuitid.relayagentcircuitid.RelayAgentCircuitId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentcircuitid.relayagentcircuitid import RelayAgentCircuitId
		return RelayAgentCircuitId(self)._read()

	@property
	def MaxRelayAgentCircuitIdCount(self):
		"""Maximum circuit ID count that can be generated.

		Get an instance of the MaxRelayAgentCircuitIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.maxrelayagentcircuitidcount.maxrelayagentcircuitidcount.MaxRelayAgentCircuitIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.maxrelayagentcircuitidcount.maxrelayagentcircuitidcount import MaxRelayAgentCircuitIdCount
		return MaxRelayAgentCircuitIdCount(self)._read()

	@property
	def RelayAgentRemoteId(self):
		"""Generate a list of remote ID so that this pool can assign addresses for those
		   DHCP clients who match any of the remote ID in the list.

		Get an instance of the RelayAgentRemoteId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentremoteid.relayagentremoteid.RelayAgentRemoteId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentremoteid.relayagentremoteid import RelayAgentRemoteId
		return RelayAgentRemoteId(self)._read()

	@property
	def MaxRelayAgentRemoteIdCount(self):
		"""Maximum remote ID count that can be generated.

		Get an instance of the MaxRelayAgentRemoteIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.maxrelayagentremoteidcount.maxrelayagentremoteidcount.MaxRelayAgentRemoteIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.maxrelayagentremoteidcount.maxrelayagentremoteidcount import MaxRelayAgentRemoteIdCount
		return MaxRelayAgentRemoteIdCount(self)._read()

	@property
	def RelayAgentVpnId(self):
		"""Generate a list of VPN ID so that this pool can assign addresses for those DHCP clients who match any of the VPN ID in the list.

		Get an instance of the RelayAgentVpnId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentvpnid.relayagentvpnid.RelayAgentVpnId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentvpnid.relayagentvpnid import RelayAgentVpnId
		return RelayAgentVpnId(self)._read()

	@property
	def RelayAgentVpnIdType(self):
		"""VPN ID Type
		NVT_ASCII : Network Virtual Terminal (NVT) ASCII VPN identifier
		RFC_2685  : RFC 2685 VPN-ID

		Get an instance of the RelayAgentVpnIdType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentvpnidtype.relayagentvpnidtype.RelayAgentVpnIdType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentvpnidtype.relayagentvpnidtype import RelayAgentVpnIdType
		return RelayAgentVpnIdType(self)._read()

	@property
	def MaxRelayAgentVpnIdCount(self):
		"""Maximum VPN ID count that can be generated.

		Get an instance of the MaxRelayAgentVpnIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.maxrelayagentvpnidcount.maxrelayagentvpnidcount.MaxRelayAgentVpnIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.maxrelayagentvpnidcount.maxrelayagentvpnidcount import MaxRelayAgentVpnIdCount
		return MaxRelayAgentVpnIdCount(self)._read()

	@property
	def Name(self):
		"""The unique name address pool object

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	def read(self, Name=None):
		"""Get `relay-agent-address-pools` resource(s). Returns all `relay-agent-address-pools` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `relay-agent-address-pools` resource

		Args:
			Name (string): The unique name address pool object
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `relay-agent-address-pools` resource

		"""
		return self._delete()

