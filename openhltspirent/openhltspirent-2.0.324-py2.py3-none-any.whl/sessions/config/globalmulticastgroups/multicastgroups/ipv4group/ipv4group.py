from openhltspirent.base import Base
class Ipv4Group(Base):
	"""IPV4 multicast group details
	"""
	YANG_NAME = 'ipv4-group'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Ipv4Group, self).__init__(parent)

	@property
	def Address(self):
		"""IP address

		Get an instance of the Address class.

		Returns:
			obj(openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv4group.address.address.Address)
		"""
		from openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv4group.address.address import Address
		return Address(self)._read()

	@property
	def PrefixLength(self):
		"""Prefix Length

		Get an instance of the PrefixLength class.

		Returns:
			obj(openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv4group.prefixlength.prefixlength.PrefixLength)
		"""
		from openhltspirent.sessions.config.globalmulticastgroups.multicastgroups.ipv4group.prefixlength.prefixlength import PrefixLength
		return PrefixLength(self)._read()

