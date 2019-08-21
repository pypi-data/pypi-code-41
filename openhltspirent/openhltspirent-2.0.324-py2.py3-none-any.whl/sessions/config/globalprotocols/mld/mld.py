from openhltspirent.base import Base
class Mld(Base):
	"""This list allows for configuring global MLD options.

	This class supports iterators and encapsulates 0..n instances of the openhltest:sessions/config/global-protocols/mld resource.
	"""
	YANG_NAME = 'mld'
	YANG_KEYWORD = 'list'
	YANG_KEY = 'name'
	YANG_PROPERTY_MAP = {"Name": "name", "Ports": "ports"}
	YANG_ACTIONS = []

	def __init__(self, parent):
		super(Mld, self).__init__(parent)

	@property
	def CalculateLatencyDelay(self):
		"""The delay (in seconds) before latency is calculated.
		The timer starts after reports are sent for each device.

		Get an instance of the CalculateLatencyDelay class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.mld.calculatelatencydelay.calculatelatencydelay.CalculateLatencyDelay)
		"""
		from openhltspirent.sessions.config.globalprotocols.mld.calculatelatencydelay.calculatelatencydelay import CalculateLatencyDelay
		return CalculateLatencyDelay(self)._read()

	@property
	def MaxBurst(self):
		"""Short-term maximum burst size in packets.
		A value of 0 specifies the maximum possible burst size.

		Get an instance of the MaxBurst class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.mld.maxburst.maxburst.MaxBurst)
		"""
		from openhltspirent.sessions.config.globalprotocols.mld.maxburst.maxburst import MaxBurst
		return MaxBurst(self)._read()

	@property
	def RatePps(self):
		"""Long-term, maximum packet rate (in packets per second).
		A value of 0 specifies the maximum possible output rate.

		Get an instance of the RatePps class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.mld.ratepps.ratepps.RatePps)
		"""
		from openhltspirent.sessions.config.globalprotocols.mld.ratepps.ratepps import RatePps
		return RatePps(self)._read()

	@property
	def VlanSubFilterType(self):
		"""To filter on the Outer or Inner VLAN tag when calculating latency for devices with a PPPoE and stacked VLAN encapsulation.
		OUTER	: Specifies that the analyzer filter will be programmed to use the Outer VLAN ID.
		INNER	: Specifies that the analyzer filter will be programmed to use the Inner VLAN ID.

		Get an instance of the VlanSubFilterType class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.mld.vlansubfiltertype.vlansubfiltertype.VlanSubFilterType)
		"""
		from openhltspirent.sessions.config.globalprotocols.mld.vlansubfiltertype.vlansubfiltertype import VlanSubFilterType
		return VlanSubFilterType(self)._read()

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
		"""Get `mld` resource(s). Returns all `mld` resources from the server if no input parameters are specified.

		"""
		return self._read(Name)

	def create(self, Name, Ports=None):
		"""Create an instance of the `mld` resource

		Args:
			Name (string): The unique name for a global protocols list item
			Ports (leafref): A list of abstract port references
		"""
		return self._create(locals())

	def delete(self):
		"""Delete all the encapsulated instances of the retrieved `mld` resource

		"""
		return self._delete()

	def update(self, Ports=None):
		"""Update the current instance of the `mld` resource

		Args:
			Ports (leafref): A list of abstract port references
		"""
		return self._update(locals())

