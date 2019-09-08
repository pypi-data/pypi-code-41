from .parser import get_arguments_parser
from .executor import execute_command


def main():
    p = parser.get_arguments_parser()
    arguments = p.parse_args()
    execute_command(arguments)
