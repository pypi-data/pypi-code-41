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

# $Id: scalablecoll.py 18048 2006-06-26 19:21:05Z higgins $

## Scalable Collection
##
## A scalable collection allows the representation of arbitrarily large
## collections in uform space.  This is accomplished through the use of
## a linked-list style structure, which yields slow seek times but fast
## appends.
##
## The recommended way to use this is to:
##      from MAYA.utils import scalablecoll
##      coll = scalablecoll.new(repos)
##
## The ScalableCollection object (which is created by the "new" function)
## supports most standard python list operations.  It also supports
## copy.copy(coll) for shallow copying, as well as "clear", "index", and
## "validate" functions.

from MAYA.VIA import uuid
from MAYA.VIA import uform
from MAYA.VIA import vsmf
from MAYA.utils.shepherding import waitForPresence
import string
import time
import traceback
import adhash

headRole = uuid._('~01b8b8d720d01e11d8a50d487872f16706')
segmentRole = uuid._('~01d2021300d01d11d8932f026153455feb')

DEFAULT_SEGMENT_SIZE = 100
DEFAULT_MAX_SPARES = 20

OutOfRange = "out of range in scalable collection"

# early iterations of this code screwed up the roles; this will fix it

def fixRoles(r, headuu):
    waitForPresence(r, headuu)
    roles = r.getAttr(headuu, 'roles') or []
    if not headRole in roles:
        roles.append(headRole)
        r.setAttr(headuu, 'roles', roles)

    curruu = r.getAttr(headuu, 'next_segment')
    while curruu:
        waitForPresence(r, curruu)
        roles = r.getAttr(curruu, 'roles') or []
        if not segmentRole in roles:
            roles.append(segmentRole)
            r.setAttr(curruu, 'roles', roles)
        curruu = r.getAttr(curruu, 'next_segment')
    return

# create a new scalable collection head segment

def create(r, headuu=None):
    if not headuu:
        headuu = uuid.UUID()
    else: # blow away existing values
        r.setAttr(headuu, 'members', [])
        r.setAttr(headuu, 'next_segment', None)

    r.setAttr(headuu, 'roles', [headRole])
    r.setAttr(headuu, 'head_segment', headuu)
    r.setAttr(headuu, 'preferred_segment_size', DEFAULT_SEGMENT_SIZE)
    updateHeader(r, headuu)
   
    return headuu


# given the UUID of a random segment, get the UUID of the head segment

def getHeadSegment(r, seguu):
    waitForPresence(r, seguu)
    return r.getAttr(seguu, 'head_segment')


# given the UUID of a random segment, get the UUID of the tail segment
    
def getTailSegment(r, seguu):
    curruu = getHeadSegment(r, seguu)
    waitForPresence(r, curruu)
    return r.getAttr(curruu, "tail_segment")


# given the UUID of a random segment, get the previously calculated
# hash of all the UUIDs in the collection    

def getStoredCollectionHash(r, seguu):
    headuu = getHeadSegment(r, seguu)
    waitForPresence(r, headuu)
    return r.getAttr(headuu, 'collection_member_hash') or ''
    
# given the UUID of a random segment, get the previously calculated
# number of members in the entire collection

def getStoredMemberCount(r, seguu):
    headuu = getHeadSegment(r, seguu)
    waitForPresence(r, headuu)
    return r.getAttr(headuu, 'collection_member_count') or 0
        

# given the UUID of a scalable collection head segment, calculate and
# store all the hashes in the collection (including the main collection hash),
# the member count, and the tail pointer

def updateHeader(r, headuu):
    digest = adhash.new()
    count = 0
    uu = headuu
    tail = headuu
    while (uu != None):
        tail = uu
        waitForPresence(r, uu)
        segdigest = adhash.new()
        members = r.getAttr(uu, 'members') or []
        count += len(members)
        for mem in members:
            segdigest.add(adhash.md5_hash(mem.getBuf()))
        digest.add(segdigest.getHash())
        r.setAttr(uu, 'segment_member_hash', vsmf.Binary(segdigest.getHash()))
        uu = r.getAttr(uu, 'next_segment')
    r.setAttr(headuu, 'tail_segment', tail)
    r.setAttr(headuu, 'collection_member_count', count)
    r.setAttr(headuu, 'collection_member_hash', vsmf.Binary(digest.getHash()))


# given the UUID of a tail segment, create a new (empty) tail segment and
# append it to the structure

