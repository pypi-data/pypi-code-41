"""This is the "displayitem.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists."""
import sys

def print_lol(the_list, indent=False, level=0, display=sys.stdout):
    """This function takes in four arguments "the_list", "indent", "level" and "display". "the_list"
prints each data item on a new line whether it is nested or not while "indent" has a default
value of 'False'. If "indent" is 'True' however, "level" inserts tab-stops whenever it finds
a nested list. "display" is used to specify where the data will be printed, it has a default
of displaying to the screen"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level + 1, display)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='', file=display)
            print(each_item, file=display)




'''
movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
          ["Graham Chapman",
           ["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]

'''
