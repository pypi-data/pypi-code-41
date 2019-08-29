from command_dictionary import cmd_dict

def run(args=None):
    if args == None:
        for key,value in cmd_dict.items():
            print(key + " : " + value)
    else:
        if cmd_dict.__contains__(args):
            print(args + " : " + cmd_dict.get(args))
        else:
            print("No such command exists!!!")


