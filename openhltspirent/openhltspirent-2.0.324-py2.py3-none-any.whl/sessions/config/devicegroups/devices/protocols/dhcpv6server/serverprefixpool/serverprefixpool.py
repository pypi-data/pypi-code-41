from openhltspirent.base import Base
class ServerPrefixPool(Base):
	"""Default Prefix pool configurations.
	"""
	YANG_NAME = 'server-prefix-pool'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(ServerPrefixPool, self).__init__(parent)

	@property
	def StartIpv6Address(self):
		"""Pool starting IPv6 address.

		Get an instance of the StartIpv6Address class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.startipv6address.startipv6address.StartIpv6Address)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.startipv6address.startipv6address import StartIpv6Address
		return StartIpv6Address(self)._read()

	@property
	def NumberOfPoolsPerServer(self):
		"""Number of pools per server.

		Get an instance of the NumberOfPoolsPerServer class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.numberofpoolsperserver.numberofpoolsperserver.NumberOfPoolsPerServer)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.numberofpoolsperserver.numberofpoolsperserver import NumberOfPoolsPerServer
		return NumberOfPoolsPerServer(self)._read()

	@property
	def PrefixLength(self):
		"""Client prefix length.

		Get an instance of the PrefixLength class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.prefixlength.prefixlength.PrefixLength)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.prefixlength.prefixlength import PrefixLength
		return PrefixLength(self)._read()

	@property
	def PreferredLifetime(self):
		"""Preferred lifetime in seconds for the addresses.

		Get an instance of the PreferredLifetime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.preferredlifetime.preferredlifetime.PreferredLifetime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.preferredlifetime.preferredlifetime import PreferredLifetime
		return PreferredLifetime(self)._read()

	@property
	def ValidLifetime(self):
		"""Valid lifetime in seconds for the addresses.

		Get an instance of the ValidLifetime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.validlifetime.validlifetime.ValidLifetime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.validlifetime.validlifetime import ValidLifetime
		return ValidLifetime(self)._read()

	@property
	def MinIaidValue(self):
		"""The minimum identifier for an IA to accept in the pool.

		Get an instance of the MinIaidValue class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.miniaidvalue.miniaidvalue.MinIaidValue)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.miniaidvalue.miniaidvalue import MinIaidValue
		return MinIaidValue(self)._read()

	@property
	def MaxIaidValue(self):
		"""The maximum identifier for an IA to accept in the pool.

		Get an instance of the MaxIaidValue class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.maxiaidvalue.maxiaidvalue.MaxIaidValue)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.maxiaidvalue.maxiaidvalue import MaxIaidValue
		return MaxIaidValue(self)._read()

	@property
	def RelayAgentInterfaceId(self):
		"""Generate a list of interface ID so that this pool can assign addresses
		for those DHCPv6 clients who match any of the interface ID in the list.

		Get an instance of the RelayAgentInterfaceId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.relayagentinterfaceid.relayagentinterfaceid.RelayAgentInterfaceId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.relayagentinterfaceid.relayagentinterfaceid import RelayAgentInterfaceId
		return RelayAgentInterfaceId(self)._read()

	@property
	def MaxRelayAgentInterfaceIdCount(self):
		"""Maximum interface ID count that can be generated.

		Get an instance of the MaxRelayAgentInterfaceIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.maxrelayagentinterfaceidcount.maxrelayagentinterfaceidcount.MaxRelayAgentInterfaceIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.maxrelayagentinterfaceidcount.maxrelayagentinterfaceidcount import MaxRelayAgentInterfaceIdCount
		return MaxRelayAgentInterfaceIdCount(self)._read()

	@property
	def RelayAgentRemoteId(self):
		"""Generate a list of remote ID so that this pool can assign addresses for those
		DHCPv6 clients who match any of the remote ID in the list.

		Get an instance of the RelayAgentRemoteId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.relayagentremoteid.relayagentremoteid.RelayAgentRemoteId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.relayagentremoteid.relayagentremoteid import RelayAgentRemoteId
		return RelayAgentRemoteId(self)._read()

	@property
	def MaxRelayAgentRemoteIdCount(self):
		"""Maximum remote ID count that can be generated.

		Get an instance of the MaxRelayAgentRemoteIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.maxrelayagentremoteidcount.maxrelayagentremoteidcount.MaxRelayAgentRemoteIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.maxrelayagentremoteidcount.maxrelayagentremoteidcount import MaxRelayAgentRemoteIdCount
		return MaxRelayAgentRemoteIdCount(self)._read()

	@property
	def CustomOptions(self):
		"""DHCPv6 Server custom options

		Get an instance of the CustomOptions class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.customoptions.customoptions.CustomOptions)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.customoptions.customoptions import CustomOptions
		return CustomOptions(self)

