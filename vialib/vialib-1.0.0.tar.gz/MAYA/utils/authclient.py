import socket, struct, binascii
from MAYA.VIA import vsmf
try:
  from MAYA.utils import crypto
except ImportError: 
  pass

__all__ = ['AuthAPI']

# public credential for Civium authserver
_AUTHSERVER_CRED = [vsmf.Binary('\x01\x00\x01'),vsmf.Binary('\x84A\x05\x8b2\x88\r\xabpv\xe8R\xc8\xe3\xec\xa0\xe3\xe0\xe0\xddoF\x9d\x94\x03K\\,H\xc8[9\xbb~\xab\xc9\xc6\xa6\xad~\xcf\xd4\xd2\xb8\xc3\xf2\xd0\x9b5\xf3\xeb\x84\xbf\xc6u.\xd6hN0\x8bQ\xad,\xda\x19\xb2zE\x98B\xa3\x88/\xed*\x13\x1c\xad\x1f\x7f\x02\xb4\xd8J\x9a\n\xb6\xa3|\x0b\x92nr\x86\x10l\x83\x06\xa4+6\x12?p\x8bT\x0c\xe7rU\xa51u\x91g\xf7\xf1+vB\xcf\xb3S\x0379%')]

class AuthClient:
  def __init__(self,addr,encrypted=1):
    self.addr = addr
    self.encrypted = encrypted
    self.reinit()

  def reinit(self):
    self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.s.connect(self.addr)
    self.aes = None
    if self.encrypted: 
      self.encrypt(self.encrypted>1)

  def encrypt(self,rotate=0):
    ## set up encryption
    self.pubkey = _AUTHSERVER_CRED
    self.aes = crypto.aes_generate()
    self.rotatekey = rotate
    
  def send_msg(self,m):
    p = vsmf.serialize(m)
    if self.aes != None:
      p = vsmf.Binary(crypto.aes_encrypt(p,self.aes))
      key = vsmf.Binary(crypto.rsa_encrypt(self.aes,self.pubkey[0],self.pubkey[1]))
      p = vsmf.serialize(('encrypted',key,p))
    pp = struct.pack(">I",len(p)) + p
    self.s.send(pp)

  def read_msg(self):
    b = ''
    while(len(b) < 4):
      b = self.s.recv(4-len(b))
    l = struct.unpack(">I",b)[0]
    b = ''
    while(len(b) < l):
      b = self.s.recv(l-len(b))
    p = vsmf.reconstitute(b)
    return self.decrypt(p)
  
  def decrypt(self,p):
    if self.aes != None:
      if p[0] != 'encrypted':
        raise Exception("warning: server did not encrypt",p)
      else:
        p = crypto.aes_decrypt(p[1],self.aes)
        p = vsmf.reconstitute(p)
        if self.rotatekey:
          self.aes = crypto.aes_generate()
    return p
      
  def rpc(self,m):
    self.send_msg(m)
    return self.read_msg()


class HttpAuthClient(AuthClient):
  def __init__(self,addr,encrypted=1):
    self.addr = addr
    self.encrypted = encrypted
    
  def send_msg(self,m):
    self.reinit()
    p = vsmf.serialize(m)
    if self.aes != None:
      p = vsmf.Binary(crypto.aes_encrypt(p,self.aes))
      key = vsmf.Binary(crypto.rsa_encrypt(self.aes,self.pubkey[0],self.pubkey[1]))
      p = vsmf.serialize(('encrypted',key,p))
    pp = 'request='+self.webquote(binascii.b2a_base64(p))
    ppp = "POST /request HTTP/1.1\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: %d\r\n\r\n" % (len(pp),) + pp
    self.s.send(ppp)

  # a somewhat pessimistic version
  def webquote(self,a):
    ret = ''
    for c in a:
      if ord(c) > ord('z') or ord(c) < ord('A'):
        c = '%%%02X'%ord(c)
      ret += c
    return ret

  def read_msg(self):
    b = ''
    while 1:
      try:
        x = self.s.recv(100000)
      except:
        x = None
      if x == None or x == '': break
      b += x
    b = binascii.a2b_base64(b)
    p = vsmf.reconstitute(b)    
    return self.decrypt(p)

