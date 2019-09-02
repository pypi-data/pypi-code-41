import time
from framedwindow import FramedWindow

class F:

    def __init__(self):
        self.w = FramedWindow()
        for i in ["hi", "bye", "lie", "cry", "bie", "vaii"]:
            self.w.cprint(i)
            time.sleep(1)


class ChIP:

    def __init__(self):
        self.menu = {
            1: ("change_internal", "Change Internal IP"),
            2: ("change_external", "Change External IP"),
            3: ("change_rtpgwd", "Change only RTP gateway IP")
        }
        self.window = FramedWindow()
        for k, v in self.menu.items():
            self.window.cprint("{}) {}".format(k, v[1]))
        choice = self.window.getch(prompt="Choice: ")
        try:
            x = int(choice)
            self.window.cprint(str(x))
            time.sleep(1)
            if x in self.menu.keys():
                self.window.cprint(self.menu[x][0])
                time.sleep(3)
        except Exception as e:
            self.window.cprint(str(e))
            time.sleep(3)


def poem():
    win = FramedWindow()
    with open("templates/pruf.poem", "r") as d:
        poem = [ line.strip("\n") for line in d.readlines() ]
    for line in poem:
        win.cprint(line)

poem()