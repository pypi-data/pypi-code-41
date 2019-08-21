from openhltspirent.base import Base
class Dhcpv6(Base):
	"""This list allows for configuring global DHCPv6 and PD options.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/global-protocols/dhcpv6 resource.
	"""
	YANG_NAME = 'dhcpv6'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "Ports": "ports"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Dhcpv6, self).__init__(parent)

	@property
	def RequestRate(self):
		"""Requests per second for DHCPv6 client leases.

		Get an instance of the RequestRate class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestrate.requestrate.RequestRate)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestrate.requestrate import RequestRate
		return RequestRate(self)._read()

	@property
	def ReleaseRate(self):
		"""Number of DHCPv6 sessions that are released per second.
		Use the Release operation to release DHCPv6 sessions.

		Get an instance of the ReleaseRate class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.releaserate.releaserate.ReleaseRate)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.releaserate.releaserate import ReleaseRate
		return ReleaseRate(self)._read()

	@property
	def RenewRate(self):
		"""Renewals per second for DHCPv6 client renewals.

		Get an instance of the RenewRate class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.renewrate.renewrate.RenewRate)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.renewrate.renewrate import RenewRate
		return RenewRate(self)._read()

	@property
	def OutstandingSessionCount(self):
		"""Number of DHCPv6 sessions to resolve at a time.

		Get an instance of the OutstandingSessionCount class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.outstandingsessioncount.outstandingsessioncount.OutstandingSessionCount)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.outstandingsessioncount.outstandingsessioncount import OutstandingSessionCount
		return OutstandingSessionCount(self)._read()

	@property
	def MaxRetryAttempt(self):
		"""Maximum Session Level Auto Retry Count.

		Get an instance of the MaxRetryAttempt class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.maxretryattempt.maxretryattempt.MaxRetryAttempt)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.maxretryattempt.maxretryattempt import MaxRetryAttempt
		return MaxRetryAttempt(self)._read()

	@property
	def SequenceType(self):
		"""Port-level sequence type that determines in what order sessions are attempted.
		SEQUENTIAL	: Sessions are attempted sequentially across host blocks under the port.
		PARALLEL	  : Sessions are attempted in parallel across host blocks under the port

		Get an instance of the SequenceType class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.sequencetype.sequencetype.SequenceType)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.sequencetype.sequencetype import SequenceType
		return SequenceType(self)._read()

	@property
	def EnableDeviceBlockRate(self):
		"""To Control Block Rate Based On Devices.
		TRUE  : Control Block Rate Based On Devices.
		FALSE : Control Block Rate Based On Port Config.

		Get an instance of the EnableDeviceBlockRate class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.enabledeviceblockrate.enabledeviceblockrate.EnableDeviceBlockRate)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.enabledeviceblockrate.enabledeviceblockrate import EnableDeviceBlockRate
		return EnableDeviceBlockRate(self)._read()

	@property
	def EnableSessionAutoRetry(self):
		"""Session Level Auto Retry.
		TRUE  : Enable Session Level Auto Retry.
		FALSE : Disable Session Level Auto Retry.

		Get an instance of the EnableSessionAutoRetry class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.enablesessionautoretry.enablesessionautoretry.EnableSessionAutoRetry)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.enablesessionautoretry.enablesessionautoretry import EnableSessionAutoRetry
		return EnableSessionAutoRetry(self)._read()

	@property
	def NoWaitMultiAdvertise(self):
		"""DHCPv6 Client Collecting Advertise.
		TRUE  : DHCPv6 Client Use The First Advertise.
		FALSE : DHCPv6 Client Will Collect Advertise.

		Get an instance of the NoWaitMultiAdvertise class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.nowaitmultiadvertise.nowaitmultiadvertise.NoWaitMultiAdvertise)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.nowaitmultiadvertise.nowaitmultiadvertise import NoWaitMultiAdvertise
		return NoWaitMultiAdvertise(self)._read()

	@property
	def SolicitMessage(self):
		"""Solicit message options

		Get an instance of the SolicitMessage class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.solicitmessage.SolicitMessage)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.solicitmessage.solicitmessage import SolicitMessage
		return SolicitMessage(self)

	@property
	def RequestMessage(self):
		"""Request message options

		Get an instance of the RequestMessage class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.requestmessage.RequestMessage)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.requestmessage.requestmessage import RequestMessage
		return RequestMessage(self)

	@property
	def ConfirmMessage(self):
		"""Confirm message options

		Get an instance of the ConfirmMessage class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.confirmmessage.confirmmessage.ConfirmMessage)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.confirmmessage.confirmmessage import ConfirmMessage
		return ConfirmMessage(self)

	@property
	def RenewMessage(self):
		"""Renew message options

		Get an instance of the RenewMessage class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.renewmessage.RenewMessage)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.renewmessage.renewmessage import RenewMessage
		return RenewMessage(self)

	@property
	def RebindMessage(self):
		"""Rebind message options

		Get an instance of the RebindMessage class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.rebindmessage.RebindMessage)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.rebindmessage.rebindmessage import RebindMessage
		return RebindMessage(self)

	@property
	def ReleaseMessage(self):
		"""Release message options

		Get an instance of the ReleaseMessage class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.releasemessage.ReleaseMessage)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.releasemessage.releasemessage import ReleaseMessage
		return ReleaseMessage(self)

	@property
	def DeclineMessage(self):
		"""Decline message options

		Get an instance of the DeclineMessage class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.declinemessage.DeclineMessage)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.declinemessage.declinemessage import DeclineMessage
		return DeclineMessage(self)

	@property
	def InfoRequestMessage(self):
		"""Information Request message options

		Get an instance of the InfoRequestMessage class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.inforequestmessage.InfoRequestMessage)
		"""
		from openhltspirent.sessions.config.globalprotocols.dhcpv6.inforequestmessage.inforequestmessage import InfoRequestMessage
		return InfoRequestMessage(self)

	@property
	def Name(self):
		"""The unique name for a global protocols list item

		Getter Returns:
			string

		Setter Allows:
			string

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('name')

	@property
	def Ports(self):
		"""A list of abstract port references

		Getter Returns:
			list(OpenHLTest.Sessions.Config.Ports.Name)

		Setter Allows:
			obj(OpenHLTest.Sessions.Config.Ports) | list(OpenHLTest.Sessions.Config.Ports.Name)

		Setter Raises:
			ValueError
			InvalidValueError
		"""
		return self._get_value('ports')

	def read(self, Name=None):
		"""Get `dhcpv6` resource(s). Returns all `dhcpv6` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, Ports=None):
		"""Create an instance of the `dhcpv6` resource

		Args:
			Name (string): The unique name for a global protocols list item
			Ports (leafref): A list of abstract port references
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `dhcpv6` resource

		"""
		return self._delete()

	def update(self, Ports=None):
		"""Update the current instance of the `dhcpv6` resource

		Args:
			Ports (leafref): A list of abstract port references
		"""
		return self._update(locals())

