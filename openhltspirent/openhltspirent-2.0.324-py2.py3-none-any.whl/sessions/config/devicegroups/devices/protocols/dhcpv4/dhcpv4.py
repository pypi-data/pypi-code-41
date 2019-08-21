from openhltspirent.base import Base
class Dhcpv4(Base):
	"""TBD
	"""
	YANG_NAME = 'dhcpv4'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv4, self).__init__(parent)

	@property
	def DefaultHostAddressPrefixLength(self):
		"""Subnet mask value to use for when the server doesn't include option 1 (Subnet Mask) in the DHCPOFFER message.

		Get an instance of the DefaultHostAddressPrefixLength class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.defaulthostaddressprefixlength.defaulthostaddressprefixlength.DefaultHostAddressPrefixLength)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.defaulthostaddressprefixlength.defaulthostaddressprefixlength import DefaultHostAddressPrefixLength
		return DefaultHostAddressPrefixLength(self)._read()

	@property
	def EnableArpServerId(self):
		"""To send an ARP to the Server ID returned during binding. The MAC address obtained in this
		process is used as the destination address for Renew Request and Release messages.
		If no ARP reply is received, the configured destination MAC is used.

		Get an instance of the EnableArpServerId class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enablearpserverid.enablearpserverid.EnableArpServerId)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enablearpserverid.enablearpserverid import EnableArpServerId
		return EnableArpServerId(self)._read()

	@property
	def EnableAutoRetry(self):
		"""Auto retry will retry sessions that fail to initially come up
		   NONE : Do not retry failed sessions
		   BLOCK_AUTO_RETRY : Retry DHCP sessions after all sessions in the same device block reach an IDLE/CONNECTED state
		   SESSION_AUTO_RETRY : Retry a DHCP session after it fails without waiting for the other sessions in the device block

		Get an instance of the EnableAutoRetry class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enableautoretry.enableautoretry.EnableAutoRetry)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enableautoretry.enableautoretry import EnableAutoRetry
		return EnableAutoRetry(self)._read()

	@property
	def AutoRetryAttempts(self):
		"""Number of retry attempts.

		Get an instance of the AutoRetryAttempts class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.autoretryattempts.autoretryattempts.AutoRetryAttempts)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.autoretryattempts.autoretryattempts import AutoRetryAttempts
		return AutoRetryAttempts(self)._read()

	@property
	def EnableBroadcastFlag(self):
		"""Enable broadcast bit to signal the DHCP server and BOOTP relay agent to broadcast
		any messages to the client on the client's subnet.

		Get an instance of the EnableBroadcastFlag class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enablebroadcastflag.enablebroadcastflag.EnableBroadcastFlag)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enablebroadcastflag.enablebroadcastflag import EnableBroadcastFlag
		return EnableBroadcastFlag(self)._read()

	@property
	def EnableClientMacAddressDataplane(self):
		"""Use client MAC address for the data plane.

		Get an instance of the EnableClientMacAddressDataplane class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enableclientmacaddressdataplane.enableclientmacaddressdataplane.EnableClientMacAddressDataplane)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enableclientmacaddressdataplane.enableclientmacaddressdataplane import EnableClientMacAddressDataplane
		return EnableClientMacAddressDataplane(self)._read()

	@property
	def EnableRouterOption(self):
		"""Enable the router option (option 3) specified in RFC 2132.

		Get an instance of the EnableRouterOption class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enablerouteroption.enablerouteroption.EnableRouterOption)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.enablerouteroption.enablerouteroption import EnableRouterOption
		return EnableRouterOption(self)._read()

	@property
	def SessionHostName(self):
		"""Unique hostname of emulated client.

		Get an instance of the SessionHostName class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.sessionhostname.sessionhostname.SessionHostName)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.sessionhostname.sessionhostname import SessionHostName
		return SessionHostName(self)._read()

	@property
	def Tos(self):
		"""Provides an indication of the quality of service wanted.

		Get an instance of the Tos class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.tos.tos.Tos)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.tos.tos import Tos
		return Tos(self)._read()

	@property
	def OptionList(self):
		"""A space-separated list of Option 55 numbers for the DHCP request messages on each session block.
		This attribute can have one or more of the following values:
		   1 - Subnet Mask Option.
		   3 - Router Option.
		   6 - Domain Name Servers Option.
		   15 - Domain Name Option.
		   33 - Static Routes Option.
		   44 - NetBIOS Name Servers Option.
		   46 - NetBIOS Node Type Option.
		   47 - NetBIOS Scope Option.
		   51 - IP Address Lease Time Option.
		   54 - Server Identifier Option.
		   58 - Renewal Time (T1) Option.
		   59 - Rebinding Time (T2) Option.

		Get an instance of the OptionList class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.optionlist.optionlist.OptionList)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.optionlist.optionlist import OptionList
		return OptionList(self)._read()

	@property
	def DnaV4DestinationIpAddress(self):
		"""Destination IP address for testing reachability per RFC 4436.

		Get an instance of the DnaV4DestinationIpAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.dnav4destinationipaddress.dnav4destinationipaddress.DnaV4DestinationIpAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.dnav4destinationipaddress.dnav4destinationipaddress import DnaV4DestinationIpAddress
		return DnaV4DestinationIpAddress(self)._read()

	@property
	def DnaV4DestinationMacAddress(self):
		"""Destination MAC address for testing reachability per RFC 4436.

		Get an instance of the DnaV4DestinationMacAddress class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.dnav4destinationmacaddress.dnav4destinationmacaddress.DnaV4DestinationMacAddress)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.dnav4destinationmacaddress.dnav4destinationmacaddress import DnaV4DestinationMacAddress
		return DnaV4DestinationMacAddress(self)._read()

	@property
	def CustomOptions(self):
		"""DHCPv4 custom options

		Get an instance of the CustomOptions class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.customoptions.customoptions.CustomOptions)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.customoptions.customoptions import CustomOptions
		return CustomOptions(self)

	@property
	def RelayAgent(self):
		"""TBD

		Get an instance of the RelayAgent class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagent.RelayAgent)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv4.relayagent.relayagent import RelayAgent
		return RelayAgent(self)._read()

