"""This is the "displayitem.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists."""
def print_lol(the_list, level):
    """This function takes in two argument "the_list" and "level". "the_list"
prints each data item on a new line whether it is nested or not while "level"
inserts tab-stops whenever it finds a nested list."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level + 1)
        else:
            for tab_stop in range(level):
                print("\t", end='')
            print(each_item)


'''
movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
          ["Graham Chapman",
           ["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]
'''
