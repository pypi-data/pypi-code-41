import asyncio
import inspect
from functools import partial, wraps, update_wrapper


class ObservableMixin:

    def __init__(self, **kwargs):
        self._listeners = list()
        self.notified_tasks = list()

    def add_listener(self, listen, predicate=None):
        '''
        Add a new listener to track when the resource is modified

        It supports async and non async listeners

        Args:
        - listen: function that will receive an event when the resource is modified
        - predicate:
        '''
        #print(type(self).__name__, '->', listen)
        predicate = predicate or (lambda _: True)
        listener = partial(self.conditional_listener, listen, predicate)
        update_wrapper(listener, listen)
        self._listeners.append(listener)

    def remove_listener(self, listener):
        result = [_listener for _listener in self._listeners if listener == _listener.args[0]]

        if not any(result):
            return

        if len(result) != 1:
            print('\n'.join(str(element) for element in result))
        assert len(result) == 1, 'Expected 1, got {}: {}'.format(len(result), result)

        self._listeners.remove(result[0])

    async def notify(self, event):
        self.notified_tasks = [task for task in self.notified_tasks if not task.done()]
        for listener in self._listeners:
            self.notified_tasks.append(asyncio.create_task(listener(event)))

    async def wait_for_notified_tasks(self):
        await asyncio.wait_for(asyncio.gather(*self.notified_tasks), timeout=10)
        self.notified_tasks.clear()

    def clear(self):
        self._listeners.clear()

    async def conditional_listener(self, action, action_condition, event):
        '''Execute an action, passing an event as parameter, if condition is
        met

        Args:
        - action: action to be executed (can be sync or async)
        - action_condition: predicate based on the event
        - event: event passed to action
        '''

        if not action_condition(event):
            return

        async_action = wrap_into_async(action)

        if len(inspect.signature(action).parameters):
            await async_action(event)
        else:
            await async_action()


def wrap_into_async(sync_or_async):
    '''Wrap the function just to run as async

    '''
    if asyncio.iscoroutinefunction(sync_or_async):
        return sync_or_async

    @wraps(sync_or_async)
    async def inner(*args, **kwargs):
        return sync_or_async(*args, **kwargs)

    return inner
