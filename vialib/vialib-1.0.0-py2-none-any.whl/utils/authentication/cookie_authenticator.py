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
#!/usr/bin/env python

"""

Authenticates a user to the repository, sets a cookie, etc

----

storeKey: Stores a user's key in a secret system keyring

parameters:
appID: identifier of a set of application that authenticate for the same reason
reposID: repository identifier, in the form host:port
user: name of the repository user
ipAddr: IP address of the machine that the user is connecting from
key: the key for decrypting the user's password for reposID from ipAddr

----

fetchKey: Retreives a user's key forom the secret system keyring

parameters:
appID: identifier of a set of application that authenticate for the same reason
reposID: repository identifier, in the form host:port
user: name of the repository user
ipAddr: IP address of the machine that the user is connecting from

----

Note:
 If this is to be used of an insecure connection, it is advisable that the
 cookie be set to not expire, and that the initial login be done on the LAN
 with the server. That way, the cleartext password is never sent over the net.


implementation and above note by Jeremiah Blatz ( blatz@maya.com )
this refactored version by Seung Chan Lim ( limsc@maya.com )

"""

###############################################################################
#
###############################################################################
import sys
import string
import os
import base64
import MAYA.VIA.uform
import MAYA.VIA.uuid
import whrandom
import tempfile
import sha
from urllib import quote, unquote
from MAYA.datatypes import Binary





###############################################################################
#
###############################################################################
_MAX_PASS_LEN_       = 127 # longest possible password

# we need a better place to manage the keys, this is an interim hack
if hasattr(tempfile, "gettempdir"):
    _KEY_FILE_BASE_PATH_ = tempfile.gettempdir()
else:
    if sys.platform[:3] == "win":
        _KEY_FILE_BASE_PATH = r"C:\\"
    else:
	_KEY_FILE_BASE_PATH_ = '/tmp'


cookie_fmt = { "token"     : "%s*pass",
	       "user"      : "%s*user",
	       "repos"     : "%s*repos", }






###############################################################################
#
###############################################################################
def authenticateToRepos(r, user_id, passwd=None):
    """
    so I wasn't aware of the fact that we had scrapped the authentication
    scheme we previously had implemented, so this code now has this
    hack to make it work like it used to before. It'll have to be revamped
    later to match the current direction on authentication.
    """
    
    p = r.portal.uuid
    portal_users = r.getAttr(p, "portal_users")

    # sys.stderr.write("Inspecting portal users %s"%(portal_users))
    
    if len(portal_users[0][0].getBuf()) == 0:
        
        ruus = r.getAttr(p, "repos_uform")
        users = r.getAttr(ruus, "repository_users") or []
        
        user_uu = None
        
        for user in users:
            if r.getAttr(user, "label").lower() == user_id.lower():
                # check password				
                if Binary(sha.new(passwd or "").hexdigest()) == r.getAttr(user, "password"):
                    # you're it
                    #sys.stderr.write("\n\n%s passed authentication\n\n"%(user_id))
                    user_uu = user
                elif passwd == None and r.getAttr("user", "password") == None:
                    user_uu =user
                    #sys.stderr.write("\n\n%s has no password.. allowing\n\n"%(user_id))
                else:
                    # you ain't it
                    #sys.stderr.write("\n\nfailed authentication\n\n")
                    pass
					
        if not user_uu:
            # failed authentication
            auth_result = 1
        else:
            portal_users[0][0] = user_uu
            auth_result = 0
            
        # new repository doesn't put user uuid in portal users
        # so I do it manually
        r.setAttr(p, "portal_users", portal_users)

        
        return auth_result


def _UuidEncode(uu):
	"""
	encode a UUID so that it may be included in a URL
	uu: a uuid or string (may be a binary string)
	returns: a string
	"""
	
	if type(uu) != type(""):
		uu = uu.getBuf()
		
	uu = base64.encodestring(uu)
	uu = string.replace(uu, "\012", "")
	uu = string.replace(uu, "=", "_")
	uu = string.replace(uu, "+", "-")
	
	return uu


def _UuidDecode(uu):
	"""
	decode a UUID that has been encoded with encodeUU
	uu: a string that has been encoded with encodeUU
	returns: a uuid
	"""
	
	uu = string.replace(uu, "-", "+")
	uu = string.replace(uu, ".", "=")
	uu = string.replace(uu, "_", "=")
	uu = base64.decodestring(uu)
	uu = MAYA.VIA.uuid.UUID(uu)
	
	return uu
    
def _stringToInt(a):
	"""
	converts string to ints for use in things like xor
	"""
	
	b = 0L
	
	for i in a:
		b = b * 255
		b = b + ord(i)
		
	return b


