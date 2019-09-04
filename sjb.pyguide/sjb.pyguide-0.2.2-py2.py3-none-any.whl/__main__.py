import sys
import argparse
from py_guide.console_menu import ConsoleMenu
from py_guide import log_4_trees


global log
log = log_4_trees.LoggerOfTrees()


def main(args=None):
    """As a best practice, main() will be the entry point for this package.  The method
        should handle parsing arguments and display a usage help message if the package
        was not called as expected.

        Note:
            Using the main() will help creating deployment packages using setup.py, wheel, and wanting
            creation of any entry point in the scripts directory of the virtual environment

        When an argument is parsed it should be routed to a handler action method.

        TODO:

            Add standard arg parse and help output for this package.
    """

    parser = parser_build()
    route_arguments(parser)


def parser_build():
    """This method builds the argument parser to handle values passed in from the command line.  Centralized in this
    method for readability.

    The Argument parser allows standard patterns for parsing.  For instance you do not have to program -h, or --help
    to explain how the command line is used.  The argument parser will build this from the arguments, and descriptions
    provided for those arguments, when building the parser object.
    """

    module_description = "py_guide is a best practices module recommending a basic project structure for a teams " \
                         "python projects.  Best Practices help teams scale.  Starting with it before you scale the " \
                         "team is a good thing."
    # Create an instance of a parser specific to this module
    parser = argparse.ArgumentParser(description=module_description)

    # Now tell the parser what arguments we expect
    argument_name = '--show_menu'
    multiple_argument_actions = "?"
    argument_action = "store_true"  # If you pass this argument, by default it is true
    argument_type = bool
    argument_help = "When this parameter is provided the flag is set to true.  When true a console menu " \
                    "will be shown."
    # The type on this argument is implied by the action being store_true.  Adding it will cause an error
    #   https://stackoverflow.com/a/33574535
    parser.add_argument(argument_name,
                        action=argument_action,
                        help=argument_help)

    argument_name = "--list_of_strings"  # Remove -- in front of the arg name means this is required
    # nargs is an optional parser argument.  If used it will allow a list of items to be associated with an action.
    #   For instance a list of zip codes provide to a single argument, would be my example of how you can use nargs
    multiple_argument_actions = "+"  # nargs - https://docs.python.org/3/library/argparse.html#nargs
    argument_action = "append"  # action - https://docs.python.org/3/library/argparse.html#action
    argument_help = "The list parameter will collect, then echo a list of strings.  This demonstrates the + " \
                    "value of nargs when using the parser."
    parser.add_argument(argument_name,
                        metavar="list", # When help is built, changes the display name. Still args.list_of_strings
                        type=str,  # Allows the parser to treat the command line string, as another tpe, like int, float
                        nargs=multiple_argument_actions,
                        action=argument_action, # Treatment of argument. Here append string to list.
                        help=argument_help)

    return parser


def route_arguments(cmdline_parser):
    """This method will use the arguments parsed from the command line to route different pieces of functionality
    in the module"""

    # Grab arguments off command line, sys.argv[1:], and parse them
    args = cmdline_parser.parse_args()

    if args.list_of_strings is not None:
        route_action_list_of_strings(args)

    if args.show_menu:
        route_action_show_menu(cmdline_parser=cmdline_parser)

    if not args.show_menu and args.list_of_strings is None:
        # If nothing was passed in, print the help usage
        cmdline_parser.print_help()


def route_action_list_of_strings(args):
    """If a list of strings is passed as a command line parameter, this method will be triggered by routing, and will
    handle that argument.  At this time we will simply echo back the values passed in, as the point is to show how 
    argument parsing works."""
    print("list_of_strings = {0}".format(args.list_of_strings))


def route_action_show_menu(cmdline_parser):
    """If ``--show_menu`` is passed as part of calling this module, this method will be triggered by routing, and
    a console menu will be shown."""
    menu = ConsoleMenu(cmdline_argument_parser=cmdline_parser, logger=log)
    menu.show_menu()


if __name__ == "__main__":
    """The __name__ == \"__main__\" construct ensures this package is only executed when the py_guide module is 
    specifically called.  One example of when this is important is using Sphinx, when the module is imported or scanned 
    by the Sphinx engine.
    
    https://docs.python.org/3/library/__main__.html"""

    # Using ``sys.exit(status)``  to exit Python cleanly. https://docs.python.org/2/library/sys.html#sys.exit
    sys.exit(main())
