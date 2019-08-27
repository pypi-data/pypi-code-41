import datetime


def log_message(msg):
    try:
        message = '\n' + str(datetime.datetime.today()) + '\t' + msg.replace('\n', '\n\t\t')
        print(message)
    except Exception as e:
        print(str(e))
