from quarchpy import isQisRunning, closeQIS, isQpsRunning, closeQPS
import subprocess, sys
from quarchpy.user_interface import *


def main(argstring,auto_update=False):
    import argparse
    parser = argparse.ArgumentParser(description='Update Quarchpy parameters')
    parser.add_argument('-au', '--auto_update', help='If you definitely want to update', type=str.lower, default="n")
    parser.add_argument('-v', '--version', help='The version of quarchpy you would like to install',type=str)
    args = parser.parse_args(argstring)
    if args.auto_update in ('yes', 'true', 't', 'y', '1'):
        auto_update = True
    else:
        auto_update = False


    if (check_if_update(auto_update)or args.version !=None):
        updateQuarchpy(args.version)


def updateQuarchpy(versionNumber):
    printText("Updating Quarchpy")
    try:
        if versionNumber !=None:
            versionNumber = "=="+versionNumber
            printText((bytes(subprocess.check_output(['pip', 'install', 'quarchpy'+versionNumber], stderr=subprocess.STDOUT)).decode()))
        else:
            printText((bytes(subprocess.check_output(['pip', 'install', 'quarchpy', '--upgrade'], stderr=subprocess.STDOUT)).decode()))

        printText("Updated successfully")
    except:
        printText("Not updated successfully")


def check_if_update(auto_update):
    # check if qpy is outdated
    update_desired = False
    package_list = (bytes(subprocess.check_output(['pip', 'list', '-o'], stderr=subprocess.STDOUT)).decode())
    if "quarchpy" in package_list:
        printText("quarchpy is outdated")
        if auto_update:
            update_desired = True
        else:
            usr_input = requestDialog(title="", message="Do you want to update Y/N?")
            update_desired = True if usr_input == "Y" or usr_input == "y" else False

        if update_desired:
            if isQpsRunning() == True:
                 usr_input = requestDialog(title="", message="QPS must be closed to update. Close QPS Y/N?")
                 if usr_input == "Y" or usr_input == "y": closeQPS()
                 else: return False
            if isQisRunning() == True:
                 usr_input = requestDialog(title="", message="QIS must be closed to update. Close QIS Y/N?")
                 if usr_input == "Y" or usr_input == "y": closeQIS()
                 else: return False
        else:
            return False
    else: #quarchpy is up to date.
        printText("quarchpy is up to date.")
        return False
    return True

if __name__ == "__main__":
    main(sys.argv[1:])