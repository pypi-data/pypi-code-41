from openhltspirent.base import Base
class RequestMessage(Base):
	"""Request message options
	"""
	YANG_NAME = 'request-message'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(RequestMessage, self).__init__(parent)

	@property
	def InitialTimeout(self):
		"""Specifiy the time (in seconds) that the host waits to receive
		a REPLY message from the delegating router after sending an initial
		REQUEST message.If the host does not receive a valid REPLY message
		within this time,it sends another REQUEST message and the timeout
		length is doubled fromthe previous attempt.

		Get an instance of the InitialTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.initialtimeout.initialtimeout.InitialTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.initialtimeout.initialtimeout import InitialTimeout
		return InitialTimeout(self)._read()

	@property
	def MaxTimeout(self):
		"""Specify the maximum timeout value (in seconds) that the host waits
		for an REPLY message.
		If an initial REQUEST message is unsuccessful and times out, the
		timeoutvalue for subsequent attempts is either double the previous
		timeout value or the value specified for this field, whichever is
		lower. Thisfield limits the retry timeout time, which can become
		long if it continuesto double with each retry. If the REQUEST
		timeout value is set to the MaximumRequest Retry Timeout value,
		the client tries to resend the REQUESTmessage for the number of
		times specified in the Request Retry Count field.

		Get an instance of the MaxTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.maxtimeout.maxtimeout.MaxTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.maxtimeout.maxtimeout import MaxTimeout
		return MaxTimeout(self)._read()

	@property
	def RetryCount(self):
		"""Specify the maximum number of retries to establish a DHCPv6/PD session with
		the REQUEST message. When this number is reached, the port increments the
		failure counter.

		Get an instance of the RetryCount class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.retrycount.retrycount.RetryCount)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.retrycount.retrycount import RetryCount
		return RetryCount(self)._read()

	@property
	def IndefiniteRetry(self):
		"""Flag indicating requests will retried indefinitely.
		TRUE  : Enable indefinite retry of requests.
		FALSE : Disable indefinite retry of requests.

		Get an instance of the IndefiniteRetry class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.indefiniteretry.indefiniteretry.IndefiniteRetry)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.indefiniteretry.indefiniteretry import IndefiniteRetry
		return IndefiniteRetry(self)._read()

	@property
	def DisableRetries(self):
		"""Flag indicating requests will be not be retried.
		TRUE  : Disable retry of requests.
		FALSE : Enable retry of requests.

		Get an instance of the DisableRetries class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.disableretries.disableretries.DisableRetries)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.disableretries.disableretries import DisableRetries
		return DisableRetries(self)._read()

	def create(self):
		"""Create an instance of the `request-message` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `request-message` resource

		"""
		return self._delete()

