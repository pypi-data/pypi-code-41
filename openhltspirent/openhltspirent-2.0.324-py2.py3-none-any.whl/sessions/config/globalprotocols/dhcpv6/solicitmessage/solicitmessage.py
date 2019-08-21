from openhltspirent.base import Base
class SolicitMessage(Base):
	"""Solicit message options
	"""
	YANG_NAME = 'solicit-message'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(SolicitMessage, self).__init__(parent)

	@property
	def InitialTimeout(self):
		"""Specifiy the time (in seconds) that the host waits to receive an ADVERTISE message from
		the delegating router after sending an initial SOLICIT message.If the host does not receive
		a valid ADVERTISE message within this time,it sends another SOLICIT message and the timeout
		length is doubled fromthe previous attempt.

		Get an instance of the InitialTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.initialtimeout.initialtimeout.InitialTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.initialtimeout.initialtimeout import InitialTimeout
		return InitialTimeout(self)._read()

	@property
	def MaxTimeout(self):
		"""Specify the maximum timeout value (in seconds) that the host waits
		for an ADVERTISE message.
		If an initial SOLICIT message is unsuccessful and times out, the
		timeoutvalue for subsequent attempts is either double the previous
		timeout value or the value specified for this field, whichever is lower.
		This field limits the retry timeout time, which can become long if it
		continues to double with each retry. If the SOLICIT timeout value is
		set to the MaximumSolicit Retry Timeout value, the client tries to
		resend the SOLICIT message for the number of times specified in the
		Solicit Retry Count field.

		Get an instance of the MaxTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.maxtimeout.maxtimeout.MaxTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.maxtimeout.maxtimeout import MaxTimeout
		return MaxTimeout(self)._read()

	@property
	def RetryCount(self):
		"""Specify the maximum number of retries to establish a DHCPv6/PD session with
		the SOLICIT message. When this number is reached, the port incrementsthe
		failure counter.

		Get an instance of the RetryCount class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.retrycount.retrycount.RetryCount)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.retrycount.retrycount import RetryCount
		return RetryCount(self)._read()

	@property
	def IndefiniteRetry(self):
		"""Enable or disable indefinite retry.
		TRUE  : Enable indefinite retry of solicits.
		FALSE : Disable indefinite retry of solicits.

		Get an instance of the IndefiniteRetry class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.indefiniteretry.indefiniteretry.IndefiniteRetry)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.indefiniteretry.indefiniteretry import IndefiniteRetry
		return IndefiniteRetry(self)._read()

	@property
	def DisableRetries(self):
		"""Flag indicating solicits will be not be retried.
		TRUE  : Disable retry of solicits.
		FALSE : Enable retry of solicits.

		Get an instance of the DisableRetries class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.disableretries.disableretries.DisableRetries)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.disableretries.disableretries import DisableRetries
		return DisableRetries(self)._read()

	def create(self):
		"""Create an instance of the `solicit-message` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `solicit-message` resource

		"""
		return self._delete()

