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

RESET_TYPE_VALUE = [
    'On',
    'ForceOff',
    'GracefulShutdown',
    'GracefulRestart',
    'ForceRestart',
    'Nmi',
    'ForceOn',
    'PushPowerButton'
]

BOOT_SOURCE_TARGET_VALUE = [
    'None',
    'Pxe',
    'Floppy',
    'Cd',
    'Usb',
    'Hdd',
    'BiosSetup',
    'Utilities',
    'Diags',
    'SDCard',
    'UefiTarget',
    'UefiShell',
    'UefiHttp',
    "RemoteDrive"
]

BOOT_SOURCE_ENABLED_VALUE = {
    'Once',
    'Continuous',
    'Disabled'
}

BOOT_SOURCE_MODE_VALUE = {
    'Legacy',
    'UEFI'
}
