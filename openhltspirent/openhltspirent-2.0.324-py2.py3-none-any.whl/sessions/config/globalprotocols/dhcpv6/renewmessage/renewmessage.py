from openhltspirent.base import Base
class RenewMessage(Base):
	"""Renew message options
	"""
	YANG_NAME = 'renew-message'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(RenewMessage, self).__init__(parent)

	@property
	def InitialTimeout(self):
		"""Specifiy  the time (in seconds) that the host waits to receive a REPLY
		message from the delegating router after sending an initial RENEW message.
		If the host does not receive a valid REPLY message within this time,it
		sends another RENEW message and the timeout length is doubled from the
		previous attempt.

		Get an instance of the InitialTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.initialtimeout.initialtimeout.InitialTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.initialtimeout.initialtimeout import InitialTimeout
		return InitialTimeout(self)._read()

	@property
	def MaxTimeout(self):
		"""Specify the maximum timeout value (in seconds) that the host waits
		for an REPLY message.
		If an initial RENEW message is unsuccessful and times out, the timeout
		value for subsequent attempts is either double the previous timeout value
		or the value specified for this field, whichever is lower. This field
		limits the retry timeout time, which can become long if it continues
		to double with each retry. If the RENEW timeout value is set to the Maximum
		Renew Retry Timeout value, the client tries to resend the RENEW message
		until time T2, when the client starts sending REBIND messages.

		Get an instance of the MaxTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.maxtimeout.maxtimeout.MaxTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.maxtimeout.maxtimeout import MaxTimeout
		return MaxTimeout(self)._read()

	@property
	def RetryCount(self):
		"""Number of renew retries.

		Get an instance of the RetryCount class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.retrycount.retrycount.RetryCount)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.retrycount.retrycount import RetryCount
		return RetryCount(self)._read()

	@property
	def IndefiniteRetry(self):
		"""Flag indicating renew will retried indefinitely.
		TRUE  : Enable indefinite retry of renew.
		FALSE : Disable indefinite retry of renew.

		Get an instance of the IndefiniteRetry class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.indefiniteretry.indefiniteretry.IndefiniteRetry)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.indefiniteretry.indefiniteretry import IndefiniteRetry
		return IndefiniteRetry(self)._read()

	@property
	def DisableRetries(self):
		"""Flag indicating renews will be not be retried.
		TRUE  : Disable retry of renews.
		FALSE : Enable retry of renews.

		Get an instance of the DisableRetries class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.disableretries.disableretries.DisableRetries)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.disableretries.disableretries import DisableRetries
		return DisableRetries(self)._read()

	def create(self):
		"""Create an instance of the `renew-message` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `renew-message` resource

		"""
		return self._delete()

