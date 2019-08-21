from openhltspirent.base import Base
class InfoRequestMessage(Base):
	"""Information Request message options
	"""
	YANG_NAME = 'info-request-message'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(InfoRequestMessage, self).__init__(parent)

	@property
	def InitialTimeout(self):
		"""Specifiy the time (in seconds) that the host waits to receive a REPLY
		message from the delegating router after sending an initial INFORMATION-REQUEST
		message.If the host does not receive a valid REPLY message within this time,it
		sends another INFORMATION-REQUEST message and the timeout length is doubled
		from the previous attempt.

		Get an instance of the InitialTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.initialtimeout.initialtimeout.InitialTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.initialtimeout.initialtimeout import InitialTimeout
		return InitialTimeout(self)._read()

	@property
	def MaxTimeout(self):
		"""Specify the maximum timeout value (in seconds) that the host waits
		for an REPLY message.
		If an initial INFORMATION-REQUEST message is unsuccessful and times out,
		the timeout value for subsequent attempts is either double the previous
		timeout value or the value specified for this field, whichever is lower.
		This field limits the retry timeout time, which can become long if it
		continues to double with each retry. If the INFORMATION-REQUEST timeout
		value is set to the Maximum INFORMATION-REQUEST Retry Timeout value,
		the client tries to resend the INFORMATION-REQUEST message until the
		IPv6 prefix's valid lifetime expires.

		Get an instance of the MaxTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.maxtimeout.maxtimeout.MaxTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.maxtimeout.maxtimeout import MaxTimeout
		return MaxTimeout(self)._read()

	@property
	def RetryCount(self):
		"""Number of info-request message retries.

		Get an instance of the RetryCount class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.retrycount.retrycount.RetryCount)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.retrycount.retrycount import RetryCount
		return RetryCount(self)._read()

	@property
	def IndefiniteRetry(self):
		"""Flag indicating info-request message will retried indefinitely.
		TRUE  : Enable indefinite retry of info-request message.
		FALSE : Disable indefinite retry of info-request message.

		Get an instance of the IndefiniteRetry class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.indefiniteretry.indefiniteretry.IndefiniteRetry)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.indefiniteretry.indefiniteretry import IndefiniteRetry
		return IndefiniteRetry(self)._read()

	@property
	def DisableRetries(self):
		"""Flag indicating info-request message will be not be retried.
		TRUE  : Disable retry of info-request message.
		FALSE : Enable retry of info-request message.

		Get an instance of the DisableRetries class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.disableretries.disableretries.DisableRetries)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.disableretries.disableretries import DisableRetries
		return DisableRetries(self)._read()

	def create(self):
		"""Create an instance of the `info-request-message` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `info-request-message` resource

		"""
		return self._delete()

