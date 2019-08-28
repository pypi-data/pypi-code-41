"""This is the "displayitem.py" module, and it provides one function called
print_lol() which prints lists that may or may not include nested lists."""
def print_lol(the_list, indent=False, level=0):
    """This function takes in three arguments "the_list", "indent" and "level". "the_list"
prints each data item on a new line whether it is nested or not while "indent" has a default
value of 'False'. If "indent" is 'True' however, "level" inserts tab-stops whenever it finds
a nested list."""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, indent, level + 1)
        else:
            if indent:
                for tab_stop in range(level):
                    print("\t", end='')
            print(each_item)




'''
movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91,
          ["Graham Chapman",
           ["Michael Palin", "John Cleese", "Terry Gilliam", "Eric Idle", "Terry Jones"]]]


version = '1.3.0'
C:\Python37\python -m twine upload dist\displayitem-1.3.0.tar.gz
'''
