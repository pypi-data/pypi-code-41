from io import StringIO
import traceback
import time
from PyQt5.QtWidgets import QMessageBox
import logging
import os
import requests
import json
import argparse

def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.
    
    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """

    # about = {}
    # with open(os.path.join('__init__.py')) as f:
    #     exec(f.read(), about)

    message = f"An unhandled exception occurred.\n" 
    message += f'A log has been written to:\n'
    message += f'{logging.getLogger("").handlers[0].baseFilename}\n'
    message += f"The problem has been automatically reported to the authors.\n" 
    message += f'\n'

    message += '-' * 80 + '\n'
    message += 'Log: \n'
    message += time.strftime("%Y-%m-%d, %H:%M:%S \n")
    # message += f'Active Image Labeler v{about["__version__"]} \n'

    message += '-' * 80 + '\n'
    message += 'Error Message: \n'
    message += f'{str(excType)}: \n' 
    message += f'{str(excValue)} \n'
    
    tbinfofile = StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    tbinfofile.seek(0)
    message += '-' * 80 + '\n'
    message += f'Traceback information: \n'
    message += f'{tbinfofile.read()}'

    logging.critical(message)


    os.system(f"python src/libs/crashreporter.py --log='{logging.getLogger('').handlers[0].baseFilename}'")

    errorbox = QMessageBox()
    errorbox.setText(message)
    errorbox.exec_()



def sendToSlack(message):

    try:
        # send message to SLACK through API
       
        # send message to SLACK (private channel on IVUL) through API
        webhook_url = "https://hooks.slack.com/services/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"
        response = requests.post(
            webhook_url,
            data=json.dumps({"text": f"*Error raised for the Active Image Labeler Software:* \n {message}"}),
            headers={"Content-type": "application/json"})

        print("... Notification send.")

    except Exception as e:
        print("... Notification sending ERROR:", e)


if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description="Report logs on SLACK")

    parser.add_argument("--log",
                        default="log.log",
                        type=str,
                        help="log file")

    args = parser.parse_args()

    contents = ""
    f=open(args.log, "r")
    if f.mode == 'r':
        contents += '```' + f.read() + '```'


    sendToSlack(str(contents))
