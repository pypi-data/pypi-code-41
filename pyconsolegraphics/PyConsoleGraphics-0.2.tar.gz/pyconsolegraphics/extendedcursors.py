"""Contains special utility cursors for PCG terminals that add special 
functionality, like rich text handling."""
import collections
import warnings

import pyconsolegraphics

class RichTextError(pyconsolegraphics.PyConsoleGraphicsException):
    """Base exception class for errors related to the RichTextCursor."""

class RichTextSyntaxError(RichTextError):
    """Raised when the RichTextCursor runs in to invalid syntax."""

#If you're wondering why we do our own parsing, and in this weird not-really-
#how-you're-supposed-to-do-it way, it's because we need to separate the
#characters to be printed from the control tags that are both coming in
#on the same stream.
class RichTextCursor(pyconsolegraphics.Cursor):
    """A cursor that implements a rich text markup format loosely based off of
    HTML and IETF RFC 1896. Accepts all positional and keyword parameters the
    normal Cursor does.

    See: https://tools.ietf.org/html/rfc1896

    Regular control characters are ignored inside <tags>.

    New commands can easily be added by subclassing this class and
    adding new methods whose name is 'encountered_tag_'+the text in the tag;
    look at the methods defined on this class.

    This thing assumes that characters are being inserted in to it in one
    continuous stream in order as they're to be printed on the screen; if you
    do stuff like print a screenful of text by moving it halfway down, printing
    the second half, then moving it up to (0,0) and printing the first half, it
    will not behave properly.

    Tags can have parameters, such as <color fgcolor=olivedrab>, or
    <color=bisque>. A parameter can be anything so long as it contains no
    spaces. Parameters are passed in to handler functions as keyword parameters.

    These are the tags that are supported in the stock RichTextCursor:
    <italic>
    <bold>
    <underline>
    <color fgcolor=... bgcolor=...>
    (<color=...> is shorthand for <color fgcolor=...>)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_reading_tag = False
        self.last_character_was_angle_bracket = False
        self.dont_print = False #is_reading_tag overrides this being False
        self.nextcommand = []
        self.nextparams = []

        #This is used to count how many times a specific tag has been opened
        #so we can handle <i><i>this should be italic</i> and so should this</i>
        #situations
        self.opencounts = collections.Counter()

        #This is used to keep track of what font, font size, font color,
        #etc... to switch to when we hit a close </color> etc... tag.
        self.stacks = collections.defaultdict(list)

    def process_control_character(self, character):
        #If we're interpreting incoming characters normally then we should
        #call the normal process_control_character() first...
        #Oh, and if the last character was an angle bracket we know that it
        #must've been the opener of a tag, so ignore that too!
        if not (self.is_reading_tag or self.dont_print or self.last_character_was_angle_bracket):
            try:
                super().process_control_character(character)
            except ValueError:
                #If process_control_character raised ValueError,
                #then that wasn't a control character as far as it's
                #concerned... but maybe we consider it as such!
                self.rich_text_process(character)
            else:
                #If process_control_character didn't complain
                #then that must've been an actual control character,
                #so we'll just emulate that behavior.
                return
        else:
            #But if not, don't.
            self.rich_text_process(character)

    def rich_text_process(self, character):
        just_saw_an_angle_bracket = self.last_character_was_angle_bracket
        self.last_character_was_angle_bracket=False
        if character == "<":
            if just_saw_an_angle_bracket:
                #The last character was a < as well, so it must be the
                #<< escape which translates to a literal <:
                #raise ValueError to tell the Cursor to treat it as normal
                raise ValueError("<< represents a single literal <.")
            else:
                self.last_character_was_angle_bracket = True
            return

        elif character == ">":
            if self.is_reading_tag:
                self.is_reading_tag = False
                if not self.nextcommand:
                    return

                originalcommand = ''.join(self.nextcommand).lower()
                self.nextcommand.clear()

                if originalcommand[0] == "/":
                    #If the first character is a slash, strip the slash
                    originalcommand = originalcommand[1:]
                    #and mark that we're going to un-do the command
                    negate = True
                else:
                    negate = False

                #Next, pick apart the parameters.
                #We also have a lot of .strip()s here since we're supposed to
                #ignore whitespace other than " ".
                params = originalcommand.split(" ")
                #The actual tag can have parameters too, so extract the tag
                #part of it, i.e. "color=red" -> "color"
                command = params[0].split("=")[0].strip()

                #_Are_ there any parameters? If so, process them.
                #They'll be passed to the handler as keyword arguments;
                #<color=(255,255,255)>, <abc def=ghi jkl=mno>, etc..
                paramdict = {}
                for theparam in params:
                    if "=" not in theparam:
                        if theparam.strip() == command: continue
                        raise RichTextSyntaxError("Invalid parameter syntax: "
                                                 "{0} (did you accidentally "
                                                 "put a space in the tag?)"
                                                  .format(originalcommand))
                    key, value = theparam.split("=")
                    #Just in case someone gets this confused with HTML,
                    #we strip out quotes.
                    paramdict[key.strip()] = value.strip('"').strip()

                method = getattr(self, "encountered_tag_"+command, None)

                # According to the spec, you're supposed to just ignore
                # tags you don't know how to handle...
                if not method: return

                method(negate, **paramdict)
                return
            else:
                #I'm not sure the spec actually mentions this but it seems to me
                #the smart thing is to assume a stray '>' is meant as a literal >
                #in the text
                raise ValueError("Non-control character {0} (code point > 31) "
                                 "passed to process_control_character.".format(character))
        else:
            if just_saw_an_angle_bracket and character != ">":
                #If we see a < followed by anything other than another <,
                #we've entered a <tag>! Unless it was an immediate >...
                self.is_reading_tag=True

            if not (self.is_reading_tag or self.dont_print):
                raise ValueError("Non-control character {0} (not a special "
                                 "char and not inside a tag) passed to "
                                 "process_control_character.".format(character))

            if self.is_reading_tag:
                    #According to the spec commands greater than 60
                    # characters are not to be accepted. I'm assuming the
                    # idea here is that if you see a "command" that long then
                    #  you've actually hit a stray unescaped <, not a tag at
                    # all...
                    #I'd print that out in that case, but that would lead to
                    #weird unpredictable behavior if you accidentally do that
                    #and then delete a few words and suddenly a whole
                    # sentence and a half disappears!
                    if len(self.nextcommand) >= 61:
                        self.nextcommand.clear()
                        self.is_reading_tag = False
                        warnings.warn(
                            "RichTextCursor encountered < and no >; commands "
                            "are supposed to be 60 characters or less.")
                        return
                    else:
                        self.nextcommand.append(character)

            return

    def encountered_tag_bold(self, negate):
        if negate:
            #Tick down the number of open <bold>s...
            a = self.opencounts["bold"] = max(self.opencounts["bold"] - 1, 0)
            #and if it turns out there are zero, don't be bold anymore.
            self.bold = bool(a)
        else:
            self.bold=True
            self.opencounts["bold"]+=1

    def encountered_tag_italic(self, negate):
        if negate:
            a = self.opencounts["italic"] = max(self.opencounts["italic"]-1, 0)
            self.italic = bool(a)
        else:
            self.italic=True
            self.opencounts["italic"]+=1
            
    def encountered_tag_underline(self, negate):
        if negate:
            a = self.opencounts["underline"] = max(self.opencounts["underline"] - 1, 0)
            self.underline = bool(a)
        else:
            self.underline=True
            self.opencounts["underline"]+=1
            
    def encountered_tag_color(self, negate, color=None, fgcolor=None,
                              bgcolor=None):
        #<color=...> is a shortcut for <color fgcolor=...>
        if negate:
            try:
                lastfg, lastbg = self.stacks["color"].pop()
            except ValueError:
                lastfg = lastbg = None
            self.fgcolor = lastfg
            self.bgcolor = lastbg

        else:
            self.stacks["color"].append((self.fgcolor, self.bgcolor))
            if color:
                fgcolor = color

            if fgcolor:
                if fgcolor[0] == "(" and fgcolor[-1] == ")":
                    fgcolor = tuple(int(x) for x in fgcolor.strip("()").split(","))
                self.fgcolor = fgcolor

            if bgcolor:
                if bgcolor[0] == "(" and bgcolor[-1] == ")":
                    bgcolor = tuple(int(x) for x in bgcolor.strip("()").split(","))
                self.bgcolor = bgcolor
