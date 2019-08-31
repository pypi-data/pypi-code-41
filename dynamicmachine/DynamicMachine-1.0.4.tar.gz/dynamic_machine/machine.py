'''
Created on Jun 18, 2014

@author: lwoydziak
'''
from time import sleep
import os
from dynamic_machine.inventory import Inventory

class MachineException(Exception):
    pass

class Machine(object):
    NODE_UP = "run"
    def __init__(self, provider, existing=False):
        if provider == None:
            raise MachineException("Machine cannot be created without a provider")
        self.__onProvider = provider
        self.__hostname = None
        self.__sshKey = None
        self.__size = None
        self.__image = None
        self.__location = None
        self.__created = existing

    def sshKey(self, path):
        onProvider = self.__onProvider
        sshKeyFilename = os.path.expanduser(path)
        with open(sshKeyFilename) as sshKeyFile:
            sshKey = sshKeyFile.read()
        keyName = (sshKey[sshKey.rfind(" ")+1:]).lstrip().rstrip()
        availableKeys = onProvider.list_key_pairs()
        while True:
            try:
                self.__sshKey = str([aKey for aKey in availableKeys if keyName in aKey.name][0].fingerprint)
                return self
            except IndexError:
                onProvider.import_key_pair_from_string(keyName, sshKey)
                availableKeys = onProvider.list_key_pairs()

    def size(self, desiredSize):
        sizes = self.__onProvider.list_sizes()
        size = [aSize for aSize in sizes if desiredSize in aSize.name][0]
        self.__size = size
        return self
    
    def image(self, desiredImage): 
        images = self.__onProvider.list_images()
        image = [anImage for anImage in images if anImage.name.startswith(desiredImage)][0]
        self.__image = image
        return self
    
    def location(self, desiredLocation):
        locations = self.__onProvider.list_locations()
        location = [aLocation for aLocation in locations if desiredLocation in aLocation.name][0]
        self.__location = location
        return self
        
    def name(self, desiredName):
        if not self.__created:
            numberOfMachines = len(Inventory(self.__onProvider).list(desiredName))
            self.__hostname = desiredName+"-"+str(numberOfMachines) if numberOfMachines > 0 else desiredName 
        else:
            self.__hostname = desiredName
        return self

    def __ensureParameters(self):
        if self.__hostname == None:
            raise MachineException("Machine Hostname not set, use: machine.name('hostname')")
        if self.__sshKey == None:
            raise MachineException("Machine SSH Key not set, use: machine.sshKey(path)")
        if self.__size == None:
            raise MachineException("Machine size not set, use: machine.size('size')")
        if self.__image == None:
            raise MachineException("Machine image not set, use: machine.image('image')")
        if self.__location == None:
            raise MachineException("Machine location not set, machine.location('location')")
    
    def create(self):
        if self.__created:
            return self
        
        self.__ensureParameters()
        self.__onProvider.create_node(name=self.__hostname, 
                                      image=self.__image, 
                                      size=self.__size, 
                                      location=self.__location,
                                      ex_ssh_key_ids=[self.__sshKey])
        self.__created = True
        return self

    def waitUntilReady(self):
        print('Creating: "' + self.__hostname + '" in https://cloud.digitalocean.com/droplets ', end="", flush=True)
        while self.__created:
            print(".",end="",flush=True)
            sleep(10)
            nodeOfInterest = Inventory(self.__onProvider).list(self.__hostname)[0]
            if self.NODE_UP in str(nodeOfInterest.state).lower():
                break
        print("Done ("+nodeOfInterest.public_ips[0]+")")
    
    def destroy(self):
        if self.__hostname == None:
            raise MachineException("Machine Hostname not set, use: machine.name('hostname')")
        
        nodeToDestroy = self.__returnNodeIfExists(self.__hostname)
        
        if not self.__created:
            return

        try:
            if not self.__onProvider.destroy_node(nodeToDestroy):
                raise MachineException("Unable to destroy node "+self.__hostname+" please manually destroy or try again later.")
        except Exception as exc:
            raise MachineException("Unable to destroy node " + self.__hostname + " please manually destroy or try again later. \n(" + str(exc) + ")" )
    
    def __returnNodeIfExists(self, hostname):
        nodeOfInterest = None
        try:
            nodeOfInterest = Inventory(self.__onProvider).list(hostname)[0]
        except MachineException:
            self.__created = False    
        if not nodeOfInterest:
            self.__created = False
        return nodeOfInterest
        
    def waitUntilDestroyed(self):
        print('Destroying: "'+self.__hostname+'"', end="", flush=True)
        while self.__created:
            print(".",end="",flush=True)
            self.__returnNodeIfExists(self.__hostname)
            if self.__created:
                sleep(10)
        print("Done")
