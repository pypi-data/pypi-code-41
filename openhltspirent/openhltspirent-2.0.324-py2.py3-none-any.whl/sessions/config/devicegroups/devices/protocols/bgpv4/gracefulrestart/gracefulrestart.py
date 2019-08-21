from openhltspirent.base import Base
class GracefulRestart(Base):
	"""TBD
	"""
	YANG_NAME = 'graceful-restart'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(GracefulRestart, self).__init__(parent)

	@property
	def LongLivedGracefulRestart(self):
		"""BGP long lived graceful restart allows a network operator to choose to maintain stale routing information
		from a failed BGP peer much longer than the existing BGP graceful restart facility.
		   TRUE  : Enable long lived graceful restart
		   FALSE : Disable long lived graceful restart

		Get an instance of the LongLivedGracefulRestart class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.longlivedgracefulrestart.longlivedgracefulrestart.LongLivedGracefulRestart)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.longlivedgracefulrestart.longlivedgracefulrestart import LongLivedGracefulRestart
		return LongLivedGracefulRestart(self)._read()

	@property
	def RestartTime(self):
		"""BGP graceful restart time. The amount of time (in seconds) that the emulated
		router will wait for its peer to re-establish the session. If the session is
		not re-established within this time frame, the stale routes will be removed
		from the route database.

		Get an instance of the RestartTime class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.restarttime.restarttime.RestartTime)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.restarttime.restarttime import RestartTime
		return RestartTime(self)._read()

	@property
	def RestartDelay(self):
		"""The amount of time to wait before initiating a new BGP session. Traffic generator
		will not initiate a new session until this timer expires. If the DUT initiates a
		new session, Spirent TestCenter will process it and establish the session.

		Get an instance of the RestartDelay class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.restartdelay.restartdelay.RestartDelay)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.restartdelay.restartdelay import RestartDelay
		return RestartDelay(self)._read()

	@property
	def AdvertiseEor(self):
		"""Advertise End-of-RIB
		   TRUE  : Send end-of-RIB marker in the update packet
		   FALSE : Do not send end-of-RIB marker in the update packet

		Get an instance of the AdvertiseEor class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.advertiseeor.advertiseeor.AdvertiseEor)
		"""
		from openhltspirent.sessions.config.devicegroups.devices.protocols.bgpv4.gracefulrestart.advertiseeor.advertiseeor import AdvertiseEor
		return AdvertiseEor(self)._read()

	def create(self):
		"""Create an instance of the `graceful-restart` resource

		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `graceful-restart` resource

		"""
		return self._delete()

