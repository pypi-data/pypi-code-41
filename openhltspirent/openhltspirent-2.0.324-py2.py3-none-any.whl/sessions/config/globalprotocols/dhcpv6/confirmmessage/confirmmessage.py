from openhltspirent.base import Base
class ConfirmMessage(Base):
	"""Confirm message options
	"""
	YANG_NAME = 'confirm-message'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(ConfirmMessage, self).__init__(parent)

	@property
	def InitialTimeout(self):
		"""Specifiy the time (in seconds) that the host waits to receive a REPLY message
		from the delegating router after sending an initial CONFIRM message.If the host
		does not receive a valid REPLY message within this time,it sends another CONFIRM
		message and the timeout length is doubled fromthe previous attempt.

		Get an instance of the InitialTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.confirmmessage.initialtimeout.initialtimeout.InitialTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.confirmmessage.initialtimeout.initialtimeout import InitialTimeout
		return InitialTimeout(self)._read()

	@property
	def MaxTimeout(self):
		"""Specify the maximum timeout value (in seconds) that the host waits
		for an REPLY message.
		If an initial CONFIRM message is unsuccessful and times out, the
		timeoutvalue for subsequent attempts is either double the previous
		timeout value or the value specified for this field, whichever is lower.
		This field limits the retry timeout time, which can become long if it
		continues to double with each retry. If the CONFIRM timeout value is
		set to the MaximumCONFIRM Retry Timeout value, the client tries to resend
		the CONFIRM message for the number of times specified in the CONFIRM
		Retry Count field.

		Get an instance of the MaxTimeout class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.confirmmessage.maxtimeout.maxtimeout.MaxTimeout)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.confirmmessage.maxtimeout.maxtimeout import MaxTimeout
		return MaxTimeout(self)._read()

	@property
	def MaxDuration(self):
		"""Specifies an upper bound on the length of time a client may retransmit the confirm message.
		The message exchange fails once the duration is exceeded.

		Get an instance of the MaxDuration class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.confirmmessage.maxduration.maxduration.MaxDuration)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.confirmmessage.maxduration.maxduration import MaxDuration
		return MaxDuration(self)._read()

	def create(self):
		"""Create an instance of the `confirm-message` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `confirm-message` resource

		"""
		return self._delete()

