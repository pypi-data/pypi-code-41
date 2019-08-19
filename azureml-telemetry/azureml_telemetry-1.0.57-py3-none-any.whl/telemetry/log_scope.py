# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Modules for log scope, including the definition of context manager and decorator."""
import uuid
from functools import wraps
from datetime import datetime
from copy import deepcopy
from contextlib import contextmanager
from collections import deque

from azureml import telemetry
from azureml.telemetry.contracts._event import Event


class LogScope:
    """LogScope class represents a single log scope in which some scope specific log context info is stored."""

    @staticmethod
    def get_current() -> 'LogScope':
        """Get the current LogScope in effect."""
        return _ScopeStack._current()

    def __init__(self, component_name, scope_name, na_properties: set = None, parent_scope: 'LogScope' = None,
                 **kwargs):
        """Construct a LogScope."""
        self.component_name = component_name
        self.name = scope_name
        self._parent_scope = parent_scope
        if parent_scope is None:
            self.shared_context = {}  # init the shared_context for the top level log scope

        # first, set na_properties, so that they will be available if neither parent nor current scope defines them
        na_value = 'NotAvailable'
        self.scoped_context = {k: na_value for k in na_properties} if na_properties is not None else {}

        # second, inherit from parent_scope
        self.id = str(uuid.uuid4())
        if parent_scope is not None:
            self.parent_id = parent_scope.id
            self.scoped_context.update(deepcopy(parent_scope.scoped_context))
        else:
            self.parent_id = self.id

        # third, save any properties passed in
        if kwargs is not None:
            self.scoped_context.update(kwargs)

    def __setitem__(self, key, value):
        """Assign value to the log signal key within this log scope."""
        self.scoped_context[key] = value

    def __getitem__(self, key):
        """Get the value of the log signal key within this log scope"""
        root_scope = _ScopeStack._root()
        shared_value = None if root_scope is None else root_scope.shared_context.get(key, None)
        return self.scoped_context.get(key, shared_value)

    def __contains__(self, key):
        """To check if signal key is set in the log scope."""
        return key in self.scoped_context or key in _ScopeStack._root().shared_context

    def __str__(self):
        """Return a string to show the log signals this log scope contains."""
        return self.scoped_context.__str__()

    def set_shared_value(self, key, value):
        """Set the value which will be shared inside the top scope."""
        if key in self.scoped_context:
            # that means key is set in current scope or inherited from a parent scope
            conflict_scope = next(  # find the top most one
                (s for s in _ScopeStack._ctx_stack if s.scoped_context.get(key, value) != value),
                None)
            if conflict_scope:
                # todo: log a special event
                print('shared context conflict for {}, value from component {} in scope {} is {}' +
                      'while value from component {} in scope {} is {}.'
                      .format(key, self.component_name, self.name, value, conflict_scope.component_name,
                              conflict_scope.name, conflict_scope[key]))
                return

        # set the value to shared context
        top_scope = _ScopeStack._root()
        top_scope.shared_context[key] = value

    def get_rollup_value(self, key):
        """
        Get the value for the key of the scope, and from all its parent scopes.
        Alone with component name and scope name.

        Parameters:
        key (str): the name of the key for which you want to get the rollup value.
        Returns:
        list of tuple: each tuple is the value for the key of a scope, the sequence in the tuple is
        component_name, scope_name and the value.

        """
        compound_values = []
        curr_scope = self
        while curr_scope is not None:
            val = curr_scope[key]
            if val is None:
                # key is not in curr_scope, this implies it is not in any of its parent scopes
                # (otherwise it will be inheritted), so it it is safe to stop the iteration
                break
            compound_values.append((curr_scope.component_name, curr_scope.name, curr_scope[key]))
            curr_scope = curr_scope._parent_scope
        return compound_values


class _ScopeStack:
    """The stack to contain all the current nested log scopes."""

    _ctx_stack = deque([])

    @classmethod
    def _create_and_push(cls, component_name, name, na_properties, **kwargs) -> LogScope:
        next = LogScope(component_name, name, na_properties, cls._current(), **kwargs)
        cls._ctx_stack.append(next)
        return next

    @classmethod
    def _pop(cls) -> LogScope:
        return cls._ctx_stack.pop()

    @classmethod
    def _current(cls) -> LogScope:
        return cls._ctx_stack[-1] if cls._ctx_stack else None

    @classmethod
    def _root(cls) -> LogScope:
        return cls._ctx_stack[0] if cls._ctx_stack else None


@contextmanager
def context_scope(component_name, name, track=False, na_properties: set = None, **kwargs):
    """
    Initialize a log scope.

    Parameters:
    component_name (str): the name of the component that owns the scope.
    name (str): name of the scope.
    track (bool): indicate if a context scope or a tracking scope should be returned.
    na_properties (set): a set of property names which are not available within the scope, and will be filled
    with value 'NotAvailable' if it is not set in any of the parent scope.
    kwargs: the list of the key/value pairs which will be initially stored in the log scope.
    Returns:
    If track is False, which is by default, will return a normal context scope, otherwise, return a track scope
    which will track the duration, compelte status and error msg automatically.

    """
    if track:
        start_time = datetime.utcnow()
        exception = None
        completion_status = 'success'
    try:
        scope = _ScopeStack._create_and_push(component_name, name, na_properties, **kwargs)
        yield scope
    except Exception as e:
        completion_status = 'failure'
        exception = e
        raise e
    finally:
        if track:
            end_time = datetime.utcnow()
            duration_ms = round((end_time - start_time).total_seconds() * 1000, 2)

            scope['completionStatus'] = completion_status
            scope['durationMs'] = duration_ms
            err_msg = str(exception) if exception else None
            logger = telemetry.get_event_logger()
            track_event = Event(
                '{}.Scope.Tracking'.format(scope.component_name),
                extension_fields={
                    'tracking_msg': 'scope {}|{}, completed with status {}, duration {}ms. error msg: {}'
                                    .format(component_name, name, completion_status, duration_ms, err_msg)
                }
            )
            logger.log_event(track_event)
        _ScopeStack._pop()


def ctx_scope(component_name, track=False, na_properties=None, **prop_kwargs):
    """ctx_scope is a function decorator, which is a short cut of context_scope apply on the whole function."""
    def cntx_scope(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with context_scope(component_name, func.__name__, track, na_properties, **prop_kwargs):
                return func(*args, **kwargs)

        return wrapper
    return cntx_scope
