#######################################################################
#
#                   Copyright 2004  MAYA Design
#
#                       All Rights Reserved.
#
#       This program is the subject of intellectual property rights
#       licensed from  MAYA Design Inc.
#
#       This legend must continue to appear in the source code
#       despite modifications or enhancements by any party.
#
#######################################################################

import threading
import Queue
import time
import sys
import heapq
import types
import traceback

from MAYA.VIA import repos
from MAYA.VIA import uform
from MAYA.VIA import uuid
from MAYA.utils import listener
from MAYA.utils import cache

class TimeoutError(Exception):

    def __init__(self, uid, addr, delay):
        self.uid = uid
        self.addr = addr
        self.delay = delay

    def __str__(self):
        return repr((self.uid, self.addr, self.delay))

class BlockDelayIsZero(Exception):
    pass

class QueueError(Exception):
    pass


# should we log performance information
LOGPERF = True

class LCRLogger:
    def __init__(self, lcrImpl, fobj=sys.stderr):
        self.fobj = fobj
        self.log("Using LCR Logger")
        self.numpurges = 0
    
    def log(self, fmt, *args):
        msg = fmt % args
        self.fobj.write(time.asctime() + ": " + msg + '\n')
        self.fobj.flush()

    def logCacheMiss(self, u):
        self.log("[LCRLogger] cache miss: " + str(u))

    def logCacheHit(self, u):
        self.log("[LCRLogger] cache hit : " + str(u))

    def logCacheUpdate(self, u, sig):
        self.log("[LCRLogger] cache update : %s, sig=%s", str(u), repr(sig))

    def logGetDuration(self, u, t, cached):
        if cached:
            cached = True
        else:
            cached = False
        self.log("[LCRLogger] get for %s : cached=%s, duration=%.3f", str(u), cached, t)

    def logSetDuration(self, u, t, cached):
        if cached:
            cached = True
        else:
            cached = False
        self.log("[LCRLogger] set for %s : cached=%s, duration=%.3f", str(u), cached, t)

    # call before you start purge
    def logStartPurge(self, cacheobj):
        self.numpurges += 1
        self.log("[LCRLogger] began purge %d with %d items", self.numpurges, len(cacheobj.cache))
    
    # call after you end purge
    def logEndPurge(self, cacheobj):
        self.log("[LCRLogger] ended purge with %d items", len(cacheobj.cache))

    


VERBOSE = 0
def log(s):
    if VERBOSE:
        print s
        sys.stdout.flush()
    return

def deepcopy(x):
    t = type(x)
    # log("deepcopy handling type " + str(t))
    if t is uform.UForm:
        y = uform.UForm(x.uuid)
        for attr in x.keys():
            # log("Copying " + attr)
            y[attr] = deepcopy(x[attr])
        return y
    elif t is types.DictType:
        y = {}
        for attr in x.keys():
            y[attr] = deepcopy(x[attr])
        return y
    elif t is types.StringType:
        return x
    elif t is types.TupleType:
        return tuple(map(deepcopy, x))
    elif t is types.ListType:
        return map(deepcopy, x)
    else:
        # log("Default deepcopy --- no copy done")
        return x

def authenticate(r):
    auf = uform.UForm()
    auf['client_type'] = ['authenticated',1]
    r.authenticate(auf)
    return

def has_values(uf):
    flag = False
    for k in uf.keys():
        if uf[k] != None:
            flag = True
            break
    return flag

def separateDefaults(uf):
    defaults = {}
    for attr in uf.keys():
        v = uf[attr]
        defaults[attr] = v
        uf[attr] = None
    # log("DEFAULTS " + str(defaults))
    return defaults

def mergeDefaults(uf, defaults):
    # log("MERGE")
    # log(str(uf))
    # log(str(defaults))

    nuf = uform.UForm(uf.uuid)
    
    for attr in defaults.keys():
        if not uf.has_key(attr):
            nuf[attr] = defaults[attr]
        elif uf[attr] is None:
            nuf[attr] = defaults[attr]
        else:
            nuf[attr] = uf[attr]
    return nuf

