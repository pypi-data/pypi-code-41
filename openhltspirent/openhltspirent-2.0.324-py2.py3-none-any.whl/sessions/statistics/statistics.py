from openhltspirent.base import Base
class Statistics(Base):
	"""The statistics pull model
	"""
	YANG_NAME = 'statistics'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {"LastActivityTimestamp": "last-activity-timestamp", "FirstActivityTimestamp": "first-activity-timestamp"}
	YANG_ACTIONS = ["clear"]

	def __init__(self, parent):
		super(Statistics, self).__init__(parent)

	@property
	def PhysicalPort(self):
		"""TBD

		Get an instance of the PhysicalPort class.

		Returns:
			obj(openhltspirent.sessions.statistics.physicalport.physicalport.PhysicalPort)
		"""
		from openhltspirent.sessions.statistics.physicalport.physicalport import PhysicalPort
		return PhysicalPort(self)

	@property
	def Port(self):
		"""TBD

		Get an instance of the Port class.

		Returns:
			obj(openhltspirent.sessions.statistics.port.port.Port)
		"""
		from openhltspirent.sessions.statistics.port.port import Port
		return Port(self)

	@property
	def PortTraffic(self):
		"""TBD

		Get an instance of the PortTraffic class.

		Returns:
			obj(openhltspirent.sessions.statistics.porttraffic.porttraffic.PortTraffic)
		"""
		from openhltspirent.sessions.statistics.porttraffic.porttraffic import PortTraffic
		return PortTraffic(self)

	@property
	def DeviceTraffic(self):
		"""TBD

		Get an instance of the DeviceTraffic class.

		Returns:
			obj(openhltspirent.sessions.statistics.devicetraffic.devicetraffic.DeviceTraffic)
		"""
		from openhltspirent.sessions.statistics.devicetraffic.devicetraffic import DeviceTraffic
		return DeviceTraffic(self)

	@property
	def Bgpv4Statistics(self):
		"""TBD

		Get an instance of the Bgpv4Statistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.bgpv4statistics.bgpv4statistics.Bgpv4Statistics)
		"""
		from openhltspirent.sessions.statistics.bgpv4statistics.bgpv4statistics import Bgpv4Statistics
		return Bgpv4Statistics(self)

	@property
	def Bgpv6Statistics(self):
		"""TBD

		Get an instance of the Bgpv6Statistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.bgpv6statistics.bgpv6statistics.Bgpv6Statistics)
		"""
		from openhltspirent.sessions.statistics.bgpv6statistics.bgpv6statistics import Bgpv6Statistics
		return Bgpv6Statistics(self)

	@property
	def Ospfv2Statistics(self):
		"""TBD

		Get an instance of the Ospfv2Statistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.ospfv2statistics.ospfv2statistics.Ospfv2Statistics)
		"""
		from openhltspirent.sessions.statistics.ospfv2statistics.ospfv2statistics import Ospfv2Statistics
		return Ospfv2Statistics(self)

	@property
	def Ospfv3Statistics(self):
		"""TBD

		Get an instance of the Ospfv3Statistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.ospfv3statistics.ospfv3statistics.Ospfv3Statistics)
		"""
		from openhltspirent.sessions.statistics.ospfv3statistics.ospfv3statistics import Ospfv3Statistics
		return Ospfv3Statistics(self)

	@property
	def IsisStatistics(self):
		"""TBD

		Get an instance of the IsisStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.isisstatistics.isisstatistics.IsisStatistics)
		"""
		from openhltspirent.sessions.statistics.isisstatistics.isisstatistics import IsisStatistics
		return IsisStatistics(self)

	@property
	def Bfdv4Statistics(self):
		"""TBD

		Get an instance of the Bfdv4Statistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.bfdv4statistics.bfdv4statistics.Bfdv4Statistics)
		"""
		from openhltspirent.sessions.statistics.bfdv4statistics.bfdv4statistics import Bfdv4Statistics
		return Bfdv4Statistics(self)

	@property
	def Bfdv6Statistics(self):
		"""TBD

		Get an instance of the Bfdv6Statistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.bfdv6statistics.bfdv6statistics.Bfdv6Statistics)
		"""
		from openhltspirent.sessions.statistics.bfdv6statistics.bfdv6statistics import Bfdv6Statistics
		return Bfdv6Statistics(self)

	@property
	def Dhcpv4Statistics(self):
		"""TBD

		Get an instance of the Dhcpv4Statistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.dhcpv4statistics.dhcpv4statistics.Dhcpv4Statistics)
		"""
		from openhltspirent.sessions.statistics.dhcpv4statistics.dhcpv4statistics import Dhcpv4Statistics
		return Dhcpv4Statistics(self)

	@property
	def Dhcpv4PortStatistics(self):
		"""TBD

		Get an instance of the Dhcpv4PortStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.dhcpv4portstatistics.dhcpv4portstatistics.Dhcpv4PortStatistics)
		"""
		from openhltspirent.sessions.statistics.dhcpv4portstatistics.dhcpv4portstatistics import Dhcpv4PortStatistics
		return Dhcpv4PortStatistics(self)

	@property
	def Dhcpv4ServerStatistics(self):
		"""TBD

		Get an instance of the Dhcpv4ServerStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.dhcpv4serverstatistics.dhcpv4serverstatistics.Dhcpv4ServerStatistics)
		"""
		from openhltspirent.sessions.statistics.dhcpv4serverstatistics.dhcpv4serverstatistics import Dhcpv4ServerStatistics
		return Dhcpv4ServerStatistics(self)

	@property
	def Dhcpv6Statistics(self):
		"""TBD

		Get an instance of the Dhcpv6Statistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.dhcpv6statistics.dhcpv6statistics.Dhcpv6Statistics)
		"""
		from openhltspirent.sessions.statistics.dhcpv6statistics.dhcpv6statistics import Dhcpv6Statistics
		return Dhcpv6Statistics(self)

	@property
	def Dhcpv6PortStatistics(self):
		"""TBD

		Get an instance of the Dhcpv6PortStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.dhcpv6portstatistics.dhcpv6portstatistics.Dhcpv6PortStatistics)
		"""
		from openhltspirent.sessions.statistics.dhcpv6portstatistics.dhcpv6portstatistics import Dhcpv6PortStatistics
		return Dhcpv6PortStatistics(self)

	@property
	def Dhcpv6ServerStatistics(self):
		"""TBD

		Get an instance of the Dhcpv6ServerStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.dhcpv6serverstatistics.dhcpv6serverstatistics.Dhcpv6ServerStatistics)
		"""
		from openhltspirent.sessions.statistics.dhcpv6serverstatistics.dhcpv6serverstatistics import Dhcpv6ServerStatistics
		return Dhcpv6ServerStatistics(self)

	@property
	def IgmpStatistics(self):
		"""TBD

		Get an instance of the IgmpStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.igmpstatistics.igmpstatistics.IgmpStatistics)
		"""
		from openhltspirent.sessions.statistics.igmpstatistics.igmpstatistics import IgmpStatistics
		return IgmpStatistics(self)

	@property
	def IgmpPortStatistics(self):
		"""TBD

		Get an instance of the IgmpPortStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.igmpportstatistics.igmpportstatistics.IgmpPortStatistics)
		"""
		from openhltspirent.sessions.statistics.igmpportstatistics.igmpportstatistics import IgmpPortStatistics
		return IgmpPortStatistics(self)

	@property
	def IgmpHostGroupStatistics(self):
		"""TBD

		Get an instance of the IgmpHostGroupStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.igmphostgroupstatistics.igmphostgroupstatistics.IgmpHostGroupStatistics)
		"""
		from openhltspirent.sessions.statistics.igmphostgroupstatistics.igmphostgroupstatistics import IgmpHostGroupStatistics
		return IgmpHostGroupStatistics(self)

	@property
	def IgmpQuerierStatistics(self):
		"""TBD

		Get an instance of the IgmpQuerierStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.igmpquerierstatistics.igmpquerierstatistics.IgmpQuerierStatistics)
		"""
		from openhltspirent.sessions.statistics.igmpquerierstatistics.igmpquerierstatistics import IgmpQuerierStatistics
		return IgmpQuerierStatistics(self)

	@property
	def MldStatistics(self):
		"""TBD

		Get an instance of the MldStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.mldstatistics.mldstatistics.MldStatistics)
		"""
		from openhltspirent.sessions.statistics.mldstatistics.mldstatistics import MldStatistics
		return MldStatistics(self)

	@property
	def MldPortStatistics(self):
		"""TBD

		Get an instance of the MldPortStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.mldportstatistics.mldportstatistics.MldPortStatistics)
		"""
		from openhltspirent.sessions.statistics.mldportstatistics.mldportstatistics import MldPortStatistics
		return MldPortStatistics(self)

	@property
	def MldHostGroupStatistics(self):
		"""TBD

		Get an instance of the MldHostGroupStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.mldhostgroupstatistics.mldhostgroupstatistics.MldHostGroupStatistics)
		"""
		from openhltspirent.sessions.statistics.mldhostgroupstatistics.mldhostgroupstatistics import MldHostGroupStatistics
		return MldHostGroupStatistics(self)

	@property
	def MldQuerierStatistics(self):
		"""TBD

		Get an instance of the MldQuerierStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.mldquerierstatistics.mldquerierstatistics.MldQuerierStatistics)
		"""
		from openhltspirent.sessions.statistics.mldquerierstatistics.mldquerierstatistics import MldQuerierStatistics
		return MldQuerierStatistics(self)

	@property
	def PimStatistics(self):
		"""TBD

		Get an instance of the PimStatistics class.

		Returns:
			obj(openhltspirent.sessions.statistics.pimstatistics.pimstatistics.PimStatistics)
		"""
		from openhltspirent.sessions.statistics.pimstatistics.pimstatistics import PimStatistics
		return PimStatistics(self)

	@property
	def FirstActivityTimestamp(self):
		"""Timestamp of the first request to this session.

		Getter Returns:
			string
		"""
		return self._get_value('first-activity-timestamp')

	@property
	def LastActivityTimestamp(self):
		"""Timestamp of the last request to this session

		Getter Returns:
			string
		"""
		return self._get_value('last-activity-timestamp')

	def Clear(self):
		"""Clear all statistic counters.

		"""
		return self._execute(Base.POST_ACTION, 'clear')

