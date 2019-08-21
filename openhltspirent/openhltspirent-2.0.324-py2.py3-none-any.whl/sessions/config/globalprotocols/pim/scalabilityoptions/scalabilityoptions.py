from openhltspirent.base import Base
class ScalabilityOptions(Base):
	"""Scalability options.
	"""
	YANG_NAME = 'scalability-options'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(ScalabilityOptions, self).__init__(parent)

	@property
	def DisableHelloExpireTimer(self):
		"""Disable hello expire timer in scalablity mode.
		TRUE	: Hello expire timer is disabled.
		FALSE	: Hello expire timer is set to user-specified value.

		Get an instance of the DisableHelloExpireTimer class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.scalabilityoptions.disablehelloexpiretimer.disablehelloexpiretimer.DisableHelloExpireTimer)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.scalabilityoptions.disablehelloexpiretimer.disablehelloexpiretimer import DisableHelloExpireTimer
		return DisableHelloExpireTimer(self)._read()

	@property
	def DisableHelloRxInNeighborState(self):
		"""Option to not process hello messages in neighbor state to increase scalability.
		TRUE	: Hello messages are not processed in neighbor state.
		FALSE	: All hello messages are processed in neighbor state.

		Get an instance of the DisableHelloRxInNeighborState class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.scalabilityoptions.disablehellorxinneighborstate.disablehellorxinneighborstate.DisableHelloRxInNeighborState)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.scalabilityoptions.disablehellorxinneighborstate.disablehellorxinneighborstate import DisableHelloRxInNeighborState
		return DisableHelloRxInNeighborState(self)._read()

	@property
	def DisableIncomingMsgProcessing(self):
		"""Option to disable processing of all incoming messages in neighbor state to increase scalability.
		TRUE  : All incoming messages are not processed in neighbor state.
		FALSE	: All incoming messages are processed in neighbor state.

		Get an instance of the DisableIncomingMsgProcessing class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.scalabilityoptions.disableincomingmsgprocessing.disableincomingmsgprocessing.DisableIncomingMsgProcessing)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.scalabilityoptions.disableincomingmsgprocessing.disableincomingmsgprocessing import DisableIncomingMsgProcessing
		return DisableIncomingMsgProcessing(self)._read()

	def create(self):
		"""Create an instance of the `scalability-options` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `scalability-options` resource

		"""
		return self._delete()

