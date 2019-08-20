#######################################################################
#
#       COPYRIGHT 2006 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
#
# ALL INTELLECTUAL PROPERTY RIGHTS IN THIS PROGRAM ARE OWNED BY MAYA DESIGN.
# THIS PROGRAM CONTAINS CONFIDENTIAL AND PROPRIETARY INFORMATION OWNED BY MAYA
# DESIGN AND MAY NOT BE DISCLOSED TO ANY THIRD PARTY WITHOUT THE PRIOR CONSENT
# OF MAYA DESIGN.  THIS PROGRAM MAY ONLY BE USED IN ACCORDANCE WITH THE TERMS
# OF THE APPLICABLE LICENSE AGREEMENT FROM MAYA DESIGN. THIS LEGEND MAY NOT BE
# REMOVED FROM THIS PROGRAM BY ANY PARTY.
#
# THIS LEGEND AND ANY MAYA DESIGN LICENSE DOES NOT APPLY TO ANY OPEN SOURCE
# SOFTWARE THAT MAY BE PROVIDED HEREIN.  THE LICENSE AGREEMENT FOR ANY OPEN
# SOURCE SOFTWARE, INCLUDING WHERE APPLICABLE, THE GNU GENERAL PUBLIC LICENSE
# ("GPL") AND OTHER OPEN SOURCE LICENSE AGREEMENTS, IS LOCATED IN THE SOURCE
# CODE FOR SUCH SOFTWARE.  NOTHING HEREIN SHALL LIMIT YOUR RIGHTS UNDER THE
# TERMS OF ANY APPLICABLE LICENSE FOR OPEN SOURCE SOFTWARE.
#######################################################################

from MAYA.VIA import uform
from MAYA.VIA import uuid
from MAYA.VIA import repos

import sys
import threading

class Listener(threading.Thread):

    def __init__(self, addr):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.stop = False
        self.listeners = {}
        self.r = repos.Repository(addr)
        auf = uform.UForm()
        auf['client_type'] = ('authenticated', 1)
        self.r.authenticate(auf)
        self.s = threading.Semaphore()
        self.id = 0

    def clearNotify(self,uf):
        try:
            self.s.acquire()
            self.id = self.id + 1
            self.r.send((self.id, 0, 22, uf))
        finally:
            self.s.release()
        return

    def registerNotify(self, uf):
        try:
            self.s.acquire()
            self.id = self.id + 1
            self.r.send((self.id, 0, repos.NOTIFY_AND_GETUFORM, uf))
        finally:
            self.s.release()
        return

    def startListening(self, uid, f):
        uf = uform.UForm(uid)
        if self.listeners.has_key(uid):
            self.clearNotify(uf)
        self.listeners[uid] = f
        self.registerNotify(uf)
        return

    def stopListening(self, uid):
        if self.listeners.has_key(uid):
            uf = uform.UForm(uid)
            self.clearNotify(uf)
            del self.listeners[uid]
        return

    def run(self):
        while not self.stop:
            reply = self.r.recv()
            if self.stop: break
            id = reply[0]
            op = reply[1]
            uf = reply[2]
            uid = uf.uuid
            if op == 23:
                self.registerNotify(uf)
            else:
                f = self.listeners.get(uid)
                if f:
                    f(uf)

        return


def test():
    import time
    
    uf = uform.UForm()
    r = repos.Repository('joshua3.maya.com:8888')
    uf['name'] = 'Mike'
    r.setAttr(uf)
    
    l = Listener('joshua3.maya.com:8888')
    l.start()

    def f(uf):
        if len(uf.keys()) == 0:
            return
        return

    print "Delaying before start listening (2)"
    time.sleep(2)
    l.startListening(uf.uuid, f)

    while 1:
        print "Waiting for other thread"
        time.sleep(10)

    return

if __name__ == '__main__':
    test()
    
