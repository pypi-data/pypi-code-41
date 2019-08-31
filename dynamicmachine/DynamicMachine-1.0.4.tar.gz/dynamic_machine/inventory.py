'''
Created on Jun 18, 2014

@author: lwoydziak
'''

class Inventory(object):
    def __init__(self, provider):
        self.__onProvider = provider

    def __filter(self, nodes, byFilter, varible):
        nodesOfInterest = [aNode for aNode in nodes if byFilter in getattr(aNode, varible)]
        return nodesOfInterest

    def list(self, filteredByHost=None, filteredByIp=None):
        nodes = self.__onProvider.list_nodes()
        if filteredByHost:
            return self.__filter(nodes, filteredByHost, "name")
        if filteredByIp:
            return self.__filter(nodes, filteredByIp, "public_ips")
        return nodes