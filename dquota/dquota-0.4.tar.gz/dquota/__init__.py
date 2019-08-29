import time
import json
from pyroute2.config import kernel
from pyroute2.netlink import genlmsg
from pyroute2.netlink.generic import GenericNetlinkSocket
from pyroute2.netlink.nlsocket import Marshal

QUOTA_NL_C_UNSPEC = 0
QUOTA_NL_C_WARNING = 1

class dquotmsg(genlmsg):
    prefix = 'QUOTA_NL_A_'
    nla_map = (('QUOTA_NL_A_UNSPEC', 'none'),
               ('QUOTA_NL_A_QTYPE', 'uint32'),
               ('QUOTA_NL_A_EXCESS_ID', 'uint64'),
               ('QUOTA_NL_A_WARNING', 'uint32'),
               ('QUOTA_NL_A_DEV_MAJOR', 'uint32'),
               ('QUOTA_NL_A_DEV_MINOR', 'uint32'),
               ('QUOTA_NL_A_CAUSED_ID', 'uint64'),
               ('QUOTA_NL_A_PAD', 'uint64'))


class MarshalDQuot(Marshal):
    msg_map = {QUOTA_NL_C_UNSPEC: dquotmsg,
               QUOTA_NL_C_WARNING: dquotmsg}


class DQuotSocket(GenericNetlinkSocket):
    def __init__(self):
        GenericNetlinkSocket.__init__(self)
        self.marshal = MarshalDQuot()
        if kernel[0] <= 2:
            self.bind(groups=0xffffff)
        else:
            self.bind()
        for group in self.mcast_groups:
            self.add_membership(group)

    def bind(self, groups=0, async=False):
        GenericNetlinkSocket.bind(self, 'VFS_DQUOT', dquotmsg,
                                  groups, None)


class DQuotNotifications:
    def __init__(self, provider):
        self.ds = DQuotSocket()
        self.provider = provider
        self.warnings = [
            "All good",
            "Inode hardlimit reached",
            "Inode grace time expired",
            "Inode softlimit reached",
            "Block hardlimit reached",
            "Block grace time expired",
            "Block softlimit reached",
            "Usage got below inode hardlimit",
            "Usage got below inode softlimit",
            "Usage got below block hardlimit",
            "Usage got below block softlimit"
        ]

    def run(self):
        while True:
            for msg in self.ds.get():
                self.provider.send(json.dumps({
                    'uid': msg.get_attr('QUOTA_NL_A_EXCESS_ID'),
                    'message': self.warnings[msg.get_attr('QUOTA_NL_A_WARNING')] }))
            time.sleep(0.1)

