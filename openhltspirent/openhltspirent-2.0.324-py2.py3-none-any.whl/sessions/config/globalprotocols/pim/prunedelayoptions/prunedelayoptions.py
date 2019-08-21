from openhltspirent.base import Base
class PruneDelayOptions(Base):
	"""Include the LAN Prune Delay option in PIM Hello messages.
	"""
	YANG_NAME = 'prune-delay-options'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(PruneDelayOptions, self).__init__(parent)

	@property
	def LanPruneDelay(self):
		"""Expected message propagation delay in milliseconds.

		Get an instance of the LanPruneDelay class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.prunedelayoptions.lanprunedelay.lanprunedelay.LanPruneDelay)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.prunedelayoptions.lanprunedelay.lanprunedelay import LanPruneDelay
		return LanPruneDelay(self)._read()

	@property
	def OverrideInterval(self):
		"""Join/Prune override interval in milliseconds.

		Get an instance of the OverrideInterval class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.prunedelayoptions.overrideinterval.overrideinterval.OverrideInterval)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.prunedelayoptions.overrideinterval.overrideinterval import OverrideInterval
		return OverrideInterval(self)._read()

	@property
	def TBit(self):
		"""Disable or enable Joins suppression.
		TRUE  : Disable Joins suppression.
		FALSE	: Enable Joins suppression.

		Get an instance of the TBit class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.pim.prunedelayoptions.tbit.tbit.TBit)
		"""
		from openhltspirent.sessions.config.globalprotocols.pim.prunedelayoptions.tbit.tbit import TBit
		return TBit(self)._read()

	def create(self):
		"""Create an instance of the `prune-delay-options` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `prune-delay-options` resource

		"""
		return self._delete()

