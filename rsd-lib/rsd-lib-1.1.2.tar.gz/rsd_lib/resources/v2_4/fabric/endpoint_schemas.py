# Copyright (c) 2018 Intel, Corp.
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

identifiers_req_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'DurableNameFormat': {'type': 'string'},
            'DurableName': {'type': 'string'}
        },
        "required": ['DurableNameFormat', 'DurableName']
    }
}

connected_entities_req_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'EntityLink': {
                'type': ['object', 'null'],
                'properties': {
                    '@odata.id': {'type': 'string'}
                },
                "required": ['@odata.id']
            },
            'EntityRole': {
                'type': 'string',
                'enum': ['Initiator', 'Target', 'Both']
            },
            'EntityType': {
                'type': 'string',
                'enum': [
                    'StorageInitiator', 'RootComplex', 'NetworkController',
                    'Drive', 'StorageExpander', 'DisplayController', 'Bridge',
                    'Processor', 'Volume'
                ]
            },
            'EntityPciId': {
                'type': 'object',
                'properties': {
                    'DeviceId': {'type': 'string'},
                    'VendorId': {'type': 'string'},
                    'SubsystemId': {'type': 'string'},
                    'SubsystemVendorId': {'type': 'string'}
                }
            },
            'PciFunctionNumber': {'type': 'number'},
            'PciClassCode': {'type': 'string'},
            'Identifiers': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'DurableNameFormat': {
                            'type': 'string',
                            'enum': ['NQN', 'iQN', 'FC_WWN', 'UUID', 'EUI',
                                     'NAA', 'NSID', 'SystemPath', 'LUN']
                        },
                        'DurableName': {'type': 'string'}
                    },
                    "required": ['DurableNameFormat', 'DurableName']
                }
            }
        },
        "required": ['EntityRole']
    }
}

protocol_req_schema = {
    'type': 'string'
}

pci_id_req_schema = {
    'type': 'object',
    'properties': {
        'DeviceId': {'type': 'string'},
        'VendorId': {'type': 'string'},
        'SubsystemId': {'type': 'string'},
        'SubsystemVendorId': {'type': 'string'}
    }
}

host_reservation_memory_bytes_req_schema = {
    'type': 'number'
}

ip_transport_details_req_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'TransportProtocol': {'type': 'string'},
            'IPv4Address': {
                'type': 'object',
                'properties': {
                    'Address': {'type': 'string'}
                }
            },
            'IPv6Address': {
                'type': 'object',
                'properties': {
                    'Address': {'type': 'string'}
                }
            },
            'Port': {'type': 'number'}
        }
    }
}

links_req_schema = {
    'type': 'object',
    'properties': {
        'Ports': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    '@odata.id': {'type': 'string'}
                }
            }
        }
    }
}

oem_req_schema = {
    'type': 'object',
    'properties': {
        'Intel_RackScale': {
            'type': 'object',
            'properties': {
                'EndpointProtocol': {'type': 'string'},
                'Authentication': {
                    'type': 'object',
                    'properties': {
                        'Username': {'type': 'string'},
                        'Password': {'type': 'string'}
                    }
                }
            }
        }
    }
}
