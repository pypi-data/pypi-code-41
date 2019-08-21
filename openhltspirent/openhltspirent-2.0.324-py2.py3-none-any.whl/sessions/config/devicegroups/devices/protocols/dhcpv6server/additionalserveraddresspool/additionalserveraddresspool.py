from openhltspirent.base import Base
class AdditionalServerAddressPool(Base):
	"""Additional address pools configurations.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/device-groups/devices/protocols/dhcpv6-server/additional-server-address-pool resource.
	"""
	YANG_NAME = 'additional-server-address-pool'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(AdditionalServerAddressPool, self).__init__(parent)

	@property
	def StartIpv6Address(self):
		"""Pool starting IPv6 address.

		Get an instance of the StartIpv6Address class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.startipv6address.startipv6address.StartIpv6Address)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.startipv6address.startipv6address import StartIpv6Address
		return StartIpv6Address(self)._read()

	@property
	def NumberOfPoolsPerServer(self):
		"""Number of pools per server.

		Get an instance of the NumberOfPoolsPerServer class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.numberofpoolsperserver.numberofpoolsperserver.NumberOfPoolsPerServer)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.numberofpoolsperserver.numberofpoolsperserver import NumberOfPoolsPerServer
		return NumberOfPoolsPerServer(self)._read()

	@property
	def PrefixLength(self):
		"""Client prefix length.

		Get an instance of the PrefixLength class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.prefixlength.prefixlength.PrefixLength)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.prefixlength.prefixlength import PrefixLength
		return PrefixLength(self)._read()

	@property
	def PreferredLifetime(self):
		"""Preferred lifetime in seconds for the addresses.

		Get an instance of the PreferredLifetime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.preferredlifetime.preferredlifetime.PreferredLifetime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.preferredlifetime.preferredlifetime import PreferredLifetime
		return PreferredLifetime(self)._read()

	@property
	def ValidLifetime(self):
		"""Valid lifetime in seconds for the addresses.

		Get an instance of the ValidLifetime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.validlifetime.validlifetime.ValidLifetime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.validlifetime.validlifetime import ValidLifetime
		return ValidLifetime(self)._read()

	@property
	def MinIaidValue(self):
		"""The minimum identifier for an IA to accept in the pool.

		Get an instance of the MinIaidValue class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.miniaidvalue.miniaidvalue.MinIaidValue)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.miniaidvalue.miniaidvalue import MinIaidValue
		return MinIaidValue(self)._read()

	@property
	def MaxIaidValue(self):
		"""The maximum identifier for an IA to accept in the pool.

		Get an instance of the MaxIaidValue class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.maxiaidvalue.maxiaidvalue.MaxIaidValue)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.maxiaidvalue.maxiaidvalue import MaxIaidValue
		return MaxIaidValue(self)._read()

	@property
	def RelayAgentInterfaceId(self):
		"""Generate a list of interface ID so that this pool can assign addresses
		for those DHCPv6 clients who match any of the interface ID in the list.

		Get an instance of the RelayAgentInterfaceId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.relayagentinterfaceid.relayagentinterfaceid.RelayAgentInterfaceId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.relayagentinterfaceid.relayagentinterfaceid import RelayAgentInterfaceId
		return RelayAgentInterfaceId(self)._read()

	@property
	def MaxRelayAgentInterfaceIdCount(self):
		"""Maximum interface ID count that can be generated.

		Get an instance of the MaxRelayAgentInterfaceIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.maxrelayagentinterfaceidcount.maxrelayagentinterfaceidcount.MaxRelayAgentInterfaceIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.maxrelayagentinterfaceidcount.maxrelayagentinterfaceidcount import MaxRelayAgentInterfaceIdCount
		return MaxRelayAgentInterfaceIdCount(self)._read()

	@property
	def RelayAgentRemoteId(self):
		"""Generate a list of remote ID so that this pool can assign addresses for those
		DHCPv6 clients who match any of the remote ID in the list.

		Get an instance of the RelayAgentRemoteId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.relayagentremoteid.relayagentremoteid.RelayAgentRemoteId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.relayagentremoteid.relayagentremoteid import RelayAgentRemoteId
		return RelayAgentRemoteId(self)._read()

	@property
	def MaxRelayAgentRemoteIdCount(self):
		"""Maximum remote ID count that can be generated.

		Get an instance of the MaxRelayAgentRemoteIdCount class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.maxrelayagentremoteidcount.maxrelayagentremoteidcount.MaxRelayAgentRemoteIdCount)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.maxrelayagentremoteidcount.maxrelayagentremoteidcount import MaxRelayAgentRemoteIdCount
		return MaxRelayAgentRemoteIdCount(self)._read()

	@property
	def CustomOptions(self):
		"""DHCPv6 Server custom options

		Get an instance of the CustomOptions class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.customoptions.customoptions.CustomOptions)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.customoptions.customoptions import CustomOptions
		return CustomOptions(self)

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
		"""Get `additional-server-address-pool` resource(s). Returns all `additional-server-address-pool` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `additional-server-address-pool` resource

		Args:
			Name (string): The unique name address pool object
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `additional-server-address-pool` resource

		"""
		return self._delete()

