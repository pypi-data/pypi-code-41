# -*- coding: utf-8 -*-
"""
Module which reads string data into :class:`housenumparser.element.Element`
elements.

eg:
- "23 bus 5, 23 bus 6" -> [<BusNumber> "23 bus 5", <BusNumber> "23 B-6"]
- "23", "24 bus 2" -> [<HouseNumber> "23", <BusNumber> "24 bus 2"]
- "25-27" -> [<HouseNumberSequence> "25-26", <HouseNumber> "27"]
"""
from __future__ import unicode_literals

import re
from builtins import str

from housenumparser.element import BisLetter
from housenumparser.element import BisLetterSequence
from housenumparser.element import BisNumber
from housenumparser.element import BisNumberSequence
from housenumparser.element import BusLetter
from housenumparser.element import BusLetterSequence
from housenumparser.element import BusNumber
from housenumparser.element import BusNumberSequence
from housenumparser.element import HouseNumber
from housenumparser.element import HouseNumberSequence
from housenumparser.element import ReadException


def read_data(data, step=None, on_exc=ReadException.Action.ERROR_MSG):
    """
    Parses a comma-seperated string of house number elements.

    :type data: str
    :param data: A :class:`str` with comma-seperated house numbers

    :type step: int
    :param step: Amount of house numbers per step. Commonly 1 or 2.
       Default None.
       When `None`, it will use 2 if beginning and ending of a
       series are both even or uneven, 1 otherwise.

    :type on_exc: .element.ReadException.Action
    :param on_exc: Flag on how to treat incorrect data. Default ERROR_MSG.

    :returns: A list from of the data.
    """
    return read_iterable(str(data).split(","), step=step,
                         on_exc=on_exc)


def read_iterable(inputs, step=None, on_exc=ReadException.Action.ERROR_MSG):
    """
    Parses an iterable of house number element strings.

    :type inputs: list[str]
    :param inputs: A list of house numbers and/or house number series.

    :type step: int
    :param step: Amount of house numbers per step. Commonly 1 or 2.
       Default None.
       When `None`, it will use 2 if beginning and ending of a series are
       both even or uneven, 1 otherwise.

    :type on_exc: .element.ReadException.Action
    :param on_exc: Flag on how to treat incorrect data. Default ERROR_MSG.

    :returns: A list of :class:`.element.Element`.
    """
    result = []
    for data in inputs:
        data = data.strip() if data else str(data)
        parsed_element = read_element(data, step=step, on_exc=on_exc)
        if parsed_element is not None:
            result.append(parsed_element)
    return result


def read_element(data, step=None, on_exc=ReadException.Action.ERROR_MSG):
    """
    Parses a single house number element string.

    :type data: str
    :param data: A String representating a house number.

    :type step: int
    :param step: Amount of house numbers per step. Commonly 1 or 2.
       Default None.
       When `None`, it will use 2 if beginning and ending of a
       series are both even or uneven, 1 otherwise.

    :type on_exc: ReadException.Action
    :param on_exc: Flag on how to treat incorrect data. Default ERROR_MSG.

    :returns: A :class:`.element.Element` OR an exception in case of
       incorrect data.
    """
    element_classes = [BusNumberSequence, BusLetterSequence, BisNumberSequence,
                       BisLetterSequence, BusNumber, BusLetter, BisNumber,
                       BisLetter, HouseNumberSequence, HouseNumber]
    stripped_data = re.sub(r'\s', '', data)
    exception = None
    try:
        for element_class in element_classes:
            match = element_class.regex.match(stripped_data)
            if match:
                args = [int(group) if group.isdigit() else group
                        for group in match.groups()]
                kwargs = {}
                if element_class == HouseNumberSequence:
                    kwargs['step'] = step
                return element_class(*args, **kwargs)
    except ValueError as e:
        exception = e
    if on_exc == ReadException.Action.RAISE:
        if exception:
            msg = str(exception)
        else:
            msg = "Could not parse/understand"
        raise ValueError(msg + ': ' + data)
    elif on_exc == ReadException.Action.DROP:
        return None
    elif on_exc in (ReadException.Action.ERROR_MSG,
                    ReadException.Action.KEEP_ORIGINAL):
        if exception:
            msg = str(exception)
        else:
            msg = "Could not parse/understand"
        return ReadException(msg, data=data, on_exc=on_exc)
    raise ValueError("Not implemented on_exc: " + str(on_exc))
