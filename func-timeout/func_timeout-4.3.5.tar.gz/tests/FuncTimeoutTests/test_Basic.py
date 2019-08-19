#!/usr/bin/env python
# vim: set ts=4 sw=4 expandtab :

'''
    Copyright (c) 2017 Tim Savannah All Rights Reserved.

    Licensed under the Lesser GNU Public License Version 3, LGPLv3. You should have recieved a copy of this with the source distribution as
    LICENSE, otherwise it is available at https://github.com/kata198/func_timeout/LICENSE
'''

import copy
import gc
import sys
import time
import threading
import subprocess

from func_timeout import func_timeout, FunctionTimedOut, func_set_timeout

from TestUtils import ARG_NO_DEFAULT, getSleepLambda, getSleepLambdaWithArgs, compareTimes

class TestBasic(object):
    '''
        TestBasic - Perform tests using the basic func_timeout function
    '''

    def test_funcTimeout(self):
        sleepFunction = getSleepLambda(2.00)

        expectedResult = 5 + 13

        startTime = time.time()
        result = sleepFunction(5, 13)
        endTime = time.time()

        assert result == expectedResult , 'Did not get return from sleepFunction'

        try:
            result = func_timeout(2.5, sleepFunction, args=(5, 13))
        except FunctionTimedOut as te:
            raise AssertionError('Got unexpected timeout at 2.5 second timeout for 2.00 second function: %s' %(str(te),))

        assert result == expectedResult , 'Got wrong return from func_timeout.\nGot:       %s\nExpected:  %s\n' %(repr(result), repr(expectedResult))

        gotException = False
        try:
            result = func_timeout(1, sleepFunction, args=(5, 13))
        except FunctionTimedOut as te:
            gotException = True

        assert gotException , 'Expected to get FunctionTimedOut exception for 1.25 sec function at 1s timeout'

        try:
            result = func_timeout(2.5, sleepFunction, args=(5,), kwargs={ 'b' : 13})
        except FunctionTimedOut as te:
            raise AssertionError('Got unexpected timeout at 2.5 second timeout for 2.00 second function: %s' %(str(te), ))
        except Exception as e:
            raise AssertionError('Got unknown exception mixing args and kwargs: < %s >  %s' %(e.__class__.__name__, str(e)))

        assert result == expectedResult , 'Got wrong result when mixing args and kwargs'

    def test_retry(self):
        sleepFunction = getSleepLambda(1.2)

        expectedResult = 5 + 19

        gotException = False
        functionTimedOut = None

        startTime = time.time()
        try:
            result = func_timeout(.8, sleepFunction, args=(5, 19))
        except FunctionTimedOut as fte:
            functionTimedOut = fte
            gotException = True
        endTime = time.time()

        assert gotException , 'Expected to get exception'
        assert compareTimes(endTime, startTime, .8, 3, deltaFixed=.15) == 0 , 'Expected to wait .8 seconds. Was: %f - %f = %f' %(endTime, startTime, round(endTime - startTime, 3))

        gotException = False
        startTime = time.time()
        try:
            result = functionTimedOut.retry()
        except FunctionTimedOut:
            gotException = True
        endTime = time.time()

        assert gotException , 'Expected to get exception on retry.'
        assert compareTimes(endTime, startTime, .8, 3, deltaFixed=.15) == 0 , 'Expected retry with no arguments to use same timeout of .8'

        gotException = False
        startTime = time.time()
        try:
            result = functionTimedOut.retry(None)
        except FunctionTimedOut:
            gotException = True
        endTime = time.time()

        assert not gotException , 'Did NOT to get exception with no timeout'
        assert compareTimes(endTime, startTime, 1.2, 3, deltaFixed=.15) == 0 , 'Expected retry with None as timeout to last full length of function'

        gotException = False
        startTime = time.time()
        try:
            result = functionTimedOut.retry(.55)
        except FunctionTimedOut:
            gotException = True
        finally:
            endTime = time.time()

        assert gotException , 'Expected to time out after .55 seconds when providing .55'
        assert compareTimes(endTime, startTime, .55, 3, deltaFixed=.15) == 0 , 'Expected providing .55 would allow timeout of up to .55 seconds'

        threadsCleanedUp = False

        for i in range(5):
            time.sleep(1)
            gc.collect()

            if threading.active_count() == 1:
                threadsCleanedUp = True
                break


        assert threadsCleanedUp , 'Expected other threads to get cleaned up after gc collection'

    def test_exception(self):
        sleepFunction = getSleepLambda(.85)

        expectedResult = 5 + 19

        gotException = False
        functionTimedOut = None

        startTime = time.time()
        try:
            result = func_timeout(.5, sleepFunction, args=(5, 19))
        except FunctionTimedOut as fte:
            functionTimedOut = fte
            gotException = True
        endTime = time.time()

        assert gotException , 'Expected to get exception'

        assert 'timed out after ' in functionTimedOut.msg  , 'Expected message to be constructed. Got: %s' %(repr(functionTimedOut.msg), )
        assert round(functionTimedOut.timedOutAfter, 1) == .5 , 'Expected timedOutAfter to equal timeout ( .5 ). Got: %s' %(str(round(functionTimedOut.timedOutAfter, 1)), )
        assert functionTimedOut.timedOutFunction == sleepFunction , 'Expected timedOutFunction to equal sleepFunction'
        assert functionTimedOut.timedOutArgs == (5, 19) , 'Expected args to equal (5, 19)'
        assert functionTimedOut.timedOutKwargs == {} , 'Expected timedOutKwargs to equal {}'


    def test_instantiateExceptionNoArgs(self):

        gotException = False

        try:
            exc = FunctionTimedOut()
            msg = str(exc)
            msg2 = exc.getMsg()

        except Exception as _e:
            sys.stderr.write('Got unexpected exception in test_instantiateExceptionNoArgs with no arguments. %s  %s\n\n' %(str(type(_e)), str(_e)))
            gotException = True

        assert gotException is False, 'Expected to be able to create FunctionTimedOut exception without arguments.'

        gotException = False

        try:
            exc = FunctionTimedOut('test')
            msg = str(exc)
            msg2 = str(exc.getMsg())

        except Exception as _e:
            sys.stderr.write('Got unexpected exception in test_instantiateExceptionNoArgs with fixed message string. %s  %s\n\n' %(str(type(_e)), str(_e)))
            gotException = True

        assert gotException is False , 'Expected to be able to create a FunctionTimedOut exception with a fixed message.'

        # Other forms (providing the function name) are tested elsewhere.



if __name__ == '__main__':
    sys.exit(subprocess.Popen('GoodTests.py -n1 "%s" %s' %(sys.argv[0], ' '.join(['"%s"' %(arg.replace('"', '\\"'), ) for arg in sys.argv[1:]]) ), shell=True).wait())

# vim: set ts=4 sw=4 expandtab :