def _intToString(a):
	"""
	converts ints to string representation
	"""
	
	b = ''
	
	while a > 0:
		b = chr(a % 255) + b
		a = a / 255
		
	return b


def _getRandomString(max_len):
	"""
	returns a random string of length /max_len/
	"""

	if sys.platform[:3] == "win":
            whrandom.seed()
        
            s = ""
            
            for i in range(max_len):
                s = "%s%s"%(s, string.letters[whrandom.randint(0, 51)])

            return s
	else:
            rand_file = open('/dev/random', 'r')
            
            return rand_file.read(max_len)


def _getReposStrVal(repos_obj):
	"""
	returns the string representation of the repository object
	"""
	
	try:
		
		return "%s_%d"%repos_obj.s.getpeername() # IP:port of repos
	except AttributeError:

		raise TypeError, "Repository Object Required"
	

		

###############################################################################
#
###############################################################################
def storeKey(app_uuid, reposStr, user, ipAddr, key):
	"""
	Stores a user's key in a secret system keyring
	
	app_uuid  : identifier of a set of application that authenticate
	            for the same reason.
		    Should be a base64 encoded UUID
	reposStr  : repository identifier, in the form host:port
	user      : name of the repository user
	ipAddr    : IP address of the machine that the user is connecting from
	key       : the key for decrypting the user's password for reposID from
	            ipAddr.
	            Should be a base64 encoded UUID
		    
	secret implementation discussion:
	 so, I could dump these all in one file, but then lookups might end
	 up being slow. I could put them in the repository, but then there
	 would be security issues. So, what I think I'll do is make 
	 directories for reposID, then have files named for ipAddr.
	 The keys will be stored in a non-scary representation. The
	 files will be structured as <appID>*<kMaxPassLen bytes of data>*<user>
	"""
	
	assert(app_uuid and reposStr and user and ipAddr and key)
	
	# prep file structure
	if not os.path.exists(_KEY_FILE_BASE_PATH_):
		
		raise IOError, 'I need a %s to work!'%(_KEY_FILE_BASE_PATH_)

 	#sys.stderr.write(reposStr+'\n')
        key_path = os.path.join(_KEY_FILE_BASE_PATH_, reposStr + '/')
	if not os.path.exists(key_path):
		os.mkdir(key_path)
		os.chmod(key_path, 0700)

        key_file = os.path.join(key_path, ipAddr)
	try:
		keyFile = open(key_file, 'w')
		#lines   = keyFile.readlines()
		lines   = []
	except IOError:
		lines   = []
		
	lines = lines + [app_uuid + '*' + key + '*' + user]
	#sys.stderr.write('lines ' + repr(lines) + '\n')
	
	lines   = string.join(lines, '\n')
	keyFile = open(key_file, 'w')
	keyFile.write(lines)
	keyFile.close()
	
	os.chmod(key_file, 0700)


def fetchKey(appID, reposStr, user, ipAddr):
	"""
	Retreives a user's key from the secret system keyring
	
	appID     : identifier of a set of application that authenticate
	            for the same reason.
		    Should be a base64 encoded UUID
	reposStr  : repository identifier, in the form host:port
	user      : name of the repository user
	ipAddr    : IP address of the machine that the user is connecting from

	returns a base64 encoded UUID buffer
	"""

	assert(appID and reposStr and user and ipAddr)
	
	
        key_path = os.path.join(_KEY_FILE_BASE_PATH_, reposStr + '/')
        key_file = os.path.join(key_path, ipAddr)
        
	if os.path.exists(key_file):
		keyFile = open(key_file, 'r')
		
		for i in keyFile.readlines():
			#sys.stderr.write('i: '+repr(i)+'\n')
			
			comma1Pos = string.find(i, '*')
			iAppID    = i[:comma1Pos]
			comma2Pos = string.find(i, '*', comma1Pos+1)
			iKey      = i[comma1Pos+1:comma2Pos]
			iUser     = i[comma2Pos+1:]
			
			#sys.stderr.write('iAppID: '+repr(iAppID)+' == '+repr(appID)+'\n')
			#sys.stderr.write('iUser: '+repr(iUser)+' == '+repr(user)+'\n')
			
			if (iAppID, iUser) == (appID, user):
				
				return iKey
			else:
				
				return ""
	else:
		sys.stderr.write('I need a ' + key_file +' to work!')
		
		raise IOError, 'I need a ' + key_file +' to work!'
	

		
###############################################################################


