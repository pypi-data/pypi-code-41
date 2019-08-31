# Card files are csv files that contain cards. Each card has a front and a back

import curses
import glob
import os
import textwrap as tw
import csv

HOME_DIR = os.path.expanduser('~')

stdscr = curses.initscr()

menu = ['Practice', 'Edit']
current = 0

if not os.path.isdir(HOME_DIR+"/.cards"):
    os.mkdir(HOME_DIR+"/.cards")

def addwrappedstr(stdscr, y, x, text, color=None, center_y=False):
    
    # If center_y is true, we wrap the text such that lines are added above and below the input
    # coordinates such that the text remains centered on the input coordinates 
    # instead of starting at the coordinates and going down from there.
    # This can cause problems as the text printed may interfere with other text
    # previously printed above the input coordinates, so it should only really be used
    # in situations where the text is being printed to the screen in an area where we can
    # be sure there is nothing close to it

    h, w = stdscr.getmaxyx()
    text = tw.wrap(text, int(w*0.9))    
    for i, line in enumerate(text):
        if center_y:
            new_x, new_y = w//2-len(line)//2, y+i-len(text)//2
        else:
            new_x, new_y = w//2-len(line)//2, y+i
        if color != None:
            stdscr.addstr(new_y, new_x, line, color)
        else:
            stdscr.addstr(new_y, new_x, line)
    return len(text)

def draw_menu(stdscr, menu, current, title=None, info=None):
    
    h, w = stdscr.getmaxyx()
    # Normally y_offset increments by 1 and so each menu line is displayed on consecutive lines
    # However, if the line to be displayed is longer than the width of the screen allows,
    # addwrappedstr puts it on 2 or more lines instead and so y_offset is incremented by
    # however many lines that call of addwrappedstr wrote to 
    y_offset = 0
    for i, elem in enumerate(menu):
        x, y = w//2-len(elem)//2, h//2-len(menu)//2+y_offset
        if i==current:
            y_offset += addwrappedstr(stdscr, y, x, elem, curses.color_pair(1))
        else:
            y_offset += addwrappedstr(stdscr, y, x, elem)
    if title != None:
        x, y = w//2-len(title)//2, h//2-len(menu)//2-2
        addwrappedstr(stdscr, y, x, title)
    if info != None:
        x, y = w//2-len(info)//2, h - 3 - len(tw.wrap(info, int(w*0.9)))
        addwrappedstr(stdscr, y, x, info)

def interactive_menu(stdscr, menu, current, title=None, delete=False, info=None):
    
    while True:

        stdscr.clear()
        draw_menu(stdscr, menu, current, title, info)
        stdscr.refresh()

        c = stdscr.getch()
        if c == curses.KEY_UP:
            current = max(0, current-1)
        elif c == curses.KEY_DOWN:
            current = min(len(menu)-1, current+1)
        elif c == curses.KEY_ENTER or c in [10, 13]:
            return current
        elif c == ord('d'):
            if delete and menu[current] not in ["New Card", "New Cardset"]:
                if interactive_menu(stdscr, ["Delete", "Cancel"], 0, title="Are you sure you want to delete that?") == 0:
                    return ["DELETE", current]
        elif c == ord('q'):
            return "BACK"

def input_box(stdscr, title=None):
    curses.curs_set(1)
    text = ''
    h, w = stdscr.getmaxyx()
    while True:
        x, y = w//2-len(text)//2, h//2
        stdscr.clear()
        if title!=None:
            x_, y_ = w//2-len(title)//2, h//2-2
            stdscr.addstr(y_, x_, title)
        stdscr.addstr(y, x, text)
        stdscr.refresh()
        c = stdscr.getch()
        if c == curses.KEY_ENTER or c in [10, 13]:
            curses.curs_set(0)
            return text
        elif c == curses.KEY_BACKSPACE or c == 127:
            text = text[:-1]
        else:
            text += chr(c)

