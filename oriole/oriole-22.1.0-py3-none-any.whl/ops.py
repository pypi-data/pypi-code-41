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
#     )                Oriole-OPS               (
#    (                  Eric.Zhou                )
#    '-------------------------------------------'
#

import tempfile

from oriole.vos import exe, get_config


def build(service):
    tmp = tempfile.NamedTemporaryFile(dir=".")
    try:
        cf = get_config()
        image = cf.get('image', 'zhouxiaoxiang/service:1.0')
        loc = "/service"
        make = "FROM {0}\nCOPY . {1}\nWORKDIR {1}\nRUN make\nCMD o r {2}\n"
        tmp.write(make.format(image, loc, service).encode())
        tmp.seek(0)
        fmt = "docker build -t {}_service -f {} ."
        exe(fmt.format(service, tmp.name))
    finally:
        tmp.close()


def open_shell(s, banner=''):
    try:
        from IPython import embed
        embed(banner1=banner, user_ns=s)
    except Exception:
        import code
        code.interact(banner, None, s)
