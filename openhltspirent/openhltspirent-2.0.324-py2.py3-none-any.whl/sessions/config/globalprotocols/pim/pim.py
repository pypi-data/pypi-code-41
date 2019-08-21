from openhltspirent.base import Base
class Pim(Base):
	"""This list allows for configuring global PIM options.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/global-protocols/pim resource.
	"""
	YANG_NAME = 'pim'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Pim, self).__init__(parent)

	@property
	def EnablePackGroupRecord(self):
		"""Specifies that multicast groups be combined in Join/Prune messages or sent individually.
		TRUE  : Enables Join/Prune message packing.
		FALSE	: Disables Join/Prune message packing.

		Get an instance of the EnablePackGroupRecord class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.enablepackgrouprecord.enablepackgrouprecord.EnablePackGroupRecord)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.enablepackgrouprecord.enablepackgrouprecord import EnablePackGroupRecord
		return EnablePackGroupRecord(self)._read()

	@property
	def PruneDelayOptions(self):
		"""Include the LAN Prune Delay option in PIM Hello messages.

		Get an instance of the PruneDelayOptions class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.prunedelayoptions.prunedelayoptions.PruneDelayOptions)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.prunedelayoptions.prunedelayoptions import PruneDelayOptions
		return PruneDelayOptions(self)

	@property
	def MsgInterval(self):
		"""Minimum gap, in seconds, between successive PIM messages.

		Get an instance of the MsgInterval class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.msginterval.msginterval.MsgInterval)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.msginterval.msginterval import MsgInterval
		return MsgInterval(self)._read()

	@property
	def MsgRate(self):
		"""Maximum rate, per second, at which PIM messages will be transmitted.

		Get an instance of the MsgRate class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.msgrate.msgrate.MsgRate)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.msgrate.msgrate import MsgRate
		return MsgRate(self)._read()

	@property
	def TriggerHelloDelay(self):
		"""Randomized interval, in seconds, for initial Hello message on boot up or
		triggered Hello message to a rebooting neighbor.

		Get an instance of the TriggerHelloDelay class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.triggerhellodelay.triggerhellodelay.TriggerHelloDelay)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.triggerhellodelay.triggerhellodelay import TriggerHelloDelay
		return TriggerHelloDelay(self)._read()

	@property
	def ScalabilityOptions(self):
		"""Scalability options.

		Get an instance of the ScalabilityOptions class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.scalabilityoptions.scalabilityoptions.ScalabilityOptions)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.scalabilityoptions.scalabilityoptions import ScalabilityOptions
		return ScalabilityOptions(self)

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

	def read(self, Name=None):
		"""Get `pim` resource(s). Returns all `pim` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name):
		"""Create an instance of the `pim` resource

		Args:
			Name (string): The unique name for a global protocols list item
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `pim` resource

		"""
		return self._delete()

