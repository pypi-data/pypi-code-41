from openhltspirent.base import Base
class DelayedAuthentication(Base):
	"""Delayed authentication
	"""
	YANG_NAME = 'delayed-authentication'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(DelayedAuthentication, self).__init__(parent)

	@property
	def DhcpRealm(self):
		"""DHCP realm that identifies the key used to generate the HMAC-MD5 value when using delayed authentication.

		Get an instance of the DhcpRealm class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.delayedauthentication.dhcprealm.dhcprealm.DhcpRealm)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.delayedauthentication.dhcprealm.dhcprealm import DhcpRealm
		return DhcpRealm(self)._read()

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
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.delayedauthentication.authprotocol.authprotocol.AuthProtocol)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.delayedauthentication.authprotocol.authprotocol import AuthProtocol
		return AuthProtocol(self)._read()

	@property
	def AuthKeys(self):
		"""A list of Authentication Keys.

		Get an instance of the AuthKeys class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.delayedauthentication.authkeys.authkeys.AuthKeys)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.dhcpv6server.delayedauthentication.authkeys.authkeys import AuthKeys
		return AuthKeys(self)

	def create(self):
		"""Create an instance of the `delayed-authentication` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `delayed-authentication` resource

		"""
		return self._delete()