class AuthAPI(HttpAuthClient):
  def check_password(self,email,passwd):
    try:
      x = self.rpc(('queryaccount', {'email':email}))
      idnum =  x[1][0]['id']
      x = self.rpc(('getkeychain',idnum,passwd))
      if x[0] == 'keychain':
        return 1
    except:
      pass
    return 0

  def get_accountid(self,email):
    try:
      x = self.rpc(('queryaccount', {'email':email}))
      return x[1][0]['id'], x[1][0]['user']
    except:
      pass
    return None

  def login(self,aid,password):
    try:
      y = self.rpc(('getkeychain',aid,password))
      return y
    except:
      pass
    return None

  def check_verified(self,email):
    try:
      x = self.rpc(('queryaccount', {'email':email}))
      idnum =  x[1][0]['id']
      return x[1][0].get('email_verified')
    except:
      pass
    return 0

  def new_account(self,email,passwd,firstname,lastname,template_type=None,send_verify=1):
    try:
      d = {'email':email, 'password':passwd, 'family_name':lastname, 'given_name':firstname}
      if template_type != None: d['template_type'] = template_type
      x = self.rpc(('register', d))
      print x
      if x[0] == 'registered':
        user,idnum = x[1:]
        if send_verify:
          x = self.rpc(('emailverify',idnum,user))
          if x[1] != 'ok': 
            print "Verify didn't work"
            pass # should maybe signal problem here
        return user,idnum
    except:
      return None

  def change_password(self,email,passwd,newp):
    try:
      x = self.rpc(('queryaccount', {'email':email}))
      idnum =  x[1][0]['id']
      x = self.rpc(('changepassword',idnum,passwd,newp))
      if x[1] == 'ok': return 1
    except:
      pass
    return 0

  def change_email(self,email,passwd,newe):
    try:
      x = self.rpc(('queryaccount', {'email':email}))
      idnum =  x[1][0]['id']
      x = self.rpc(('changeemail',idnum,passwd,newe))
      if x[1] == 'ok': return 1
    except:
      pass
    return 0

  def verify_account(self,vstring):
    try:
      x = self.rpc(('verifyaccount',vstring))
      if x[0] == 'emailverified':
        return x[1:]
    except:
      pass
    return None

  def email_passwd(self,email):
    try:
      x = self.rpc(('queryaccount', {'email':email}))
      idnum =  x[1][0]['id']
      user =  x[1][0]['user']
      print x,user
      x = self.rpc(('emailpassword',idnum, user))
      if x[1] == 'ok': return 1
    except:
      pass
    return 0

  def send_email_verify(self,email):
    try:
      x = self.rpc(('queryaccount', {'email':email}))
      idnum =  x[1][0]['id']
      user =  x[1][0]['user']
      x = self.rpc(('emailverify',idnum,user))
      if x[1] == 'ok': return 1
    except:
      pass
    return 0

  def send_email_request_passwd(self,email):
    try:
      x = self.rpc(('queryaccount', {'email':email}))
      idnum =  x[1][0]['id']
      user =  x[1][0]['user']
      print x,user
      x = self.rpc(('sendchangepasswordemail',idnum,user ))
      if x[1] == 'ok': return 1
    except:
      pass
    return 0

  def reset_password(self,email,code,newp):
    try:
      x = self.rpc(('queryaccount', {'email':email}))
      idnum =  x[1][0]['id']
      user =  x[1][0]['user']
      print x,user
      x = self.rpc(('emailchangepassword',idnum,code,newp))
      print x
      if x[1] == 'ok': return 1
    except:
      pass
    return 0
