from openhltspirent.base import Base
class Authentication(Base):
	"""TBD
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
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv6.authentication.authenticationtype.authenticationtype.AuthenticationType)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv6.authentication.authenticationtype.authenticationtype import AuthenticationType
		return AuthenticationType(self)._read()

	@property
	def Md5Password(self):
		"""Type a value to be used as a secret MD5 Key for authentication.
		This field is available only if you select MD5 as the type of Authentication.

		Get an instance of the Md5Password class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv6.authentication.md5password.md5password.Md5Password)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv6.authentication.md5password.md5password import Md5Password
		return Md5Password(self)._read()

	def create(self):
		"""Create an instance of the `authentication` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `authentication` resource

		"""
		return self._delete()