def verifyAuthentication(user_id, token, repos, application_id, client_IP):
	"""
	user_id        : content of the userid string stored in your cookie
	token          : content of the token string stored in your cookie
	application_id :
	repos_str      :
	
	attempts to authenticate the user to repos. Returns a tuple
	of the user name, a MAYA.repos.Repository, a repos portal,
	and a result code.

	The results have the following meanings:
	 ('', None, 1) Could not connect to the repository
	 ('', p, 0) There was no cookie, the user is logged in as anonymous
	 ('', p, 1) There was no cookie, the user is not logged in
	 (s,  p, 0) The user succesfully logged in as s
	 (s,  p, 1) The user attempted to log in as s, but failed
	
	application_id is a string that identifies your application. Different
	programs can share the same application_id, but they should all
	authenticate with the same intent.
	"""
	
	assert( (type(user_id)        == type("")) and
		(type(token)          == type("")) and
		(type(application_id) == type("")) and
		(type(client_IP)      == type("")) )

	
	assert( repos != None )
	#sys.stderr.write('application_id: ' + str(application_id) + '\n')
	
	if user_id and token:

		assert( (len(client_IP) > 0) and
			(len(application_id) > 0) )
		
		#sys.stderr.write('user: ' + user_id + '\n')

		repos_str = _getReposStrVal(repos)
		
		# fetch key
		key  = _UuidDecode(fetchKey(_UuidEncode(
			                         MAYA.VIA.uuid.UUID(application_id)
						 ),
						repos_str,
						user_id,
						client_IP))

		if key:
			key = key.getBuf()
		else:
			
			return ('', p, 1)
		
		enc_pass = _UuidDecode(token).getBuf()
		#sys.stderr.write('key: ' + repr(key) + '\n')
		#sys.stderr.write('enc_pass: ' + repr(enc_pass) + '\n')
		
		passwd = _intToString(_stringToInt(enc_pass) ^ \
				      _stringToInt(key))
		#sys.stderr.write('pass: ' + passwd + '\n')

		if passwd == "":
			authUF = MAYA.VIA.uform.UForm(eform={'userid'   : user_id})
		else:
			authUF = MAYA.VIA.uform.UForm(eform={'userid'   : user_id,
								   'password' : Binary(passwd)})
	else:
		user_id = ''
		authUF  = MAYA.VIA.uform.UForm()

	authResult = repos.authenticateWithReturnCode(authUF)

        # now we do manual traversal-based authentication for now
	if authUF.has_key("password"):
		temp = authenticateToRepos(repos, authUF["userid"], authUF["password"].getBuf())
	else:
		temp = authenticateToRepos(repos, authUF["userid"])
                
	if temp != None:
		authResult[1] = temp 

	return (user_id, authResult[0].uuid, authResult[1])




def authenticateUser(repos, user_id, password, application_id, client_IP):
	"""
	
	repos          : repository object
	user_id        : user id string
	password       : password string
	application_id : application id string
	client_IP      : IP address of the authenticating client
	
	"""
	
	assert( (type(user_id)        == type("")) and
		(type(password)       == type("")) and
		(type(application_id) == type("")) and
		(type(client_IP)      == type("")) )
		
	# do I need to trap a socket error here?
	if user_id != "" and password != "":
		authUF = MAYA.VIA.uform.UForm(eform={'userid'  : user_id,
                                                     'password': Binary(password)})
	elif password == "":
		authUF = MAYA.VIA.uform.UForm(eform={'userid':user_id})
	else:
		# authenticating as anonymous
		authUF = MAYA.VIA.uform.UForm('babyskratch')
	
	(portal, resp) = repos.authenticateWithReturnCode(authUF)

        # we do manual traversal-baesd authentication for now
	temp = authenticateToRepos(repos, user_id, password)
        
	if temp != None:
		resp = temp
		
	if resp != 0:
		sys.stderr.write("failed to authenticate to the repository\n")
		
		return 0
	else:
		# Jer:
		#  login successful
		#  get a key from /dev/random (to be more cross-platform,
		#  we should check for dev random, and get random numbers
		#  some other way if it isn't there
		rand_str  = _getRandomString(_MAX_PASS_LEN_)
		repos_str = _getReposStrVal(repos)

		# store key
		storeKey(_UuidEncode(MAYA.VIA.uuid.UUID(application_id)),
			 repos_str,
			 user_id,
			 client_IP,
			 _UuidEncode(MAYA.VIA.uuid.UUID(rand_str)))

		repos_str = string.join(string.split(repos_str,"_"),":")

		
		return {
			cookie_fmt["repos"]%(application_id)     : repos_str,
			cookie_fmt["user"]%(application_id)      : user_id,
			cookie_fmt["token"]%(application_id)     : _UuidEncode(
			                                             MAYA.VIA.uuid.UUID(
			                                              _intToString(_stringToInt(password) ^
								      _stringToInt(rand_str)))
								     )
			}