def appendSegment(r, tailuu):
    waitForPresence(r, tailuu)
    headuu = getHeadSegment(r, tailuu)
    waitForPresence(r, headuu)
    spares = r.getAttr(headuu, 'spare_segments') or []
    if len(spares) > 0:
        uu = spares[0]
        r.setAttr(headuu, 'spare_segments', spares[1:])
    else:
        uu = uuid.UUID()
    uf = uform.UForm(uu, {'previous_segment':tailuu, 'head_segment':headuu, 'roles':[segmentRole], 'members':[], 'segment_member_hash':vsmf.Binary(adhash.new().getHash()), 'next_segment':None})
    r.setAttr(uf)
    r.setAttr(tailuu, 'next_segment', uu)
    r.setAttr(headuu, 'tail_segment', uu)
    return uu

# given the UUID of the head segment of a scalable collection and one
# or more new member UUIDs to add (new_members accepts either lists
# or UUIDs), append the new items to the end of the collection, creating
# new segments as necessary if the additions would cause the tail segment
# to exceed the number of members specified by max_segment_members.
# Pass updatehead=0 to skip the expensive updateHeader call.  Remember to call
# it later!
   
def append(r, headuu, new_members, updatehead=1, max_segment_members = DEFAULT_SEGMENT_SIZE):
    tailuu = getTailSegment(r, headuu)
    waitForPresence(r, tailuu)
    waitForPresence(r, headuu)
    headhash = adhash.new(r.getAttr(headuu, 'collection_member_hash'))
    headcount = r.getAttr(headuu, 'collection_member_count') or 0

    members = r.getAttr(tailuu, 'members') or []
    if type(new_members) == type([]):
        for mem in new_members:
            headcount = headcount + 1
            headhash.add(adhash.md5_hash(mem.getBuf()))
            members.append(mem)
    else:
        headcount = headcount + 1
        headhash.add(adhash.md5_hash(new_members.getBuf()))
        members.append(new_members)
    
    curruu = tailuu
    while len(members) > max_segment_members:
        old_tail_members = members[:max_segment_members]
        members = members[max_segment_members:]
        __setMembers(r, curruu, old_tail_members)
        curruu = appendSegment(r, curruu)

    __setMembers(r, curruu, members)    
    r.setAttr(curruu, 'members', members)

    headuf = uform.UForm(headuu, {'collection_member_count':headcount, 'collection_member_hash':vsmf.Binary(headhash.getHash())})
    r.setAttr(headuf)

    return

# sets the members of a segment and recomputes its hash from scratch
# assumes that the head hash has already been updated appropriately
    
def __setMembers(r, seguu, members):
    waitForPresence(r, seguu)
    r.setAttr(seguu, 'members', members)
    seghash = adhash.new()
    for mem in members:
        seghash.add(adhash.md5_hash(mem.getBuf()))
    r.setAttr(seguu, 'segment_member_hash', vsmf.Binary(seghash.getHash()))
    

# determine which segment an index value falls inside of, and compute
# the index relative to that segment

def segmentForIndex(r, headuu, index):
    currentOffset = 0
    uf = uform.UForm(headuu, ['collection_member_count', 'collection_member_hash'])
    waitForPresence(r, headuu)
    uf = r.getAttr(uf)
    memberCount = uf['collection_member_count'] or 0
    if (index < 0) or (index > memberCount):
        raise OutOfRange
    curr = headuu
    segMembers = r.getAttr(curr, 'members')
    while index > (currentOffset + len(segMembers) - 1):
        currentOffset = currentOffset + len(segMembers)
        curr = r.getAttr(curr, 'next_segment')
        waitForPresence(r, curr)
        segMembers = r.getAttr(curr, 'members')
        
    return (curr, index - currentOffset)

# get the item at the specified index
# DO NOT use this for iteration, as you will be a very unhappy camper!

def get(r, headuu, index):
    if (index < 0):
        length = r.getAttr(headuu, 'collection_member_count') or 0
        index = length + index
    seguu, segidx = segmentForIndex(r, headuu, index)
    members = r.getAttr(seguu, 'members')
    return members[segidx]

# remove the item at the specified index from the scalable collection
    
def remove(r, headuu, index):
    seguu, segidx = segmentForIndex(r, headuu, index)
    headhash = r.getAttr(headuu, 'collection_member_hash')
    memberCount = r.getAttr(headuu, 'collection_member_count')
    seghash = r.getAttr(seguu, 'segment_member_hash')
    members = r.getAttr(seguu, 'members')
    item = members[segidx]
    del members[segidx]
    headhash = adhash.removeValue(headhash, item.getBuf())
    seghash = adhash.removeValue(seghash, item.getBuf())
    memberCount = memberCount - 1
    r.setAttr(headuu, 'collection_member_hash', vsmf.Binary(headhash))
    r.setAttr(headuu, 'collection_member_count', memberCount)
    r.setAttr(seguu, 'members', members)
    r.setAttr(seguu, 'segment_member_hash', vsmf.Binary(seghash))
    return item
    
