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

# $Id: signing.py 35013 2008-10-07 20:55:16Z vanstone $
# This file contains a bunch of utility functions which are useful for signing.
# Be sure to call enableSignatureReads() on a repository before trying any of the other functions on it!

from MAYA.utils import uform_auth
from MAYA.VIA import uuid, uform
from MAYA.utils.shepherding import waitForPresence
from MAYA.utils import roles
from MAYA.utils import scalablecoll
from MAYA.utils import crypto
from MAYA.VIA import vsmf
from MAYA.utils.indexing import hier_index, hier_index_iterator

ACU_ROLE = uuid._('~fd000a02510bfd4301b149') # access-controlled uform role
ACL_ROLE = uuid._('~fd000a02510bfd6ccc319d') # access control list role

# Creates a dictionary containing both the UUID of the credential (as "public") and the bytes of the private signature 
# (as "private").  Will raise an exception if the public and private keys don't appear to match.
#
# repos - repository containing the public credential
# creduu - the UUID of the credential to load
# credfilename - the filename of a simple binary file containing the private key
# returns - a dictionary containing the two

def loadCredential(repos, creduu, credfilename):
    cred = {'public':creduu}
    cred['private'] = open(credfilename, 'rb').read()
    pubkey = repos.getAttr(cred['public'], 'rsa-publickey')
    secret = cred['private']
    digest = 'abc'
    sig = vsmf.Binary(crypto.rsa_sign(digest, pubkey[1], secret))
    match = crypto.rsa_verify(digest, sig, pubkey[1], pubkey[0])
    if not match:
        raise "public and private keys didn't match"

    return cred

# Does the magic which is required to access the shepherding attributes when they're signed.
#
# repos - the repository on which the magic incantation is to be performed
    
def enableSignatureReads(repos):
    auf = uform.UForm()
    auf['client_type'] = ['authenticated', 1]
    repos.authenticate(auf)
    
# Determines whether a given uform is signed.  Checks only the form of the uform, not the validity of the signature.
#
# repos - the repository
# targetuu - the UUID of the uform to be checked
# returns - boolean value; True if signature attributes "look" right, False if the uform appears to be unsigned

def isSigned(repos, targetuu):
    enableSignatureReads(repos)
    waitForPresence(repos, targetuu)
    uf = uform.UForm(targetuu, ['shepherd_signature', 'acu_owner_signature', 'roles'])
    uf = repos.getAttr(uf)
    hasAcuRole  = roles.plays_role(repos, targetuu, ACU_ROLE)
    hasOwnerSig = bool(uf['acu_owner_signature'])
    hasProperSig = type(uf['shepherd_signature']) == type([])
    return hasAcuRole and hasOwnerSig and hasProperSig
    
# Sets the credential "cred" as the sole owner, and attaches the given acu_list to specify the list of writers.
# DON'T USE THIS ON SIGNED UFORMS unless you know what you're doing, as it will replace any existing signature.
#
# repos - the repository
# targetuu - the UUID of the uform to be signed
# cred - credential dictionary obtained by loadCredential function
# acu_list - the UUID of an access control list uform
    
def addSignature(repos, targetuu, cred, acu_list = None):
    waitForPresence(repos, targetuu)
    repos.lockUForm(targetuu)
    roles.ensure_role(repos, targetuu, ACU_ROLE)
    uf = uform.UForm(targetuu)
    if (acu_list):
        uf['acu_list'] = acu_list
    uf['acu_owners'] = [cred['public']]
    repos.setAttr(uf)
    uform_auth.dsig_sign_uform_owner(repos, targetuu, cred['public'], cred['private'])
    uform_auth.dsig_sign_uform(repos, targetuu, cred['public'], cred['private'])
    waitForPresence(repos, targetuu)
    uform_auth.dsig_sign_uform(repos, targetuu, cred['public'], cred['private'])
    repos.unlockUForm(targetuu)


def ensureSignature(repos, targetuu, cred, acu_list = None):
    if not isSigned(repos, targetuu):
        addSignature(repos,targetuu,cred,acu_list)
    else: 
        acu_owners = repos.getAttr(targetuu,'acu_owners')
        if not cred['public'] in acu_owners:
            signUForm(repos,targetuu,cred)
        else:
            ownerSignUForm(repos,targetuu,cred)

def ownerSignUForm(repos,targetuu,cred):
    waitForPresence(repos, targetuu)
    repos.lockUForm(targetuu)
    roles.ensure_role(repos, targetuu, ACU_ROLE)
    uf = uform.UForm(targetuu)
    uform_auth.dsig_sign_uform_owner(repos, targetuu, cred['public'], cred['private'])
    uform_auth.dsig_sign_uform(repos, targetuu, cred['public'], cred['private'])
    waitForPresence(repos, targetuu)
    uform_auth.dsig_sign_uform(repos, targetuu, cred['public'], cred['private'])
    repos.unlockUForm(targetuu)


# Signs the uform using the given credential.  Does not replace or modify the owners sig or attributes
#
# repos - the repository
# targetuu - the UUID of the uform to be signed
# cred - credential dictionary obtained by loadCredential function
# acu_list - the UUID of an access control list uform

