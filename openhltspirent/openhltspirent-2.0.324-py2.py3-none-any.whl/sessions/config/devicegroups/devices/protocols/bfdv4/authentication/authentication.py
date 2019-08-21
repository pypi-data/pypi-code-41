from openhltspirent.base import Base
class Authentication(Base):
	"""Type of authentication to be used
	NONE   : no authentication
	SIMPLE : The packet is authenticated by the receiving router if the password
	matches the authentication key that is included in the packet.
	This method provides little security because the authentication
	key can be learned by capturing packets.
	MD5    : The packet contains a cryptographic checksum, but not the authentication
	key itself. The receiving router performs a calculation based on the
	MD5 algorithm and an authentication key ID. The packet is authenticated
	if the calculated checksum matches. This method provides a stronger
	assurance that routing data originated from a router with a valid
	authentication key.
	"""
	YANG_NAME = 'authentication'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Authentication, self).__init__(parent)

	@property
	def AuthenticationType(self):
		"""Type of authentication to be used

		Get an instance of the AuthenticationType class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bfdv4.authentication.authenticationtype.authenticationtype.AuthenticationType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bfdv4.authentication.authenticationtype.authenticationtype import AuthenticationType
		return AuthenticationType(self)._read()

	@property
	def Password(self):
		"""Authentication password.

		Get an instance of the Password class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bfdv4.authentication.password.password.Password)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bfdv4.authentication.password.password import Password
		return Password(self)._read()

	def create(self):
		"""Create an instance of the `authentication` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `authentication` resource

		"""
		return self._delete()

