###########################################################################
#
# this module meant to provide general handling to python files
#
###########################################################################


# will print an array
def print_arr(arr, divider='\n'):
    print(divider.join(arr))


# will ask the user for an input
def ask_for_input(question):
    return input(question + '\n')

# will