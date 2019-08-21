from openhltspirent.base import Base
class Ipv6Group(Base):
	"""IPV6 multicast group details
	"""
	YANG_NAME = 'ipv6-group'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv6Group, self).__init__(parent)

	@property
	def Address(self):
		"""Start IPv6 address

		Get an instance of the Address class.

		Returns:
			obj(openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv6group.address.address.Address)
		"""
		from openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv6group.address.address import Address
		return Address(self)._read()

	@property
	def PrefixLength(self):
		"""IPv6 Prefix Length

		Get an instance of the PrefixLength class.

		Returns:
			obj(openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv6group.prefixlength.prefixlength.PrefixLength)
		"""
		from openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv6group.prefixlength.prefixlength import PrefixLength
		return PrefixLength(self)._read()

