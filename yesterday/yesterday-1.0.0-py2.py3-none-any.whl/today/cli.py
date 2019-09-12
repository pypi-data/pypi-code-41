import sys
import click
from today import __version__ as VERSION
from today.entries import *
from today.Questionairre import start_log
import pyfiglet
from today.Pretty import Pretty

global __user__
__user__ = None


def validatekey(key):
    # TODO
    return 'Raiyan'


def login():
    print(Pretty.OKGREEN +'Looks like you are a new user . Let\'s get you started !! \n ' + Pretty.ENDC )
    key = click.prompt(Pretty.WARNING + "Please enter your SECRET KEY : " + Pretty.ENDC)
    __user__ = validatekey(key)
    return __user__


def get_user_profile():
    # TODO
    __user__ = "Raiyan"


def start_log_session():
    pass


@click.command()
@click.option('--version', is_flag=True, help="Gives the installed version of Today")
def main(version):
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_banner = pyfiglet.figlet_format("TODAY",font='slant')
    print(ascii_banner)
    print(" === ======= ======= = ======= === ========= ========")
    print(" Quick Journals for Everyone ! ")
    print(" === ======= ======= = ======= === ========= ======== \n")
    if version:
        print(VERSION)
        sys.exit()
    if check_if_user_exists():
        get_user_profile()
        print(Pretty.HEADER+'Welcome back ' + __user__ + Pretty.ENDC)
        start_log()
    else:
        user = login()
        print(Pretty.OKBLUE+(' \n Welcome to Today {} , let\'s get started with your very first record !! \n '.format(user)) + Pretty.ENDC)
        start_log()


if __name__ == "__main__":
    main()
