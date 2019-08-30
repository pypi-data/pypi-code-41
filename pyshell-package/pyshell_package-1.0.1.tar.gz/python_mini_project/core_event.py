"""core_event file is the main entry gate of the project.
The core event loop - code that accepts user input, tokenize
and evaluate commands"""
# importing required in-built module
import sys
import dispatcher
from command_list import commands
""" This function handles all the input entered by user and accordingly
calls dispatcher to run respective commands """


def run():
    # This file will store all the commands entered by user
    all_history = ""
    while True:
        try:
            try:
                command = input("pyshell>> ")
            # this will handle keyboard interrupts like ctrl+c
            except KeyboardInterrupt as e:
                print(e)
                continue
            if command == "history":
                print(all_history)
                continue
            all_history = all_history + command + '\n'
            if command == "exit":
                break
            # splitting command into arguments
            args = command.split()
            if args[0] == "exit" and len(args) == 1:
                break
            if args[0] in commands:
                dispatcher.run(args)
            # dispatching respective module
            else:
                print("Invalid Command")
        except Exception as e:
            print("", end="")


if __name__ == '__main__':
    run()
