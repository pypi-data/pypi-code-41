"""UI helper classes based on ClickZone-s."""
import math

import pyconsolegraphics

class VisibleClickZone(pyconsolegraphics.ClickZone):
    """This is what you should generally be using to actually make UIs with
    Pyconsolegraphics. This is just a ClickZone except with facilities to
    draw itself to the screen and change color when it is highlighted."""

    def __init__(self, terminal, center, label,
                 fgcolor = None, bgcolor="gray25",
                 highlightfgcolor = None, highlightbgcolor = "gray",
                 cursor = None, width = None, height=1,
                 group="default", hotkey=""):
        if width is None:
            width = len(label)
        super().__init__(terminal, center, width, height, group)
        self.label = label
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.highlightbgcolor = highlightbgcolor
        self.highlightfgcolor = highlightfgcolor
        self.calculate_positions()

        self.need_to_draw = True

        if cursor:
            self.cursor = cursor
        else:
            self.cursor = pyconsolegraphics.Cursor(terminal, self.cursororigin,
                    fgcolor=fgcolor, bgcolor=bgcolor, cursorchar=None)

        if hotkey == "":
            candidatelist = list(self.label)
            candidatelist.reverse()
            takenhotkeys = {z.hotkey for z in self.manager.groups[group]}
            while candidatelist:
                hotkeycandidate = candidatelist.pop()
                if hotkeycandidate not in takenhotkeys:
                    self.hotkey=hotkeycandidate
                    break
            else:
                #If all of the characters in our label are already hotkeys,
                #there's nothing we can do; we'll just have to not have a
                # hotkey.
                self.hotkey=None
        else:
            self.hotkey=hotkey

    def __repr__(self):
        return "<{0} '{1}'>".format(type(self).__name__, self.label)

    def calculate_positions(self):
        """Recenter the label and rectangle origins; handy if you're
        subclassing VisibleClickZone and you expect the length of the label
        or the size and or position of the ClickZone to change."""
        center = self.center
        label = self.label
        width, height = self.width, self.height
        self.cursororigin = center[0] - (len(label) // 2), center[1]
        self.topleft = center[0] - (width // 2), center[1] - (height // 2)

    def on_draw(self, currently_highlighted):
        if not self.need_to_draw:
            return
        self.need_to_draw = False

        bg = self.highlightbgcolor if currently_highlighted else self.bgcolor
        fg = self.highlightfgcolor if currently_highlighted else self.fgcolor

        ox, oy = self.topleft
        realbg = pyconsolegraphics._color_name_conversion(bg)
        for x in range(ox, ox+self.width):
            for y in range(oy, oy+self.height):
                try:
                    self.terminal[x, y].bgcolor=realbg
                except IndexError:
                    #Bits of a clickzone being off-screen is okay, I guess...
                    pass

        self.cursor.pos = self.cursororigin
        self.cursor.bgcolor = bg #redundant
        self.cursor.fgcolor = fg
        for thechar in self.label:
            try:
                self.cursor.smart_writechar(thechar)
            except IndexError:
                #want to handle bits of the _label_ being offscreen gracefully too
                pass

    def on_highlight(self):
        self.need_to_draw=True
    def on_lose_highlight(self):
        self.need_to_draw=True
    def on_activate(self):
        self.need_to_draw=True
    def on_terminal_blank(self):
        self.need_to_draw=True

class TickBoxClickZone(VisibleClickZone):
    """A UI element specifically for on/off situations that appends a tickbox to
    the beginning of the button label."""
    def __init__(self, terminal, center, label, starton = False, fgcolor=None,
                 bgcolor="gray25",
                 highlightfgcolor = None, highlightbgcolor="gray",
                 cursor=None, width=None, height=1, group="default"):
        if width is None:
            width = len(label) + 2 #to account for a space and a tickbox
        super().__init__(terminal, center, label, fgcolor, bgcolor,
                         highlightfgcolor, highlightbgcolor,
                         cursor, width, height, group)
        self.toggle = starton

    def on_draw(self, currently_highlighted):
        bg = self.highlightbgcolor if currently_highlighted else self.bgcolor

        self.cursor.pos = self.topleft
        for x in range(self.height):
            for t in range(self.width):
                self.cursor.smart_writechar(" ")
            self.cursor.x = self.topleft[0]
            self.cursor.y += 1

        self.cursor.pos = self.cursororigin
        self.cursor.x -= 1
        self.cursor.bgcolor = bg
        tickandlabel = "{0} {1}".format("☑" if self.toggle else "☐", self.label)
        for thechar in tickandlabel:
            self.cursor.smart_writechar(thechar)

    def on_click(self):
        self.toggle = not self.toggle
        self.need_to_draw=True

class ToggleClickZone(VisibleClickZone):
    """A UI element specifically for on/off situations that has a different
    label when it is toggled on or off."""
    def __init__(self, terminal, center, onlabel, offlabel, starton = False,
                 fgcolor=None, bgcolor="gray25", highlightbgcolor="gray",
                 cursor=None, width=None, height=1, group="default"):
        if width is None:
            width = max(len(onlabel), len(offlabel))

        self.onlabel = onlabel
        self.offlabel = offlabel
        self.toggle = starton

        super().__init__(terminal, center, self.label, fgcolor, bgcolor,
                         highlightbgcolor, cursor, width, height, group)
        self.toggle = starton

    @property
    def label(self):
        return self.onlabel if self.toggle else self.offlabel
    @label.setter
    def label(self, x):
        return

    def on_click(self):
        self.toggle = not self.toggle
        self.need_to_draw=True

class SpinnerClickZone(VisibleClickZone):
    """A UI element that lets users select among the given options by
    pressing left and right arrow keys while the clickzone is highligted,
    or by clicking on it mutliple times to page through the given options.

    Give the list of labels as a list to the options parameter, then read the
    .selectedoption to see which element of that list is currently being
    displayed.
    """
    def __init__(self, terminal, center, options,
                 fgcolor=None, bgcolor="gray25",
                 highlightfgcolor=None, highlightbgcolor="gray",
                 cursor=None, width=None, height=1, group="default"):
        if width is None:
            width = max([len(str(x)) for x in options]) + 2
        self.options = options
        self.currentindex = 0

        super().__init__(terminal, center, self.label,
                         fgcolor, bgcolor,
                         highlightfgcolor, highlightbgcolor,
                         cursor, width, height, group, None)

    @property
    def label(self):
        return str(self.selectedoption)
    @label.setter
    def label(self, x):
        return

    def on_draw(self, currently_highlighted):
        if not self.need_to_draw: return
        #Clean up any spoor from a previous, longer label
        self.cursor.y = self.center[1]
        self.cursor.x = self.topleft[0]
        for t in range(self.width):
            self.cursor.writechar_raw(" ")

        super().on_draw(currently_highlighted)

        self.cursor.y = self.center[1]
        self.cursor.x = self.topleft[0]
        self.cursor.smart_writechar("←")
        self.cursor.x += self.width - 1
        self.cursor.smart_writechar("→")

    @property
    def selectedoption(self):
        return self.options[self.currentindex]

    def on_left_pressed(self):
        self.currentindex -= 1
        if self.currentindex < 0:
            self.currentindex = len(self.options) - 1
        self.calculate_positions()
        self.need_to_draw=True

    def on_right_pressed(self):
        self.currentindex += 1
        if self.currentindex >= len(self.options):
            self.currentindex = 0
        self.calculate_positions()
        self.need_to_draw = True

    def on_click(self):
        self.on_right_pressed()

class GroupSwitchingSpinnerClickZone(SpinnerClickZone):
    """Similar to a SpinnerClickZone, except designed to switch between
    groups of other ClickZone-s. Feed it a list of (Label,Group) pairs,
    and whenever the user presses left/right on it, it will deactivate the
    group it is currently on and activate the group previous/next in the list."""

    def __init__(self, terminal, center, label_group_pairs,
                 fgcolor=None, bgcolor="gray25",
                 highlightfgcolor=None, highlightbgcolor="gray",
                 cursor=None, width=None, height=1, group="default",
                 blank_occupied_cells=True):
        """Label_group_pairs is a list of 2-tuples of strings; first element
        of the tuple is the label you want the SpinnerClickZone to show while
        that group is active, the second is the actual group name that will
        be fed to activate_group().

        The spinner starts on the 0th group in the list, and activates that
        group as part of its initialization.

        blank_occupied_cells gets passed through to deactivate_group on the
        group that is being switched away from; if it is True the cells occupied
        by the deactivated clickzones will be cleared after deactivation, if it is
        'fgonly' only the fgcolor and character of those cells will be cleared.
        """

        options, self.groups = zip(*label_group_pairs)
        self.blank_occupied_cells=blank_occupied_cells

        super().__init__(terminal, center, options,
                         fgcolor, bgcolor,
                         highlightfgcolor, highlightbgcolor,
                         cursor, width, height, group)

        self.terminal.clickzonemanager.activate_group(self.groups[self.currentindex])

    def switch_groups_if_appropriate(self, prevgroup):
        newgroup=self.groups[self.currentindex]
        if newgroup != prevgroup:
            self.terminal.clickzonemanager.deactivate_group(prevgroup, self.blank_occupied_cells)
            self.terminal.clickzonemanager.activate_group(newgroup)

    def on_left_pressed(self):
        prevgroup = self.groups[self.currentindex]
        super().on_left_pressed()
        self.switch_groups_if_appropriate(prevgroup)

    def on_right_pressed(self):
        prevgroup = self.groups[self.currentindex]
        super().on_right_pressed()
        self.switch_groups_if_appropriate(prevgroup)


class IncrementDecrementClickZone(VisibleClickZone):
    """A clickzone specifically for numeric values within a certain range,
    allowing the user to press right to increase the value and left to
    decrease the value.

    Input float("inf") and float("-inf") for the ranges if you want unlimited
    range.

    Be aware that incrementing past the maximum sets the value to the
    maximum, even if the interval jumps over it. If you set max to 31,
    min to 0, and interval to 5, going all the way up would look like:
    0 5 10 15 20 25 30 31
    and going all the way back down would look like:
    31 26 21 16 11 6 1 0
    This might not be what you want; if not, make sure max and min are both
    multiples of interval!

    The label is a format string; {val} will be replaced with the value.

    Access the current value from the .value attribute."""

    def __init__(self, terminal, center,
                 initialvalue=0, increment=1,
                 minval=float("-inf"), maxval=float("inf"),
                 label = "{value}",
                 fgcolor=None, bgcolor="gray25",
                 highlightfgcolor=None, highlightbgcolor="gray",
                 cursor=None, width=None, height=1, group="default"):

        if width is None:
            if maxval == float("inf"):
                width = len(label.format(value=(increment * 10))) + 2
                width = max(6, width)
            else:
                width = len(label.format(value=maxval)) + 2

        self.value = initialvalue
        self.increment = increment
        self.minval = minval
        self.maxval = maxval
        self._label = label

        super().__init__(terminal, center, self.label,
                         fgcolor, bgcolor,
                         highlightfgcolor, highlightbgcolor,
                         cursor, width, height, group, None)


    @property
    def label(self):
        return self._label.format(value=self.value)
    @label.setter
    def label(self, x):
        pass

    def on_draw(self, currently_highlighted):
        if not self.need_to_draw: return

        #Clean up any spoor from a previous, longer label
        self.cursor.y = self.center[1]
        self.cursor.x = self.topleft[0]
        for t in range(self.width):
            self.cursor.writechar_raw(" ")

        super().on_draw(currently_highlighted)

        self.cursor.y = self.center[1]
        self.cursor.x = self.topleft[0]
        self.cursor.smart_writechar("-")
        self.cursor.x += self.width - 1
        self.cursor.smart_writechar("+")

    def on_left_pressed(self):
        self.value -= self.increment
        if self.value < self.minval:
            self.value = self.minval
        self.calculate_positions()
        self.need_to_draw = True

    def on_right_pressed(self):
        self.value += self.increment
        # We want the maximum value to be selectible even if the interval
        # jumps over it.
        if self.value > self.maxval:
            self.value = self.maxval
        self.calculate_positions()
        self.need_to_draw = True

    def on_click(self):
        if self.value == self.maxval:
            self.value = self.minval

        else:
            self.value += self.increment
            if self.value > self.maxval:
                self.value = self.maxval
        self.calculate_positions()
        self.need_to_draw = True

class LeftJustifiedVisibleClickZone(VisibleClickZone):
    """A VisibleClickZone except the first character of the label is on the
    leftmost character of the ClickZone rectangle (still centered
    vertically), as opposed to the label being centered at the center of the
    rectangle."""

    def calculate_positions(self):
        """Recenter the label and rectangle origins; handy if you're
        subclassing VisibleClickZone and you expect the length of the label
        or the size and or position of the ClickZone to change."""
        center = self.center
        label = self.label
        width, height = self.width, self.height
        self.cursororigin = center[0] - (width // 2), center[1]
        self.topleft = center[0] - (width // 2), center[1] - (height // 2)

class VerticalMenu:
    """An easy way to build a clickable list of options with ClickZones.
    Pass a dict mapping strings to callables to the constructor, and the
    VerticalMenu will create ClickZone-s in its own group that are labeled
    with the strings and when clicked call the callables.

    That dict should probably be an OrderedDict unless you don't care what
    order the buttons will be in."""

    def __init__(self, options, terminal, topcenter=None,
                 fgcolor=None, bgcolor=None,
                 highlightbgcolor = "lightgrey", highlightfgcolor="black",
                 group=None, left_justify=True):
        """Options is a dict mapping strings (labels of buttons) to callables
        (called when that button is clicked.) Group is the group you want the
        buttons to be in; leave it as None to generate an arbitrary group
        name.

        Options should probably be an OrderedDict unless you don't care what
        order the buttons will be in.

        If left_justify is True, the labels of the individual buttons will
        begin at their leftmost extent; if not, they will be centered.

        If group is left as None, a group name will be automatically generated.

        :type options dict[str,callable]"""

        if not group:
            group = repr(self)
        self.group = group

        if not topcenter:
            topcenter = terminal.topcenter


        width = max((len(x) for x in options.keys()))
        halfwidth = math.ceil(width / 2)

        self.zones = []

        nextx, nexty = topcenter
        CZClass = LeftJustifiedVisibleClickZone if left_justify else VisibleClickZone
        for label, func in options.items():
            nexty += 1
            thezone=CZClass(terminal, (nextx, nexty), label,
                                     fgcolor, bgcolor,
                                     highlightfgcolor, highlightbgcolor,
                                     width=width, group=self.group)
            thezone.on_click = func
            self.zones.append(thezone)
























