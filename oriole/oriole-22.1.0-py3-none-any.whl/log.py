#
#                __   _,--="=--,_   __
#               /  \."    .-.    "./  \
#              /  ,/  _   : :   _  \/` \
#              \  `| /o\  :_:  /o\ |\__/
#               `-'| :="~` _ `~"=: |
#                  \`     (_)     `/
#           .-"-.   \      |      /   .-"-.
#    .-----{     }--|  /,.-'-.,\  |--{     }-----.
#     )    (_)_)_)  \_/`~-===-~`\_/  (_(_(_)    (
#    (                                           )
#     )                Oriole-LOG               (
#    (                  Eric.Zhou                )
#    '-------------------------------------------'
#

import logging


def logger(level='DEBUG', fmt='', dfmt=''):
    level = getattr(logging, level, logging.DEBUG)
    logger = logging.getLogger('services')
    logger.setLevel(level)
    fmter = logging.Formatter(fmt, dfmt)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmter)
    logger.addHandler(ch)
    logger.propagate = False

    return logger
