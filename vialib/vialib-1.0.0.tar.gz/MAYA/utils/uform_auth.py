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
#
# This provides some example code to generate and verify
# u-form digital signatures.
#
from MAYA.utils import crypto
from MAYA.VIA import vsmf

# protocol type for default kind of signature
RSA_KEY_1 = 1

def canonical_sv(uu,sv):        
    if sv[0] != uu: sv.insert(0,uu) #add prefix uuid if it wasn't there
    tail = sv[2:]  #all entries other than head version (and uuid prefix) are sorted)
    tail.sort()
    return vsmf.serialize(sv[0:2] + tail)

#
# Given a uform verify that the signatures are valid.
# This does not verify if those signatures are found in ACL stuff
def dsig_verify_uform(rps, uu):
    x = rps.getAttr(uu,'shepherd_versions')
    l = rps.listAttrInfo(uu)
    writer_digest = ''
    writer_digest2 = ''
    owner_digest = ''
    ks = map(lambda a: a.lower().encode('utf8'), l.keys())
    ks.sort()
    sha_csv = crypto.SHA(canonical_sv(uu,x)).digest()

    for k in ks:
      # skip certain shepherd attrs
      if k.startswith('shepherd_') and k != 'shepherd_versions': continue
      writer_digest += k + l[k.decode('utf8')][0].getBuf()
      if k == 'shepherd_versions':
          writer_digest2 += k + sha_csv
      else:
          writer_digest2 += k + l[k.decode('utf8')][0].getBuf()
      if k in ('acu_list', 'acu_perm_owners', 'acu_owners'):
          owner_digest += k + l[k.decode('utf8')][0].getBuf()          

    # verify acu_owner_signature
    owner_valid = None
    sig = rps.getAttr(uu,'acu_owner_signature')
    if sig != None:
      protocol, dsig = sig  
      owner_cred, owner_dsig = dsig
      owner_pubkey = rps.getAttr(owner_cred,'rsa-publickey')
      owner_valid = crypto.rsa_verify(owner_digest,owner_dsig,owner_pubkey[1],owner_pubkey[0])

    # verify writer
    writer_valid = None
    sig = rps.getAttr(uu,'shepherd_signature')
    if (type(sig) == type(()) or type(sig) == type([])) and len(sig) > 2:
      cksum, protocol, dsig = sig
      writer_cred,writer_dsig = dsig
      writer_pubkey = rps.getAttr(writer_cred,'rsa-publickey')
      writer_valid = crypto.rsa_verify(writer_digest2,writer_dsig,writer_pubkey[1],writer_pubkey[0])
      if not writer_valid: # if not canonical valid -- try older non-canonical sv
          writer_valid = crypto.rsa_verify(writer_digest,writer_dsig,writer_pubkey[1],writer_pubkey[0])

    ret = [None,None]
    if owner_valid: ret[0] = owner_cred
    if writer_valid: ret[1] = writer_cred
    return ret

def dsig_sign_uform(rps, uu, writer_cred, writer_secret, canonical_sv_flag=True):
    # for some reason you have to make sure to look at the versions to get it
    # to update before you set the signature
    x = rps.getAttr(uu,'shepherd_versions')
    l = rps.listAttrInfo(uu)
    if canonical_sv_flag:        # re-serialize SV so that it is canonical - this is a step to fixup old 
        csv = canonical_sv(uu,x) # repositories that don't canonicalize sv
        l['shepherd_versions'] = (vsmf.Binary(crypto.SHA(csv).digest()),len(csv)) # replace with canonicalized chksum
    writer_digest = ''

    ks = map(lambda a: a.lower().encode('utf8'), l.keys())
    ks.sort()
    for k in ks:
      # skip certain shepherd attrs
      if k.startswith('shepherd_') and k != 'shepherd_versions': continue
      writer_digest += k + l[k.decode('utf8')][0].getBuf()

    writer_pubkey = rps.getAttr(writer_cred,'rsa-publickey')
    writer_dsig = vsmf.Binary(crypto.rsa_sign(writer_digest,writer_pubkey[1],writer_secret))
    # check secret validity (to verify secret key matches public key):
    writer_valid = crypto.rsa_verify(writer_digest,writer_dsig,writer_pubkey[1],writer_pubkey[0])
    if not writer_valid: raise "secret key incorrect match for credential"
    
    oldchksum = rps.getAttr(uu,'shepherd_signature')
    if type(oldchksum) == type([]) or type(oldchksum) == type(()):
        oldchksum = oldchksum[0]
        ## make sig a tuple if it wasn't:
        rps.setAttr(uu,'shepherd_signature',(oldchksum,))
    sig = (oldchksum,RSA_KEY_1,(writer_cred,writer_dsig))
    rps.setAttr(uu,'shepherd_signature',sig)    

def dsig_sign_uform_owner(rps, uu, owner_cred, owner_secret):
    l = rps.listAttrInfo(uu)
    owner_digest = ''
    ks = map(lambda a: a.lower().encode('utf8'), l.keys())
    ks.sort()
    for k in ks:
      if k in ('acu_list', 'acu_perm_owners', 'acu_owners',):
          owner_digest += k + l[k.decode('utf8')][0].getBuf()          
      
    owner_pubkey = rps.getAttr(owner_cred,'rsa-publickey')
    owner_dsig = vsmf.Binary(crypto.rsa_sign(owner_digest,owner_pubkey[1],owner_secret))
    # check secret validity:
    owner_valid = crypto.rsa_verify(owner_digest,owner_dsig,owner_pubkey[1],owner_pubkey[0])
    if not owner_valid: raise "secret key incorrect match for credential"
    rps.setAttr(uu,'acu_owner_signature',(RSA_KEY_1, (owner_cred,owner_dsig)))