def practice(stdscr):
    
    h, w = stdscr.getmaxyx()

    cardsets = [cardset[len(HOME_DIR)+8:-4] for cardset in glob.glob(HOME_DIR+"/.cards/*.csv")]
    if len(cardsets) == 0:
            stdscr.clear()
            t = "No Cardsets. Create Some In The Edit Menu"
            x, y = w//2-len(t)//2, h//2
            addwrappedstr(stdscr, y, x, t)
            stdscr.getch()
            return

    current = 0
    
    while True:

        i = "Move: [arrow keys], select: [enter], back: [q]"
        selected = interactive_menu(stdscr, cardsets, current, title='Available Cardsets:', info=i)
        if selected == "BACK":
            return
        
        cardfile = HOME_DIR+"/.cards/"+cardsets[selected]+".csv"
        cards = csv.reader(open(cardfile), delimiter=',')
        cards = [row for row in cards]
        if cards == []:
            stdscr.clear()
            t = "No Cards In This Set"
            x, y = w//2-len(t)//2, h//2
            addwrappedstr(stdscr, y, x, t)
            stdscr.getch()
        else:
            i=0
            while True:
                stdscr.clear()
                if i%2==0:
                    t = cards[i//2%len(cards)][0]
                else:
                    t = cards[i//2%len(cards)][1]
                x, y = w//2-len(t)//2, h//2
                addwrappedstr(stdscr, y, x, t, center_y=True)
                stdscr.refresh()
                if stdscr.getch() == ord('q'):
                    break
                i+=1   

def edit(stdscr):

    h, w = stdscr.getmaxyx()

    current = 0
    
    while True:

        cardsets = [cardset[len(HOME_DIR)+8:-4] for cardset in glob.glob(HOME_DIR+"/.cards/*.csv")] + ["New Cardset"]
        i = "Move: [arrow keys], select: [enter], back: [q], delete: [d]"
        selected = interactive_menu(stdscr, cardsets, current, title='Available Cardsets:', delete=True, info=i)
        if type(selected) == list and selected[0] == "DELETE":
            os.remove(HOME_DIR+"/.cards/"+cardsets[selected[1]]+".csv")
            continue
        if selected == "BACK":
            return
        if selected == len(cardsets)-1:
            cardfile = HOME_DIR+"/.cards/"+input_box(stdscr, "Select Name:")+".csv"
            cards = [[]]
        else: 
            cardfile = HOME_DIR+"/.cards/"+cardsets[selected]+".csv"
            cards = csv.reader(open(cardfile), delimiter=',')
            cards = [row for row in cards]
        
        menu_cards = [', '.join(elem) for elem in cards] + ["New Card"]

        while True:

            current = 0
            if len(menu_cards) == 0 or len(menu_cards[0]) == 0:
                selected = interactive_menu(stdscr, menu_cards[1:], current, title="Cardset Empty:", info=i)
            else:
                selected = interactive_menu(stdscr, menu_cards, current, title="Loaded Cards:", delete=True, info=i)
            if type(selected) == list and selected[0] == "DELETE":
                cards.remove(cards[selected[1]])
                menu_cards.remove(menu_cards[selected[1]])
                f = open(cardfile, "w")
                f_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                [f_writer.writerow(cards) for cards in cards]
                f.close()
                continue
            if selected == "BACK":
                break
            else:
                f = input_box(stdscr, "Front Of Flashcard:")
                b = input_box(stdscr, "Back Of Flashcard:")
                if selected == len(menu_cards)-1:
                    cards.append([f, b])
                else:
                    cards[selected] = [f, b]
                menu_cards = [', '.join(elem) for elem in cards] + ["New Card"]
                f = open(cardfile, "w")
                f_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                [f_writer.writerow(cards) for cards in cards]
                f.close()


def fcards(stdscr, menu, current):

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.curs_set(0)

    while True:
        im = interactive_menu(stdscr, menu, current)
        if im == "BACK":
            break
        elif im == 0:
            practice(stdscr)
        else:
            edit(stdscr)

def main():
    curses.wrapper(fcards, menu, current)

if __name__=="__main__":
    main()

