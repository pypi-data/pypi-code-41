from openhltspirent.base import Base
class Dhcpv4Server(Base):
	"""TBD
	"""
	YANG_NAME = 'dhcpv4-server'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv4Server, self).__init__(parent)

	@property
	def AssignStrategy(self):
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

		Get an instance of the AssignStrategy class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.assignstrategy.assignstrategy.AssignStrategy)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.assignstrategy.assignstrategy import AssignStrategy
		return AssignStrategy(self)._read()

	@property
	def AuthenticationToken(self):
		"""Token authentication for forcerenew message.

		Get an instance of the AuthenticationToken class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.authenticationtoken.authenticationtoken.AuthenticationToken)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.authenticationtoken.authenticationtoken import AuthenticationToken
		return AuthenticationToken(self)._read()

	@property
	def DeclineReserveTime(self):
		"""Time in seconds an address will be reserved after it is declined by the client.

		Get an instance of the DeclineReserveTime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.declinereservetime.declinereservetime.DeclineReserveTime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.declinereservetime.declinereservetime import DeclineReserveTime
		return DeclineReserveTime(self)._read()

	@property
	def EnableOverlapAddress(self):
		"""Reuse addresses based on circuit ID.
		For example: say we configured 1 pool with 100 addresses and 5 different circuit ID,
		server can assign 100 addresses for each circuit ID. It is like we have 500 addresses..

		Get an instance of the EnableOverlapAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.enableoverlapaddress.enableoverlapaddress.EnableOverlapAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.enableoverlapaddress.enableoverlapaddress import EnableOverlapAddress
		return EnableOverlapAddress(self)._read()

	@property
	def HostName(self):
		"""Server host name.

		Get an instance of the HostName class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.hostname.hostname.HostName)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.hostname.hostname import HostName
		return HostName(self)._read()

	@property
	def Tos(self):
		"""Provides an indication of the quality of service wanted.

		Get an instance of the Tos class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.tos.tos.Tos)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.tos.tos import Tos
		return Tos(self)._read()

	@property
	def LeaseTime(self):
		"""Default lease time in seconds.

		Get an instance of the LeaseTime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.leasetime.leasetime.LeaseTime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.leasetime.leasetime import LeaseTime
		return LeaseTime(self)._read()

	@property
	def MinAllowedLeaseTime(self):
		"""Minimum allowed lease time in seconds.

		Get an instance of the MinAllowedLeaseTime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.minallowedleasetime.minallowedleasetime.MinAllowedLeaseTime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.minallowedleasetime.minallowedleasetime import MinAllowedLeaseTime
		return MinAllowedLeaseTime(self)._read()

	@property
	def OfferReserveTime(self):
		"""Time in seconds an address will be reserved while the server is waiting
		for a response for an offer..

		Get an instance of the OfferReserveTime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.offerreservetime.offerreservetime.OfferReserveTime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.offerreservetime.offerreservetime import OfferReserveTime
		return OfferReserveTime(self)._read()

	@property
	def RebindingTimePercent(self):
		"""(T2) Percent of the lease time at which the client should begin the rebinding process  .

		Get an instance of the RebindingTimePercent class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.rebindingtimepercent.rebindingtimepercent.RebindingTimePercent)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.rebindingtimepercent.rebindingtimepercent import RebindingTimePercent
		return RebindingTimePercent(self)._read()

	@property
	def RenewalTimePercent(self):
		"""(T1) Percent of the lease time at which the client should begin the renewal process.

		Get an instance of the RenewalTimePercent class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.renewaltimepercent.renewaltimepercent.RenewalTimePercent)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.renewaltimepercent.renewaltimepercent import RenewalTimePercent
		return RenewalTimePercent(self)._read()

	@property
	def DefaultServerAddressPool(self):
		"""Default pool configurations.

		Get an instance of the DefaultServerAddressPool class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.defaultserveraddresspool.DefaultServerAddressPool)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.defaultserveraddresspool.defaultserveraddresspool import DefaultServerAddressPool
		return DefaultServerAddressPool(self)._read()

	@property
	def CustomOptions(self):
		"""DHCPv4 Server custom options

		Get an instance of the CustomOptions class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.customoptions.customoptions.CustomOptions)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.customoptions.customoptions import CustomOptions
		return CustomOptions(self)

	@property
	def RelayAgentAddressPools(self):
		"""Default pool configurations.

		Get an instance of the RelayAgentAddressPools class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentaddresspools.RelayAgentAddressPools)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4server.relayagentaddresspools.relayagentaddresspools import RelayAgentAddressPools
		return RelayAgentAddressPools(self)

