#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of Pymetrick.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Modulo para identificar clientes conectados"""

from pymetrick import version
__author__ = version.__author__
__copyright__ = version.__copyright__
__license__ = version.__license__
__version__ = version.__version__
__date__ = '2012-09-21'
__modify__ = '2019-08-26'
__credits__ = ''
__text__ = 'Identificacion de conexiones y funciones de encriptacion'
__file__ = 'session.py'

#--- CHANGES ------------------------------------------------------------------
# 2012-09-21 v0.01 PL: - First version
# 2014-08-30 v0.02 PL: - Second version
# 2015-09-10 v0.03 PL: - Adaptado a python 3.x
# 2017-10-02 v0.43 PL: - Migrar a PYTHON 3.6
# 2018-02-13 v0.44 PL: - Add json web tokens JWT
# 2019-08-26 v0.48.6 PL: - Add encryp and decrypt with AES

import sys
import os
import string
import stat
import hmac
import binascii
import hashlib
import pyaes
import logging
import logging.handlers
import copy

try:
    import json
except:
    import simplejson as json

try:
    from itertools import izip as zip
except ImportError: # will be 3.x series
    pass

from datetime import date, time, datetime, timedelta
from random import SystemRandom,choice
from time import localtime,mktime
from pymetrick.helpers import *
from pymetrick import ipaddress