def replace(r, headuu, index, value):
    seguu, segidx = segmentForIndex(r, headuu, index)
    headhash = r.getAttr(headuu, 'collection_member_hash')
    seghash = r.getAttr(seguu, 'segment_member_hash')
    members = r.getAttr(seguu, 'members')
    item = members[segidx]
    headhash = adhash.removeValue(headhash, item.getBuf())
    seghash = adhash.removeValue(seghash, item.getBuf())
    members[segidx] = value
    headhash = adhash.addValue(headhash, value.getBuf())
    seghash = adhash.addValue(seghash, value.getBuf())
    r.setAttr(headuu, 'collection_member_hash', vsmf.Binary(headhash))
    r.setAttr(seguu, 'members', members)
    r.setAttr(seguu, 'segment_member_hash', vsmf.Binary(seghash))
    return item

# apply the function f to every uuid in the scalable collection.
# it can be useful to pass a closure, or an object method, in order
# to carry state along with you (e.g., keep a count of some value).
# this is not the most efficient thing to do, because it prevents you
# from pipelining independent accesses
    
def sc_apply(r, headuu, f):
    curruu = headuu

    while curruu:
        waitForPresence(r, curruu)
        members = r.getAttr(curruu, 'members') or []
        map(f, members)
        curruu = r.getAttr(curruu, 'next_segment')

    return

# Be careful of this!  It could return a huge number of items

def getAllMembers(r, headuu):
    all = []
    def g(uid):
        all.append(uid)
        return
    sc_apply(r, headuu, g)
    return all

SLICE_TYPE = type(slice(0))

def new(repository, head_segment_uuid = None):
    return ScalableCollection(repository, head_segment_uuid)

class ScalableCollection:
    def __init__(self, repository, head_segment_uuid = None):
        self.r = repository
        self.head = head_segment_uuid
        self.segment_size = DEFAULT_SEGMENT_SIZE
        self.max_spares = DEFAULT_MAX_SPARES
        
        if not self.head:
            self.head = create(self.r)
            
        waitForPresence(self.r, self.head)
        self.segment_size = self.r.getAttr(self.head, 'preferred_segment_size') or DEFAULT_SEGMENT_SIZE
        roles = self.r.getAttr(self.head, 'roles') or []
        if not (headRole in roles):
            roles.append(headRole)
            uf = uform.UForm(self.head, {'head_segment':self.head, 'tail_segment':self.head, 'roles':roles})
            self.r.setAttr(uf)
            updateHeader(self.r, self.head)
    
    def setPreferredSegmentSize(self, new_size):
        self.segment_size = new_size
        waitForPresence(self.r, self.head)
        self.r.setAttr(self.head, 'preferred_segment_size', new_size)
    
    def __len__(self):
        waitForPresence(self.r, self.head)
        return self.r.getAttr(self.head, 'collection_member_count') or 0
    
    def append(self, new_item):
        append(self.r, self.head, new_item, 1, self.segment_size)
    
    def __getitem__(self, index):
        if type(index) == SLICE_TYPE:
            if index.step:
                raise OutOfRange
            results = []
            itr = ScalableCollectionIterator(self.r, self.head)
            startidx = index.start
            endidx = index.stop or len(self)
            seguu, segidx = segmentForIndex(self.r, self.head, startidx)
            itr.jump(seguu, segidx)
            idx = startidx
            while (idx < endidx):
                results.append(itr.next())
                idx = idx + 1
            return results
            
        return get(self.r, self.head, index)
        
    def __setitem__(self, index, value):
        return replace(self.r, self.head, index, value)

    def __delitem__(self, index):
        remove(self.r, self.head, index)
        
    def __iter__(self):
        return ScalableCollectionIterator(self.r, self.head)
    
    # clears collection contents    
    def clear(self):
        r = self.r
        head = self.head
        waitForPresence(r, head)
        next = r.getAttr(head, 'next_segment') or None
        spare = r.getAttr(head, 'spare_segments') or []
        headuf = uform.UForm(head, {'next_segment':None, 'tail_segment':head, 'members':[]})
        r.setAttr(headuf)
        while next:
            waitForPresence(r, next)
            r.setAttr(next, 'members', [])
            spare.append(next)
            next = r.getAttr(next, 'next_segment') or None
        r.setAttr(head, 'spare_segments', spare[:self.max_spares])
        updateHeader(r, head)
        
    # redistributes the members so that all but the last segment have
    # a member count equal to self.segment_size
    # not particularly elegant, and not memory-efficient, but it should do the job
    
    def rebalance(self):
        members = list(self)
        self.clear()
        self.append(members)
    
    # calculates average deviation from ideal segment size
    # (excluding the tail segment, since it's probably half-full)
    # returns float >= 0.0; 0 means completely balanced, 1.0 means 100% difference from ideal segment size
        
    def calcSegmentSizeDeviation(self):
        sum = 0
        count = 0
        r = self.r
        curr = self.head
        
        while curr:
            waitForPresence(r, curr)
            uf = uform.UForm(curr, ['next_segment', 'members'])
            uf = r.getAttr(uf)
            curr = uf['next_segment']
            if uf['next_segment']:
                sum = sum + abs(len(uf['members'] or []) - self.segment_size)
                count = count + 1

        if count == 0:
            return 0.0
        
        return (float(sum)/float(count))/float(self.segment_size)
        
    # for use by the system copy.copy() function to perform a shallow copy    
    
    def __copy__(self):
        other = ScalableCollection(self.r)
        itr = ScalableCollectionIterator(self.r, self.head)
        buf = []
        try:
            while True:
                item = itr.next()
                buf.append(item)
                if (len(buf) >= 500):
                    other.append(buf)
                    buf = []
        except StopIteration:
            other.append(buf)
        return other
            
    # returns the index of the first instance of the given value in the collection
        
    def index(self, value):
        idx = 0
        for val in self:
            if val == value:
                return idx
            idx = idx + 1
        return -1
    
    # validates the structure, throws a ValidationException on problems
        
    def validate(self):
        validate(self.r, self.head)
        
