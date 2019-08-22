''' List of References '''

from ..base_node import SchemeBaseNode
from .list_of_nodes import ListOfNodesNode


class ReferenceNode(SchemeBaseNode):
    ''' Reference Node - node referring to another node '''
    PATH = ".reference"
    DEREFERENCE = True

    def _initialize(self, *args, **kwargs):
        ''' Initialize '''
        self._data = None

    def _set_data(self, data):
        ''' Set Data '''
        self._data = data

    def _dereference(self):
        ''' Dereference this item  '''
        items = self._get_by_path(self.PATH)
        return "<%s>" % self._data

    def _get_data(self):
        ''' Get Data '''
        if self.DEREFERENCE:
            return self._dereference()
        return self._data


def Reference(path, dereference=ReferenceNode.DEREFERENCE):
    ''' Generate Reference Class '''

    class Reference(ReferenceNode):
        ''' Generated Reference  Node '''
        PATH = path
        DEREFERENCE = dereference

    return Reference


class ListOfReferencesNode(ListOfNodesNode):
    ''' List of References '''
    TYPE = list

    def _initialize(self, *args, **kwargs):
        ''' Initialization hook for object - called before the data is set'''
        #print("Created List of Reference: %s" % self.TYPE)
        self._data = []

    def _set_data(self, data):
        ''' Set data for this object '''
        item_list = []
        if not isinstance(data, list):
            data = [data]
        for idx, item in enumerate(data):
            # print("Adding item#%s (%s) to the list" % (idx, item))
            child = self._create_child(self.TYPE, identity=idx, value=item)
            item_list.append(child)
        #print("Adding %s" % item_list)
        self._data = item_list

    def _get_data(self):
        ''' Get data  '''
        item_list = []
        for item in self._data:
            value = item if not isinstance(
                item, SchemeBaseNode) else item.quick_scheme.get_data()
            item_list.append(value)
        return item_list


def ListOfReferences(node_type, reference_path, dereference=True):
    '''
    Generates a list of nodes node

    :param node_type: type of the node in this list
    :param reference_path: reference_path
    :param dereference: dereference data 

    '''

    class QuickListOfReferences(ListOfReferencesNode):
        ''' Quickly Defined typed list '''
        TYPE = Reference(reference_path, dereference)

    return QuickListOfReferences


def ListOfReferencesInst(item_type, reference_path, dereference=True, **kwargs):
    ''' Create ListOfReferences instance '''
    return ListOfReferences(item_type, reference_path, dereference)(**kwargs)
