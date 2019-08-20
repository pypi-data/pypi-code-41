
import shutil
import sys
from warnings import warn
from colorama import init, deinit
from colorama import Fore, Style

from pyux.errors import ColorValueError
from pyux.errors import StyleValueError
from pyux.__utils__ import _build_iterable


class Wheel:
    """Print a wheel turning at the same speed as iterations.

    This class decorates an iterable in a for statement by printing a turning wheel
    and the iteration index at each step.

    :param iterable: default ``None`` : an iterable, or an integer for
        standard ``range(n)`` values
    :type iterable: iterable or int
    :param print_value: default ``False`` : print the iteration value instead of
        the iteration index next to the wheel
    :type print_value: bool
    
    ``Wheel`` can also be used manually (without iterable), which is useful if you
    need to print messages different than the iteration value or index. It is compatible
    with generators, which makes it a good indicator that the code is still running
    when you do not know the total number of iterations beforehand.
    
    :raise: ``TypeError`` if ``iterable`` is not an iterable
    
    :Example:
    
    >>> for _ in Wheel(['a', 'b', 'c', 'd']):    # print the index at each step next to the weel
    >>> for _ in Wheel(5):                       # same behaviour than previous
    >>> for letter in Wheel(['a', 'b', 'c', 'd'], print_value = True):
    >>>     # this whill print the iteration value (letters)
    >>>     # rather than the iteration index
    """
    def __init__(self, iterable = None, print_value: bool = False):
        self.print_value = print_value
        self.iterable = _build_iterable(iterable)
        self.last_message = None
        
    def __iter__(self):
        self.n = 0
        for element in self.iterable:
            yield element
            if self.print_value:
                self.print(step = self.n, message = element)
                self.last_message = element
            else:
                self.print(step = self.n)
                self.last_message = self.n + 1
            self.n += 1
        self.close(message = self.last_message)
        
    @staticmethod
    def print(step: int, message: str = None) -> None:
        """Print the wheel for a given step and message."""
        message = step if message is None else message
        if step % 4 == 0:
            sys.stdout.write('\r - | %s' % message)
            sys.stdout.flush()
        elif step % 4 == 1:
            sys.stdout.write('\r \\ | %s' % message)
            sys.stdout.flush()
        elif step % 4 == 2:
            sys.stdout.write('\r | | %s' % message)
            sys.stdout.flush()
        else:
            sys.stdout.write('\r / | %s' % message)
            sys.stdout.flush()
        return
    
    def close(self, message: str = None) -> None:
        """Print the wheel for the last iteration then flush console.
        
        This method makes the last printed value equal to the
        number of iterations. If a message is provided, it is printed
        instead of the former.
        
        :param message: default ``None`` : message to print next to the wheel
        :type message: str
        
        This method is automatically called when the wheel is used as decorator of
        an iterable in a for statement.
        
        When ``close`` is called with no iterable given as argument at class
        instanciation, it will print ``0`` since a missing iterable as
        argument is internally seen as an iterable of length zero.
        A workaround is to use ``close(message = '')`` if you want the last printed
        value to stay, or any other message if you want it to be replaced by an
        closing message.
        
        :Example:
        
        >>> wheel = Wheel(iterable = 'A string iterable')
        >>> wheel.close()
        >>> wheel.close(message = 'Overriding length of iterable')
        """
        try:
            last_n = len(self.iterable)
        except TypeError:
            last_n = self.n
        if message is not None:
            self.print(step = last_n, message = message)
        else:
            self.print(step = last_n)
        sys.stdout.write('\n')
        sys.stdout.flush()
        return


def wordy(message: str = '.', catch: bool = False, failure_message: str = '!', colors: tuple = None):
    """Print a message at each function call.

    A decorator to print a message at each function call with ``sys.stdout``.
    Exceptions can be catch and returned as the function's result, or raised.
    If an exception is catch, a specific message can be printed.

    :param message: default ``'.'`` : message to print *after* function call
    :type message: str
    :param catch: default ``False`` : catch an exception from the decorated
        function rather than raising it
    :type catch: bool
    :param failure_message: default ``'!'`` : message to print if an exception
        is catch during function call
    :type failure_message: str
    :param colors: default ``None`` : a tuple of one or two colors for the
        the printed messages
    :type colors: tuple

    :return: a function decorated with a printed message after execution

    Both ``message`` and ``failure_message`` can be printed (internally using
    ``ColourPen``). If ``colors`` is not specified, standard terminal text color
    will be used. When ``catch = True``, if specified, the ``colors`` tuple must
    be of length two.
    
    :Example:

    >>> @wordy()
    >>> def one():
    >>>     return 1
    >>> [one() for _ in range(10)]
    """
    if catch and colors is None:
        colors = ('RESET', 'RESET')
    elif not catch and colors is None:
        colors = tuple(['RESET'])
    
    if catch and len(colors) != 2:
        raise ValueError('`colors` must be length-two when catch = True, was %s' % repr(colors))
    elif not catch and len(colors) > 1:
        warn('`colors` was more than length one, only first value will be used')
    elif not catch and len(colors) < 1:
        raise ValueError('`colors` must be length-one, was %s ' % repr(colors))
    pen = ColourPen()
    
    def decorated(fun):
        def wrapper(*args, **kwargs):
            try:
                response = fun(*args, **kwargs)
                pen.write(message = message, color = colors[0], reset = True)
            except Exception as e:
                if catch:
                    response = e
                    pen.write(message = failure_message, color = colors[1], reset = True)
                else:
                    raise e
            return response
        
        return wrapper
    
    return decorated


