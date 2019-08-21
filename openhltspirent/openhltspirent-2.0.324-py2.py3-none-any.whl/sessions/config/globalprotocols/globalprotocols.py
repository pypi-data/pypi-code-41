from openhltspirent.base import Base
class GlobalProtocols(Base):
	"""This list allows for configuring global protocols options.
	"""
	YANG_NAME = 'global-protocols'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(GlobalProtocols, self).__init__(parent)

	@property
	def Dhcpv4(self):
		"""This list allows for configuring global DHCPv4 options.

		Get an instance of the Dhcpv4 class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv4.dhcpv4.Dhcpv4)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv4.dhcpv4 import Dhcpv4
		return Dhcpv4(self)

	@property
	def Dhcpv6(self):
		"""This list allows for configuring global DHCPv6 and PD options.

		Get an instance of the Dhcpv6 class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.dhcpv6.Dhcpv6)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.dhcpv6 import Dhcpv6
		return Dhcpv6(self)

	@property
	def Igmp(self):
		"""This list allows for configuring global IGMP options.

		Get an instance of the Igmp class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.igmp.igmp.Igmp)
		"""
		from openhltspirent.sessions.config.globalprotocols.igmp.igmp import Igmp
		return Igmp(self)

	@property
	def Mld(self):
		"""This list allows for configuring global MLD options.

		Get an instance of the Mld class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.mld.mld.Mld)
		"""
		from openhltspirent.sessions.config.globalprotocols.mld.mld import Mld
		return Mld(self)

	@property
	def Pim(self):
		"""This list allows for configuring global PIM options.

		Get an instance of the Pim class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.pim.Pim)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.pim import Pim
		return Pim(self)