def dsig_batch_sign_uform(r, uids, writer_cred, writer_secret,
                          writer_pubkey=None,
                          verify=False,
                          canonical_sv_flag=True
                          ):
    if not writer_pubkey:
        writer_pubkey = r.getAttr(writer_cred, 'rsa-publickey')

    r.setBatchMode(1)
    for uid in uids:
        r.getAttr(uid, 'shepherd_versions')
        r.listAttrInfo(uid)
        r.getAttr(uid, 'shepherd_signature')
    replies = r.commit(1)

    i = 0
    j = 0
    while i < len(replies):
        uid = uids[j]
        j += 1
        
        x = replies[i] #sv
        i += 1
        l = replies[i]
        i += 1
        oldchksum = replies[i]
        i += 1

        if canonical_sv_flag:
            csv = canonical_sv(uid,x) 
            l['shepherd_versions'] = (vsmf.Binary(crypto.SHA(csv).digest()),len(csv)) # replace with canonicalized chksum

        writer_digest = ''
        ks = map(lambda a: a.lower().encode('utf8'), l.keys())
        ks.sort()
        for k in ks:
            if k.startswith('shepherd_') and k != 'shepherd_versions': continue
            writer_digest += k + l[k.decode('utf8')][0].getBuf()

        writer_dsig = vsmf.Binary(crypto.rsa_sign(writer_digest,
                                                  writer_pubkey[1],
                                                  writer_secret))
        if verify:
            writer_valid = crypto.rsa_verify(writer_digest,
                                             writer_dsig,
                                             writer_pubkey[1],
                                             writer_pubkey[0])
            if not writer_valid:
                raise "secret key incorrect match for credential"

        if type(oldchksum) == type([]) or type(oldchksum) == type(()):
            oldchksum = oldchksum[0]
            r.setAttr(uid, 'shepherd_signature', (oldchksum,))
        sig = (oldchksum,RSA_KEY_1,(writer_cred,writer_dsig))
        r.setAttr(uid, 'shepherd_signature', sig)

    r.commit()
    r.setBatchMode(0)

    return

acu_attrs = ('acu_list', 'acu_perm_owners', 'acu_owners')
def dsig_batch_sign_uform_owner(r, uids, owner_cred, owner_secret,
                                owner_pubkey=None,
                                verify=False):
    if not owner_pubkey:
        owner_pubkey = r.getAttr(owner_cred, 'rsa-publickey')

    r.setBatchMode(1)
    for uid in uids:
        r.listAttrInfo(uid)
    replies = r.commit(1)

    i = 0
    for l in replies:
        uid = uids[i]
        i += 1

        owner_digest = ''
        ks = map(lambda a: a.lower().encode('utf8'), l.keys())
        ks.sort()
        for k in ks:
            if k in acu_attrs:
                owner_digest += k + l[k.decode('utf8')][0].getBuf()

        owner_dsig = vsmf.Binary(crypto.rsa_sign(owner_digest,
                                                 owner_pubkey[1],
                                                 owner_secret))
        if verify:
            owner_valid = crypto.rsa_verify(owner_digest,
                                            owner_dsig,
                                            owner_pubkey[1],
                                            owner_pubkey[0])
            if not owner_valid:
                raise "secret key incorrect match for credential"

        r.setAttr(uid, 'acu_owner_signature', (RSA_KEY_1, (owner_cred,
                                                           owner_dsig)))
    r.commit()
    r.setBatchMode(0)

    return
    
if __name__ == '__main__':
    import sys
    from MAYA.VIA import repos,uuid
    if len(sys.argv) < 2:
      print 'Usage: \n\tverify uuid\n\tsign uuid cred-uuid file-containing-secret\n\towner uuid cred-uuid file-containing-secret'
    elif sys.argv[1] == 'verify':
        rps = repos.Repository('joshua.maya.com:9889')
        uu = uuid._(sys.argv[2])
        print "Verifying ",uu
        v = dsig_verify_uform(rps, uu)
        print "VALID OWNER: ",v[0]
        print "VALID WRITER: ",v[1]

    elif sys.argv[1] == 'sign' or sys.argv[1] == 'owner':
        rps = repos.Repository('joshua.maya.com:9889')
        uu = uuid._(sys.argv[2])
        creduu = uuid._(sys.argv[3])

        acc_role = uuid._('~fd000a02510bfd4301b149')
        rls =         rps.getAttr(uu,'roles')
        if acc_role not in rls:
            rls.append(acc_role)
            rps.setAttr(uu,'roles',rls)
        
        secret = open(sys.argv[4],'rb').read()
        if sys.argv[1] == 'owner':
            print "Signing as Owner",uu
            v = dsig_sign_uform_owner(rps, uu, creduu, secret)
        else:
            print "Signing as Writer",uu
            v = dsig_sign_uform(rps, uu, creduu, secret)
        
