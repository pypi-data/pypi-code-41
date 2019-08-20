import csv
import timeit
import sys
from os.path import exists as path_exists
from functools import partial

from time import sleep
from pyux.errors import DelayTypeError
from pyux.errors import NoDurationsError
from pyux.__utils__ import _build_iterable


class Timer:
    """Print a descending timer for a given delay.

    A message can be printed next to the timer.
    The class can be used on the iterable of a for
    loop to wait the same amount of time at each iteration.
    
    :param iterable: default ``None`` : *for decorator use only* : an iterable,
        or an integer for standard ``range(n)`` values
    :type iterable: iterable or int
    :param delay: default ``None`` : time to wait, must be provided. Default
        to seconds, can be milliseconds with ``ms = True``
    :type delay: int
    :param message: default ``''`` : message to print when used manually
    :type message: str
    :param ms: default ``False`` : use a delay in milliseconds rather than seconds
    :type ms: bool
    :param pattern: default ``''`` : *for decorator use only* : prefix to print before iterated value when
        used as a loop decorator and ``print_value = False``
    :type pattern: str
    :param print_value: default ``False`` : *for decorator use only* : Print running value of the iterable
        when used to decorate a loop instead of iteration index
    :type print_value: bool
    :param overwrite: default ``False`` : do not print a new line when the timer
        is finished (useful almost only when used within a loop)
    :type overwrite: bool
    
    When used within a for loop, the default behavior is to print the
    iteration index next to the timer. You can add a constant
    string prefix to it using the argument ``pattern`` (which
    is not used otherwise), or use ``print_value = True`` to
    print the running value of the iterable.
    
    Specifying a value for ``iterable`` while calling ``Timer()`` outside of a for
    statement will have no effect (except if you use the result in a for statement
    afterwards, obviously).
    
    :raises: ``DelayTypeError`` if no or wrong type delay is given
    
    :Example:
    
    >>> # One-shot usage
    >>> Timer(delay = 10, message = "Waiting for 10 seconds")
    >>> # Usage as a decorator
    >>> for index in Timer(3, delay = 3):
    >>>     pass
    """
    def __init__(self,  iterable = None, delay: int = None,
                 message: str = '', ms: bool = False,
                 pattern: str = '', print_value: bool = False,
                 overwrite: bool = False) -> None:
        self.delay = delay
        
        # Attributes for iteration only
        self._sleep_time = 1 / 1000 if ms else 1
        self._print_value = print_value
        self._pattern = pattern
        self.iterable = _build_iterable(iterable)
        
        # If iterable is generator, it doesn't have a len, and will be launched
        # with __iter__
        try:
            len(self.iterable)
        except TypeError:
            return
        # Launch only when self.iterable = [], otherwise it will be launched
        # with __iter__
        if len(self.iterable) == 0:
            self._launch(
                delay = delay,
                message = message,
                overwrite = overwrite
            )
        return
    
    def __iter__(self):
        self.n = 0
        for element in self.iterable:
            yield element
            message = element if self._print_value else '%s%d' % (self._pattern, self.n)
            self.n += 1
            self._launch(delay = self.delay, message = message, overwrite = True)
        print('')
        
    def _launch(self, delay, message, overwrite) -> None:
        """Launch the timer for the given delay."""
        try:
            values = range(delay)
        except TypeError:
            raise DelayTypeError('No or wrong type value provided for argument `delay`')
        for n in values:
            remaining_time = str(delay - n).zfill(len(str(delay)))
            self.print(time = remaining_time, message = message)
            sleep(self._sleep_time)
        self.close(message = message, overwrite = overwrite)
        return

    @staticmethod
    def print(time: str, message: str) -> None:
        """Print the counter for a given time, counter and message."""
        sys.stdout.write('\r%s | %s' % (time, message))
        sys.stdout.flush()
        return
    
    def close(self, message: str, overwrite: bool) -> None:
        """Print ``'0'`` when time has passed (last iteration is ``1``)."""
        self.print(time = '0', message = message)
        if not overwrite:
            sys.stdout.write('\n')
            sys.stdout.flush()
        return


def wait(delay: float, before: bool = True, timer: bool = False, **timer_args):
    """Wait a given delay before or after a function call.

    The function is used as a target function's decoration. With default values
    nothing is printed during pause, but a ``Timer`` can be printed instead.

    :param delay: time to wait (in seconds)
    :type delay: float
    :param before: default ``True`` : pause before function execution
    :type before: bool
    :param timer: default ``False`` : print a timer during pause
    :type timer: bool
    :param timer_args: keyword arguments for ``Timer`` when ``timer = True``
    :type timer_args: see ``Timer``
    
    :return: a function decorated with a timer

    :Example:

    >>> @wait(delay = 3)
    >>> def print_hello():
    >>>     print('hello')
    >>> print_hello()
    """
    def decorated(fun):
        def wrapper(*args, **kwargs):
            pause = partial(Timer, delay = delay, iterable = None, **timer_args) if timer else partial(sleep, delay)
            if before:
                pause()
            response = fun(*args, **kwargs)
            if not before:
                pause()
            return response
        return wrapper
    return decorated


