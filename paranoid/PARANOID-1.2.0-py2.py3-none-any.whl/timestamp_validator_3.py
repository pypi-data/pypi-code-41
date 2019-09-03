from datetime import datetime


# Just month's names
months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul',
          'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

_today = datetime.today()


def l_mon(_mon):
    if _mon == 1:
        return 'Jan'
    elif _mon == 2:
        return 'Feb'
    if _mon == 3:
        return 'Mar'
    elif _mon == 4:
        return 'Apr'
    if _mon == 5:
        return 'May'
    elif _mon == 6:
        return 'Jun'
    if _mon == 7:
        return 'Jul'
    elif _mon == 8:
        return 'Aug'
    if _mon == 9:
        return 'Sep'
    elif _mon == 10:
        return 'Oct'
    if _mon == 11:
        return 'Nov'
    elif _mon == 12:
        return 'Dec'
    else:
        return ""


# new validator coded with only build-in functions
# six variants of date processing
def validate_timestamp(_word):
    if (_word[0:4].isdigit() and
            int(_word[0:4]) in range(0, 2019) and
            _word[4:5] in '-' and _word[5:7].isdigit()
            and int(_word[5:7]) in range(1, 31)
            and _word[7:8] in '-' and _word[8:10].isdigit()
            and int(_word[8:10]) in range(1, 31)):
        return True, _today.strftime('%Y-%m-%d') + _word[10:]
    # Jun 09 2018 15:28:14
    if (_word[0:3] in months and _word[3:4] in ' '
            and _word[4:6].isdigit() and int(_word[4:6]) in range(1, 31)
            and _word[7:11].isdigit() and
            int(_word[7:11]) in range(0, 2019)):
        return True, _today.strftime('%m %d %Y') + _word[11:]
    # Apr 20 00:00:35 2010
    if (_word[0:3] in months and _word[3:4] in ' ' and
            _word[4:6].isdigit() and
            int(_word[4:6]) in range(1, 31)
            and int(_word[len(_word) - 4:]) in range(0, 2019)):
        return True, (f'{l_mon(_today.month)} {_today.day} {_today.hour}:' +
                      f'{_today.minute}:{_today.second} {_today.year}')
    # 23 Apr 2017 11:42:35
    if (_word[0:2].isdigit() and int(_word[0:2]) in range(1, 31)
            and _word[3:6] in months and _word[7:11].isdigit()
            and int(_word[7:11]) in range(0, 2019)):
        return True, (f'{_today.day} {l_mon(_today.month)} {_today.year} ' +
                      f'{_today.hour}:{_today.minute}:{_today.second}')
    # 10-04-19 12:00:17
    if (_word[0:2].isdigit() and int(_word[0:2]) in range(1, 31)
            and _word[2:3] in '-' and _word[3:5].isdigit()
            and int(_word[3:5]) in range(1, 12)
            and _word[6:8].isdigit() and
            int(_word[6:8]) in range(0, _today.year - 1999)):
        return True, (f'{_today.day}-{l_mon(_today.month)}-{str(_today.year)[2:4]} ' +
                      f'{_today.hour}:{_today.minute}:{_today.second}')
    # 06/01/22 04:11:05
    if (_word[0:2].isdigit() and int(_word[0:2]) in range(0, 19)
            and _word[2:3] in '/' and _word[3:5].isdigit()
            and int(_word[3:5]) in range(1, 12)
            and _word[6:8].isdigit() and
            int(_word[6:8]) in range(0, 31)):
        return True, (f'{str(_today.year)[2:4]}/{_today.month}/{_today.day} ' +
                      f'{_today.hour}:{_today.minute}:{_today.second}')

    return False, ''