# Caracteres permitidos en session
ALLOWED_CHARS = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'''
# Para ofuscar la encriptacion de password
SALT_CHARS = '''abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'''
# Caracteres desordenados para generar una password aleatoria
PASSWORD_CHARS = '''BCIOQSVXYZclovxz23478ADEFGHJKLMNPRTUW15690abdefghijkmnpqrstuwy'''
# Numero de veces que se encriptara la password
DEFAULT_PBKDF2_ITERATIONS = 1000
long = int

# Comprobar codigo en desarrollo
DEBUG = False

#Tratamiento de errores en LOG
'''
DEBUG - debug message
INFO - info message
WARNING - warn message
ERROR - error message
CRITICAL - critical message
'''
LOG_FILENAME = '-'.join([os.path.abspath(__file__).split(os.sep)[len(os.path.abspath(__file__).split(os.sep))-1],])[:-3]
LOG = logging.getLogger(LOG_FILENAME)

if 'LD_LIBRARY_PATH' in list(os.environ.keys()):
    # CGI environment
    sys.stdout = sys.stderr
    if DEBUG:
        logging.basicConfig(stream = sys.stderr, level=logging.DEBUG, format='%(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(stream = sys.stderr, level=logging.WARNING, format='%(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
else:
    # not CGI environment
    logging.basicConfig(stream=sys.stderr)
    hdlr = logging.handlers.RotatingFileHandler(filename=LOG_FILENAME+'.log',mode='a', encoding='utf-8', maxBytes=1048576, backupCount=3)
    formatter = logging.Formatter('%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s - %(message)s')
    hdlr.setFormatter(formatter)
    LOG.addHandler(hdlr)
    if DEBUG:
        LOG.setLevel(logging.DEBUG)
    else:
        LOG.setLevel(logging.WARNING)

_builtin_safe_str_cmp = getattr(hmac, 'compare_digest', None)
_sys_rng = SystemRandom()



class Jwt:
    ''' JSON WEB TOKENS stateless authentication '''

    def __init__(self, environ = {}, authorized_days = 1):
        '''constructor
        @Parameters  environ
            environ : dict with values of http request
            - keys to work :
                HTTP_COOKIE
                HTTP_X_AUTHORIZATION or X_REQUEST_WITH
                HTTP_HOST
                HTTP_CLIENT_IP o HTTP_X_FORWARDED_FOR o REMOTE_ADDR

            authorized_days = default 1 day or 24 hours

            token            base64 header.payload.signature
            secret           string
            days_to_expire   integer
        '''
        try:
            self.ip = None
            self.session = dict()  # session values
            self.session["domain"] = '.'
            self.session['expires'] = None
            self.session['access_token'] = ''
            self.ipv6_address = ipaddress._BaseV6(None)
            # ipv4 localhost con norma ipv6 como int
            self.int_ipv4_localhost = int(self.ipv6_address._ip_int_from_string(str(ipaddress.ip_address('::ffff:%s' % '127.0.0.1'))))
            # ipv6 localhost como int
            self.int_ipv6_localhost = int(self.ipv6_address._ip_int_from_string('::1'))

            self.ip_addr(environ)

            self.days_to_expire = authorized_days

            self.attr = None

            dict_cookie = dict()
            if isinstance(environ,(dict,)):
                # buscar valores cookie
                if environ.get('HTTP_COOKIE',None):
                    # identificar y separar en dict los valores de HTTP_COOKIE
                    list_cookie = environ['HTTP_COOKIE'].split(';')
                    # obtener clave y valor
                    if len(list_cookie)>0:
                        for n in list_cookie:
                            # separar por valores por =
                            l = n.split('=')
                            if len(l)>1:
                                # obtener clave y valor
                                dict_cookie[l[0].strip()] = l[1].strip()
                            elif len(l)==1:
                                # obtener solo clave
                                dict_cookie[l[0].strip()] = None

            # guardar dominio
            if environ.get('HTTP_HOST',None):
                self.session['domain'] = '.'.join(environ['HTTP_HOST'].split('.')[-2:])
            else:
                self.session['domain'] = '.'

            self.secret = b'A0B9C8D7E6Z1Y2X3W4V5'

            # JSON WEB TOKEN
            self.auth = None

            if isinstance(environ,(dict,)):
                # buscar JSON WEB TOKEN authorization
                if environ.get('HTTP_X_AUTHORIZATION',None) or environ.get('X_REQUEST_WITH',None):
                    # en X_AUTHORIZATION
                    self.auth = environ.get('HTTP_X_AUTHORIZATION',None) if environ.get('HTTP_X_AUTHORIZATION',None) else environ.get('X_REQUEST_WITH',None);
                    self.auth = self.auth.replace('Bearer','').strip()
                    LOG.debug("X_AUTHORIZATION or X_REQUEST_WITH %s" % (self.auth,))
                    self.check_token(token=self.auth)

                elif dict_cookie.get('access_token',None):
                    # en COOKIE SESSION
                    self.auth = dict_cookie['access_token']
                    LOG.debug("HTTP_COOKIE %s" % (self.auth,))
                    self.check_token(token=self.auth)
                else:
                    # crear nuevo JWT
                    LOG.debug('NEW JWT')
                    self.set_token()
            else:
                # crear nuevo JWT
                LOG.debug('NEW JWT')
                self.set_token()

        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('Jwt <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('Jwt <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def ip_addr(self,environ):
        '''Seleccionar la ip

        localhost en ipv4 127.0.0.1 y en ipv6 ::1

        @Parameters
             environ : dict with values of http request
             - keys to work :
                 HTTP_CLIENT_IP o
                 HTTP_X_FORWARDED_FOR o
                 REMOTE_ADDR ( VALOR # 127.0.0.1  Y VALOR # NULO)
             and get IP from IPv4 or IPv6
        @Process
             if IPv4 change to IPv6  ::ffff:xxxx.xxxx.xxxx.xxxx and change to int
             if IPv6 change to int
        '''
        try:

            self.ip = None

            if isinstance(environ,(dict,)):
                # buscar IP
                if environ.get("HTTP_CLIENT_IP",None) and self.ip is None:
                    if len(environ['HTTP_CLIENT_IP'])>0:
                        # prevenir multiples direcciones ip
                        str_address = environ['HTTP_CLIENT_IP'].split(', ')[-1]
                        # corregir errores en direccion ip
                        addr = ipaddress.ip_address(str_address)
                        if addr.version == 4:
                            # convertir ipv4 a norma ipv6
                            addr = ipaddress.ip_address('::ffff:%s' % str_address)
                        addr = self.ipv6_address._ip_int_from_string(str(addr))
                        # comprobar si distinto de ip localhost
                        if int(addr) != self.int_ipv4_localhost and int(addr) != self.int_ipv6_localhost:
                            # seleccionar como origen ip en formato integer
                            self.ip = int(addr)

                elif environ.get("HTTP_X_FORWARDED_FOR",None) and self.ip == None:
                    if len(environ['HTTP_X_FORWARDED_FOR'])>0:
                        # prevenir multiples direcciones ip
                        str_address = environ['HTTP_X_FORWARDED_FOR'].split(', ')[-1]
                        # corregir errores en direccion ip
                        addr = ipaddress.ip_address(str(str_address))
                        if addr.version == 4:
                            # convertir ipv4 a norma ipv6
                            addr = ipaddress.ip_address('::ffff:%s' % str_address)
                        addr = self.ipv6_address._ip_int_from_string(str(addr))
                        # comprobar si distinto de ip localhost
                        if int(addr) != self.int_ipv4_localhost and int(addr) != self.int_ipv6_localhost:
                            # seleccionar como origen ip en formato integer
                            self.ip = int(addr)


                elif environ.get("REMOTE_ADDR",None) and self.ip == None:
                    if len(environ['REMOTE_ADDR'])>0:
                        # prevenir multiples direcciones ip
                        str_address = environ['REMOTE_ADDR'].split(', ')[-1]
                        # corregir errores en direccion ip
                        addr = ipaddress.ip_address(str_address)
                        if addr.version == 4:
                            # convertir ipv4 a norma ipv6
                            addr = ipaddress.ip_address('::ffff:%s' % str_address)
                        addr = self.ipv6_address._ip_int_from_string(str(addr))
                        # comprobar si distinto de ip localhost
                        if int(addr) != self.int_ipv4_localhost and int(addr) != self.int_ipv6_localhost:
                            # seleccionar como origen ip en formato integer
                            self.ip = int(addr)

            if self.ip is None:
                self.ip = self.int_ipv6_localhost


        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('ip_addr <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('ip_addr <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def is_ip(self,ip=None):
        '''Verificacion de ip de conexion con norma ipv6'''
        try:
            if ip:
                addr = ipaddress.ip_address(ip)
                if addr.version == 4:
                    # convertir ipv4 a norma ipv6
                    addr = ipaddress.ip_address('::ffff:%s' % addr)
                addr = self.ipv6_address._ip_int_from_string(str(addr))
                # comprobar si distinto de ip localhost
                if int(addr) != self.ip:
                    return False
                else:
                    return True
            else:
                return False
        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('is_ip <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('is_ip <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def set_token(self, **kwargs):
        '''
        @Parameters
           sub  subject
           days_to_expire  days to expiration
           admin int
           role  int
        '''

        try:
            if kwargs.get('secret',None):
                self.secret = kwargs['secret']

            if not isinstance(self.secret,(bytes,bytearray)):
                self.secret= str2bytes(self.secret)

            if kwargs.get("days_to_expire",None):
                if isinstance(kwargs["days_to_expire"],(int,)):
                    self.days_to_expire = kwargs['days_to_expire']

            if self.auth is None:
                if kwargs.get('token',None):
                    self.check_token(kwargs['token'])
                else:
                    self.header = { "typ" : "JWT",
                                    "alg" : "HS256"
                                  }
                    self.payload= { "sub" : "",
                                    "iat" : datetime2timestamp(),
                                    "exp" : datetime2timestamp(days=self.days_to_expire),
                                    "admin" : 0,
                                    "role": 0
                                  }
                    self.session['expires'] = (timestamp2datetime(self.payload['exp'])).strftime("%a, %d-%b-%Y %H:%M:%S UTC")

            if len(kwargs)>0:
                for n in list(kwargs.keys()):
                    if self.payload.get(n,None):
                        if isinstance(self.payload[n],(int,long)):
                            try:
                                self.payload[n] = int(kwargs[n])
                            except TypeError:
                                self.payload[n] = 0
                        else:
                            self.payload[n] = kwargs[n]
                    else:
                        if n not in ('secret','days_to_expire','token'):
                            self.payload[n] = kwargs[n]

            self.header_b64 = str2bytes(set_base64(json.dumps(self.header, default=to_json),prefix="").strip())
            self.payload_b64= str2bytes(set_base64(json.dumps(self.payload, default=to_json),prefix="").strip())
            # Sign the request
            self.signature = str2bytes(hmac.HMAC(str2bytes(self.secret), self.header_b64+b"."+self.payload_b64 , digestmod=hashlib.sha256).hexdigest())

            # Base64 encode the signature to JWT
            self.auth =  (self.header_b64+b"."+self.payload_b64+b"."+self.signature)
            # insert JWT into cookie session
            self.session['access_token'] = self.auth

        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('set_token <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('set_token <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def set_attr(self, **kwargs):
        '''Es posible asociar datos a Jwt'''
        try:
            if self.check_token(token=self.auth):
                self.attr = kwargs
            else:
                selt.attr = None
        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('set_attr <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('set_attr <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def get_ip(self):
        try:
            return self.ip
        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('get_ip <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('get_ip <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))


    def get_payload(self):
        try:
            self.payload = {}
            if self.check_token(token=self.auth):
                return self.payload
            else:
                self.set_token()
                return self.payload
        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('get_payload <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('get_payload <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def get_token(self):
        try:
            if self.check_token(token=self.auth):
                LOG.debug("self.auth %s" % (bytes2str(self.auth),))
                return bytes2str(self.auth)
            else:
                LOG.debug("self.auth %s" % (bytes2str(self.auth),))
                self.set_token()
                return bytes2str(self.auth)
        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('get_token <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('get_token <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def get_attr(self):
        '''Recuperar datos asociados a Jwt'''
        try:
            if self.check_token(token=self.auth):
                return self.attr
            else:
                return None
        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('get_attr <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('get_attr <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def get_cookie(self):
        '''prepara informacion para introducir en cookie
        keys :
           expires
           path
           comment
           domain
           max-age
           secure
           version
           httponly
        '''
        self.set_token()
        return ("access_token=%s; Domain=%s; path=/; expires=%s; Secure; HttpOnly;" % (bytes2str(self.session['access_token']),'.'+self.session["domain"],self.session["expires"]))


    def del_attr(self):
        '''Eliminar datos asociados a Jwt'''
        try:
            self.attr = None
        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('del_attr <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('del_attr <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def check_token(self, token = None):
        try:
            if token is not None:
                self.auth = str2bytes(token)
            self.data_list = self.auth.split(b".")
            if len(self.data_list)==3:
                if str2bytes(hmac.HMAC(self.secret, self.data_list[0]+b"."+self.data_list[1], digestmod=hashlib.sha256).hexdigest().strip()) == self.data_list[2]:
                    self.header = json.loads(get_base64(self.data_list[0],prefix=""))
                    self.payload = json.loads(get_base64(self.data_list[1],prefix=""))
                    # check if self.session['expire']
                    self.session['expires'] = (timestamp2datetime(self.payload['exp'])).strftime("%a, %d-%b-%Y %H:%M:%S UTC")
                     # check if now <= days to expire
                    if datetime2timestamp()<=self.payload['exp']:
                        return True
            self.del_attr()
            self.auth = None
            self.set_token()
            return False
        except Exception as e:
            if hasattr(e, 'message'):
                LOG.error('check_token <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
            else:
                LOG.error('check_token <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

    def __del__(self):
        '''Eliminar objeto y objetos dependientes'''
        self.del_attr()
        self.auth = None


def safe_str_cmp(a, b):
    '''This function compares strings in somewhat constant time.  This
    requires that the length of at least one string is known in advance.
    Returns `True` if the two strings are equal or `False` if they are not.
    '''
    try:
        if _builtin_safe_str_cmp is not None:
            return _builtin_safe_str_cmp(a, b)
        if len(a) != len(b):
            return False
        rv = 0
        for x, y in zip(a, b):
            rv |= ord(x) ^ ord(y)
        return rv == 0
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('safe_str_cmp <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('safe_str_cmp <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))


def gen_salt(length = 8):
    '''Genera una cadena aleatoria de SALT_CHARS
       @Parameters
           length : longitud de cadena de caracteres a obtener
       @Return
            una cadena de caracteres aleatoria

    '''
    try:
        if length <= 0:
            raise ValueError('requested salt of length <= 0')
        return (''.join(_sys_rng.choice(SALT_CHARS) for _ in range(length))).strip()
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('gen_salt <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('gen_salt <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

def _find_hashlib_algorithms():
    try:
        algos = getattr(hashlib, 'algorithms', None)
        if algos is None:
            algos = ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512')
        # mostrar metodos disponibles
        rv = {}
        for algo in algos:
            func = getattr(hashlib, algo, None)
            if func is not None:
                rv[algo] = func
        return rv
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('_find_hashlib_algorithms <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('_find_hashlib_algorithms <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

_hash_funcs = _find_hashlib_algorithms()

def pbkdf2_hex(data, salt, iterations=DEFAULT_PBKDF2_ITERATIONS,
               keylen=None, hashfunc=None):
    '''como la funcion 'pbkdf2_bin' pero devuelve una cadena hexadecimal.

    @Parameters
        data: the data to derive.
        salt: the salt for the derivation.
        iterations: the number of iterations.
        keylen: the length of the resulting key.  If not provided
                   the digest size will be used.
        hashfunc: the hash function to use.  This can either be the
                     string name of a known hash function or a function
                     from the hashlib module.  Defaults to sha1.
    '''
    try:
        rv = pbkdf2_bin(data, salt, iterations, keylen, hashfunc)
        return to_native(codecs.encode(rv, 'hex_codec'))
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('pbkdf2_hex <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('pbkdf2_hex <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))


def pbkdf2_bin(data, salt, iterations=DEFAULT_PBKDF2_ITERATIONS,
               keylen=None, hashfunc=None):
    '''Returns a binary digest for the PBKDF2 hash algorithm of `data`
    with the given `salt`. It iterates `iterations` time and produces a
    key of `keylen` bytes. By default SHA-1 is used as hash function,
    a different hashlib `hashfunc` can be provided.

    @Parameters
        data: the data to derive.
        salt: the salt for the derivation.
        iterations: the number of iterations.
        keylen: the length of the resulting key.  If not provided
                   the digest size will be used.
        hashfunc: the hash function to use.  This can either be the
                     string name of a known hash function or a function
                     from the hashlib module.  Defaults to sha1.
    '''
    try:
        if isinstance(hashfunc, string_types):
            hashfunc = _hash_funcs[hashfunc]
        elif not hashfunc:
            hashfunc = hashlib.sha1
        salt = to_bytes(salt)
        mac = hmac.HMAC(to_bytes(data), None, hashfunc)
        if not keylen:
            keylen = mac.digest_size
        def _pseudorandom(x, mac=mac):
            h = copy.copy(mac)
            h.update(x)
            return bytearray(h.digest())
        buf = bytearray()
        for block in range_type(1, -(-keylen // mac.digest_size) + 1):
            rv = u = _pseudorandom(salt + _pack_int(block))
            for i in range_type(iterations - 1):
                u = _pseudorandom(bytes(u))
                rv = bytearray(starmap(xor, izip(rv, u)))
            buf.extend(rv)
        return bytes(buf[:keylen])
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('pbkdf2_bin <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('pbkdf2_bin <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

def _hash_internal(method, salt , password):
    '''Contraseña Interna ayudante hash. Soporta texto claro sin ofuscar,
       contraseñas sin ofuscar y ofuscada. En el caso de contraseñas ofuscadas se utiliza
       HMAC.
    @Parameters
        method : metodo para encriptar la password, permite devolver el texto sin encriptar con 'plain'
        salt   : cadema de caracteres que permitira ofuscar los caracteres que componen la password
        password : texto que deseamos tratar.
    @Return
        tuple( texto de password encriptado y/o ofuscado, metodo de encriptacion)
    '''
    try:
        if method == 'plain':
            return password, method

        password = password.encode('utf-8')

        if method.startswith('pbkdf2:'):
            args = method[7:].split(':')
            if len(args) not in (1, 2):
                raise ValueError('Invalid number of arguments for PBKDF2')
            method = args.pop(0)
            iterations = args and int(args[0] or 0) or DEFAULT_PBKDF2_ITERATIONS
            is_pbkdf2 = True
            actual_method = 'pbkdf2:%s:%d' % (method, iterations)
        else:
            is_pbkdf2 = False
            actual_method = method

        hash_func = _hash_funcs.get(method)
        if hash_func is None:
            raise TypeError('invalid method %r' % method)

        if is_pbkdf2:
            if not salt:
                raise ValueError('Salt is required for PBKDF2')
            rv = pbkdf2_hex(password, salt, iterations,
                            hashfunc=hash_func)
        elif salt:
            salt = salt.encode('utf-8')
            rv = hmac.HMAC(salt, password, hash_func).hexdigest()
        else:
            h = hash_func()
            h.update(password)
            rv = h.hexdigest()
        return rv, actual_method
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('_hash_internal <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('_hash_internal <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

def generate_password_hash(password, method='sha1', salt_length=8):
    '''Encripta una contraseña con el método dado y derivada de ofuscacion con la longitud
    dada. El formato de la cadena devuelta incluye el método que se utilizó de forma que
    `check_password_hash` pueda comprobar el hash.

    El formato de la cadena hash se ve así::

        method$salt$hash

    Este método no puede generar contraseñas sin ofuscacion, pero es posible
    generar las contraseñas en texto plano. Si utiliza derivada de ofuscacion,
    HMAC se utiliza internamente para ofuscar la contraseña.

    @parameters
        password: cadena de caracteres a encriptar
        method: metodo de encriptacion empleado (soportado por hashlib)
        salt_length: numero de caracteres usados de ofuscar la contraseña
    '''
    try:
        salt = method != 'plain' and gen_salt(salt_length) or ''
        h, actual_method = _hash_internal(method, salt, password)
        return '%s$%s$%s' % (actual_method, salt, h)
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('generate_password_hash <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('generate_password_hash <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))


def check_password_hash(pwhash, password):
    '''comprobar una contraseña con un valor de contraseña dada salada y hash.
    Con el fin de apoyar las contraseñas sin sal heredados Este método admite
    contraseñas de texto sin formato MD5 y SHA1 hashes (tanto con y sin sal).

    Returns `True` if the password matched, `False` otherwise.
    @Parameters
        pwhash: una password encriptada como la que se genera desde generate_password_hash()
        password: texto sin encriptar, correspondiente a la password, para comparar.
    @Return
        'True' si la password coincide o 'False' en cualquier otro caso.
    '''
    try:
        if pwhash.count('$') < 2:
            return False
        method, salt, hashval = pwhash.split('$', 2)
        return safe_str_cmp(_hash_internal(method, salt, password)[0], hashval)
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('check_password_hash <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('check_password_hash <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

def csrf_token(csrf_length=32):
    '''genera un string con valores aleatorios con una longitud determinada
       orientado al Cross Site Request Forgery protection
       puede ser usado con las comunicaciones ajax
       en la sesion del servidor deberá indicarse como csrftoken y se indicara
       el valor aleatorio en cada pagina generada, recibiendo el mismo valor
       cuando se realice una solicitud ajax o envío de un formulario GET, POST,
       PUT, DELETE.
       @Parameters
           csrf_length : longitud de la cadena de caracteres a obtener
       @Return
           cadena de caracteres aleatoria con la longitud solicitada
    '''
    try:
        return (gen_salt(csrf_length))
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('csrf_token <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('csrf_token <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

def new_password(length = 15, chars = None):
    '''Genera password aleatoria dependiendo de la cadena de caracteres recibida o cadena por defecto
       @Parameters
                length = longitud de password
                chars  = cadena de caracteres para generacion aleatoria de password, aunque por defecto
                         puede utilizar una cadena propia
       @Return
                String = password sin encriptacion de la longitud solicitada u 8 caracteres por defecto
    '''
    try:
        local_chars = PASSWORD_CHARS if(chars) is None else chars;
        if len(local_chars)<30:
            # si la cadena recibida contiene menos de 30 caracteres se amplia de letras y numeros
            local_chars = string.letters + string.digits
        return ''.join(choice(local_chars) for _ in range(length))
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('new_password <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('new_password <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

def file2checksums(__path__, blocksize=65536):
    '''obtener el hash de un fichero para identificarlo de forma unica
    '''
    try:
        hash = hashlib.md5()
        with open(__path__, "rb", encoding='utf-8') as f:
            block_read = ( lambda: f.read( blocksize ))
            for block in iter( block_read, b'' ):
                hash.update( block )
        return hash.hexdigest()
    except Exception as e:
        if hasattr(e, 'message'):
            LOG.error('file2checksums <%s> in line %s !!!' % (e.message,format(sys.exc_info()[-1].tb_lineno)))
        else:
            LOG.error('file2checksums <%s> in line %s !!!' % (e,format(sys.exc_info()[-1].tb_lineno)))

# AES encrypt or decrypt
def encryptAES(data,key=None):
    if key is None or key.length()<33:
        key = PASSWORD_CHARS[0:32]
    key = key.encode('utf-8')
    aes = pyaes.AESModeOfOperationCTR(key)    
    ciphertext = aes.encrypt(data)
    return ciphertext

def decryptAES(data,key=None):
    if key is None or key.length()<33:
        key = PASSWORD_CHARS[0:32]
    key = key.encode('utf-8')
    aes = pyaes.AESModeOfOperationCTR(key)    
    plaintext = aes.decrypt(data).decode('utf-8')
    return plaintext

if __name__ == "__main__":
    print ('''copyright {0}'''.format( __copyright__))
    print ('''license {0}'''.format( __license__))
    print ('''version {0}'''.format( __version__))
    if len(sys.argv) < 2:
        sys.stderr.write("For help use -h o --help")
    elif sys.argv[1]=='-h' or sys.argv[1]=='--help':
        print ('''
               Gestion de seguridad de acceso ''')

