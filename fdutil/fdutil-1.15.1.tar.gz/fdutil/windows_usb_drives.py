# encoding: utf8

import sys
import logging_helper

logging = logging_helper.setup_logging()

try:
    import win32com.client as win32com_client
except ImportError:
    win32com_client = None


def logical_disk_to_volume_lookup():
    """
    Creates a dictionary of logical disk to volume name
    e.g. if there are two USB Drives that show up in Windows
    as "SANDISK (D:)" and "BACKUP (E:)", this function will
    :return: {u'D:': u'SANDISK',
              u'E:': u'BACKUP'}

    Adapted from: https://stackoverflow.com/questions/33784537/python-get-name-of-a-usb-flash-drive-device-windows

    For more info on WMI classes (properties aren't obvious from Python):
        https://docs.microsoft.com/en-us/windows/desktop/cimwin32prov/win32-diskdrive
        https://docs.microsoft.com/en-us/windows/desktop/cimwin32prov/win32-diskdrivetodiskpartition
        https://docs.microsoft.com/en-us/windows/desktop/cimwin32prov/win32-logicaldisktopartition
        https://docs.microsoft.com/en-us/windows/desktop/cimwin32prov/win32-logicaldisk
    """
    if not win32com_client:
        if not sys.platform.startswith('win'):
            raise RuntimeError(u'logical_disk_to_volume_lookup is only available on Windows.')
        else:
            raise ImportError(u'Unable to import win32com.client. Please install pywin32.')

    wmi = win32com_client.GetObject("winmgmts:")

    lookup = {}

    # 1. Use Win32_DiskDrive to find USB drives
    # DeviceID: u'\\\\.\\PHYSICALDRIVE1'
    physical_devices = [device.DeviceID.split('\\')[-1]
                        for device in wmi.InstancesOf("Win32_DiskDrive") if device.InterfaceType == "USB"]

    # 2. Use Win32_DiskDriveToDiskPartition to get drive and partitions matching the USB drives.
    # Antecedent: u'\\\\MYPC\\root\\cimv2:Win32_DiskDrive.DeviceID="\\\\\\\\.\\\\PHYSICALDRIVE1"'
    # Dependent: u'\\\\MYPC\\root\\cimv2:Win32_DiskPartition.DeviceID="Disk #1, Partition #0"'
    disks_and_partitions = []
    for mapping in [dd2dp
                    for dd2dp in wmi.InstancesOf("Win32_DiskDriveToDiskPartition")]:
        device_id = mapping.Antecedent.split('\\')[-1][:-1]
        if device_id in physical_devices:
            disk_and_partition = mapping.Dependent.split('=')[1].replace('"', '')
            disks_and_partitions.append(disk_and_partition)

    # 3. Use Win32_LogicalDiskToPartition to map disk drive and partition to a drive letter
    # Antecedent: u'\\\\MYPC\\root\\cimv2:Win32_DiskPartition.DeviceID="Disk #1, Partition #0"'
    # Dependent: u'\\\\MYPC\\root\\cimv2:Win32_LogicalDisk.DeviceID="D:"'
    
    for mapping in [ld2p for ld2p in wmi.InstancesOf("Win32_LogicalDiskToPartition")]:
        found_disk_and_partition = mapping.Antecedent
        for disk_and_partition in disks_and_partitions:
            if disk_and_partition in found_disk_and_partition:
                logical_drive = mapping.Dependent.split('"')[-2]
                lookup[logical_drive] = None

    # 4. Use Win32_LogicalDisk to map drive letter to volume name
    # DeviceID: u'D:'
    # VolumeName: u'SANDISK'
    for disk in [ld for ld in wmi.InstancesOf("Win32_LogicalDisk")]:
        for logical_drive in lookup:
            if disk.DeviceID == logical_drive:
                lookup[logical_drive] = disk.VolumeName

    return lookup


if __name__ == "__main__":
    print(logical_disk_to_volume_lookup())