class WriteQueue(threading.Thread):

    def __init__(self, r, store, sync_delay=1, batch_n=100):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.stop = False
        self.r = r
        self.r.setBatchMode(1)

        self.semaphore = threading.Semaphore() 
        self.q = []
        self.q_members = {}
        self.working_q = []
        self.working_q_members = {}

        self.store = store

        self.sync_delay = sync_delay
        self.batch_n = batch_n

    def __len__(self):
        return len(self.q_members) + len(self.working_q_members)

    def is_in(self, uid):
        flag = False        
        self.semaphore.acquire()
        flag = (uid in self.q_members) or (uid in self.working_q_members)
        self.semaphore.release()
        return flag
    
    def add(self, uid):
        self.semaphore.acquire()
        if not uid in self.q_members:
            self.q_members[uid] = 1
            self.q.append(uid)
        self.semaphore.release()        
        return

    def flush(self):
        entered = 0
        if self.q:
            entered = 1
            # log("FLUSH")
        while self.q:
            # log("q len: " + str(len(self.q)))
            self.working_q = []
            self.working_q_members = {}
            # log("Blocked on semaphore")                 
            self.semaphore.acquire()
            # log("- acquired")
            if len(self.q):
                self.working_q = self.q[:]
                for uid in self.working_q:
                    self.working_q_members[uid] = None
                self.q = []
                self.q_members = {}
            self.semaphore.release()                    
            # log("- released")
            if len(self.working_q):
                i = 0        
                while i < len(self.working_q):                    
                    i = i + 1
                    if i % self.batch_n == 0:
                        # log("Committing up to " + str(i))
                        self.r.commit()                       
                    uf = self.store.cache_get(self.working_q[i-1], safe=True)
                    #del self.working_q_members[uf.uuid]                    
                    self.r.setAttr(uf)
                # log("Committing leftovers")
                self.r.commit()
                self.working_q = []
                self.working_q_members = {}
        # if entered: log("EXIT FLUSH")        
        return

    def run(self):
        while not self.stop:
            time.sleep(self.sync_delay)
            self.flush()
        # log("Finishing WriteQueue")
        return
        

# there can be only one        
class CallBackQueue(threading.Thread):
    def __init__(self, sync_delay=1, callback=None):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.callback = callback
        self.stop = False
        self.q = Queue.Queue()
       
    #
    def add(self, uf):
	self.q.put(uf)

    #
    def run(self):
	while not self.stop:
	    uf = self.q.get(True)
	    try:
		self.callback(uf)
	    except:
                traceback.print_exc()
	    

# hostport should be a repository host and port number, e.g.,
#     replication.civium.net:80
# cachesize should be half the maximum  number of u-forms to hold in RAM
# sync_delay is the frequency with which u-forms are written back from the
#     cache.  If there are many writes, a large queue can develop and cause
#     the real delay to be longer.  This is the delay before the queue is
#     processed.
# batch_n is the number of u-forms to write in one transaction
# block_delay is the number of seconds a getAttr will be blocked waiting
#     for the u-form to arrive.  Pass -1 to wait forever.
class ListeningCachingRepository:

    def __init__(self, hostport=None, cachesize=1000,
                 sync_delay=1, batch_n=100, block_delay=30,
                 fast=False,function_hook=None,lcr_log_file=None):
        self.lcr = None
        self.lcr = ListeningCachingRepositoryImplementation(hostport,
                                                            cachesize,
                                                            sync_delay,
                                                            batch_n,
                                                            block_delay,
                                                            fast,function_hook,lcr_log_file)

    def __del__(self):
        # log("LCR being collected")
        if not self.lcr is None:
            self.lcr._finish()
        # log("LCR done being collected")
        return

    def lockUForm(self,uu):
        return self.lcr.wr.lockUForm(uu)

    def unlockUForm(self,uu):
        return self.lcr.wr.unlockUForm(uu)

    def getHostAndPort(self):
        return self.lcr.getHostAndPort()

    def getAttr(*l):
        self = l[0]
        return self.lcr.getAttr(*l[1:])

    def getUForm(self, uu):
	return self.lcr.getUForm(uu)

    def setAttr(*l):
        self = l[0]
        return self.lcr.setAttr(*l[1:])

    def setAttrNoListen(*l):
        self = l[0]
        return self.lcr.setAttrNoListen(*l[1:])            

    def listAttr(self, uf):
        return self.lcr.listAttr(uf)  

    def forgetUForm(self,uu):
        return self.lcr.delete_uf(uu)

    def knows(self, uf):
        return self.lcr.knows(uf)

    def cacheSize(self):
        return self.lcr.cacheSize()
        
    def flush(self):
        self.lcr.flush()

    def __len__(self):
        return len(self.lcr)

