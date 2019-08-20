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

#
# Interfaces to Cypto stuff for use in VIA
#
from __future__ import absolute_import

# there are 2 ways to get the crypto behavior we rely upon:
# either pycrypt is installed or the _mpicrypt module (which Jeff wrote
# based on mpi code from the xyssl)

SHA = None
EMPTY_IV = '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
DEFAULT_RSA_SIZE=2048
try:
  import _mpicrypt
  USE_MPICRYPT=True
  try: 
    SHA = _mpicrypt.sha1
    SHA2 = _mpicrypt.sha256
    MD5 = _mpicrypt.md5
    def HMAC_SHA(k,m): return _mpicrypt.HMAC(20,k,m)
    def HMAC_SHA2(k,m): return _mpicrypt.HMAC(32,k,m)
    def HMAC_MD5(k,m): return _mpicrypt.HMAC(16,k,m)
  except: pass
except:
  print "No _mpicrypt found. Using pycrypto..."
  USE_MPICRYPT=False
if SHA is None: # find SHA1 elsewhere
  try:
    import hashlib
    SHA = hashlib.sha1
    SHA2 = hashlib.sha256
    MD5 = hashlib.md5
  except:
    import sha
    SHA = sha.new
  try:
    import hmac
    def HMAC_SHA(k,m): return hmac.new(k,m,SHA)
    def HMAC_SHA2(k,m): return hmac.new(k,m,SHA2)
    def HMAC_MD5(k,m): return hmac.new(k,m,MD5)
  except:
    pass

# this is: EMSA_PKCS1_v1.5 (with SHA1, or SHA256)
def msg_digest(msg,digest_type=1,cklen=128):
  if digest_type == 1: 
    m = SHA(msg).digest()
    hash_id = '\x00\x30\x21\x30\x09\x06\x05\x2b\x0e\x03\x02\x1a\x05\x00\x04\x14'
  elif digest_type == 2: # sha256  
    m = SHA2(msg).digest()    
    hash_id = '\x00\x30\x31\x30\x0d\x06\x09\x60\x86\x48\x01\x65\x03\x04\x02\x01\x05\x00\x04\x20'
  # later could add other digest types here...
  else:
    raise Exception("unknown digest type")
  return ''.join(("\x00\x01",("\xFF"*(cklen - 2 - len(hash_id) - len(m))),hash_id,m))

class CryptKey(object):
  def decrypt(self,m):
    return self.crypt(0,m)
  def encrypt(self,m):
    return self.crypt(1,m)
  def sign(self,msg,digest_type=1):
    return self.decrypt(msg_digest(msg,digest_type))
  def verify(self,msg,sig,digest_type=1):
    return msg_digest(msg,digest_type)[1:] == self.encrypt(sig)

if USE_MPICRYPT:
  # first try to get new impl
  try:
    from randbytes import get_random_bytes
  except:
    from randpool import RandomPool
    random_pool = RandomPool()
    get_random_bytes = random_pool.get_bytes

  class CryptKeyM(CryptKey):
    __slots__ = ('x',)
    def __init__(self,*a):
      self.x = _mpicrypt.key_import(*a)
    def crypt(self,encrypt_flag,m):
      return self.x.encrypt(encrypt_flag,m)
    def check(self,s):
      return self.x.check(s)

  def rsa_generate(keysize=DEFAULT_RSA_SIZE):
    return _mpicrypt.key_generate(keysize,get_random_bytes)

  def rsa_import_key(n,e,d=''):
    return CryptKeyM(n,e,d)

  def aes_generate(keysize=32):
    return get_random_bytes(keysize) # todo : provide get_random_bytes

  def aes_encrypt(msg, key, padto=16, cbc=False,IV=EMPTY_IV):
    if padto != 16: raise Exception("bad padding")
    if cbc:
        return _mpicrypt.aes_encrypt(key,5,msg,IV)
    else:
        return _mpicrypt.aes_encrypt(key,1,msg)

  def aes_decrypt(msg, key,cbc=False,IV=EMPTY_IV):
    if cbc:
        return _mpicrypt.aes_encrypt(key,4,msg,IV)
    else:
        return _mpicrypt.aes_encrypt(key,0,msg)

