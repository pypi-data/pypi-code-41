
from pytermcolor.ansiTermcolor import ansi_colored


import sys
import platform
import os


USE_ANSI = True
USE_WIN_COLOR = False

handle = sys.stdout
if not ('TERM' in os.environ and os.environ['TERM'] == 'ANSI'):
    if hasattr(handle, "isatty") and handle.isatty():
        if platform.system() == 'Windows':
            # print("Windows, ansi color disabled")
            from pytermcolor.winTermcolor import win_cprint
            USE_ANSI = False
            USE_WIN_COLOR = True
    else:
        # print("ansi color disabled")
        USE_ANSI = False


def colored(text, color=None, back_color=None, attrs=None):
    """
    Colorize text if ANSI terminal
    Available text and background colors:
        red, green, yellow, blue, magenta, cyan, white.
    :param text: the text to colorize
    :type text: str
    :param color: the color of the text
    :type color: str
    :param back_color: background color
    :type back_color: str
    :param attrs: text attribute
        Available attributes:
            bold, dark, underline, blink, reverse, concealed.
    :type attrs: str
    :return: the ansi colored text if ANSI terminal, the original text otherwise
    :rtype: str
    """
    if USE_ANSI:
        return ansi_colored(text,color,back_color,attrs)
    else:
        return text


def cprint(text, color=None, back_color=None, attrs=None, **kwargs):
    """
    Print colorize text.

    It accepts arguments of print function.
    """
    if USE_ANSI:
        print((colored(text, color, back_color, attrs)), **kwargs)
    elif USE_WIN_COLOR:
        win_cprint(text, color, back_color)
    else:
        print(text)


if __name__ == '__main__':
    print('Current terminal type: %s' % os.getenv('TERM'))
    print('Test basic colors:')
    cprint('Grey color', 'grey')
    cprint('Red color', 'red')
    cprint('Green color', 'green')
    cprint('Yellow color', 'yellow')
    cprint('Blue color', 'blue')
    cprint('Magenta color', 'magenta')
    cprint('Cyan color', 'cyan')
    cprint('White color', 'white')
    print(('-' * 78))

    print('Test highlights:')
    cprint('On grey color', back_color='grey')
    cprint('On red color', back_color='red')
    cprint('On green color', back_color='green')
    cprint('On yellow color', back_color='yellow')
    cprint('On blue color', back_color='blue')
    cprint('On magenta color', back_color='magenta')
    cprint('On cyan color', back_color='cyan')
    cprint('On white color', color='grey', back_color='white')
    print('-' * 78)

    print('Test attributes:')
    cprint('Bold grey color', 'grey', attrs=['bold'])
    cprint('Dark red color', 'red', attrs=['dark'])
    cprint('Underline green color', 'green', attrs=['underline'])
    cprint('Blink yellow color', 'yellow', attrs=['blink'])
    cprint('Reversed blue color', 'blue', attrs=['reverse'])
    cprint('Concealed Magenta color', 'magenta', attrs=['concealed'])
    cprint('Bold underline reverse cyan color', 'cyan',
            attrs=['bold', 'underline', 'reverse'])
    cprint('Dark blink concealed white color', 'white',
            attrs=['dark', 'blink', 'concealed'])
    print(('-' * 78))

    print('Test mixing:')
    cprint('Underline red on grey color', 'red', 'grey',
            ['underline'])
    cprint('Reversed green on red color', 'green', 'red', ['reverse'])