class ListeningCachingRepositoryImplementation:

    def __init__(self, hostport=None, cachesize=1000,
                 sync_delay=1, batch_n=100, block_delay=30,
                 fast=False,function_hook=None, lcr_log_file=None):
        self.fast = fast  
        self.cbq = None
        if function_hook:
            self.cbq = CallBackQueue(sync_delay,function_hook)
            self.cbq.start()
            
        self.listener = listener.Listener(hostport)
        self.listener.start()
        self.wr = repos.Repository(hostport)
        authenticate(self.wr)

        if block_delay == 0:
            raise BlockDelayIsZero
        self.block_delay = block_delay

        self.cache_semaphore = threading.Semaphore()
        self.cache = cache.Cache(cachesize)

        self.wq = WriteQueue(self.wr, self, sync_delay, batch_n)
        
        self.wq.start()
        def flush(x):
            self.flush()
        def rem(x):
            self.removeListener(x)
        self.cache.register_cleanup(flush)
        self.cache.register_remove(rem)

        self.interest_map_semaphore = threading.Semaphore()
        self.interest_map = {}

        self.listening_map = {}

        self.scheduler = Scheduler()
        self.scheduler.start()

        # register logging functions after everything else is setup
        try:
            if lcr_log_file:
                self.logger = LCRLogger(self, fobj=lcr_log_file)
                self.cache.register_cleanup(self.logger.logStartPurge)
                self.cache.register_cleanupdone(self.logger.logEndPurge)
            else:
                self.logger = None
        except:
            traceback.print_exc()

    # Private methods here
    def removeListener(self,uu):
        del self.listening_map[uu]
    
    def delete_uf(self, uu):
        self.cache.remove(uu)
    
    def update_uf(self, uf):
        if self.cbq:
            self.cbq.add(uf)
        log("Got update on " + uf.uuid.toString())
        if self.logger:
            self.logger.logCacheUpdate(uf.uuid, uf.get("shepherd_signature"))
        # empty update; drop it
        if not has_values(uf):
            log("Empty update; dropping")
            return
        # pending write on that u-form!  drop it
        if self.wq.is_in(uf.uuid):
            log("Pending write; dropping")
            return
        log("update is non-empty")
        try:                        
            self.cache_semaphore.acquire()
            cached_uf = self.cache.get(uf.uuid)
            if not cached_uf:
                self.cache.put(uf.uuid, uf)
            else:
                # mutate cache!
                # This works because we get the whole u-form every notify
                for k in cached_uf.keys(): # blow away existing keys
                    del cached_uf[k]
                for k in uf.keys(): # add new keys
                    cached_uf[k] = uf[k]         
            notifies = self.interest_map.get(uf.uuid, [])
            for notify in notifies:
                notify()

        finally:
            
            self.cache_semaphore.release()
            self.cache.clean()
        return

    def unblock(self, uid):
        notifies = self.interest_map.get(uid, [])
        for notify in notifies:
            notify()
        return

    def startListening(self, uid):
        
        if self.block_delay > -1:
            def unblock():
                self.unblock(uid)
                return
            self.scheduler.scheduleAfter(unblock, self.block_delay)
        if uid in self.listening_map:
            return
        self.listening_map[uid] = None
        self.listener.startListening(uid, self.update_uf)

        log("Started listening on " + uid.toString())
        return

    # WriteQueue uses this, so it's not really private
    def cache_get(self, uid, safe):
        
        self.cache_semaphore.acquire()        
        uf = self.cache.get(uid)
        if (not safe) and (not uf is None):
            uf = uf.copy()        
        self.cache_semaphore.release()
        
        return uf

    def cacheGetUForm(self, uf, safe=False):
        cacheGetUFormStartTime = time.time()
        
        cache_uf = self.cache_get(uf.uuid, safe)
        if cache_uf:
            if self.logger:
                self.logger.logCacheHit(uf.uuid)
                self.logger.logGetDuration(uf.uuid, time.time() - cacheGetUFormStartTime, True)
            return cache_uf
        else:
            if self.logger:
                self.logger.logCacheMiss(uf.uuid)

        # otherwise, block until it arrives or we're unblocked by timeout

        evt = threading.Event()
        evt.clear()

        def update_uf():
            evt.set()
            return

        uid = uf.uuid
        self.interest_map_semaphore.acquire()
        if self.interest_map.has_key(uid):
            self.interest_map[uid].append(update_uf)
        else:
            self.interest_map[uid] = [update_uf]
        self.interest_map_semaphore.release()
        if self.listening_map.has_key(uid):
            del self.listening_map[uid]
        self.startListening(uid)
	#print "Waiting for", uid
        evt.wait()
        cache_uf = self.cache_get(uid, safe)        
        self.interest_map_semaphore.acquire()
        if self.interest_map.has_key(uid):
            self.interest_map[uid].remove(update_uf)
        self.interest_map_semaphore.release()

        if self.logger:
            self.logger.logGetDuration(uf.uuid, time.time() - cacheGetUFormStartTime, False)
        return cache_uf

    def cacheSetAttr(self, uf, dontlisten=False):
        cacheSetUFormStartTime = time.time()

        try:
        
            self.cache_semaphore.acquire()
            cached_uf = self.cache.get(uf.uuid)
            if cached_uf:
            
                # mutate cache!
                for k in uf.keys():
                    cached_uf[k] = uf[k]
            else:
            
                self.cache.put(uf.uuid, uf.copy())
                if not dontlisten:
                    self.startListening(uf.uuid)
            self.wq.add(uf.uuid)
        finally:
        
            self.cache_semaphore.release()
            self.cache.clean()

        if self.logger:
            self.logger.logSetDuration(uf.uuid, time.time() - cacheSetUFormStartTime, cached_uf)
        return

    # Public partial repository API implemented below
        
    def getHostAndPort(self):
        return self.wr.getHostAndPort()

    def getUForm(self, uid):
	if uid is None: raise ValueError(uid)
	uf = uform.UForm(uid)
	uf = self.cacheGetUForm(uf, safe=True)
	if uf:
	    if self.fast:
		return uf
	    else:
		return deepcopy(uf)
	else:
	    raise TimeoutError(uid, self.getHostAndPort(), self.block_delay)

    def getAttr(*l):
        self = l[0]
        if len(l) == 2:
            uf = l[1]
            uid = uf.uuid
	    if uid is None: raise ValueError(uid)
            defaults = separateDefaults(uf)
            uf = self.cacheGetUForm(uf, safe=True)
            if uf:
                uf = mergeDefaults(uf, defaults)
                if self.fast:
                    return uf
                else:
                    return deepcopy(uf)
            else:
                raise TimeoutError(uid, self.getHostAndPort(), self.block_delay)
        elif len(l) == 3:
            uid = l[1]
            attr = l[2]
	    if uid is None: raise ValueError(uid)
            uf = uform.UForm(uid)
            uf[attr] = None
            uf = self.cacheGetUForm(uf, safe=True)
            if uf:
                if self.fast:
                    return uf.get(attr)
                else:
                    return deepcopy(uf.get(attr))
            else:
                raise TimeoutError(uid, self.getHostAndPort(), self.block_delay)
        return

    def setAttr(*l):
        self = l[0]
        if len(l) == 2:
            uf = l[1]
            self.cacheSetAttr(uf)
        elif len(l) == 4:
            uid = l[1]
	    if uid is None: raise ValueError(uid)
            attr = l[2]
            v = l[3]
            uf = uform.UForm(uid)
            uf[attr] = v
            self.cacheSetAttr(uf)
        return

    def setAttrNoListen(*l):
        self = l[0]
        if len(l) == 2:
            uf = l[1]
            self.cacheSetAttr(uf, dontlisten=True)
        elif len(l) == 4:
            uid = l[1]
	    if uid is None: raise ValueError(uid)
            attr = l[2]
            v = l[3]
            uf = uform.UForm(uid)
            uf[attr] = v
            self.cacheSetAttr(uf, dontlisten=True)
        return
        

    def listAttr(self, uf):
        if uuid.isa(uf):
            uf = uform.UForm(uf)
	if uf.uuid is None: raise ValueError(uf)
        uf = self.cacheGetUForm(uf, safe=True)
        if uf:
            return uf.keys()
        else:
            raise TimeoutError(uf.uuid, self.getHostAndPort(), self.block_delay)
        return

    def knows(self, uf):
        if uuid.isa(uf):
            uid = uf
        else:
            uid = uf.uuid
	    if uid is None: raise ValueError(uf)
        x = self.cache_get(uid, safe=True)
        if x and len(x.keys()):
            return True
        return False

    def _finish(self):
        #log("Running finish")
        self.flush()
        self.scheduler.stop = True
	if self.cbq:
	    self.cbq.stop = True # assume this works -- should check at some point
        self.listener.stop = True
        self.listener.startListening(uuid.UUID(), None) # poke it to get a recv
        self.wq.stop = True
        self.scheduler = None
        self.listener = None
        self.wq = None
        #log("Finish is done")
        return

    def flush(self):
        while len(self):            
            time.sleep(1)   
        return
    
    def cacheSize(self):
        return self.cache.cacheSize()

    def __len__(self):
        return len(self.wq)

