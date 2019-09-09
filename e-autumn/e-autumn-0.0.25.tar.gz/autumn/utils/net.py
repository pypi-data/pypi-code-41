import socket
from loguru import logger


SO_BINDTODEVICE = 25

# iface参数指Linux的网卡接口，如(eth0,wlan0)，这个参数只支持Linux并且需要root权限


def get_free_port(iface=None):
    """
    Get a free port

    :param iface: the interface of network devices: eth0
    :returns: port
    """
    s = socket.socket()
    if iface:
        s.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE, bytes(iface, 'utf8'))
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    logger.debug("Get a free port [{}]", port)
    return port
