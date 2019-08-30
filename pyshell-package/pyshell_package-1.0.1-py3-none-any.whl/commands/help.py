# help---to get help regarding commands
# importing modules required
from command_dictionary import cmd_dict


def run(args=None):
    """ this function is called when help along with required argument are
    entered in PyShell"""
    if args is None:
        for key, value in cmd_dict.items():
            print(key + " : " + value)
    else:
        if cmd_dict.__contains__(args):
            print(args + " : " + cmd_dict.get(args))
        else:
            from extern import extern_var
            print(extern_var.get('no_cmd'))
