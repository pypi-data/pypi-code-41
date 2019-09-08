from copy import copy, deepcopy
from types import SimpleNamespace as o
from .fns import appendOne, assign, noop

_initialState = o(
    tests=[],
    suites=[],
    currentSuite=None,
    testsFound=False,
    succeeded=True,
    after=noop,
    afterEach=[],
    before=noop,
    beforeEach=[],
)


state = deepcopy(_initialState)


def _getState():
    return state


def initState():
    global state
    state = deepcopy(_initialState)
    return state


def _getCommon(*, label, fn, parentSuite, rootState, after, before):
    return o(
        label=label,
        fn=fn,
        parentSuite=parentSuite,
        rootState=rootState,
        after=after,
        before=before,
    )


def addSuite(label, after, afterEach, before, beforeEach, fn):
    currentSuite = state.currentSuite
    parent = currentSuite or state

    if afterEach is noop:
        afterEach = copy(parent.afterEach)
    else:
        afterEach = appendOne(afterEach)(parent.afterEach)

    if beforeEach is noop:
        beforeEach = copy(parent.beforeEach)
    else:
        beforeEach = appendOne(beforeEach)(parent.beforeEach)

    newSuite = assign(
        o(
            tests=[],
            suites=[],
            succeeded=True,
            afterEach=afterEach,
            beforeEach=beforeEach,
        )
    )(
        _getCommon(
            label=label,
            fn=fn,
            parentSuite=currentSuite,
            rootState=state,
            after=after,
            before=before,
        )
    )

    parent.suites.append(newSuite)

    return state


def addTest(label, after, before, fn):
    global state
    currentSuite = state.currentSuite
    test = _getCommon(
        label=label,
        fn=fn,
        parentSuite=currentSuite,
        rootState=state,
        after=after,
        before=before,
    )

    if currentSuite is None:
        state.tests.append(test)
    else:
        currentSuite.tests.append(test)

    state.testsFound = True

    return state