class ScalableCollectionIterator:
    def __init__(self, repository, head_segment_uuid):
        self.r = repository
        self.head = head_segment_uuid
        self.segidx = 0
        self.seguf = self.__loadseg(self.head)
        
    def __loadseg(self, seguu):
        waitForPresence(self.r, seguu)
        uf = uform.UForm(seguu, ['next_segment', 'members'])
        uf = self.r.getAttr(uf)
        return uf
        
    def __iter__(self):
        return self
    
    def jump(self, segment_uuid, segment_index):
        self.segidx = segment_index
        self.seguf = self.__loadseg(segment_uuid)
        
    def next(self):
        while (self.segidx >= len(self.seguf['members'] or [])):
            if self.seguf['next_segment'] == None:
                raise StopIteration
	    elif self.seguf['next_segment'] == self.seguf.uuid:
		raise StopIteration
            self.segidx = 0
            self.seguf = self.__loadseg(self.seguf['next_segment'])
        
        result = (self.seguf['members'] or [])[self.segidx]
        self.segidx = self.segidx + 1
        return result

class ValidationException(Exception):
    pass

def validate(r, headuu):
    waitForPresence(r, headuu)
    headuf = uform.UForm(headuu, ['collection_member_count', 'collection_member_hash', 'previous_segment', 'head_segment', 'next_segment', 'roles', 'segment_member_hash', 'members'])
    headuf = r.getAttr(headuf)
    totalCount = 0
    totalHash = adhash.new()
    headCount = headuf['collection_member_count'] or 0
    headHash = headuf['collection_member_hash']
    headstr = headuf.uuid.toString()
    
    seguf = headuf
    prevuu = None
    done = 0
    while not done:
        segstr = seguf.uuid.toString()
        if seguf['head_segment'] == seguf.uuid:
            if not (headRole in seguf['roles']):
                raise ValidationException('header ' + segstr + ' does not play header role')
        else:
            if not (segmentRole in seguf['roles']):
                raise ValidationException('segment ' + segstr + ' does not play segment role')
        if (seguf['previous_segment'] != prevuu):
            raise ValidationException('segment ' + segstr + ' has incorrect previous segment')
        if (seguf['head_segment'] != headuf.uuid):
            raise ValidationException('segment ' + segstr + ' has incorrect head segment')
        
        members = seguf['members'] or []
        totalCount = totalCount + len(members)
        segHash = adhash.new()
        for mem in members:
            if type(mem) == type(''):
                memhash = adhash.md5_hash(mem)
            else:
                memhash = adhash.md5_hash(mem.getBuf())
            totalHash.add(memhash)
            segHash.add(memhash)
        
        if str(segHash.getHash()) != str(seguf['segment_member_hash']):
            raise ValidationException('segment hash out of date in ' + segstr)
        
        if not seguf['next_segment']:
            done = 1
        else:
            prevuu = seguf.uuid
            seguf = uform.UForm(seguf['next_segment'], ['roles', 'members', 'previous_segment', 'next_segment', 'head_segment', 'segment_member_hash'])
            waitForPresence(r, seguf.uuid)
            seguf = r.getAttr(seguf)
    
    if totalCount != headCount:
        raise ValidationException('actual count of ' + str(totalCount) + ' does not match header count of ' + str(headCount) + ' in ' + headstr)
    if str(totalHash.getHash()) != str(headHash):
        raise ValidationException('actual hash does not match header hash')
                
        
