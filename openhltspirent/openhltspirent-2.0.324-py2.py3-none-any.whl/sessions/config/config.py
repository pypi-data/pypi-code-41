from openhltspirent.base import Base
class Config(Base):
	"""This container aggregates all other top level configuration submodules.
	"""
	YANG_NAME = 'config'
	YANG_KEYWORD = 'container'
	YANG_KEY = None
	YANG_PROPERTY_MAP = {}
	YANG_ACTIONS = ["commit", "port-control", "clear", "load", "save", "arp-control", "traffic-control", "device-groups-control", "bgpv4-control", "bgpv6-control", "ospfv2-control", "ospfv3-control", "isis-control", "bfdv4-control", "bfdv6-control", "dhcpv4-control", "dhcpv4-server-control", "dhcpv6-control", "dhcpv6-server-control", "igmp-control", "igmp-querier-control", "mld-control", "mld-querier-control", "pim-control", "invoke", "verify-traffic"]

	def __init__(self, parent):
		super(Config, self).__init__(parent)

	@property
	def Ports(self):
		"""A list of abstract test ports

		Get an instance of the Ports class.

		Returns:
			obj(openhltspirent.sessions.config.ports.ports.Ports)
		"""
		from openhltspirent.sessions.config.ports.ports import Ports
		return Ports(self)

	@property
	def Layer1Groups(self):
		"""A group of layer1 settings that will be applied to each port's location.
		The vendor implementation should apply layer 1 settings when starting protocols.
		If the port's location is empty then nothing will be applied to that port.

		Get an instance of the Layer1Groups class.

		Returns:
			obj(openhltspirent.sessions.config.layer1groups.layer1groups.Layer1Groups)
		"""
		from openhltspirent.sessions.config.layer1groups.layer1groups import Layer1Groups
		return Layer1Groups(self)

	@property
	def GlobalMulticastGroups(self):
		"""A list of multi-cast groups.

		Get an instance of the GlobalMulticastGroups class.

		Returns:
			obj(openhltspirent.sessions.config.globalmulticastgroups.globalmulticastgroups.GlobalMulticastGroups)
		"""
		from openhltspirent.sessions.config.globalmulticastgroups.globalmulticastgroups import GlobalMulticastGroups
		return GlobalMulticastGroups(self)

	@property
	def GlobalProtocols(self):
		"""This list allows for configuring global protocols options.

		Get an instance of the GlobalProtocols class.

		Returns:
			obj(openhltspirent.sessions.config.globalprotocols.globalprotocols.GlobalProtocols)
		"""
		from openhltspirent.sessions.config.globalprotocols.globalprotocols import GlobalProtocols
		return GlobalProtocols(self)._read()

	@property
	def DeviceGroups(self):
		"""A list of device-groups.
		Each device-groups object can contain 0..n devices.

		Get an instance of the DeviceGroups class.

		Returns:
			obj(openhltspirent.sessions.config.devicegroups.devicegroups.DeviceGroups)
		"""
		from openhltspirent.sessions.config.devicegroups.devicegroups import DeviceGroups
		return DeviceGroups(self)

	@property
	def PortTraffic(self):
		"""A list of traffic streams where each traffic stream
		has a single transmit port as its source and a list of user defined frames.

		Get an instance of the PortTraffic class.

		Returns:
			obj(openhltspirent.sessions.config.porttraffic.porttraffic.PortTraffic)
		"""
		from openhltspirent.sessions.config.porttraffic.porttraffic import PortTraffic
		return PortTraffic(self)

	@property
	def DeviceTraffic(self):
		"""This is a collection of nodes that the server uses to generate 1..n traffic-streams.
		The source and destinations of the device traffic group can only come from the device-groups list or its children.

		Get an instance of the DeviceTraffic class.

		Returns:
			obj(openhltspirent.sessions.config.devicetraffic.devicetraffic.DeviceTraffic)
		"""
		from openhltspirent.sessions.config.devicetraffic.devicetraffic import DeviceTraffic
		return DeviceTraffic(self)

	def Commit(self):
		"""Notify the server to push all uncommitted config changes to vendor hardware

		"""
		return self._execute(Base.POST_ACTION, 'commit')

	def PortControl(self, input):
		"""Control one or more physical hardware test ports and/or
		virtual machine test ports.
		An empty targets list signifies that all ports will be subject to the mode specified.

		Args:
			input {"targets": "leafref", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'port-control', input)

	def Clear(self):
		"""Clear the current configuration

		"""
		return self._execute(Base.POST_ACTION, 'clear')

	def Load(self, input):
		"""Load a configuration

		Args:
			input {"mode": "enumeration", "file-name": "string"}

		"""
		import copy 
		new_input_arg = copy.deepcopy(input) 
		with open(input['file-name'], 'rb') as fid:
			import base64
			new_input_arg['file-name'] = base64.b64encode(fid.read()).decode('UTF-8', 'ignore')
		return self._execute(Base.POST_ACTION, 'load',new_input_arg)

	def Save(self, input):
		"""Save the current configuration

		Args:
			input {"mode": "enumeration", "file-name": "string"}

		Returns:
			{"content": "string"}

		"""
		output = self._execute(Base.POST_ACTION, 'save', input)
		if 'openhltest:output' not in output: 
			 return None 
		import os
		import base64
		if os.name == 'nt':
			def_dir = os.path.normpath('%s/openhltspirent' % os.getenv('USERPROFILE', 'c:/'))
		else:
			def_dir = os.path.normpath('%s/openhltspirent' % (os.environ['HOME']))
		if not os.path.exists(def_dir):
			os.makedirs(def_dir)
		from datetime import datetime
		now = datetime.now()
		date_time = now.strftime('%Y-%m-%d_%H-%M-%S')
		if 'content' in output['openhltest:output']:
			file_name = input['file-name']
			if 0 == len(file_name):
				file_name = 'save_file-name_' + date_time
				file_name = os.path.join(def_dir, file_name)
			with open(file_name, 'wb') as fid:
				fid.write(base64.b64decode(output['openhltest:output']['content']))
		return output['openhltest:output']

	def ArpControl(self, input):
		"""ARP control command.
		An empty targets list signifies that ARP will be performed globally

		Args:
			input {"targets": "union[leafref]", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'arp-control', input)

	def TrafficControl(self, input):
		"""Control one or more traffic groups.
		An empty list signifies that all traffic will be subject to the mode specified.

		Args:
			input {"targets": "union[leafref]", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'traffic-control', input)

	def DeviceGroupsControl(self, input):
		"""Control one or more device-groups.
		An empty list signifies that all device-groups will be subject to the mode specified.

		Args:
			input {"targets": "leafref", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'device-groups-control', input)

	def Bgpv4Control(self, input):
		"""Start one or more emulated BGPV4 protocol groups.
		An empty targets list signifies that all BGPV4 protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "leafref", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'bgpv4-control', input)

	def Bgpv6Control(self, input):
		"""Start one or more emulated BGPV6 protocol groups.
		An empty targets list signifies that all BGPV6 protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "leafref", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'bgpv6-control', input)

	def Ospfv2Control(self, input):
		"""Start one or more emulated OSPFV2 protocol groups.
		An empty targets list signifies that all OSPFV2 protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "leafref", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'ospfv2-control', input)

	def Ospfv3Control(self, input):
		"""Start one or more emulated OSPFV3 protocol groups.
		An empty targets list signifies that all OSPFV3 protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "leafref", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'ospfv3-control', input)

	def IsisControl(self, input):
		"""Start one or more emulated ISIS protocol groups.
		An empty targets list signifies that all ISIS protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "leafref", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'isis-control', input)

	def Bfdv4Control(self, input):
		"""Start one or more emulated BFD v4 protocol groups.
		An empty targets list signifies that all BFD v4 protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "leafref", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'bfdv4-control', input)

	def Bfdv6Control(self, input):
		"""Start one or more emulated BFD v6 protocol groups.
		An empty targets list signifies that all BFD v6 protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "leafref", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'bfdv6-control', input)

	def Dhcpv4Control(self, input):
		"""Start one or more emulated DHCPv4 Client protocol groups.
		An empty targets list signifies that all DHCPv4 Client protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "string", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'dhcpv4-control', input)

	def Dhcpv4ServerControl(self, input):
		"""Start one or more emulated DHCPv4 Server protocol groups.
		An empty targets list signifies that all DHCPv4 Server protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "string", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'dhcpv4-server-control', input)

	def Dhcpv6Control(self, input):
		"""Start one or more emulated DHCPv6/PD Client protocol groups.
		An empty targets list signifies that all DHCPv6/PD Client protocol groups will be subject to the mode specified.

		Args:
			input {"filename": "string", "targets": "string", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'dhcpv6-control', input)

	def Dhcpv6ServerControl(self, input):
		"""Start one or more emulated DHCPv6 Server protocol groups.
		An empty targets list signifies that all DHCPv6 Server protocol groups will be subject to the mode specified.

		Args:
			input {"targets": "string", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'dhcpv6-server-control', input)

	def IgmpControl(self, input):
		"""Start one or more emulated IGMP Hosts protocol groups.
		An empty targets list signifies that all IGMP Hosts groups will be subject to the mode specified.

		Args:
			input {"calculate-latency": "boolean", "join-leave-delay": "uint8", "rx-data-duration": "uint32", "join-failed-retry-counter": "uint8", "mode": "enumeration", "targets": "string"}

		"""
		return self._execute(Base.POST_ACTION, 'igmp-control', input)

	def IgmpQuerierControl(self, input):
		"""Start or Stops one or more emulated IGMP querier protocol groups.
		An empty targets list signifies that all IGMP querier groups will be subject to the mode specified.

		Args:
			input {"targets": "string", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'igmp-querier-control', input)

	def MldControl(self, input):
		"""Start one or more emulated MLD Hosts protocol groups.
		An empty targets list signifies that all MLD Hosts groups will be subject to the mode specified.

		Args:
			input {"calculate-latency": "boolean", "join-leave-delay": "uint8", "rx-data-duration": "uint32", "join-failed-retry-counter": "uint8", "mode": "enumeration", "targets": "string"}

		"""
		return self._execute(Base.POST_ACTION, 'mld-control', input)

	def MldQuerierControl(self, input):
		"""Start or Stops one or more emulated MLD querier protocol groups.
		An empty targets list signifies that all MLD querier groups will be subject to the mode specified.

		Args:
			input {"targets": "string", "mode": "enumeration"}

		"""
		return self._execute(Base.POST_ACTION, 'mld-querier-control', input)

	def PimControl(self, input):
		"""Start or Stops one or more emulated PIM protocol groups.
		An empty targets list signifies that all PIM groups will be subject to the mode specified.

		Args:
			input {"mdt-interval": "uint16", "data-mdt-multicast-group": "string", "mdt-delay": "uint16", "mode": "enumeration", "traffic-targets": "union[leafref]", "targets": "string"}

		"""
		return self._execute(Base.POST_ACTION, 'pim-control', input)

	def Invoke(self, input):
		"""invoke the stc native commands

		Args:
			input {"command": "string"}

		Returns:
			{"retvalue": "string"}

		"""
		ret = self._execute(Base.POST_ACTION, 'invoke', input)
		if isinstance(ret, dict) and 'openhltest:output' in ret: 
			return ret['openhltest:output'] 
		else: 
			return None 

	def VerifyTraffic(self, input):
		"""Verifies traffic loss on stream based TX and RX frames according to speicified criteria.
		e.g. A stream traffic is considered pass if expected-tolerance <= actual rx <= expected+tolerance (in frames).

		Args:
			input {"flow-per-stream": "string", "name": "string", "return-format": "string", "verify-mode": "string", "debug": "boolean", "empty-stats-db": "string", "traffic-item-spec": {"expected": "string", "tolerance-mode": "string", "tolerance": "string", "name": "string", "expected-mode": "string"}, "traffic-items": {"name": "string", "traffic-item-spec": {"expected": "string", "tolerance-mode": "string", "tolerance": "string", "name": "string", "expected-mode": "string"}, "tolerance-mode": "string", "expected": "string", "tolerance": "string", "expected-mode": "string", "all-traffic-items": "boolean"}, "ports": {"name": "string", "all-ports": "boolean", "tolerance-mode": "string", "expected": "string", "port-stream-spec": {"expected": "string", "tolerance-mode": "string", "tolerance": "string", "name": "string", "expected-mode": "string"}, "tolerance": "string", "expected-mode": "string", "port-spec": {"name": "string", "tolerance-mode": "string", "expected": "string", "port-stream-spec": {"expected": "string", "tolerance-mode": "string", "tolerance": "string", "name": "string", "expected-mode": "string"}, "tolerance": "string", "expected-mode": "string"}}, "tolerance-mode": "string", "mode": "string", "negative-deviation-db": "string", "expected": "string", "save-db": "boolean", "port-stream-spec": {"expected": "string", "tolerance-mode": "string", "tolerance": "string", "name": "string", "expected-mode": "string"}, "all-ports": "boolean", "tolerance": "string", "expected-mode": "string", "port-spec": {"name": "string", "tolerance-mode": "string", "expected": "string", "port-stream-spec": {"expected": "string", "tolerance-mode": "string", "tolerance": "string", "name": "string", "expected-mode": "string"}, "tolerance": "string", "expected-mode": "string"}, "all-traffic-items": "boolean"}

		Returns:
			{"Loss-percent": "string", "Rx-Bytes": "string", "IP-Destination-Address": "string", "Tx-Bytes": "string", "frames-delta": "string", "ApiStreamBlockHandle": "string", "FlowCount": "string", "Tx-Port-Location": "string", "FilteredValue_4": "string", "Rx-Rate-Mbps": "string", "TCP-TCP-Source-Port": "string", "FilteredValue_8": "string", "DataSetId": "string", "Tx-Rate-Kbps": "string", "loss": "string", "Frames-Delta": "string", "IP-Source-Address": "string", "store-forward-min-latency": {"base": "string", "value": "string"}, "Store-Forward-Max-Latency-ns": "string", "StreamBlock_FrameConfig_udp-Udp_sourcePort": "string", "seq": "string", "ParentStreamBlock": "string", "negative-deviation-db": {"file-extension": "string", "file-content": "file-content"}, "Packet-Loss-Duration-ms": "string", "StreamId": "string", "ApiRxPortHandle": "string", "tx-l1-rate-bps": {"value": "string"}, "flow-stats": {"DuplicateFrameCount": "string", "StreamBlock_FrameConfig_udp-Udp_sourcePort": "string", "Rx-Rate-bps": "string", "seq": "string", "Loss-percent": "string", "ParentStreamBlock": "string", "ApiTxPortHandle": "string", "IP-Source-Address": "string", "Tx-Rate-bps": "string", "Packet-Loss-Duration-ms": "string", "Comp16_3": "string", "Comp16_2": "string", "Rx-Bytes": "string", "Comp16_4": "string", "StreamId": "string", "TxStreamId": "string", "TCP-TCP-Source-Port": "string", "ApiRxPortHandle": "string", "Store-Forward-Min-Latency-ns": "string", "Rx-Rate-Bps": "string", "Tx-Rate-Mbps": "string", "ApiStreamBlockHandle": "string", "StreamBlock_FrameConfig_ipv6-IPv6_1_destAddr": "string", "Tx-Bytes": "string", "IsExpectedPort": "string", "FilteredValue_2": "string", "FilteredValue_3": "string", "FilteredValue_1": "string", "FilteredValue_6": "string", "FilteredValue_7": "string", "FilteredValue_4": "string", "FilteredValue_5": "string", "FlowCount": "string", "Rx-Rate-Kbps": "string", "FilteredValue_9": "string", "Tx-Port-Location": "string", "Rx-Port-Location": "string", "TxPortHandle": "string", "StreamBlock_FrameConfig_tcp-Tcp_destPort": "string", "First-TimeStamp": "string", "Tx-Port": "string", "Rx-Port": "string", "RxFilterList": "string", "Rx-Rate-Mbps": "string", "RxPortHandle": "string", "Rx-Frames": "string", "StreamBlock_FrameConfig_udp-Udp_destPort": "string", "Tx-Rate-Bps": "string", "Rx-Expected-Frames": "string", "Tx-Frame-Rate": "string", "StreamBlock_FrameConfig_tcp-Tcp_sourcePort": "string", "FilteredValue_8": "string", "DataSetId": "string", "Tx-Rate-Kbps": "string", "StreamBlock_FrameConfig_ipv6-IPv6_1_sourceAddr": "string", "Tx-Frames": "string", "Frames-Delta": "string", "Traffic-Item": "string", "FilteredValue_10": "string", "UDP-UDP-Dest-Port": "string", "Comp16_1": "string", "TCP-TCP-Dest-Port": "string", "UDP-UDP-Source-Port": "string", "Last-TimeStamp": "string", "Store-Forward-Max-Latency-ns": "string", "Store-Forward-Avg-Latency-ns": "string", "Rx-Frame-Rate": "string", "IP-Destination-Address": "string"}, "traffic-item": "string", "flow-table": "string", "tx-rate-bps": {"value": "string"}, "tolerance": {"base": "enumeration", "value": "string"}, "Rx-Port-Location": "string", "store-forward-avg-latency": {"base": "string", "value": "string"}, "Tx-Port": "string", "base": "string", "Rx-Expected-Frames": "string", "StreamBlock_FrameConfig_tcp-Tcp_sourcePort": "string", "Tx-Frames": "string", "empty-stats-db": {"file-extension": "string", "file-content": "file-content"}, "Traffic-Item": "string", "UDP-UDP-Dest-Port": "string", "UDP-UDP-Source-Port": "string", "Last-TimeStamp": "string", "Store-Forward-Avg-Latency-ns": "string", "DuplicateFrameCount": "string", "Rx-Rate-bps": "string", "ApiTxPortHandle": "string", "rx-l1-rate-bps": {"value": "string"}, "file-content": "file-content", "StreamBlock_FrameConfig_ipv6-IPv6_1_sourceAddr": "string", "rx-frames": "string", "Rx-Rate-Bps": "string", "Tx-Rate-Mbps": "string", "StreamBlock_FrameConfig_ipv6-IPv6_1_destAddr": "string", "store-forward-max-latency": {"base": "string", "value": "string"}, "expected": {"base": "enumeration", "value": "string"}, "TxPortHandle": "string", "rx-rate-bps": {"value": "string"}, "Tx-Frame-Rate": "string", "Rx-Frames": "string", "FilteredValue_10": "string", "value": "string", "packet-loss-duration": {"base": "string", "value": "string"}, "IsExpectedPort": "string", "Rx-Frame-Rate": "string", "Comp16_4": "string", "rx-port": "string", "Comp16_1": "string", "Comp16_3": "string", "Comp16_2": "string", "item-stats": {"status": "string", "loss": "string", "tx-frames": "string", "tx-port": "string", "rx-rate-bps": {"value": "string"}, "rx-port": "string", "seq": "string", "frames-delta": "string", "store-forward-avg-latency": {"base": "string", "value": "string"}, "tolerance": {"base": "enumeration", "value": "string"}, "store-forward-max-latency": {"base": "string", "value": "string"}, "tx-l1-rate-bps": {"value": "string"}, "traffic-item": "string", "value": "string", "rx-l1-rate-bps": {"value": "string"}, "base": "string", "store-forward-min-latency": {"base": "string", "value": "string"}, "packet-loss-duration": {"base": "string", "value": "string"}, "tx-rate-bps": {"value": "string"}, "expected": {"base": "enumeration", "value": "string"}, "rx-frames": "string"}, "TxStreamId": "string", "Store-Forward-Min-Latency-ns": "string", "FilteredValue_2": "string", "FilteredValue_3": "string", "FilteredValue_1": "string", "FilteredValue_6": "string", "FilteredValue_7": "string", "Tx-Rate-bps": "string", "FilteredValue_5": "string", "Rx-Rate-Kbps": "string", "FilteredValue_9": "string", "status": "string", "StreamBlock_FrameConfig_tcp-Tcp_destPort": "string", "First-TimeStamp": "string", "tx-port": "string", "Rx-Port": "string", "RxFilterList": "string", "RxPortHandle": "string", "file-extension": "string", "StreamBlock_FrameConfig_udp-Udp_destPort": "string", "Tx-Rate-Bps": "string", "tx-frames": "string", "item-table": "string", "TCP-TCP-Dest-Port": "string"}

		"""
		output = self._execute(Base.POST_ACTION, 'verify-traffic', input)
		if 'openhltest:output' not in output: 
			 return None 
		import os
		import base64
		if os.name == 'nt':
			def_dir = os.path.normpath('%s/openhltspirent' % os.getenv('USERPROFILE', 'c:/'))
		else:
			def_dir = os.path.normpath('%s/openhltspirent' % (os.environ['HOME']))
		if not os.path.exists(def_dir):
			os.makedirs(def_dir)
		from datetime import datetime
		now = datetime.now()
		date_time = now.strftime('%Y-%m-%d_%H-%M-%S')
		if 'empty-stats-db' in output['openhltest:output']:
			file_name = input['empty-stats-db']
			if 0 == len(file_name):
				file_ext = '.' + output['openhltest:output']['empty-stats-db']['file-extension']
				file_name = 'verify-traffic_empty-stats-db_' + date_time + file_ext
				file_name = os.path.join(def_dir, file_name)
			with open(file_name, 'wb') as fid:
				fid.write(base64.b64decode(output['openhltest:output']['empty-stats-db']['file-content']))
		if 'negative-deviation-db' in output['openhltest:output']:
			file_name = input['negative-deviation-db']
			if 0 == len(file_name):
				file_ext = '.' + output['openhltest:output']['negative-deviation-db']['file-extension']
				file_name = 'verify-traffic_negative-deviation-db_' + date_time + file_ext
				file_name = os.path.join(def_dir, file_name)
			with open(file_name, 'wb') as fid:
				fid.write(base64.b64decode(output['openhltest:output']['negative-deviation-db']['file-content']))
		return output['openhltest:output']

