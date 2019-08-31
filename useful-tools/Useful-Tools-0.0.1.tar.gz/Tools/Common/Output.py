"""
Hello from Tools/Common/Output.py

Functions:
    PersonalizedOutput
        Personalized display texts.
    Demo
        This function is a demo of all functions and classes in this module.
"""
DEFAULT = 0
HIGHLIGHT = 1
UNDERLINE = 4
TWINKLE = 5
REVERSE = 7
HIDE = 8
FG_BLACK = 30
FG_RED = 31
FG_GREEN = 32
FG_YELLOW = 33
FG_BLUE = 34
FG_PURPLE_RED = 35
FG_CYAN = 36
FG_WHITE = 37
BG_BLACK = 40
BG_RED = 41
BG_GREEN = 42
BG_YELLOW = 43
BG_BLUE = 44
BG_PURPLE_RED = 45
BG_CYAN = 46
BG_WHITE = 47


def PersonalizedOutput(content, display_mode=DEFAULT, fg=FG_BLACK, bg=BG_WHITE):
    """
    Personalized display texts.
    It only works in Pycharm.

    Parameters
    ----------
    content: str
        It's the content to be displayed.
    display_mode: int
        This is one of them:
            DEFAULT
            HIGHLIGHT
            UNDERLINE
            TWINKLE
            REVERSE
            HIDE
    fg: int
        This is one of them:
            FG_BLACK
            FG_RED
            FG_GREEN
            FG_YELLOW
            FG_BLUE
            FG_PURPLE_RED
            FG_CYAN
            FG_WHITE
    bg: int
        This is one of them:
            BG_BLACK
            BG_RED
            BG_GREEN
            BG_YELLOW
            BG_BLUE
            BG_PURPLE_RED
            BG_CYAN
            BG_WHITE
    """
    assert display_mode in [0, 1, 4, 5, 7, 8]
    assert fg in [i for i in range(30, 38)]
    assert bg in [i for i in range(40, 48)]
    print(f"\033[{display_mode};{fg};{bg}m{content}\033[0m")


def Demo():
    """This function is a demo of all functions and classes in this module."""
    PersonalizedOutput("Hi", HIGHLIGHT, FG_CYAN, BG_PURPLE_RED)
    PersonalizedOutput("Hi", REVERSE, FG_GREEN, BG_RED)
    PersonalizedOutput("Hi", UNDERLINE, FG_BLUE, BG_YELLOW)


if __name__ == '__main__':
    Demo()