class Chronos:
    """Time chunks of code in a script.
    
    The class works as a stopwatch during a race on track : after starting it,
    for each *lap*, a button is pushed that records time at this moment, using
    ``timeit.default_timer()``.
    
    :param iterable: default ``None`` : *for decorator use only* : an iterable,
        or an integer for standard ``range(n)`` values.
    :type iterable: iterable or int
    :param ms: default ``False`` : compute durations in milliseconds rather than seconds
    :type ms: bool
    :param console_print: default ``False`` : *for decorator use only* : print durations in tsv format
        in console when loop is finished
    :type console_print: bool
    :param pattern: default ``'iteration '`` : *for decorator use only* : pattern for naming laps, will be
        suffixed with the iteration number
    :type pattern: str
    :param write_tsv: default ``False`` : *for decorator use only* : write out tsv file end loop is finished
    :type write_tsv: bool
    :param run_name: default ``'default'`` : *for decorator use only* : name to give to execution for column Execution
    :type run_name: str
    :param path: default ``None`` : *for decorator use only* : full path to file to write
    :type path: str
    :param col_names: default ``None`` : *for decorator use only* : column names (length 3)
    :type col_names: tuple

    Recorded times do not have a meaning by themselves since they do not correspond
    to durations and depends on the previous recorded times. When you want to
    know duration of recorded laps, use ``compute_durations()``, which gives
    durations for each lap and total duration.
    
    Chronos can be used as a decorator in a for loop. In that case, it records
    duration for each iteration. Since you cannot get the object back, you can
    either print the values to console (in tsv format) or write out the values
    in a tsv file.
    
    Specifying an ``iterable`` argument while calling ``Chronos()`` outside of a for
    statement has no effect. In that case, you can still use it manually, as if
    you entered nothing for that argument.
    
    Results can be exported in a tsv file with ``write_tsv()``.
    
    :Example:
    
    >>> from time import sleep
    >>> chrono = Chronos()
    >>> sleep(2)
    >>> chrono.lap(name = 'lap 1')
    >>> sleep(5)
    >>> chrono.lap(name = 'lap 2')
    >>> chrono.compute_durations().durations
    >>> # In a for loop
    >>> for index in Chronos(10, console_print = True, write_tsv = False, ms = True):
    >>>     pass
    """
    def __init__(self, iterable = None, console_print: bool = False,
                 pattern: str = 'iteration ', write_tsv: bool = False,
                 run_name: str = 'default', path: str = None, col_names = None, ms: bool = False):
        self.lap_times = [timeit.default_timer()]
        self.lap_names = ['start']
        self.durations = {}
        self.results = None
        
        # Attributes for iteration only
        self._iterable = _build_iterable(iterable)
        self._print = console_print
        self._pattern = pattern
        self._path = path
        self._run_name = run_name
        self._write_tsv = write_tsv
        self._colnames = col_names
        self._ms = ms
        
    def __iter__(self):
        self.n = 0
        for element in self._iterable:
            yield element
            self.lap(name = '%s%d' % (self._pattern, self.n))
            self.n += 1
        self.compute_durations(ms = self._ms)
        if self._write_tsv:
            self.write_tsv(
                run_name = self._run_name,
                path = self._path,
                col_names = self._colnames
            )
        if self._print:
            print('\nStep\tDuration')
            for step, duration in self.durations.items():
                print('%s\t%d' % (step, duration))
    
    def __repr__(self):
        return 'Chronos(laps = %s)' % ', '.join(self.lap_names)
    
    def lap(self, name: str):
        """Record time for this lap; a name must be provided."""
        self.lap_names.append(name)
        self.lap_times.append(timeit.default_timer())
        return self
    
    def compute_durations(self, ms: bool = False):
        """Compute laps durations.

        Duration is the difference between two adjacent laps. Results
        are stored in ``self.durations``, in seconds by default. They can be stored
        in milliseconds. The total duration is also calculated.

        :param ms: express durations in milliseconds rather than seconds
        :type ms: bool

        :return: ``self``
        """
        for i in range(len(self.lap_names)):
            if i == 0:
                pass
            else:
                duration = self.lap_times[i] - self.lap_times[i - 1]
                if ms:
                    duration = round(duration * 1e3, 0)
                else:
                    duration = round(duration, 3)
                self.durations[self.lap_names[i]] = duration
        self.durations['total'] = sum(self.durations.values())
        return self
    
    def write_tsv(self, run_name: str, path: str, col_names: tuple = None):
        """Export durations in a tsv file.
        
        Write three columns, the first containing ``run_name`` : a string describing
        which execution the durations came from. This way you can append several
        execution times to the same file.
        
        Default values for column names are : Execution, Step, Duration (secs)
        
        :param run_name: name to give to execution for column Execution
        :type run_name: str
        :param path: full path to file to write
        :type path: str
        :param col_names: default ``None`` : column names of length 3
        :type col_names: tuple
        
        :return: ``self``
        """
        if len(self.durations) == 0:
            raise NoDurationsError('durations attribute is empty (have you compute_durations before ?')
        if col_names is None:
            col_names = ('Execution', 'Step', 'Duration (secs)')
        elif len(col_names) < 3 or len(col_names) > 3:
            raise ValueError('column names must be of length 3, was %s' % repr(col_names))
        table = [(run_name, step, str(time)) for step, time in self.durations.items()]
        
        file_exists = path_exists(path)
        with open(path, 'a') as out_table:
            tsv_writer = csv.writer(out_table, delimiter = '\t')
            if not file_exists:
                tsv_writer.writerow(col_names)
            for row in table:
                tsv_writer.writerow(row)
                
        return self
