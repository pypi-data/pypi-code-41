import logging

from arps.core.simulator.resource import Resource, TrackedValue

class TouchPoint:
    '''
    Base class that represents a touchpoint

    It offers a method to read the current touchpoint's state
    '''

    def __init__(self, resource):
        '''
        Initializes the class setting its resource

        Args:
        - resource: resource to be read or set
        '''
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.debug(
            'TouchPoint created, type: {}'.format(
                self.category()))

        self._resource = resource

    def read(self):
        '''
        Returns the content of the touchpoint
        Do not assume any format, it can be str or a dict for example
        '''
        return self._resource.value

    @classmethod
    def category(cls):
        '''
        Derived classes must define class attribute category
        '''
        return cls._category

    @property
    def resource(self):
        return self._resource


class Sensor(TouchPoint):
    '''
    Base class for sensor
    '''

    def __str__(self):
        return 'Sensor category {} on resource {}'.format(self.category(), self.resource)

class Actuator(TouchPoint):
    '''
    Base class for actuator
    '''

    def set(self, **parameters):
        '''
        Modifies the actuator state

        Args:
        - parameters: keyword arguments. Expected value, epoch, and identifier of who is modifying
        '''

        tracked_value = TrackedValue(parameters['value'], parameters['epoch'],
                                     parameters['identifier'], Resource.EvtType.mas)
        self._set(tracked_value)

    def _set(self, tracked_value):
        '''
        Just set the current resource state

        This method can be inherited if more elaborated assignment need be done
        '''
        self.resource.value = tracked_value
