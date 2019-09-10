# Copyright 2018 99cloud, Inc.
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

vlan_network_interface_req_schema = {
    "type": "object",
    "properties": {
        "VLANId": {"type": "number"},
        "VLANEnable": {"type": "boolean"},
        "Oem": {
            "type": "object",
            "properties": {
                "Intel_RackScale": {
                    "type": "object",
                    "properties": {"Tagged": {"type": "boolean"}},
                    "required": ["Tagged"],
                }
            },
            "required": ["Intel_RackScale"],
        },
    },
    "required": ["VLANId", "VLANEnable", "Oem"],
    "additionalProperties": False,
}

acl_rule_req_schema = {
    "type": "object",
    "oneOf": [
        {
            "properties": {"Action": {"enum": ["Forward"]}},
            "required": ["ForwardMirrorInterface"],
        },
        {
            "properties": {"Action": {"enum": ["Mirror"]}},
            "required": [
                "ForwardMirrorInterface",
                "MirrorPortRegion",
                "MirrorType",
            ],
        },
        {"properties": {"Action": {"enum": ["Permit", "Deny"]}}},
    ],
    "properties": {
        "RuleId": {"type": "number"},
        "Action": {
            "type": "string",
            "enum": ["Permit", "Deny", "Forward", "Mirror"],
        },
        "ForwardMirrorInterface": {
            "type": "object",
            "properties": {"@odata.id": {"type": "string"}},
            "required": ["@odata.id"],
        },
        "MirrorPortRegion": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"@odata.id": {"type": "string"}},
                "required": ["@odata.id"],
            },
        },
        "MirrorType": {
            "type": "string",
            "enum": ["Egress", "Ingress", "Bidirectional", "Redirect"],
        },
        "Condition": {
            "type": "object",
            "properties": {
                "IPSource": {
                    "type": "object",
                    "properties": {
                        "IPv4Addresses": {"type": "string"},
                        "Mask": {"type": ["string", "null"]},
                    },
                    "required": ["IPv4Address"],
                },
                "IPDestination": {
                    "type": "object",
                    "properties": {
                        "IPv4Address": {"type": "string"},
                        "Mask": {"type": ["string", "null"]},
                    },
                    "required": ["IPv4Address"],
                },
                "MACSource": {
                    "type": "object",
                    "properties": {
                        "MACAddress": {"type": "string"},
                        "Mask": {"type": ["string", "null"]},
                    },
                    "required": ["MACAddress"],
                },
                "MACDestination": {
                    "type": "object",
                    "properties": {
                        "MACAddress": {"type": "string"},
                        "Mask": {"type": ["string", "null"]},
                    },
                    "required": ["MACAddress"],
                },
                "VLANId": {
                    "type": "object",
                    "properties": {
                        "Id": {"type": "number"},
                        "Mask": {"type": ["number", "null"]},
                    },
                    "required": ["Id"],
                },
                "L4SourcePort": {
                    "type": "object",
                    "properties": {
                        "Port": {"type": "number"},
                        "Mask": {"type": ["number", "null"]},
                    },
                    "required": ["Port"],
                },
                "L4DestinationPort": {
                    "type": "object",
                    "properties": {
                        "Port": {"type": "number"},
                        "Mask": {"type": ["number", "null"]},
                    },
                    "required": ["Port"],
                },
                "L4Protocol": {"type": ["number", "null"]},
            },
        },
    },
    "required": ["Action", "Condition"],
    "additionalProperties": False,
}

port_req_schema = {
    "type": "object",
    "properties": {
        "PortId": {"type": "number"},
        "LinkType": {"type": "string", "enum": ["Ethernet", "PCIe"]},
        "OperationalState": {"type": "string", "enum": ["Up", "Down"]},
        "AdministrativeState": {"type": "string", "enum": ["Up", "Down"]},
        "LinkSpeedMbps": {"type": ["number", "null"]},
        "NeighborInfo": {
            "type": "object",
            "properties": {
                "SwitchId": {"type": "string"},
                "PortId": {"type": "string"},
                "CableId": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "NeighborMAC": {"type": "string"},
        "FrameSize": {"type": ["number", "null"]},
        "Autosense": {"type": "boolean"},
        "FullDuplex": {"type": "boolean"},
        "MACAddress": {"type": "string"},
        "IPv4Addresses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Address": {"type": "string"},
                    "SubnetMask": {"type": "string"},
                    "AddressOrigin": {
                        "type": "string",
                        "enum": ["Static", "DHCP", "BOOTP", "IPv4LinkLocal"],
                    },
                    "Gateway": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "IPv6Addresses": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "Address": {"type": "string"},
                    "PrefixLength": {
                        "type": "number",
                        "minimum": 1,
                        "maximum": 128,
                    },
                    "AddressOrigin": {
                        "type": "string",
                        "enum": ["Static", "DHCPv6", "LinkLocal", "SLAAC"],
                    },
                    "AddressState": {
                        "type": "string",
                        "enum": [
                            "Preferred",
                            "Deprecated",
                            "Tentative",
                            "Failed",
                        ],
                    },
                },
                "additionalProperties": False,
            },
        },
        "PortClass": {
            "type": "string",
            "enum": ["Physical", "Logical", "Reserved"],
        },
        "PortMode": {
            "type": "string",
            "enum": [
                "LinkAggregationStatic",
                "LinkAggregationDynamic",
                "Unknown",
            ],
        },
        "PortType": {
            "type": "string",
            "enum": ["Upstream", "Downstream", "MeshPort", "Unknown"],
        },
        "Status": {
            "type": "object",
            "properties": {
                "State": {
                    "type": "string",
                    "enum": [
                        "Enabled",
                        "Disabled",
                        "StandbyOffline",
                        "StandbySpare",
                        "InTest",
                        "Starting",
                        "Absent",
                        "UnavailableOffline",
                        "Deferring",
                        "Quiesced",
                        "Updating",
                    ],
                },
                "HealthRollup": {
                    "type": "string",
                    "enum": ["OK", "Warning", "Critical"],
                },
                "Health": {
                    "type": "string",
                    "enum": ["OK", "Warning", "Critical"],
                },
            },
            "additionalProperties": False,
        },
        "VLANs": {
            "type": "object",
            "properties": {"@odata.id": {"type": "string"}},
            "required": ["@odata.id"],
        },
        "StaticMACs": {
            "type": "object",
            "properties": {"@odata.id": {"type": "string"}},
            "required": ["@odata.id"],
        },
        "Links": {
            "type": "object",
            "properties": {
                "PrimaryVLAN": {
                    "type": "object",
                    "properties": {"@odata.id": {"type": "string"}},
                    "required": ["@odata.id"],
                },
                "Switch": {
                    "type": "object",
                    "properties": {"@odata.id": {"type": "string"}},
                    "required": ["@odata.id"],
                },
                "MemberOfPort": {
                    "type": "object",
                    "properties": {"@odata.id": {"type": "string"}},
                    "required": ["@odata.id"],
                },
                "PortMembers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@odata.id": {"type": "string"}},
                        "required": ["@odata.id"],
                    },
                },
                "ActiveACLs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {"@odata.id": {"type": "string"}},
                        "required": ["@odata.id"],
                    },
                },
            },
            "additionalProperties": False,
        },
    },
    "required": ["PortId"],
    "additionalProperties": False,
}
