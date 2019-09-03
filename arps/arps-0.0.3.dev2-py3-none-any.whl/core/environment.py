import warnings
from typing import Dict

__REGISTERED_POLICIES: Dict = {}


def list_registered_policies(manager_id):
    '''
    List registered policies associated with a manager

    Args:
    - manager_id : registered policies will be associated with this id
    '''
    return list(__REGISTERED_POLICIES.get(manager_id, {}).keys())


def register_policy(manager_id, policy_id, policy_class):
    '''
    Register policy class to be available globally

    Args:
    - manager_id : registered policies will be associated with this id
    - policy_id : policy unique identification
    - policy_class : policy class
    '''
    __REGISTERED_POLICIES.setdefault(manager_id, {})[policy_id] = policy_class


def unregister_policy(manager_id, policy_id):
    '''
    Removes policy class from the policy repository

    Args:
    - manager_id : registered policies will be associated with this id
    - policy_id : policy unique identification
    '''

    del __REGISTERED_POLICIES[manager_id][policy_id]


def load_policy(manager_id, policy_id):
    '''
    Returns a new instance of policy associated with policy id

    Args:
    - manager_id : registered policies will be associated with this id
    - policy_id : policy unique identification

    Raises:
    - KeyError if policy id is not registered
    '''
    return __REGISTERED_POLICIES[manager_id][policy_id]()


def is_policy_registered(manager_id, policy_id):
    '''
    Returns True if policy was previously registered, False otherwise

    Args:
    - manager_id : registered policies will be associated with this id
    - policy_id : policy identifier
    '''
    return policy_id in __REGISTERED_POLICIES[manager_id]


def clear_policies():
    '''Remove all policies stored

    This is used in tests and will be here on provisional basis; will
    be removed when these functions are extracted to a class

    '''
    warnings.warn('This is here just to make tests work; it will be removed as soon as issue #41 is closed', FutureWarning)

    __REGISTERED_POLICIES.clear()


class Environment:

    def __init__(self, sensors=None, actuators=None):
        '''
        Receives instances that will be used during application execution lifetime
        and need to be accessible by other classes

        Keyword parameters:
        - sensors : a dict containing sensor id and instance
        - actuators : a dict containing actuator id and instance

        See that sensors and actuator are global while policies will be created local required,
        that why sensor and actuator are instances while policies are just a class

        Raises:
        - TypeError if sensors or actuators are not a dict instance
        '''
        sensors = sensors or {}
        actuators = actuators or {}

        if not isinstance(sensors, dict):
            raise TypeError(
                'Wrong parameter type on sensors: {}'.format(sensors))

        if not isinstance(actuators, dict):
            raise TypeError(
                'Wrong parameter type on actuators: {}'.format(actuators))

        self._sensors = sensors
        self._actuators = actuators

    @property
    def sensors(self):
        return self._sensors

    @property
    def actuators(self):
        return self._actuators

    def sensor(self, sensor_id):
        '''
        Return sensor global instance based on id

        Parameters:
        - sensor_id : sensor identifier

        Raises KeyError when an invalid sensor id is supplied
        '''
        return self._sensors[sensor_id]

    def actuator(self, actuator_id):
        '''
        Return actuator instance based on id

        Parameters:
        - actuator_id : actuator identifier

        Raises KeyError when an invalid actuator id is supplied
        '''
        return self._actuators[actuator_id]

    def resources(self):
        '''
        Return a dictionary containing touchpoint category as key and touchpoint resource as value
        '''
        sensors_resources = {
            sensor_category: sensor.resource for sensor_category,
            sensor in self._sensors.items()}
        actuators_resources = {
            actuator_category: actuator.resource for actuator_category,
            actuator in self._actuators.items()}

        return {**sensors_resources, **actuators_resources}
