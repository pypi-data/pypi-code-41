''' key Based List '''

from ..base_node import SchemeBaseNode
from quick_scheme.field import FieldValue
from .node import SchemeNode


class KeyBasedListNode(SchemeNode):
    ''' Key Based Dictionary, where each item is of same type '''
    TYPE = dict

    def _set_data(self, data):
        ''' Set data for this object '''
        new_data = self._get_map_class_instance()
        if data is not None:
            for identity, value in data.items():
                new_data[identity] = self._create_child(
                    self.TYPE, identity, value)
        self._data = new_data

    def _get_data(self):
        ''' Get data  '''
        data = self._get_map_class_instance()
        #print("get data...")
        for key, value in self._data.items():
            #print("Key: %s, Value: %s (%s)" % (key, value, type(value)))
            if isinstance(value, FieldValue):
                data[key] = value.get_data()
            elif isinstance(value, SchemeBaseNode):
                data[key] = value.quick_scheme.get_data()
            else:
                data[key] = value
        return data


def KeyBasedList(item_type, preserve_order=KeyBasedListNode.PRESERVE_ORDER):
    '''
    Generates a key based list of objects

    :param item_type: type of the item in this list
    :param preserve_order: if true, the items in the list attempt to retain their order

    '''

    class QuickTypedKeyBasedList(KeyBasedListNode):
        ''' Quickly Defined typed list '''
        TYPE = item_type
        PRESERVE_ORDER = preserve_order

    return QuickTypedKeyBasedList


def KeyBasedListInst(item_type, preserve_order=KeyBasedListNode.PRESERVE_ORDER, **kwargs):
    ''' Create KeyBasedList instance '''
    return KeyBasedList(item_type, preserve_order)(**kwargs)
