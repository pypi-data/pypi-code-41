#help function for tangly

def help():
    print("hello, you are using tangly, a simple tool to display lists as tables")
    print("Here is what you need to do to use it:\n\n")
    print("1- Create a list like so:\n")
    print(">>> my_list = [['he', 'she'],")
    print("              ['his', 'hers'],]")
    print("\n\nNow just use the command table() to tranform it:\n")
    print(">>> table(my_list)")
    print("\nThis will be the output:\n")
    print("""| first  | second |
-------------------
| he     | she    |
| his    | hers   |""")
    print("""\n\nYou can also use some aditional parameters to change the columns
names:\n\n""")
    print(">>> table(my_list, 'male', 'female')\n")
    print("This will be the output:\n\n")
    print("""| male  | female  |
-------------------
| he    | she     |
| his   | hers    |\n\n""")
    print("Simple as that.\n")
    insta = input("would you like to see instalation help too?(y/n)")
    if insta == 'y':
        print("\n\n\n")
        print("--"*40)
        print("""\n\n\nTo install Tangly, you must have pip installed,
then, on the terminal,  type:\n
pip install tangly\n
although it is not nescessary you might also need to try:\n
pip3 install tangly , this will give you the version for python 3.x\n\n
Now to import it just type:\n
>>>import tangly
\nall done""")
    else:
        pass