class Speak:
    """Print a message after each iteration or every *n* iterations.
    
    This class decorates an iterable in a for statement by printing a message
    either after each iteration, or after a given amount of iterations.

    :param iterable: default ``None`` : an iterable, or an integer for
        standard ``range(n)`` values
    :type iterable: iterable or int
    :param every: default ``1`` : frequency of printing messages
    :type every: int
    :param message: default ``'.'`` : message to print
    :type message: str
    :param newline: default ``False`` : flushes a new line after printing
    :type newline: bool
    
    Printing is done with ``sys.stdout``, so that the default behavior is to
    keep the console cursor on the current line. To print the message on a
    newline at each step, use ``newline = True``.

    :Example:

    >>> for _ in Speak(50, every = 5, message = '*'):
    >>>     pass
    """
    def __init__(self, iterable = None, every: int = 1, message: str = '.', newline: bool = False):
        assert isinstance(every, int) and every > 0, "`every` must be a positive integer"
        self.message = message
        self.every = every
        self.newline = newline
        self.iterable = _build_iterable(iterable)
    
    def __iter__(self):
        self.n = 0
        for element in self.iterable:
            yield element
            if self.n % self.every == 0:
                sys.stdout.write(self.message)
                if self.newline:
                    sys.stdout.write('\n')
                sys.stdout.flush()
            self.n += 1
        self.close()
    
    def close(self) -> None:
        """Flush a new line when ``self.newline = False``.

        This method is automatically called when the for loop finishes, so
        that the console cursor starts a new line when the loop is over.

        :return: ``None``
        """
        if not self.newline:
            sys.stdout.write('\n')
            sys.stdout.flush()
        return


class ProgressBar:
    """Print a progress bar with progression percentage and number of iterations.

    ``ProgressBar`` is meant to be used as a decorator in a for statement :
    for each iteration, it prints the percentage of progress, the number of iterations
    against the total number of iterations to do, and a progress bar.
    
    :param iterable: default ``None`` : an iterable, or an integer for
        standard ``range(n)`` values
    :type iterable: iterable or int
    :param ascii_only: Use ascii character ``=`` to print the bar
    :type ascii_only: bool
    
    A progress bar can also be created manually if you want to call it outside
    of a for statement.
    However it still *needs* an iterable to know the total number of
    iterations. This means it cannot be used with generators.
    
    A workaround if you really want to use it even if you don't know how long
    the iteration will last, give an approximation as an integer to the ``iterable``
    argument. This might cause unwanted behaviour in console, especially if your
    approximation is too short.
    
    :raise: ``TypeError`` if ``iterable`` is not an iterable
    
    :Example:
    
    >>> from time import sleep
    >>> for _ in ProgressBar(3000, ascii_only = True):
    >>>     sleep(0.001)
    """
    def __init__(self, iterable = None, ascii_only: bool = False):
        self.iterable = _build_iterable(iterable)
        self.bar_char = '=' if ascii_only else '\u2588'
        
        self.real_width = len(self.iterable)
        give_space = 4 + 3 + len(str(self.real_width))*2 + 1 + 3 + 2    # xxx% | step/total_step | ===... |
        self.bar_width = shutil.get_terminal_size()[0] - give_space
        self.real_step = self.real_width / self.bar_width
        
        self.current_console_step = 0
        
    def __repr__(self):
        return "ProgressBar(real_width = %d)" % self.real_width
        
    def __iter__(self):
        self.n = 0
        for element in self.iterable:
            yield element
            self.print(step = self.n)
            self.n += 1
        self.close()
        
    def print(self, step: int) -> None:
        """Print the progress bar for the current iteration."""
        if step >= self.current_console_step * self.real_step:
            str_values = (
                step * 100 / self.real_width,
                str(step).zfill(len(str(self.real_width))),
                self.real_width,
                self.bar_char * self.current_console_step
            )
            sys.stdout.write('\r%d%% | %s/%d | %s' % str_values)
            sys.stdout.flush()
            self.current_console_step += 1
        return
    
    def close(self) -> None:
        """Print the bar with 100% completion.

        When the for loop has finished, this prints a last progress bar with 100%
        completion. This method is automatically called at the end of a for loop
        when ``ProgressBar`` decorates a for statement.
        
        Without closing, the iteration index would end just before reaching 100%
        due to index starting from zero rather than one.
        
        :Example:
        
        >>> ProgressBar(iterable = 'A string iterable').close()
        """
        sys.stdout.write('\r100%% | %d/%d | ' % (self.real_width, self.real_width))
        sys.stdout.write(self.bar_char * self.bar_width + ' |\n')
        sys.stdout.flush()
        return


