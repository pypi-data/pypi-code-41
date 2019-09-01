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


# will copy to the clipboard
def copy_to_clipboard(text):
    import pyperclip
    pyperclip.copy(text)
    pyperclip.paste()


# will return the current text from the clipboard
def get_from_clipboard():
    import pyperclip
    return pyperclip.paste()
