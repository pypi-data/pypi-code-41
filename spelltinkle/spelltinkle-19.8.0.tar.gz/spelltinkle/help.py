from spelltinkle.keys import keynames, doubles
from spelltinkle.document import Document


x = """
check state of file every two seconds when active?
e -m ase.cal<tab-complete>

Fast and simple editor based on Python and Pygments.

XKCD: automation 1319

   SPEL
   LTIN
   KLE


([[](()))
        ^: ]?

Color names: GOOD, BAD, OK, IMPORTANT, IRRELEVANT, ...

C-p/C-n: up/down 1 line instead of one screen-line

http://stackoverflow.com/questions/2230037/how-to-fetch-an-email-body-using-imaplib-in-python
http://stackoverflow.com/questions/122267/imap-how-to-move-a-message-from-one-folder-to-another
http://stackoverflow.com/questions/12490648/imap-fetch-subject


$ spelltinkle dir/ -> open fileinput

only one file-list at the time

replace+color
no indent after return

Put help for opening files on the filelist page

When selcting area with mouse use scrollbar to scroll up or down

remove tabs when reading (or replace with 4 tabs that display as spaces?)
smooth scrolling when jumping?
b block: b:begin, r:rectangle, l:lines
f replace,x:regex
g goto 123,()[]{},x:inner
h help,x:search in help
i-(tab) x:insert file or !shell
j- x:join
k kill,x:backwards
l delete line
m- x:makro
n
o open file or !shell or >>> python
q quit,x:ask
r reverse find,x:word under cursor
s find
t
y mark: wl()[]{},x:inner
z delete wl()[]{},x:inner

How about ^Z?

^#12 or ^1^2?

Jump to marked point? Put position on stack

<c-1><c-2>: repeat 12 times
scroll:up, down,center,top, bottom
big movements

scripting: abc<enter><up><end>

Use number columns to show stuff: last changed line(s)

"""


class HelpDocument(Document):
    def __init__(self):
        Document.__init__(self)
        self.name = '[help]'
        lines = []
        for c in sorted(keynames):
            k = keynames[c]
            if not isinstance(k, str):
                k = '+'.join(k)
            lines.append('  {}: {}'.format(c, k))
        for c1 in doubles:
            for c2, k in doubles[c1].items():
                if not isinstance(k, str):
                    k = '+'.join(k)
                lines.append('{}{:2}: {}'.format(c1, c2, k))
        lines += x.split('\n')
        self.change(0, 0, 0, 0, lines)
