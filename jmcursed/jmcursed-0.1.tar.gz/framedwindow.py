import curses


class FramedWindow:

    dimensions ={
        "h": 25,
        "w": 80,
        "x": 0,
        "y": 2
    }

    def __new__(cls):
        """ Create as a subgleton. """
        if not hasattr(cls, "instance"):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, **kwargs):
        """ Start curses, set window into screen, allow scroll """
        # Allow framing of window, h: height, w: width, x: offset from side of screen,
        # y: offset from top of screen
        if kwargs:
            for key, value in kwargs.items():
                if key in self.dimensions.keys():
                    self.dimensions[key] = value
        # load stuff
        self.screen, self.window =  self.start_buffer()
        ## flush the output buffer, ie show the output
        self.cprint("\n")
    
    def __del__(self):
        """ make entirely sure to deconstruct curses or echo will be off on terminal """
        self.screen.erase()
        curses.endwin()
        del self.window
        del self.screen
        print("Nuked.")



    def start_buffer(self):
        """ Start curses, in fancy color render mode, construct the window. Note the buffer is not flushed here."""
        screen = curses.initscr()
        curses.start_color()
        screen.scrollok(True)
        win = curses.newwin(
            self.dimensions["h"],
            self.dimensions["w"],
            self.dimensions["y"],
            self.dimensions["x"]
        )
        win.scrollok(True)
        return screen, win

    def decompile(self):
        """
        Destroy the window entirely, and call the curses deconstructor. IF not using this, you will echo response
        when typing in the terminal! It is very annoying. Make sure to use this.
        """
        self.window.clear()
        curses.endwin()

    def recompile_window(self):
        """ Redraw the window entirely, and put the cursor back at the spot where it was when it was first drawn."""
        self.window.clear()
        self.window.redrawwin()
        self.window.chgat(self.dimensions["y"] + 4, self.dimensions["x"] + 4)
        self.cprint("\n")

    def reload(self):
        """ Write what is in the output buffer. Must call border before and after to kee the border. """
        ## do border twice cus docker or sth
        self.window.border(0)
        self.window.refresh()
        self.window.border(0)

    def cprint(self,
               data: str,
               end: str = "\n",
               offset: int = 4,
               reload_on_end=True
               ):
        """ Print a string to the screen. Works like print()"""
        xo = " " * offset
        self.window.addstr(xo + data)
        self.window.addstr(end)
        self.reload()
        curses.napms(100)

    def getstr(self, 
                prompt: str = None,
                 offset: int = 4
                 ):
        """ Get a string from the user until \n. Like input()"""
        if prompt is None:
            self.cprint("", end="", offset=offset)
        else:
            self.cprint("{}".format(prompt), end="", offset=offset)
        x = self.window.getstr()
        return x.decode()

    def getch(self,
                prompt: str = None,
                offset: int = 0
                ):
        """ Recieve a single character of input, like getch """
        if prompt is not None:
            self.cprint(prompt, end="")
        x = self.window.getkey()
        return x

    def _get_starting(self):
        """ Get the present Y, X position of the cursor. """
        y, x = self.window.getyx()
        return y, x

    def get_keyinput(self, menudict=None):
        """ Get keypad UP/DOWN/LEFT/RIGHT key input
        Does not work btw.
        """
        if menudict is None:
            menudict = {
                "Do thing1": "thing1",
                "Do thing2": "thing2",
                "Do thing3": "thing3",
                "Exit": "exit"
            }

        mapped = {
            "KEY_UP": 'up',
            "KEY_DOWN": 'down',
            "KEY_LEFT": 'left',
            "KEY_RIGHT" : 'right'
        }
        numopts = len(menudict.keys())
        pos = 0
        y, x = self._get_starting()


        self.screen.keypad(True)
        k = self.screen.getkey()
        self.reload()
        if k in mapped.keys():
            self.cprint(mapped[k])
            if mapped[k] == "up":
                pos -= 1 if pos >= 1 else 0
            elif mapped[k] == "down":
                pos += 1 if pos < numopts else numopts
            elif mapped[k] == "left":
                x -= 1 if x >= 1 else 0
            elif mapped[k] == "right":
                x += 1 if x < len(menudict.values()) else len(menudict.values())
            self.cprint("{}  {} ".format(pos, x))
            return mapped[k]
        else:
            self.screen.keypad(False)
            return k

import time