class Scheduler(threading.Thread):

    def __init__(self, sleep_delay=1):
        threading.Thread.__init__(self)
        self.setDaemon(1)
        self.stop = False
        self.sleep_delay = sleep_delay
        self.run_q = []
        heapq.heapify(self.run_q)
        self.run_q_semaphore = threading.Semaphore()

    def scheduleAfter(self, f, delay):        
        self.run_q_semaphore.acquire()
        t = time.time() + delay
        heapq.heappush(self.run_q, (t, f))
        self.run_q_semaphore.release()        
        return

    def run(self):
        while not self.stop:
            time.sleep(self.sleep_delay)
            while self.run_q and (time.time() >= self.run_q[0][0]):                
                self.run_q_semaphore.acquire()
                (t,  f) = heapq.heappop(self.run_q)
                self.run_q_semaphore.release()                
                f()
        # log("Finishing Scheduler")
        return

# This is not much good if your data changes underneath you, but is simple.
# It is also not much good if you do a lot of writes, since writes kick
# things out of the cache.
class SimpleCachingRepository(repos.Repository):

    def __init__(self,
                 hostport=None,
                 authUF=None,
                 connection=None, 
                 batch=0,
                 cachesize=1000):
        repos.Repository.__init__(self, 
                                  hostport=hostport,
                                  authUF=authUF,
                                  connection=connection,
                                  batch=batch)
        self.c = cache.Cache(cachesize)

    def request(self, opcode, args):
        if opcode == repos.GETATTR:
            uf = args[0]

            defaults = separateDefaults(uf)
            
            answer = self.c.get(uf.uuid)
            if answer:
                answer = answer.copy()
                answer_keys = answer.keys()
                log("** answer keys: " + str(answer_keys))
                log("** reques keys: " + str(uf.keys()))
                flag = 1
                nuf = uform.UForm(uf.uuid)
                for k in uf.keys():
                    if k in answer_keys:
                        nuf[k] = answer[k]
                    else:
                        flag = 0
                        break
                if flag:
                    log("CACHE HIT")
                    return [mergeDefaults(nuf, defaults)]
                else:
                    log("CACHE MISS ON SOME ATTRS: Storing " +
                        uf.uuid.toString())
                    nanswer = repos.Repository.request(self, opcode, args)
                    new_uf = self.getUFormFormatResult(nanswer)
                    for k in new_uf.keys():
                        answer[k] = new_uf[k]
                    self.c.put(uf.uuid, answer.copy())
                    return [mergeDefaults(answer, defaults)]
            else:
                log("CACHE MISS: Storing " + uf.uuid.toString())
                nanswer = repos.Repository.request(self, opcode, args)
                new_uf = self.getUFormFormatResult(nanswer)
                self.c.put(uf.uuid, new_uf.copy())
		log("GOT UF:" + str(new_uf))
                return [mergeDefaults(new_uf, defaults)]
	elif opcode == repos.GETUFORM:
            uf = args[0]

            answer = self.c.get(uf.uuid)
            if answer:
		return [answer.copy()]
            else:
                log("CACHE MISS: Storing " + uf.uuid.toString())
                nanswer = repos.Repository.request(self, opcode, args)
                new_uf = self.getUFormFormatResult(nanswer)
                self.c.put(uf.uuid, new_uf.copy())
                return [new_uf]


        elif ((opcode == repos.SETATTR) or
              (opcode == repos.SETUFORM)):
            uf = args[0]
            log("DETECTED WRITE; DROPPING " + uf.uuid.toString())
            self.c.remove(uf.uuid)
            return repos.Repository.request(self, opcode, args)
        else:
            log("NON CACHED REPOSITORY OP " + str(opcode))
            return repos.Repository.request(self, opcode, args)

