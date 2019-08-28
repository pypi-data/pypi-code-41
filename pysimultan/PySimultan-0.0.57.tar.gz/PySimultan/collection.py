from PySimultan.base_classes import TrackedClass
from PySimultan.update_handler import UpdateHandler
from PySimultan.geo_functions import print_status


class Collection(object):

    def __init__(self, tracked_class=None):

        self.tracked_class = None
        self.instances = list()
        self._observers = []
        self._UpdateHandler = UpdateHandler()
        super().__init__()

    def add_instance(self, instance):

        if self.tracked_class is None:
            self.tracked_class = instance.__class__

        if instance.__class__ == self.tracked_class:
            if next((x for x in self.instances if x == instance), None) is None:
                self.instances.append(instance)
                self.bind_to(instance)
            else:
                print('instance already present in list')
        else:
            raise ValueError('Cannot add instance to the collection. Instance is not the right class')

    def remove(self, instance):
        try:
            self.instances.remove(instance)
        except Exception as e:
            print('Could not remove instance, instance not in list')

    def append(self, instance):
        if self.tracked_class is None:
            self.tracked_class = instance.__class__
        if instance.__class__ == self.tracked_class:
            self.instances.append(instance)
            self.bind_to(instance)

    def bind_to(self, callback):
        if callback not in self._observers:
            self._observers.append(callback)

    def unbind(self, callback):
        if callback in self._observers:
            self._observers.remove(callback)

    def _default_set_handling(self, attr_name, value):
        default_notification = True

        if isinstance(value, tuple):
            setattr(self, '_' + attr_name, value[0])
            notify_observers = default_notification
            if value.__len__() > 1:
                if 'notify_observers' in value[1]:
                    notify_observers = value[1]['notify_observers']
                else:
                    notify_observers = default_notification
        else:
            setattr(self, '_' + attr_name, value)
            notify_observers = default_notification

        if notify_observers:

            for callback in self._observers:
                print(attr_name + '_changed')
                instance = callback.__self__
                instance._UpdateHandler.add_notification(callback, attr_name)
                # callback(ChangedAttribute=attr_name)

    def print_status(self, *args, **kwargs):
        print_status(*args, **kwargs)


class BuildingCollection(TrackedClass):

    def __init__(self):
        super().__init__()
        self.Layer_collection = Collection()
        self.Vertex_collection = Collection()
        self.Edge_collection = Collection()
        self.Edge_loop_collection = Collection()
        self.Polyline_collection = Collection()
        self.Face_collection = Collection()
        self.Zone_collection = Collection()
        self.Proxy_geometrie_collection = Collection()
        self.Window_collection = Collection()
        self.Part_collection = Collection()
        self.MatLayer_collection = Collection()
        self.Material_collection = Collection()
        self.collections = [self.Layer_collection,
                            self.Vertex_collection,
                            self.Edge_collection,
                            self.Edge_loop_collection,
                            self.Polyline_collection,
                            self.Face_collection,
                            self.Zone_collection,
                            self.Proxy_geometrie_collection,
                            self.Window_collection,
                            self.Part_collection,
                            self.MatLayer_collection,
                            self.Material_collection,
                            ]

    def add_collection(self, name):
        self.__setattr__(name, Collection())
        self.collections.append(self.__getattribute__(name))

    def remove_collection(self, name):
        self.__delattr__(name)

    def add_instance(self, instance):
        # check which collection to add:
        collection = next((x for x in self.collections if x.tracked_class == instance.__class__), None)

        if collection is not None:
            collection.add_instance(instance)
        else:
            self.add_collection(instance.__class__.__name__)
            self.__getattribute__(instance.__class__.__name__).add_instance(instance)
            
            
if __name__ == '__main__':
    Collection()
    building_collection = BuildingCollection()