def signUForm(repos, targetuu, cred):
    waitForPresence(repos,targetuu)
    repos.lockUForm(targetuu)
    uform_auth.dsig_sign_uform(repos, targetuu, cred['public'], cred['private'])
    waitForPresence(repos, targetuu)
    uform_auth.dsig_sign_uform(repos, targetuu, cred['public'], cred['private'])
    repos.unlockUForm(targetuu)

# Signs any members of a collection that aren't presently signed.
#
# repos - the repository
# coll - the UUID of a uform playing the role collection
# cred - a credential object created using loadCredential()
# acu_list - (optional) the UUID of a uform playing the role ACL_ROLE
    
def signCollectionMembers(repos, coll, cred, acu_list = None):
    waitForPresence(repos, coll)
    members = repos.getAttr(coll, 'members')
    for mem in members:
        if not isSigned(repos, mem):
            addSignature(repos, mem, cred, acu_list)
            
# Signs any members of a scalable collection that aren't presently signed.
#
# repos - the repository
# coll - the UUID of a uform playing the role scalable collection head segment
# cred - a credential object created using loadCredential()
# acu_list - (optional) the UUID of a uform playing the role ACL_ROLE
                
def signScalableCollMembers(repos, colluu, cred, acu_list = None):
    coll = scalablecoll.new(repos, colluu)
    for mem in coll:
        if not isSigned(repos, mem):
            addSignature(repos, mem, cred, acu_list)
            
# Recursively traverses a given uform and its children, signing any unsigned ones it finds using the given credential
#
# repos - the repository
# startuu - the UUID of the uform from which to start exploring
# cred - a credential produced by the loadCredential method
# acu_list - (optional) UUID of a uform playing the role ACL_ROLE
# verbose - set to True to print debugging output to the console
# seenset - recursion parameter for keeping track of which uforms have already been processed--don't use
            
def recursiveSignUnsigned(repos, startuu, cred, acu_list = None, verbose = False, seenset = None):
    if (seenset == None):
        seenset = {}
        
    if (seenset.has_key(startuu)):
        return
        
    seenset[startuu] = True
    
    if (verbose):
        print 'processing ' + startuu.toString()
    waitForPresence(repos, startuu)
    if not isSigned(repos, startuu):
        if (verbose):
            print '\tadding signature'
        addSignature(repos, startuu, cred, acu_list)
    try:
        if (roles.plays_role(repos, startuu, roles.scalable_collection_head_role)):
            if (verbose):
                print '\tdescending into scalable collection members'
            coll = scalablecoll.new(repos, startuu)
            for mem in coll:
                recursiveSignUnsigned(repos, mem, cred, acu_list, verbose, seenset)
        elif (roles.plays_role(repos, startuu, roles.collection_role)):
            if (verbose):
                print '\tdescending into collection members'
            members = repos.getAttr(startuu, 'members') or []
            for mem in members:
                recursiveSignUnsigned(repos, mem, cred, acu_list, verbose, seenset)
    except:
        pass
        
def signHierIndex(repos, index_root, cred, acu_list = None, verbose = False):
    def memberHandler(uu):
        recursiveSignUnsigned(repos, uu, cred, acu_list, verbose)
        
    index = hier_index.HIndexReader(repos, index_root)
    iterator = hier_index_iterator.HierIndexIterator(index, memberHandler)
    iterator.iterate()


# Determines whether targetuu is owned by creduu
#

def isOwned(repos, targetuu, creduu):
    enableSignatureReads(repos)
    waitForPresence(repos, targetuu)
    if not isSigned(repos, targetuu):
        return False
    else:
        uf = uform.UForm(targetuu, ['acu_owners'])
        uf = repos.getAttr(uf)
        try:
            return bool(creduu in uf['acu_owners'])
        except TypeError:
            # uf.acu_owners not a sequence
            return False

def inACUList(repos, acu_lists, creduu):
    """Determines whether creduu is in any of the acu_lists. 
       Acu_lists can be none or a single UUID."""
    if uuid.isa(acu_lists):
        acu_lists = [ acu_lists ]
    try:
        for acluu in acu_lists:
            if not uuid.isa(acluu):
                continue
            waitForPresence(repos, acluu)
            if not roles.plays_role(repos, acluu, ACL_ROLE):
                continue
            writers = repos.getAttr(acluu, 'acu_writers') or []
            if writers and (creduu in writers):
                return True
    except TypeError:
        pass # acu_list attribute was neither a list, nor a uuid
    return False
    
# Determines whether targetuu is writeable by creduu
#
def isWriteable(repos, targetuu, creduu):
    enableSignatureReads(repos)
    waitForPresence(repos, targetuu)

    if not isSigned(repos, targetuu):
        return True
    elif isOwned(repos, targetuu, creduu):
        return True
    else:
        uf = uform.UForm(targetuu, ['acu_list'])
        uf = repos.getAttr(uf)
        acu_lists = uf['acu_list'] or []
        return inACUList(repos, acu_lists, creduu)
