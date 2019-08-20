import redis
import cPickle as pickle
from MAYA.VIA.repos import *
from MAYA.VIA import vsmf

class ConflictException(Exception): pass
def compare_shepherd_versions(v1, v2):
    if not v1:
        return 1 if v2 else 0
    elif not v2:
        return -1
    if uuid.isa(v1[0]):
        v1 = v1[1:]
    if uuid.isa(v2[0]):
        v2 = v2[1:]
    venue_versions = dict(v1)
    rv = 0
    for vuu, vv2 in v2:
        vv1 = venue_versions.get(vuu, 0)
        if vv1 > vv2:
            if rv == 1:
                raise ConflictException
            rv = -1
        elif vv2 > vv1:
            if rv == -1:
                raise ConflictException
            rv = 1
    return rv

class CachingRepository(Repository):
    REPOS_OP_SETCOND = 119
    LOGGING = False
    UFORM_PRESENT = 0
    POISON_PILL = -1

    def __init__(self,
                 hostport=DEFAULT_HOST+":"+str(DEFAULT_PORT),
                 authUF=None,
                 connection=None,
                 batch=0):
        self.redis = redis.StrictRedis()
        return Repository.__init__(self,
                                   hostport=hostport,
                                   authUF=authUF,
                                   connection=connection,
                                   batch=batch)


    def __update_cache_if_necessary(self, uf):
        uuid_str = uf.uuid.toString()
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(uuid_str)
                    cached_entry = pipe.get(uuid_str)
                    if cached_entry:
                        # otherwise if not in cache, just write it
                        code, cached_uf = pickle.loads(cached_entry)
                        if code == self.UFORM_PRESENT:
                            rv = compare_shepherd_versions(cached_uf.get('shepherd_versions'), uf.get('shepherd_versions'))
                            if rv != 1:
                                # older or the same, so no reason to update cache
                                # make sure to return cached u-form
                                uf = cached_uf
                                # pipe reset should unwatch
                                break
                        elif code == self.POISON_PILL:
                            if self.LOGGING:
                                print 'cache has poison pill for: {}, do not write'.format(uuid_str)
                            # poison pill, do not write into cache
                            break
                    # if not short-circuited, write new contents to cache
                    pipe.multi()
                    pipe.set(uuid_str, pickle.dumps([self.UFORM_PRESENT, uf], pickle.HIGHEST_PROTOCOL))
                    pipe.execute()
                    break
                except redis.WatchError:
                    print "Got watch error on %s, retrying" % uuid_str
                    continue
                finally:
                    pipe.reset()
        return uf


    def __check_cached_entry(self, uuid_str, cached_entry):
        if cached_entry:
            code, cached_uf = pickle.loads(cached_entry)
            if code == self.UFORM_PRESENT:
                # only way not to return None
                return cached_uf
            elif code == self.POISON_PILL:
                # clear poison pill in readiness for repos fetch
                self.__set_poison_pill(uuid_str, False)
        return None


    def __set_poison_pill(self, uuid_str, flag):
        with self.redis.pipeline() as pipe:
            while True:
                try:
                    pipe.watch(uuid_str)
                    pipe.multi()
                    if flag:
                        pipe.set(uuid_str, pickle.dumps([self.POISON_PILL, None], pickle.HIGHEST_PROTOCOL))
                        if self.LOGGING:
                            print 'cache set poison pill for: {}'.format(uuid_str)
                    else:
                        pipe.delete(uuid_str)
                        if self.LOGGING:
                            print 'cache clear poison pill for: {}'.format(uuid_str)
                    pipe.execute()
                    break
                except redis.WatchError:
                    print "Got watch error on {}, retrying".format(uuid_str)
                    continue
                finally:
                    pipe.reset()


    def getAttr(self, uf, attr=""):
        if uuid.isa(uf) or type(uf) == type(""):
            uuid_str = uf.toString()
        elif uform.isa(uf):
            uuid_str = uf.uuid.toString()
        else:
            raise Exception("RepositoryError: (%s) invalid UForm or uuid"%(repr(uf)))

        cached_entry = self.redis.get(uuid_str)
        cached_uf = self.__check_cached_entry(uuid_str, cached_entry)
        if cached_uf:
            if self.LOGGING:
                print 'getAttr cache hit for: {}'.format(uuid_str)
            if not attr:
                return vsmf.UForm(cached_uf.uuid,
                                  {k: cached_uf.get(k) for (k, v) in uf.iteritems()})
            else:
                return cached_uf.get(attr)
        else:
            if self.LOGGING:
                print 'getAttr cache miss for: {}'.format(uuid_str)
            uf = makeUForm(uf)
            resp = self.request(GETUFORM, [uf])
            formatted_uform = self.getUFormFormatResult(resp)
            formatted_uform = self.__update_cache_if_necessary(formatted_uform)
            if not attr:
                return vsmf.UForm(formatted_uform.uuid,
                                  {k: formatted_uform.get(k) for (k, v) in uf.iteritems()})
            else:
                return formatted_uform.get(attr)


    def getUForm(self, uf):
        uuid_str = uf.toString()
        cached_entry = self.redis.get(uuid_str)
        cached_uf = self.__check_cached_entry(uuid_str, cached_entry)
        if cached_uf:
            if self.LOGGING:
                print 'getUForm cache hit for: {}'.format(uuid_str)
            return cached_uf
        else:
            if self.LOGGING:
                print 'getUForm cache miss for: {}'.format(uuid_str)
            uf = makeUForm(uf)
            resp=self.request(GETUFORM,[uf])
            formatted_uform = self.getUFormFormatResult(resp)
            formatted_uform = self.__update_cache_if_necessary(formatted_uform)
            return formatted_uform


    def getUForms(self, uuids):
        if not uuids:
            return []
        uuid_strs = [uuid.toString() for uuid in uuids]
        cached_entries = self.redis.mget(uuid_strs)
        ids_and_values = zip(uuids, uuid_strs, cached_entries)
        return_values = []

        cache_misses = 0
        for uuid, uuid_str, cached_entry in ids_and_values:
            cached_uform = self.__check_cached_entry(uuid_str, cached_entry)
            if cached_uform:
                if self.LOGGING:
                    print 'getUForms cache hit for: {}'.format(uuid_str)
                return_values.append([uuid, uuid_str, cached_uform])
            else:
                if self.LOGGING:
                    print 'getUForms cache miss for: {}'.format(uuid_str)
                cache_misses += 1
                request_uform = makeUForm(uuid)
                self.send([GETUFORM, request_uform])
                return_values.append([uuid, uuid_str, None])
        if cache_misses:
            for entry in return_values:
                uuid, uuid_str, uform = entry
                if uform is None:
                    uform = self.recv()[1]
                    uform = self.__update_cache_if_necessary(uform)
                    entry[2] = uform
        return return_values


    def setAttr(self, uf, attr='', val=None, append=False):
        # Invalidate redis cache
        if uuid.isa(uf) or type(uf) == type(""):
            uuid_str = uf.toString()
        elif uform.isa(uf):
            uuid_str = uf.uuid.toString()
        else:
            raise Exception("RepositoryError: (%s) invalid UForm or uuid"%(repr(uf)))

        self.redis.delete(uuid_str)
        if self.LOGGING:
            print 'setAttr cache invalidate for: {}'.format(uuid_str)

        rv = Repository.setAttr(self, uf, attr, val, append)
        if rv < 0:
            print "setAttr set %s failed with return value %d" % (uuid_str, rv)
        self.__set_poison_pill(uuid_str, True)

        return rv


    def setAttrCond(self, uf, aname=None, aval=None, cksum=None, append=False):
        # Invlidate redis cache
        if uuid.isa(uf) or type(uf) == type(""):
            uuid_str = uf.toString()
        elif uform.isa(uf):
            uuid_str = uf.uuid.toString()
        else:
            raise Exception("RepositoryError: (%s) invalid UForm or uuid"%(repr(uf)))

        self.redis.delete(uuid_str)
        if self.LOGGING:
            print 'setAttrCond cache invalidate for: {}'.format(uuid_str)

        rv = Repository.setAttrCond(self, uf, aname, aval, cksum, append)
        # if uuid.isa(uf) or type(uf) == type(""):
        #     rv = self.request(self.REPOS_OP_SETCOND, [vsmf.UForm(uf, {aname: aval}), cksum])[1]
        #     uf = vsmf.UForm(uf)
        # elif uform.isa(uf):
        #     rv = self.request(self.REPOS_OP_SETCOND, [uf, cksum])[1]
        #     uf = vsmf.UForm(uf.uuid)
        self.__set_poison_pill(uuid_str, True)

        return rv
