''' Basic List Of Nodes '''

from ..base_node import SchemeBaseNode


class ListOfNodesNode(SchemeBaseNode):
    ''' List Of Nodes Node '''
    TYPE = dict

    def _initialize(self, *args, **kwargs):
        ''' Initialization hook for object - called before the data is set'''
        self._data = []

    def _set_data(self, data):
        ''' Set data for this object '''
        item_list = []
        if data:
            if not isinstance(data, list):
                data = [data]
            for idx, item in enumerate(data):
                child = self._create_child(self.TYPE, identity=idx, value=item)
                item_list.append(child)
        self._data = item_list

    def _get_data(self):
        ''' Get data  '''
        item_list = []
        for item in self._data:
            value = item if not isinstance(
                item, SchemeBaseNode) else item.quick_scheme.get_data()
            item_list.append(value)
        return item_list


def ListOfNodes(node_type):
    '''
    Generates a list of nodes node

    :param node_type: type of the node in this list

    '''

    class QuickListOfNodesNode(ListOfNodesNode):
        ''' Quickly Defined typed list '''
        TYPE = node_type

    return QuickListOfNodesNode


def ListOfNodesInst(item_type, **kwargs):
    ''' Create KeyBasedList instance '''
    return ListOfNodes(item_type)(**kwargs)