class ColourPen:
    """Write colored and styled messages in console.
    
    Only one pen instance is needed to print texts with different styles.
    By default, styles and colours remain the same until changed or reset,
    allowing to write successive prints with the same format,
    without having to specify format at each call.

    Available colors are :

    - black
    - red
    - green
    - yellow
    - blue
    - magenta
    - cyan
    - white
    - reset (to reset color to default)

    Available styles are :

    - dim (thin)
    - normal
    - bright
    - reset_all (to reset both color and style)

    Any other value will raise a ``ColorValueError`` or a ``StyleValueError``.

    :Example:
    
    >>> pen = ColourPen()
    >>> pen.write('A blue and bright message', color = 'cyan', style = 'bright')
    >>> pen.write('Still a blue message', reset = True, newline = True)
    >>> pen.write('That message is back to normal')
    >>> pen.close()
    """
    __colors__ = [
        'BLACK',
        'RED',
        'GREEN',
        'YELLOW',
        'BLUE',
        'MAGENTA',
        'CYAN',
        'WHITE',
        'RESET'
    ]
    __styles__ = [
        'DIM',
        'NORMAL',
        'BRIGHT',
        'RESET_ALL'
    ]
    
    def __init__(self):
        init()
        self.message = ''
    
    def __repr__(self):
        return "ColourPen(message = %s)" % self.message
    
    def _colourise(self, color = 'RESET'):
        """Colourise the message with the given color.

        Color argument is checked against possible values and
        is case insensitive. Can be combined with style.
        
        :param color: default ``'RESET'`` : color to use. Giving ``None`` does
           nothing, which is, returns the message with the color from the
           previous call to ``write()``
        :type color: str
        
        :raises: ``ColorValueError``
        """
        try:
            color = color.upper()
        except AttributeError:
            pass
        try:
            color_prefix = getattr(Fore, color)
        except TypeError:
            color_prefix = ''
        except AttributeError:
            raise ColorValueError("color must be one of %s" % repr(self.__colors__))
        self.message = color_prefix + self.message
        return self
    
    def _style(self, style = 'RESET_ALL'):
        """Style the message with the given style.

        Style argument is checked against possible values and
        is case insensitive. Can be combined with colourise.
        
        :param style: default ``'RESET_ALL'`` : style to use. Giving ``None`` does
        nothing, which is, returns the message with the style from the
        previous call to ``write()``
        :type style: str
        
        :raises: ``StyleValueError``
        """
        try:
            style = style.upper()
        except AttributeError:
            pass
        try:
            style_prefix = getattr(Style, style)
        except TypeError:
            style_prefix = ''
        except AttributeError:
            raise StyleValueError("style must be one of %s" % repr(self.__styles__))
        self.message = style_prefix + self.message
        return self

    def write(self, message: str = '',
              color: str = None, style: str = None,
              flush: bool = True, newline: bool = False, reset: bool = False):
        """Write a colored and styled message.
        
        The method returns ``self`` so that calls to the method can be chained
        from a single instance.
        
        :param message: default ``''`` : the message to write
        :type message: str
        :param color: default ``None`` : the colour to use, checked against possible values
        :type color: str
        :param style: default ``None`` : the style to use, checked against possible values
        :type style: str
        :param flush: default ``True`` : flush the message to the console
        :type flush: bool
        :param newline: default ``False`` : insert a new line after writing the message
        :type newline: bool
        :param reset: default ``False`` : reset style and colour after writing the message
        :type reset: bool
        
        The default behavior is to pass on current style to subsequent calls, so you
        only need to style and colour once if you want to keep the same format
        for following messages. This is accomplished through ``None`` values given
        for the ``color`` and/or ``style`` arguments, which means that giving
        ``None`` does not ignore style and color !
        
        To remove style for the message to print, use ``style = 'RESET_ALL'``.
        To remove style *after* printing the styled message, use ``reset = True``.
        
        Message is printed with ``sys.stdout.write()`` rather than ``print()``,
        allowing precise control over where to print in the console.
        The default behavior is to flush at each print and to keep the console
        cursor where it is.
        
        You can decide to "write" several messages and flush them all at once,
        and you can add a newline after a message to get the equivalent of a
        ``print()`` statement.
        
        :return: ``self``
        :raises: ``ColorValueError``, ``StyleValueError``

        :Example:
        
        >>> pen = ColourPen()
        >>> pen.write('Hello... ', color = 'cyan').write('Goodbye !', reset = True, newline = True)
        """
        self.message = message
        self._colourise(color = color)\
            ._style(style = style)
        sys.stdout.write(self.message)
        
        if reset:
            self.write(message = '', style = 'RESET_ALL', reset = False, newline = newline)
            return self
        if newline:
            self.write(message = '\n', newline = False, reset = reset)
            return self
        if flush:
            sys.stdout.flush()
        return self
        
    def close(self) -> None:
        """Reset all styles and close ``colorama`` util.
        
        The method flushes an empty message with reset styles and a new line.
        Closing make the ``sys.stdout`` go back to normal : styling and colouring
        will not be recognised after it.
        """
        self.write(message = '', flush = True, reset = True, newline = True)
        deinit()
        return
