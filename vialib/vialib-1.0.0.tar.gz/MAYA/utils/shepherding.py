#######################################################################
#
#       COPYRIGHT 2005 MAYA DESIGN, INC., ALL RIGHTS RESERVED.
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

# $Id: shepherding.py 25638 2007-10-14 02:06:55Z higgins $

import time
import CachingRepository

class TimeoutError(RuntimeError):
    pass

# blocks until a uform is present in the given repository
# so that complex data structure operations can be run against a local repos
#
# r = (Repository) repository we want to contain the given uform
# uu = (Uuid) the UUID of the uform we want r to contain 
# timeoutSecs = (float) number of seconds we're willing to wait; 0
#               blocks until the uform appears
# testInterval = (float) number of seconds we want to wait between presence
#               tests

def waitForPresence(r, uu, timeoutSecs = 30, testInterval = 1):
    if uu == '':
        raise "Empty UUID in waitForPresence"
    if uu == None:
	raise "UUID cannot be None in waitForPresence"

    if r.__class__ is CachingRepository.ListeningCachingRepository:
        try:
            r.getAttr(uu, 'foobar')
        except CachingRepository.TimeoutError, e:
            raise TimeoutError('timed out after waiting for UUID %s to be present in repository %s for %d seconds' % (e.uid.toString(), e.addr, e.delay))
        return
    elif hasattr(r, '_implements_timeout'):
	return
 
    start = time.time()
    if not r.knows(uu): r.getAttr(uu,'foobar')
    else: return
    while not r.knows(uu):
        if (timeoutSecs > 0) and ((time.time() - start) > timeoutSecs):
            raise TimeoutError('timed out after waiting for UUID %s to be present in repository %s for %d seconds' % (uu.toString(), r.getHostAndPort(), int(timeoutSecs)))
        time.sleep(testInterval)

def multiGet(r, uids, attr, batch):
    answers = []
    r.setBatchMode(1)
    i = 0
    while i < len(uids):
        uid = uids[i]
        i = i + 1
        if i % batch == 0:
            answers.extend(r.commit(1))
        r.getAttr(uid, attr)
    answers.extend(r.commit(1))
    r.setBatchMode(0)
    return answers

def uniquify(xs):
    h = {}
    for x in xs:
        h[x] = 1
    return h.keys()

def multiWaitForPresence(r, uids, batch=100, timeoutSecs=300, testInterval=1):
    found = {}
    uids = uniquify(uids)
    def find(r, uids):
        missing_uids = []
        for uid in uids:
            if not found.has_key(uid):
                missing_uids.append(uid)
        answers = multiGet(r, missing_uids, 'shepherd_versions', batch)
        uid_answers = zip(missing_uids, answers)
        for (uid, answer) in uid_answers:
            if not answer is None:
                found[uid] = 1
        return len(found) == len(uids)
    start = time.time()
    while not find(r, uids):
        if (timeoutSecs > 0) and ((time.time() - start) > timeoutSecs):
            missing_uids = []
            for uid in uids:
                if not found.has_key(uid):
                    missing_uids.append(uid)
            raise TimeoutError('timed out missing UUIDs %s in repository %s after %d seconds' % (str(missing_uids), r.getHostAndPort(), int(timeoutSecs)))
        time.sleep(testInterval)
    return