else:
  # requires some stuff from pycrypto:
  from Crypto.Util import number,randpool
  from Crypto.Cipher import AES
  from Crypto.PublicKey import RSA
  random_pool = randpool.RandomPool()
  get_random_bytes = random_pool.get_bytes

  ## RSA stuff
  class CryptKeyPC(CryptKey):
    __slots__ = ('n','e','d')
    def __init__(self,n,e,d=''): 
      self.n = number.bytes_to_long(n)
      self.e = number.bytes_to_long(e)
      self.d = number.bytes_to_long(d)
    def crypt(self,encrypt_flag,m):
      m = number.bytes_to_long(m)
      if self.n > m:
        if encrypt_flag: 
          inout = self.e
        else:
          inout = self.d
        return number.long_to_bytes(pow(m,inout,self.n))
      else: raise Exception("rsa_encrypt: source too big")
    def check(self,s):
      return number.bytes_to_long(s) == self.d
      

  def rsa_import_key(n,e,d=''):
    return CryptKeyPC(n,e,d)

  # returns (public_exponent, public_key, secret_key)
  def rsa_generate(keysize=DEFAULT_RSA_SIZE,l2b = number.long_to_bytes):
    rsa = RSA.generate(keysize,get_random_bytes)
    return l2b(rsa.e),l2b(rsa.n),l2b(rsa.d)

  # block end padding via PKCS#5/RFC2630/NIST 800-38a
  def aes_encrypt(msg, key, padto=16, cbc=False, IV=None):
    pad = padto - (len(msg)%padto)
    if pad == 0: pad = padto
    msg = msg + chr(pad)*pad
    if cbc:
       a = AES.new(key,mode=2,IV=IV)
    else:
       a = AES.new(key)
    return a.encrypt(msg)

  def aes_decrypt(msg, key, cbc=False, IV=None):
    if cbc:
       a = AES.new(key,mode=2,IV=IV)
    else:
       a = AES.new(key)
    res = a.decrypt(msg)
    return res[:-ord(res[-1])]

## This interface is slightly deprecated: it would be faster if you have a 
## key sitting around to use the:
## k = rsa_import_key(...)
## k.encrypt(...)  k.sign(...)  k.verify(...) interface since it will not have
## to re-load the key everytime
def rsa_encrypt(src,e,m):
  return rsa_import_key(m,e).encrypt(src)

def rsa_sign(msg, public, secret, digest_type=1):
  return rsa_import_key(public,'',secret).sign(msg,digest_type)

def rsa_verify(msg, sig, public, e, digest_type=1):
  return rsa_import_key(public,e).verify(msg,sig,digest_type)

## AES stuff
def aes_generate(keysize=32):
  return get_random_bytes(keysize)

## new PBKDF2 stuff...
def PRF_SHA(a,b):
  return SHA(a).update(b).digest()

def PRF_SHA2(a,b):
  return SHA2(a).update(b).digest()

def PBKDF2(P, S, c=2000, dkLen=16, PRF=PRF_SHA2):
  def binxor(a, b): return "".join([chr(ord(x) ^ ord(y)) for (x, y) in zip(a, b)])
  from struct import pack
  ret = ''
  i = 0
  while len(ret) < dkLen:
    i += 1
    U = S + pack("!L", i)
    UU = U
    for j in xrange(2, 1+c):
      U = PRF(P,U)
      UU = binxor(U,UU)
    ret += UU
  return ret[:dkLen]
  
## passphrase to key--
## converts pass-phrase to crypto key (ala RFC 2440: Iterated and Salted S2K)
## this version uses SHA1 as the hash (or SHA256)
## Note: we should update to http://en.wikipedia.org/wiki/PBKDF2
## (see code above)
def pp_key(passphrase, salt, count=256, keysize=16, offset=0, hash_type=1, method=0):
  t = salt + passphrase
  tl = len(t)
  if hash_type == 1: 
    s = SHA()
  elif hash_type == 2: 
    s = SHA2()
  else: raise Exception('unknown hash_type')
  if method == 0:
    if offset>0: s.update(chr(0)*offset)
    s.update(t)
    count -= tl
    while count > 0:
      if count >= tl:
        s.update(t)
      else:
        s.update(t[:count])
      count -= tl
    return s.digest()[:keysize]
  elif method == 1:
    return PBKDF2(passphrase, salt, count, keysize, PRF_SHA)
  elif method == 2:
    return PBKDF2(passphrase, salt, count, keysize, PRF_SHA2)
  else: raise Exception('unknown method',method)
      
## generate pass phrase salt
def pp_generate(salt_size=8):
  return get_random_bytes(salt_size)

def pp_protect_secret(passphrase, secret, count=256, salt=None, method=0):
  if salt == None: salt = pp_generate()
  secret = aes_encrypt(secret,pp_key(passphrase, salt, count, method=method))
  if method == 0:
    return salt,count,secret
  else:
    return method,salt,count,secret

def pp_retrieve_secret(passphrase, secured):
  if len(secured) == 3:
      salt,count,secret = secured
      method = 0
  else:
      method,salt,count,secret = secured      
  return aes_decrypt(secret,pp_key(passphrase, salt, count,method=method))






