# Copyright 2019 Intel, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from copy import deepcopy

from rsd_lib.resources.v2_1.types import RESOURCE_CLASS as RESOURCE_CLASS_V21

from rsd_lib.resources.v2_2.chassis import chassis
from rsd_lib.resources.v2_2.chassis import power
from rsd_lib.resources.v2_2.chassis import thermal
from rsd_lib.resources.v2_2.ethernet_switch import ethernet_switch
from rsd_lib.resources.v2_2.ethernet_switch import ethernet_switch_metrics
from rsd_lib.resources.v2_2.ethernet_switch import ethernet_switch_port
from rsd_lib.resources.v2_2.ethernet_switch import ethernet_switch_port_metrics
from rsd_lib.resources.v2_2.fabric import fabric
from rsd_lib.resources.v2_2.fabric import port
from rsd_lib.resources.v2_2.fabric import port_metrics
from rsd_lib.resources.v2_2.fabric import switch
from rsd_lib.resources.v2_2.node import node
from rsd_lib.resources.v2_2.system import computer_system_metrics
from rsd_lib.resources.v2_2.system import memory
from rsd_lib.resources.v2_2.system import memory_metrics
from rsd_lib.resources.v2_2.system import processor
from rsd_lib.resources.v2_2.system import processor_metrics
from rsd_lib.resources.v2_2.system import system
from rsd_lib.resources.v2_2.telemetry_service import metric
from rsd_lib.resources.v2_2.telemetry_service import metric_definition
from rsd_lib.resources.v2_2.telemetry_service import metric_report
from rsd_lib.resources.v2_2.telemetry_service import metric_report_definition
from rsd_lib.resources.v2_2.telemetry_service import telemetry_service
from rsd_lib.resources.v2_2.telemetry_service import triggers
from rsd_lib.resources.v2_2.update_service import action_info
from rsd_lib.resources.v2_2.update_service import update_service


RESOURCE_CLASS = deepcopy(RESOURCE_CLASS_V21)
RESOURCE_CLASS.update(
    {
        "Chassis": chassis.Chassis,
        "ChassisCollection": chassis.ChassisCollection,
        "ComposedNodeCollection": node.NodeCollection,
        "ComputerSystem": system.System,
        "ComputerSystemCollection": system.SystemCollection,
        "ActionInfo": action_info.ActionInfo,
        "ComputerSystemMetrics": computer_system_metrics.ComputerSystemMetrics,
        "EthernetSwitch": ethernet_switch.EthernetSwitch,
        "EthernetSwitchCollection": ethernet_switch.EthernetSwitchCollection,
        "EthernetSwitchMetrics": ethernet_switch_metrics.EthernetSwitchMetrics,
        "EthernetSwitchPort": ethernet_switch_port.EthernetSwitchPort,
        "EthernetSwitchPortCollection":
            ethernet_switch_port.EthernetSwitchPortCollection,
        "EthernetSwitchPortMetrics":
            ethernet_switch_port_metrics.EthernetSwitchPortMetrics,
        "Fabric": fabric.Fabric,
        "FabricCollection": fabric.FabricCollection,
        "Memory": memory.Memory,
        "MemoryCollection": memory.MemoryCollection,
        "MemoryMetrics": memory_metrics.MemoryMetrics,
        "Metric": metric.Metric,
        "MetricDefinition": metric_definition.MetricDefinition,
        "MetricDefinitionCollection":
            metric_definition.MetricDefinitionCollection,
        "MetricReport": metric_report.MetricReport,
        "MetricReportCollection": metric_report.MetricReportCollection,
        "MetricReportDefinition":
            metric_report_definition.MetricReportDefinition,
        "MetricReportDefinitionCollection":
            metric_report_definition.MetricReportDefinitionCollection,
        "Port": port.Port,
        "PortCollection": port.PortCollection,
        "PortMetrics": port_metrics.PortMetrics,
        "Power": power.Power,
        "Processor": processor.Processor,
        "ProcessorCollection": processor.ProcessorCollection,
        "ProcessorMetrics": processor_metrics.ProcessorMetrics,
        "Switch": switch.Switch,
        "SwitchCollection": switch.SwitchCollection,
        "TelemetryService": telemetry_service.TelemetryService,
        "Thermal": thermal.Thermal,
        "Triggers": triggers.Triggers,
        "TriggersCollection": triggers.TriggersCollection,
        "UpdateService": update_service.UpdateService,
    }
)