# not thread-safe; doesn't listen to underlying changes; batches writes
class AnotherCachingRepository:

    def __init__(self, r, cachesize=10000, writeback_size=500):
	self.r = r
	self.cache = cache.Cache(cachesize)

	self.writeback = {}
	self.writeback_size = writeback_size

    def get(self, uf):
	uid = uf.uuid
	if self.cache.get(uid):
	    if len(uf.keys()) == 0: # getUForm
		return deepcopy(self.cache.get(uid))
	    else:
		new_uf = uform.UForm(uid)
		found_uf = self.cache.get(uid)
		for k in uf.keys():
		    new_uf[k] = uf[k]
		    if k in found_uf:
			new_uf[k] = deepcopy(found_uf[k])
		return new_uf
	else:
	    new_uf = self.r.getUForm(uf.uuid)
	    self.cache.put(new_uf.uuid, new_uf)
	    self.cache.clean()
	    return self.get(uf)

    def getAttr(self, uid, attr=None):
	if uform.isa(uid):
	    return self.get(uid)
	else:
	    uf = uform.UForm(uid)
	    uf[attr] = None
	    return self.get(uf)[attr]

    def listAttr(self, uid):
	uf = self.get(uform.UForm(uid))
	if uf:
	    return uf.keys()
	return []

    def getUForm(self, uid):
	return self.get(uform.UForm(uid))

    def set(self, uf):
	uid = uf.uuid
	if self.cache.get(uid):
	    old_uf = self.cache.get(uid)
	    uf = deepcopy(uf)
	    for k in uf:
		old_uf[k] = uf[k]
	    self.writeback[uf.uuid] = old_uf
	    
	    if len(self.writeback) > self.writeback_size:
		self.flush()

	    return 0
	else: # not in the cache; write straight through
	    #print "Write-thru", uf.uuid
	    return self.r.setAttr(uf)

    def setAttr(self, uid, attr=None, value=None):
	if uform.isa(uid):
	    return self.set(uid)
	else:
	    uf = uform.UForm(uid)
	    uf[attr] = value
	    return self.set(uf)

    def knows(self, uid):
	if self.get(uform.UForm(uid)):
	    return True
	else:
	    return False

    def flush(self):
	self.r.setBatchMode(1)
	for uf in self.writeback.values():
	    self.r.setAttr(uf)
	self.r.commit()
	self.r.setBatchMode(0)
	self.writeback = {}
	return

    def __del__(self):
	self.flush()
	return

    
