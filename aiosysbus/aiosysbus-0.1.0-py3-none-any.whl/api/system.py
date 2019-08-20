class System:

    def __init__(self, access):
        self._access = access

    async def get_deviceinfo(self):
        ''' Get device information '''
        return await self._access.post('DeviceInfo:get')

    async def get_devices(self):
        ''' Get devices '''
        return await self._access.post('Devices:get')

    async def get_led(self):
        ''' Get LED information '''
        return await self._access.post('LED:get')

    async def get_usbhosts(self):
        ''' Get USB Hosts '''
        return await self._access.post('USBHosts:get')

    async def checkForUpgrades(self):
        ''' Check upgrade version '''
        return await self._access.post('NMC:checkForUpgrades')

    async def disableRemoteAccess(self):
        ''' Set disable remote access '''
        return await self._access.post('NMC:disableRemoteAccess')

    async def enableRemoteAccess(self):
        ''' Set  enable remote acess '''
        return await self._access.post('NMC:enableRemoteAccess')

    async def get_nmc(self):
        ''' Get WAN information '''
        return await self._access.post('NMC:get')

    async def get_WANStatus(self):
        ''' Get WAN status '''
        return await self._access.post('NMC:getWANStatus')

    async def reboot(self):
        ''' Reboot livebox '''
        return await self._access.post('NMC:reboot')

    async def reset(self):
        ''' Reset livebox '''
        return await self._access.post('NMC:reset') 

    async def setWanMode(self,conf):
        '''
        Set WAN Mode
        {"parameters":{"WanMode":"WanMode","Username":"pnp/orange2","Password":"orange"}}
        '''
        return await self._access.post('NMC:setWanMode',conf)

    async def username(self):
        ''' Get username '''
        return await self._access.post('NMC:Username')

    async def get_remoteaccess(self):
        ''' Get Remote access information '''
        return await self._access.post('RemoteAccess:get')

    async def get_usermanagement(self):
        ''' Get users information '''
        return await self._access.post('UserManagement:getUsers')

    async def get_guest(self):
        ''' Get guests '''
        return await self._access.post('NMC/Guest:get')

    async def get_orangetv_IPTVStatus(self):
        ''' Get iptv status '''
        return await self._access.post('NMC/OrangeTV:getIPTVStatus')

    async def get_orangetv_IPTVMultiScreens(self):
        ''' Get multiscreeens for iptv '''
        return await self._access.post('NMC/OrangeTV:getIPTVMultiScreens')

    async def get_orangetv_IPTVConfig(self):
        ''' Get iptv information '''
        return await self._access.post('NMC/OrangeTV:getIPTVConfig')

    async def get_networkconfig(self):
        ''' Get saveset configuration '''
        return await self._access.post('NMC/NetworkConfig:get')

    async def set_networkconfig_NetworkBR(self,conf={"parameters":{"state":"true"}}):
        ''' Save configuration '''
        return await self._access.post('NMC/NetworkConfig:enableNetworkBR',conf)

    async def get_IPv6(self):
        ''' Get IPv6 information '''
        return await self._access.post('NMC/IPv6:get')

    async def get_autodetect(self):
        ''' Autodetect '''
        return await self._access.post('NMC/Autodetect:get')

    async def get_remoteaccess_TimeLeft(self):
        ''' Get timeleft for remote access '''
        return await self._access.post('RemoteAccess:getTimeLeft')

    async def get_usbhosts_Devices(self):
        ''' Get usb devices '''
        return await self._access.post('USBHosts:getDevices')

    async def get_time_LocalTimeZoneName(self):
        ''' Get local  zone information '''
        return await self._access.post('Time:getLocalTimeZoneName') 

    async def set_time_LocalTimeZoneName(self,conf):
        ''' Set local zone information '''
        return await self._access.post('Time:setLocalTimeZoneName',conf)

    async def get_time_Time(self):
        ''' Get time information '''
        return await self._access.post('Time:getTime')
