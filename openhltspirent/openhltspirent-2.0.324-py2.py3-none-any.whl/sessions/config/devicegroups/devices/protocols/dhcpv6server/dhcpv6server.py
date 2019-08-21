from openhltspirent.base import Base
class Dhcpv6Server(Base):
	"""TBD
	"""
	YANG_NAME = 'dhcpv6-server'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv6Server, self).__init__(parent)

	@property
	def AssignStrategy(self):
		"""The strategy that server choose address pools which are used for assign address.
		INTERFACE_ID : Assign address from those pools who match the relay agent interface ID option received.
		REMOTE_ID	 : Assign address from those pools who match the relay agent remote ID option received.

		Get an instance of the AssignStrategy class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.assignstrategy.assignstrategy.AssignStrategy)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.assignstrategy.assignstrategy import AssignStrategy
		return AssignStrategy(self)._read()

	@property
	def EmulationMode(self):
		"""Server emulation mode.
		DHCPV6    : Server will emulate a full DHCPv6 server.
		DHCPV6_PD : Server will emulate only a DHCP-PD server.

		Get an instance of the EmulationMode class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.emulationmode.emulationmode.EmulationMode)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.emulationmode.emulationmode import EmulationMode
		return EmulationMode(self)._read()

	@property
	def DelayedAuthentication(self):
		"""Delayed authentication

		Get an instance of the DelayedAuthentication class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.delayedauthentication.delayedauthentication.DelayedAuthentication)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.delayedauthentication.delayedauthentication import DelayedAuthentication
		return DelayedAuthentication(self)

	@property
	def ReconfigurationKey(self):
		"""Specify reconfiguration keys

		Get an instance of the ReconfigurationKey class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.reconfigurationkey.reconfigurationkey.ReconfigurationKey)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.reconfigurationkey.reconfigurationkey import ReconfigurationKey
		return ReconfigurationKey(self)

	@property
	def Ipv6TrafficClass(self):
		"""Traffic Class Value in IP Header.

		Get an instance of the Ipv6TrafficClass class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.ipv6trafficclass.ipv6trafficclass.Ipv6TrafficClass)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.ipv6trafficclass.ipv6trafficclass import Ipv6TrafficClass
		return Ipv6TrafficClass(self)._read()

	@property
	def PreferredLifetime(self):
		"""Preferred lifetime in seconds for the addresses.

		Get an instance of the PreferredLifetime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.preferredlifetime.preferredlifetime.PreferredLifetime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.preferredlifetime.preferredlifetime import PreferredLifetime
		return PreferredLifetime(self)._read()

	@property
	def ValidLifetime(self):
		"""Valid lifetime in seconds for the addresses.

		Get an instance of the ValidLifetime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.validlifetime.validlifetime.ValidLifetime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.validlifetime.validlifetime import ValidLifetime
		return ValidLifetime(self)._read()

	@property
	def RebindingTimePercent(self):
		"""Rebinding lease time (T2) as a percentage of Lease Time.

		Get an instance of the RebindingTimePercent class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.rebindingtimepercent.rebindingtimepercent.RebindingTimePercent)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.rebindingtimepercent.rebindingtimepercent import RebindingTimePercent
		return RebindingTimePercent(self)._read()

	@property
	def RenewalTimePercent(self):
		"""Renewal lease time (T2) as a percentage of Lease Time.

		Get an instance of the RenewalTimePercent class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.renewaltimepercent.renewaltimepercent.RenewalTimePercent)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.renewaltimepercent.renewaltimepercent import RenewalTimePercent
		return RenewalTimePercent(self)._read()

	@property
	def CustomOptions(self):
		"""DHCPv6 Server custom options

		Get an instance of the CustomOptions class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.customoptions.customoptions.CustomOptions)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.customoptions.customoptions import CustomOptions
		return CustomOptions(self)

	@property
	def ServerAddressPool(self):
		"""Default Address pool configurations.

		Get an instance of the ServerAddressPool class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serveraddresspool.serveraddresspool.ServerAddressPool)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serveraddresspool.serveraddresspool import ServerAddressPool
		return ServerAddressPool(self)._read()

	@property
	def ServerPrefixPool(self):
		"""Default Prefix pool configurations.

		Get an instance of the ServerPrefixPool class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.serverprefixpool.ServerPrefixPool)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.serverprefixpool.serverprefixpool import ServerPrefixPool
		return ServerPrefixPool(self)._read()

	@property
	def AdditionalServerAddressPool(self):
		"""Additional address pools configurations.

		Get an instance of the AdditionalServerAddressPool class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.additionalserveraddresspool.AdditionalServerAddressPool)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserveraddresspool.additionalserveraddresspool import AdditionalServerAddressPool
		return AdditionalServerAddressPool(self)

	@property
	def AdditionalServerPrefixPool(self):
		"""Additional prefix delegation pools configurations.

		Get an instance of the AdditionalServerPrefixPool class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserverprefixpool.additionalserverprefixpool.AdditionalServerPrefixPool)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.additionalserverprefixpool.additionalserverprefixpool import AdditionalServerPrefixPool
		return AdditionalServerPrefixPool(self)

