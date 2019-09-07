'''reactive dataclasses'''

import sys
from typing import Sequence
from functools import wraps, partial
from contextlib import contextmanager


from dataclasses import (_field_assign as _original_field_assign,
                         dataclass as _original_dataclass,
                         field as _original_field,
                         Field as OriginalField,
                         MISSING,
                         fields)
import dataclasses

import rx
import rx.subject
import rx.operators as rxoperators

from . import typeguard


DELETE = object()
ASSIGNER_FUNCTION_NAME = '__rx_frozen_class_assigner__'

class ValueEmittingSubject(rx.subject.Subject):
    '''
    class for subjects able emitting its attribute value
    '''

class FieldSubject(rx.subject.Subject):
    def __init__(self, field):
        super().__init__()
        self.field = field

    def __call__(self, obj, invokes=None):
        _subjected = lambda items: ((o.subject(obj) if isinstance(o, Field) else o) for o in items)

        def invoked(invokes=invokes):
            if invokes is None:
                invokes = self.field.invokes

            yield rxoperators.filter(lambda item: item[0] is obj)
            yield rxoperators.map(lambda item: item[1])
            for operator in _subjected(invokes):
                if getattr(operator, '_typeguard', False):
                    yield operator(type=self.field.type, name=self.field.name)
                else:
                    yield operator

        def observes(*_observes, pipelines=None):
            if pipelines is None:
                pipelines = self.field.pipelines
            combined = rx.combine_latest(*_subjected(_observes)).pipe(*_subjected(pipelines))
            combined.subscribe(on_next=lambda item: self.on_next((obj, item)))
            return combined

        terminal = ValueEmittingSubject()

        terminal.__dict__['observes'] = observes

        self.pipe(*invoked()).subscribe(terminal)

        def emit(value=MISSING):
            if value is MISSING:
                value = getattr(obj, self.field.name)
            terminal.on_next(value)

        terminal.__dict__['emit'] = emit

        return terminal


class Field(OriginalField):
    '''
    reactive Field
    '''
    @_original_dataclass
    class RX:
        '''
        field level RX settings. For each `None` value - setting taken from `dataclass` decorator
        '''
        # field respects observed values
        init: bool = _original_field(default=None)
        # field reacts during setattr.
        setattr: bool = _original_field(default=None)
        # field reacts during delattr.
        delattr: bool = _original_field(default=None)

        def __post_init__(self):
            assert isinstance(self.init, (bool, type(None)))
            assert isinstance(self.setattr, (bool, type(None)))
            assert isinstance(self.delattr, (bool, type(None)))

    __slots__ = OriginalField.__slots__ + ('observes',
                                           'pipelines',
                                           'invokes',
                                           'scheduler',
                                           'rx',
                                           'subject')

    def __init__(self, observes, pipelines, invokes, scheduler, rx, *args):
        '''store attrs and create default subject'''
        super().__init__(*args)

        self.observes = observes if isinstance(observes, Sequence) else [observes]
        self.pipelines = pipelines if isinstance(pipelines, Sequence) else [pipelines]
        self.invokes = invokes if isinstance(invokes, Sequence) else [invokes]
        self.scheduler = scheduler
        self.rx = rx if isinstance(rx, Field.RX) else Field.RX(**rx)

        self.subject = FieldSubject(self)


def field(observe=[],
          pipeline=[],
          invoke=[],
          scheduler=None,
          rx=Field.RX(), 
          default=MISSING,
          default_factory=MISSING,
          init=True,
          repr=True,
          hash=None,
          compare=True,
          metadata=None):
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError('cannot specify both default and default_factory')
    return Field(observe, pipeline, invoke, scheduler, rx, default, default_factory, init, repr, hash, compare, metadata)


@contextmanager
def _field_assign_overriden(_overriden):
    # '_field_assign' must be temporarily returned to its original value (dataclasses.py:390)
    # during calls to 'dataclasses.dataclass' that performed during call to `rxdata.dataclass`
    # also it must be returned to original value after call to `rxdata.dataclass`
    _orig_field_assign = dataclasses._field_assign
    try:
        dataclasses._field_assign = _overriden
        yield
    finally:
        dataclasses._field_assign = _orig_field_assign


def _create_rxdataclass_specific_assigners(cls):
    @wraps(cls.__setattr__)
    def _rxdataclass_specific_setattr(obj, name, value):
        rxsubject(cls, name).on_next((obj, value))

    @wraps(cls.__delattr__)
    def _rxdataclass_specific_delattr(obj, name):
        rxsubject(cls, name).on_next((obj, DELETE))

    return _rxdataclass_specific_setattr, _rxdataclass_specific_delattr


@_original_dataclass
class RXDataclassSettings:
    '''
    RX related settings
    '''
    init: bool = _original_field(default=True)
    setattr: bool = _original_field(default=True)
    delattr: bool = _original_field(default=False)

    def __post_init__(self):
        assert isinstance(self.init, bool)
        assert isinstance(self.setattr, bool)
        assert isinstance(self.delattr, bool)

