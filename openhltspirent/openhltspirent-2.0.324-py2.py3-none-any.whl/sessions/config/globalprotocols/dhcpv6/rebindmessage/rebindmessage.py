from openhltspirent.base import Base
class RebindMessage(Base):
	"""Rebind message options
	"""
	YANG_NAME = 'rebind-message'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(RebindMessage, self).__init__(parent)

	@property
	def InitialTimeout(self):
		"""Specifiy the time (in seconds) that the host waits to receive a REPLY
		message from the delegating router after sending an initial REBIND
		message.If the host does not receive a valid REPLY message within this
		time,it sends another REBIND message and the timeout length is doubled
		from the previous attempt.

		Get an instance of the InitialTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.initialtimeout.initialtimeout.InitialTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.initialtimeout.initialtimeout import InitialTimeout
		return InitialTimeout(self)._read()

	@property
	def MaxTimeout(self):
		"""Specify the maximum timeout value (in seconds) that the host waits
		for an REPLY message.
		If an initial REBIND message is unsuccessful and times out, the timeout
		value for subsequent attempts is either double the previous timeout value
		or the value specified for this field, whichever is lower. This field
		limits the retry timeout time, which can become long if it continues
		to double with each retry. If the REBIND timeout value is set to the
		Maximum Rebind Retry Timeout value, the client tries to resend the REBIND
		message until the IPv6 prefix's valid lifetime expires..

		Get an instance of the MaxTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.maxtimeout.maxtimeout.MaxTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.maxtimeout.maxtimeout import MaxTimeout
		return MaxTimeout(self)._read()

	@property
	def RetryCount(self):
		"""Number of rebind retries.

		Get an instance of the RetryCount class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.retrycount.retrycount.RetryCount)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.retrycount.retrycount import RetryCount
		return RetryCount(self)._read()

	@property
	def IndefiniteRetry(self):
		"""Flag indicating rebind will retried indefinitely.
		TRUE  : Enable indefinite retry of rebind.
		FALSE : Disable indefinite retry of rebind.

		Get an instance of the IndefiniteRetry class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.indefiniteretry.indefiniteretry.IndefiniteRetry)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.indefiniteretry.indefiniteretry import IndefiniteRetry
		return IndefiniteRetry(self)._read()

	@property
	def DisableRetries(self):
		"""Flag indicating rebinds will be not be retried.
		TRUE  : Disable retry of rebinds.
		FALSE : Enable retry of rebinds.

		Get an instance of the DisableRetries class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.disableretries.disableretries.DisableRetries)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.disableretries.disableretries import DisableRetries
		return DisableRetries(self)._read()

	def create(self):
		"""Create an instance of the `rebind-message` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `rebind-message` resource

		"""
		return self._delete()

