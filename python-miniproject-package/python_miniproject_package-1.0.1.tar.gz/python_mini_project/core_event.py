import sys
import dispatcher
from command_list import commands

#commands=["ls","grep","mkdir","pwd","cd","cp","mv","rmdir", "rm","whoami","hostname", "timeit","date","sizeof","cat","head","tail","find"]


def run():
    all_history=""
    while True:
        try:
            command = input("pyshell>> ")
        
        except KeyboardInterrupt as e:
            print(e)
            continue
        
        if command == "history":
            print(all_history)
            continue
        all_history= all_history + command + '\n'
        if command == "exit":
            break
       
            
        
        
            
        args = command.split()
        if args[0] == "exit" and len(args) == 1:
            break
        #print(args)
        if args[0] in commands:
            dispatcher.run(args)
        else:
            print("Invalid Command")

if __name__ == '__main__':
    run()