def dataclass(_cls=None, *,
              subject=None,
              rx=RXDataclassSettings(),
              init=True,
              repr=True,
              eq=True,
              order=False,
              unsafe_hash=False,
              frozen=False):
    '''
    During execution of this function - patch with own version of functions
    [dataclasses._field_assign, __setattr__, __delattr__].
    That versions of (dataclasses._field_assign, __setattr__, __delattr__) are specific for `_cls`
    class and contains its as closure.
    '''
    if not isinstance(rx, RXDataclassSettings):
        rx = RXDataclassSettings(**rx)

    def rxwrap(cls):
        _setattr, _delattr = _create_rxdataclass_specific_assigners(cls)
        if frozen:

            def _rx_field_assign(_, name, value, self_name):
                return f'{self_name}.{ASSIGNER_FUNCTION_NAME}.__func__({self_name},{name!r},{value})'
        else:
            def _rx_field_assign(_, name, value, self_name):
                return f'{self_name}.{name}={value}'

        @wraps(_original_dataclass)
        def _dataclasses_dataclass_forcing_original_field_assign(_cls=None, **kwargs):
            # this function used intstead of `dataclasses.dataclass` during `rxdata.dataclass`
            # and temporarily reinvokes dataclasses._field_assign to its original value
            # thus another dataclasses can be defined with no errors during `rxdata.dataclass`

            _original_wrapper = _original_dataclass(_cls=None, **kwargs)

            @wraps(_original_wrapper)
            def _wrapper_restoring_original_field_assign(cls):
                with _field_assign_overriden(_original_field_assign):
                    return _original_wrapper(cls)

            if cls is None:
                return _wrapper_restoring_original_field_assign

            return _wrapper_restoring_original_field_assign(cls)

        with _field_assign_overriden(_rx_field_assign):
            dataclasses.dataclass = _dataclasses_dataclass_forcing_original_field_assign
            try:

                _cls = dataclasses._process_class(cls, init, repr, eq, order, unsafe_hash, frozen)

                if frozen:
                    setattr(_cls, ASSIGNER_FUNCTION_NAME, _setattr)

                else:
                    if dataclasses._set_new_attribute(_cls, '__setattr__', _setattr):
                        raise TypeError(f'Cannot overwrite attribute __setattr__ '
                                        f'in class {_cls.__name__}')

                    if dataclasses._set_new_attribute(_cls, '__delattr__', _delattr):
                        raise TypeError(f'Cannot overwrite attribute __delattr__ '
                                        f'in class {_cls.__name__}')


                if subject is not None:
                    # create subclass containing quick links to Field subjects
                    # assuming subject=='field':
                    # Node.field.id(node).observes(Root.field.id(root))
                    setattr(_cls,
                            subject,
                            type(subject,
                                 (),
                                 dict((((field.name, field.subject) for field in fields(_cls))))))

                _orig_init = _cls.__init__


                @wraps(_orig_init)
                def __init__(self, *args, **kwargs):
                    observed_initial_values = {}

                    subscriptions = {}

                    _rxfields = [f for f in fields(_cls) if isinstance(f, Field)]
                    for field in _rxfields:
                        _subject = field.subject(self)
                        subscriptions[field] = {'subject': _subject}
                        subscriptions[field]['setattr'] = _subject.subscribe(
                            on_next=partial(object.__setattr__, self, field.name)
                            )

                        _subject.pipe(rxoperators.first()).subscribe(
                            on_next=partial(observed_initial_values.__setitem__, field)
                            )

                        if field.observes:
                            # set reaction that includes defined pipeline
                            subscriptions[field]['observes'] = \
                                _subject.observes(*field.observes, pipelines=field.pipelines)
                            if (field.rx.init is None and rx.init) or (field.rx.init is True):
                                emitters = (s for s in field.observes
                                            if isinstance(s, ValueEmittingSubject))
                                # force emit of object for external rx fields
                                for emitter in emitters:
                                    emitter.emit()


                    _orig_init.__get__(self, _cls)(*args, **kwargs)

                    for field, observed_value in observed_initial_values.items():
                        # re-setattr first passed values - that must be observed values
                        # if they defined or default if no observed defined
                        if isinstance(field, Field):
                            # if rx['init'] == False for class or field - just use default values
                            if (field.rx.init is None and rx.init) or (field.rx.init is True):
                                object.__setattr__(self, field.name, observed_value)

                    if not frozen:
                        for field in _rxfields:
                            # possibly rearrange subscriptions to fit
                            # per-class and per-field settings
                            if not ((field.rx.setattr is None and rx.setattr) or (field.rx.setattr is True)):
                                # if 'setattr' reaction disabled
                                #  * create new subject with empty invoke
                                #  * subscribe setattr there
                                #  * dispose old subject if no observed fields
                                subscriptions[field]['setattr'].dispose()
                                if not 'observes' in subscriptions[field]:
                                    subscriptions[field]['subject'].dispose()

                                subscriptions[field]['subject'] = field.subject(self, invokes=())

                                subscriptions[field]['subject'].subscribe(
                                    on_next=partial(object.__setattr__, self, field.name)
                                    )

                            if ((field.rx.delattr is None and rx.delattr)
                                    or (field.rx.delattr is True)):
                                # if 'delattr' reaction enabled - add `on_completed` reaction
                                subscriptions[field]['subject'].subscribe(
                                    on_completed=partial(object.__delattr__, self, field.name))

                _cls.__init__ = __init__
                return _cls

            finally:
                dataclasses.dataclass = _original_dataclass

    if _cls is None:
        return rxwrap
    return rxwrap(_cls)


def rxsubject(dataclass, name):
    '''find field level subject for dataclass'''

    for field in fields(dataclass):
        if field.name == name:
            return field.subject
    raise NameError(f'class {dataclass!r} does not includes field {name!r}')

__all__ = ['dataclass', 'field', 'typeguard']
