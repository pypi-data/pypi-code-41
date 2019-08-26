"""The base API of the Terminal and Cursors is simple, flexible,
and powerful, but as a consequence is somewhat tedious to work with,
especially when you're doing really simple things.

For beginners and simple applications I suggest using the ezmode interface,
which presents a more conventional 'put this text here' style of API."""
import time

import pyconsolegraphics


class EZMode:
    """Wrap one of these around a pyconsolegraphics Terminal initialized as
    you want it to use the easy-mode interface. For example:

    import pyconsolegraphics, pyconsolegraphics.ezmode
    term = pyconsolegraphics.Terminal( font = "Courier" )
    pyconsolegraphics.autodraw(term)
    gfx = pyconsolegraphics.ezmode.EZMode(term)

    gfx.center_line_at("Hello world!", 0, 0, offsetfrom = "center")
    """

    def __init__(self, term):
        self.terminal = term #type: pyconsolegraphics.Terminal

    def _cursor_predicate(self):
        """For internal use only. Return term.ezmodecursor, or create it if
        it does not exist."""
        try:
            return self.terminal.ezmodecursor
        except AttributeError:
            self.terminal.ezmodecursor = pyconsolegraphics.InputCursor(
                                                                self.terminal)
            return self.terminal.ezmodecursor

    _valid_pos_strings = {"topleft", "topcenter", "topright",
                          "centerleft", "center", "centerright",
                          "bottomleft", "bottomcenter", "bottomright"}

    def _process_pos(self, pos):
        """For internal use only. Turn a reference that may be to a position
        identifier or a position tuple into a position tuple, or raise
        ValueError if it is invalid. If it is None, return None."""

        if pos is None: return None

        if isinstance(pos, str):
            if pos in self._valid_pos_strings:
                pos = getattr(self.terminal, pos)
            else:
                raise ValueError("{0} is not a valid position identifier."
                                 .format(pos))

        else:
            if 0 > pos[0] > self.terminal.width - 1 or\
                    0 > pos[1] > self.terminal.height:
                raise ValueError("Position {0} is off the edges of the terminal."
                                 .format(pos))

        #Need to splat it otherwise Pos.__new__ will think we want that tuple to be the x value of the new pos...
        return pyconsolegraphics.Pos(*pos)

    def put_cursor(self, pos):
        """Put the cursor at the given position.

        Pos is either a 2-tuple of cartesian coordinates, x being from 0 to
        width - 1, and y being from 0 to height - 1, or a string.

        Valid pos strings are:

        topleft
        topcenter
        topright
        centerleft
        center
        centerright
        bottomleft
        bottomcenter
        bottomright
        """
        cursor = self._cursor_predicate()

        cursor.pos = self._process_pos(pos)

    def move_cursor(self, move):
        """Add the given 2-tuple of coordinates to the cursor's position."""
        cursor = self._cursor_predicate()

        x, y = cursor.pos
        dx, dy = move
        cursor.pos = x + dx, y + dy

    def get_cursor_pos(self):
        """Return the current position of the cursor as a 2-tuple of
        coordinates."""
        cursor = self._cursor_predicate()
        return cursor.pos

    def put_line(self, theline, fgcolor=None, bgcolor=None):
        """Put the given text at the cursor position. If included, it will
        be drawn with the given foreground (text) and background (behind the
        text) color; otherwise it will be locked to the terminal colors."""
        cursor=self._cursor_predicate()

        oldfgcolor, oldbgcolor         = cursor.fgcolor, cursor.bgcolor
        cursor.fgcolor, cursor.bgcolor = fgcolor, bgcolor

        for thechar in str(theline):
            cursor.smart_writechar(thechar)

        cursor.fgcolor, cursor.bgcolor = oldfgcolor, oldbgcolor

    def write_line(self, theline, fgcolor=None, bgcolor=None):
        r"""Write the given text at the cursor position and start a new line.
        Equivalent to put_line(theline + "\n").
        
        If included, the line will be drawn with the given foreground (text) 
        and  background (behind the text) color; otherwise it will be locked to 
        the terminal colors."""
        self.put_line(str(theline) + "\n")

    def put_line_at(self, theline, pos, offsetfrom=(0,0),
                    fgcolor=None, bgcolor=None, allow_wrap=True,
                    error_if_out_of_bounds = False):
        """Write the given text at the given position. Specifically,
        the position is that of the first character.

        pos and offsetfrom can be any value that move_cursor will accept; a
        position tuple or a position identifier string. Pos is the position
        relative to offsetfrom that the text will begin.

        For example:

        put_line_at("spam", "center")

        will put "spam" so that the 's' is at the center of the screen.

        put_line_at("ham", (-2, 0), offsetfrom="center")

        will put 'foo' on the terminal so that the 'm' is at the center of the
        screen.

        You can also do this:

        paragraphpos = (5, random.randint(1,5))
        put_line_at("line1", (0, 0), offsetfrom=paragraphpos)
        put_line_at("line2", (0, 1), offsetfrom=paragraphpos)

        That will make it so that wherever paragraphpos actually is,
        'line1' will always begin there, and 'line2' will begin on the next
        line.

        If offsetfrom is omitted, the pos will be taken from the upper left
        corner of the terminal (coordinates (0, 0)) as usual.

        If allow_wrap is set to False, the text will not be allowed to wrap
        around to the next line if it goes off the right edge of the
        terminal; instead it'll simply not be printed.

        fgcolor and bgcolor work just like they do with write_line; see its
        documentation.
        """
        o = self._process_pos(offsetfrom)
        d = self._process_pos(pos)
        abspos = o + d

        if 0 > abspos[0] > self.terminal.width or\
           0 > abspos[1] > self.terminal.height:
            raise ValueError(
                "Effective pos {0} ({1} + {2}) is off the edge of the "
                "terminal.".format( abspos, offsetfrom, pos))

        tempcursor=pyconsolegraphics.Cursor(self.terminal, abspos,
                        fgcolor=fgcolor, bgcolor=bgcolor, allow_wrap=allow_wrap)


        try:
            for thechar in theline:
                tempcursor.smart_writechar(thechar)

        except pyconsolegraphics.CursorOverflowError:
            #If putting the rest of the string on screen would push the
            #cursor out of bounds... then just don't, unless the caller has
            #specifically asked to be alerted if that happens.
            if error_if_out_of_bounds:
                raise

        finally:
            self.terminal.cursors.remove(tempcursor)


    def center_line_at(self, theline, pos, offsetfrom = (0,0),
                       fgcolor=None, bgcolor=None, allow_wrap=True,
                       error_if_out_of_bounds=False):
        """Just like .put_line_at, but offsets the beginning of the line left by
        len(theline) // 2, effectively centering it (or putting it one character
        left of center if it's an even number of characters) on the given
        position instead of beginning it there.

        If there's characters that would go off the left end of the screen,
        they'll be omitted.

        i.e. if you center "my super long string" at (0,1), only "long string"
        will be printed, with the 'l' being at (0,0)."""

        offsetfrom = self._process_pos(offsetfrom)
        ox = offsetfrom[0]

        x, y = self._process_pos(pos)
        x -= len(theline) // 2

        #Gotta check if the beginning would go off the left bound...
        if x + ox < 0:
            #And if so, just cut off the part that's causing the problem.
            overage = -(x + ox)
            theline = theline[overage : ]
            x += overage


        self.put_line_at(theline, (x, y), offsetfrom=offsetfrom,
                         fgcolor=fgcolor, bgcolor=bgcolor,
                         allow_wrap=allow_wrap,
                         error_if_out_of_bounds=error_if_out_of_bounds)

    def get_line(self, prompt="", fgcolor=None, bgcolor=None, promptpos = None, offsetfrom = (0,0), allow_wrap=True):
        """Prompt the user for text input, printing the prompt first if
        provided and then allowing the user to enter text, both at the
        cursor position (the entry field coming immediately after the
        prompt.)"""
        cursor=self._cursor_predicate()

        promptpos = self._process_pos(promptpos)

        if promptpos is None:
            self.put_line(prompt, fgcolor, bgcolor)
        else:
            self.put_line_at(prompt, promptpos, offsetfrom, fgcolor, bgcolor, allow_wrap)
            self.put_cursor(promptpos)
            prevwrap, cursor.allow_wrap = cursor.allow_wrap, True
            cursor.advance(len(prompt))
            cursor.allow_wrap = prevwrap
        self.update()

        cursor.input_line_mode=True
        cursor.allow_wrap=allow_wrap
        cursor.fgcolor, cursor.bgcolor = fgcolor, bgcolor


        while True:
            try:
                return cursor.get_line().strip("\n")
                break
            except pyconsolegraphics.InputAlreadyActiveError:
                time.sleep(0.05)

    def blank(self):
        """Call the terminal's .blank() method, clearing all characters and
        colors from it."""
        self.terminal.blank()

    def wait(self, fps = 30):
        """Block until the user presses a key or mouse button."""
        #Wait for any keys that might already be down to be cleared...
        while any((self.terminal.backend.get_keypresses(),
               self.terminal.backend.get_characters(),
               self.terminal.backend.get_left_click(),
               self.terminal.backend.get_right_click())):
            time.sleep(1 / fps)
            self.terminal.draw()

        while not any((self.terminal.backend.get_keypresses(),
               self.terminal.backend.get_characters(),
               self.terminal.backend.get_left_click(),
               self.terminal.backend.get_right_click())):
            time.sleep(1 / fps)
            self.terminal.draw()

    def sleep(self, secs, fps=30):
        """Return roughly secs seconds later, drawing the terminal at fps
        frames per second in the meantime."""
        starttime = time.monotonic()
        if time.monotonic() - starttime >= secs:
            return

        self.terminal.draw()
        #Backends often put "do this so we don't crash" stuff in
        # get_characters()
        self.terminal.backend.get_characters()
        time.sleep(1 / fps)

    def update(self):
        """Call self.terminal.process() followed by self.terminal.draw()."""
        self.terminal.process()
        self.terminal.draw()










