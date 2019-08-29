class deprint:
    """
    Print fancy terminal output.
    Supported on all ANSI/VT100 terminal emulators.

    maintainer: Wattanit Hotrakool (@rorasa)
    """

    def __init__(self):
        self.fg_colour = {
            "black": "\033[30m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "light_grey": "\033[37m",
            "dark_grey": "\033[90m",
            "light_red": "\033[91m",
            "light_green": "\033[92m",
            "light_yellow": "\033[93m",
            "light_blue": "\033[94m",
            "light_magenta": "\033[95m",
            "light_cyan": "\033[96m",
            "white": "\033[97m",
            "default": "\033[39m",
            "reset": "\033[39m" 
        }

        self.bg_colour = {
            "black": "\033[40m",
            "red": "\033[41m",
            "green": "\033[42m",
            "yellow": "\033[43m",
            "blue": "\033[44m",
            "magenta": "\033[45m",
            "cyan": "\033[46m",
            "light_grey": "\033[47m",
            "dark_grey": "\033[100m",
            "light_red": "\033[101m",
            "light_green": "\033[102m",
            "light_yellow": "\033[103m",
            "light_blue": "\033[104m",
            "light_magenta": "\033[105m",
            "light_cyan": "\033[106m",
            "white": "\033[107m",
            "default": "\033[49m",
            "reset": "\033[49m" 
        }

        self.text_style = {
            "bold": "\033[1m",
            "dim": "\033[2m",
            "underlined": "\033[4m",
            "blink": "\033[5m",
            "inverse": "\033[7m",
            "hidden": "\033[8m",
            "default": "\033[0m",
            "reset": "\033[0m"
        }

        self.persistent = False
        self.oneliner = False

    def clear(self):
        print("\033[H\033[J", end = '')
        return self

    def emptylines(self, num=1):
        print("".join(["\n" for i in range(0, num)]), end = '')
        return self       

    def reset(self):
        self.setColour('reset')
        self.setBackground('reset')
        self.setStyle('reset')
        self.persistent = False
        self.oneliner = False
        return self

    def print(self, text):
        if self.oneliner:
            print(text, end = '')
        else:
            print(text)

        if not self.persistent:
            self.reset()

    def setColour(self, colour):
        self.colour(colour)
        self.persistent = True

    def setBackground(self, colour):
        self.bg(colour)
        self.persistent = True

    def setStyle(self, style):
        self.style(style)
        self.persistent = True

    def colour(self, colour):
        self.persistent = False
        if str(colour).isdigit():
            print("\033[38;5;{}m".format(colour), end = '')
        else:
            print(self.fg_colour[colour], end = '')
        return self

    def bg(self, colour):
        self.persistent = False
        if str(colour).isdigit():
            print("\033[48;5;{}m".format(colour), end = '')
        else:
            print(self.bg_colour[colour], end = '')
        return self 

    def style(self, style):
        self.persistent = False
        print(self.text_style[style], end = '')
        return self

    def hold(self):
        self.persistent = False
        self.oneliner = True
        return self

if __name__ == '__main__':
    dp = deprint()

    dp.clear()
    dp.style('bold').print("Deprint - declarative Python fancy print statement")
    dp.emptylines()

    dp.print("Declarative style")
    dp.print("dp.colour('blue').print('blue text'): ")
    dp.colour('blue').print('blue text')
    dp.print("dp.colour('red').style('underlined').print('red underlined text'): ")
    dp.colour('red').style('underlined').print('red underlined text')
    dp.print("dp.colour('white').bg('cyan').style('bold').print('white bold text on cyan background'): ")
    dp.colour('white').bg('cyan').style('bold').print('white bold text on cyan background')

    dp.emptylines()
    dp.print("Persistent style")
    dp.print("dp.setColour('blue')")
    dp.print("dp.print('blue text')")
    dp.setColour('blue')
    dp.print('blue text')
    print("normal print is also blue!")
    dp.reset()
    dp.print("dp.setColour('red')")
    dp.print("dp.setStyle('underlined')")
    dp.print("dp.print('red underlined text')")
    dp.setColour('red')
    dp.setStyle('underlined')
    dp.print('red underlined text')
    dp.reset()
