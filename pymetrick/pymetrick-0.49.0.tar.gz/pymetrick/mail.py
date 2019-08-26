#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Pymetrick.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

"""Modulo para gestionar mail"""

from pymetrick import version
__author__ = version.__author__
__copyright__ = version.__copyright__
__license__ = version.__license__
__version__ = version.__version__
__date__ = '2014-05-21'
__credits__ = ''
__text__ = 'Gestion de funciones para Mail'
__file__ = 'mail.py'

#--- CHANGES ------------------------------------------------------------------
# 2015-05-04 v0.01 PL: - First version
# 2017-10-02 v0.43 PL: - Migrar a PYTHON 3.6

import sys
import os
import logging
import logging.handlers

try:
    import ssl
    from smtplib import SMTP, SMTP_SSL        # use this for standard SMTP protocol   (port 25, no encryption or port 465, uses SSL)
    from imaplib import IMAP4, IMAP4_SSL
    IS_SSL = True
except:
    from smtplib import SMTP                  # use this for standard SMTP protocol   (port 25, no encryption or port 465, uses SSL)
    from imaplib import IMAP4
    IS_SSL = False

import socket

# For guessing MIME type based on file name extension
import mimetypes

from optparse import OptionParser

import email
import mailbox
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE, formatdate

from datetime import datetime, timedelta, tzinfo
from pymetrick.helpers import *

# PY3
long = int

# Check development code
DEBUG = True

# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.

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


SMTP_PORT = 25
SMTP_SSL_PORT = 465
SMTP_TLS_PORT = 587

def sendMail(*args,**kwargs):
    '''Enviar email,
       @Arguments:
           _sender       - str  -  enviado desde
           _to           - list -  enviar a
           _cc           - list -  enviar copias
           _bcc          - list -  enviar copias ocultas
           _subject      - str  -  asunto
           _text         - str  -  text/plain del mensaje
           _html         - str  -  text/html  del mensaje
           _user         - str  -  usuario
           _password     - str  -  password
           _smtpserver   - str  -  servidor
           _port         - str  -  puerto
           _files        - list -  ficheros adjuntos
           _output       - str  -  el contenido del mensaje se grabara como un fichero
       @Returns 200|401
    '''
    # for standard SMTP protocol port 25, no encryption
    # for standard SMTP protocol port 465, SSL
    # for standard SMTP protocol port 587, TLS

    #Tratamiento de errores en LOG


    try:

        # Create the root message and fill in the from, to, and subject headers
        msgRoot = MIMEMultipart('related')
        msgRoot['Subject'] = bytes2str(kwargs.get('_subject',''))
        # my email address
        msgRoot['From'] = bytes2str(kwargs.get('_sender',''))
        lstTo = list()

        if kwargs.get('_to',None):
            # recipient's email address
            _to = bytes2str(kwargs.get('_to')) if isinstance(kwargs.get('_to'),(list,tuple)) else bytes2str([kwargs.get('_to')]);
            msgRoot['To'] = COMMASPACE.join(_to)
            lstTo = _to
        if kwargs.get('_cc',None):
            _cc = bytes2str(kwargs.get('_cc')) if isinstance(kwargs.get('_cc'),(list,tuple)) else bytes2str([kwargs.get('_cc')]);
            msgRoot['cc'] = COMMASPACE.join(_cc)
            lstTo += _cc
        if kwargs.get('_bcc',None):
            _bcc = bytes2str(kwargs.get('_bcc')) if isinstance(kwargs.get('_bcc'),(list,tuple)) else bytes2str([kwargs.get('_bcc')]);
            msgRoot['bcc'] = COMMASPACE.join(_bcc)
            lstTo += _bcc
        #msgRoot['Date'] = timeZone('Madrid').strftime( "%m/%d/%Y %H:%M" )
        msgRoot.preamble = 'This is a multi-part message in MIME format.'

        # Encapsulate the plain and HTML versions of the message body in an
        # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)
        # MIMEText(_text[, _subtype[, _charset]])
        # Record the MIME types - text/plain
        text = MIMEText(bytes2str(kwargs.get('_text','')), _subtype='plain',_charset='utf-8')
        msgAlternative.attach(text)
        # Record the MIME types - text/html.
        html = MIMEText(bytes2str(kwargs.get('_html','')), _subtype='html',_charset='utf-8')
        msgAlternative.attach(html)

        # Ejemplo de como introducir una imagen en el texto html
        #'<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>Nifty!'

        # We reference the file in the SRC attribute by the ID
        if kwargs.get('_files',None):
            _files = kwargs['_files']

            for file in _files:
                ctype, encoding = mimetypes.guess_type(file)
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                if maintype == 'text':
                    with open(file) as fp:
                        # Note: we should handle calculating the charset
                        msg = MIMEText(fp.read(), _subtype=subtype)
                elif maintype == 'image':
                    with open(file, 'rb') as fp:
                        msg = MIMEImage(fp.read(), _subtype=subtype)
                elif maintype == 'audio':
                    with open(file, 'rb') as fp:
                        msg = MIMEAudio(fp.read(), _subtype=subtype)
                else:
                    with open(file, 'rb') as fp:
                        msg = MIMEBase(maintype, subtype)
                        msg.set_payload(fp.read())
                    # Encode the payload using Base64
                    encoders.encode_base64(msg)
                # Set the filename parameter
                msg.add_header('Content-Disposition', 'attachment', filename=file)
                msgRoot.attach(msg)

        # Send the email (this example assumes SMTP authentication is required)
        port = kwargs.get('_port',SMTP_PORT)  # or 587
        if port==SMTP_SSL_PORT:                  # SSL
            server = SMTP_SSL(host=kwargs.get('_smtpserver',''),port=port,timeout=86400)
        else:
            server = SMTP(host=kwargs.get('_smtpserver',''),port=port,timeout=86400)
        server.set_debuglevel(True) # show communication with the server
        server.connect(kwargs.get('_smtpserver',None), port)
        server.ehlo()
        if IS_SSL and server.has_extn('STARTTLS') and port==SMTP_TLS_PORT:
            context = ssl.create_default_context()
            server.starttls(context=context)
            server.ehlo()   # re-identify ourselves over TLS connection
        if kwargs.get('_output',None):
            with open(kwargs.get('_output','.'), 'w') as fp:
                fp.write(msg.as_string())
        else:
            socket.setdefaulttimeout(30)
            server.login(kwargs.get('_user',None),kwargs.get('_password',None))
            server.sendmail(bytes2str(kwargs.get('_sender','')), lstTo, msgRoot.as_string())
        return 200
    except smtplib.SMTPException as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPException <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except smtplib.SMTPResponseException as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPResponseException <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except smtplib.SMTPSenderRefused as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPSenderRefused <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except smtplib.SMTPRecipientsRefused as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPRecipientsRefused <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except smtplib.SMTPDataError as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPDataError <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except smtplib.SMTPConnectError as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPConnectError <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except smtplib.SMTPHeloError as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPHeloError <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except smtplib.SMTPNotSupportedError as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPNotSupportedError <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except smtplib.SMTPAuthenticationError as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPAuthenticationError <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except smtplib.SMTPNotSupportedError as e:
        tb = sys.exc_info()[2]
        LOG.error('SMTPNotSupportedError <%s> en linea %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    except Exception as e:
        tb = sys.exc_info()[2]
        LOG.error('sendEmail <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        return 401
    finally:
        server.quit()
        del server

IMAP4_PORT = 143
IMAP4_SSL_PORT = 993

def getMail(*args,**kwargs):
    '''Recibir email POP3 o IMAP
       @Arguments:
           _user         - str  -  usuario
           _password     - str  -  password
           _imapserver   - str  -  servidor IMAP
           _pop3server   - str  -  servidor POP3
           _port         - str  -  puerto
           _criteria     - str  -   ALL - devuelve todos los mensajes que coinciden con el resto del criterio
                                    ANSWERED - coincide con los mensajes con la bandera \\ANSWERED establecida
                                    BCC "cadena" - coincide con los mensajes con "cadena" en el campo Bcc:
                                    BEFORE "fecha" - coincide con los mensajes con Date: antes de "fecha"
                                    BODY "cadena" - coincide con los mensajes con "cadena" en el cuerpo del mensaje
                                    CC "cadena" - coincide con los mensajes con "cadena" en el campo Cc:
                                    DELETED - coincide con los mensajes borrados
                                    FLAGGED - coincide con los mensajes con la bandera \\FLAGGED establecida (algunas veces referidos como Importante o Urgente)
                                    FROM "cadena" - coincide con los mensajes con "cadena" en el campo From:
                                    KEYWORD "cadena" - coincide con los mensajes con "cadena" como palabra clave
                                    NEW - coincide con los mensajes nuevos
                                    OLD - coincide con los mensajes antiguos
                                    ON "fecha" - coincide con los mensajes con Date: coincidiendo con "fecha"
                                    RECENT - coincide con los mensajes con la bandera \\RECENT establecida
                                    SEEN - coincide con los mensajes que han sido leídos (la bandera \\SEEN esta estabecido)
                                    SINCE "fecha" - coincide con los mensajes con Date: despues de "fecha"
                                    SUBJECT "cadena" - coincide con los mensajes con "cadena" en Subject:
                                    TEXT "cadena" - coincide con los mensajes con el texto "cadena"
                                    TO "cadena" - coincide con los mensajes con "cadena" en To:
                                    UNANSWERED - coincide con los mensajes que no han sido respondidos
                                    UNDELETED - coincide con los mensajes que no están eliminados
                                    UNFLAGGED - coincide con los mensajes que no tienen bandera
                                    UNKEYWORD "cadena" - coincide con los mensajes que no tienen la palabra clave "cadena"
                                    UNSEEN - coincide con los mensajes que aun no han sido leidos
           _outputdir    - str  -  fichero donde grabara los correos leidos
       @Returns 200|401
    '''
    # for standard IMAP protocol port 143, no encryption
    # for standard IMAP protocol port 993, SSL
    # for standard IMAP protocol port 143, TLS


    try:

        if kwargs.get('_imapserver',None):
            # Receive the email (this example assumes IMAP authentication is required)
            port = kwargs.get('_port',IMAP4_PORT)

            if port==IMAP4_SSL_PORT:
                server = IMAP4_SSL(kwargs['_imapserver'],port)
            else:
                server = IMAP4(kwargs['_imapserver'],port)

            if IS_SSL and port == IMAP4_PORT: # situar en NOAUTH
                context = ssl.create_default_context()
                server.starttls(ssl_context=context)

            server.login(kwargs.get('_user',None),kwargs.get('_password',None))   # AUTH

            #server.select(mailbox='INBOX', readonly=False)
            server.select(readonly=False)
            typ, data = server.search(None, kwargs.get('_criteria','UNSEEN'))
            if typ == 'OK':
                for num in data[0].split():
                    typ, data = server.fetch(num, '(RFC822)')
                    email_message=email.message_from_bytes(data[0][1])
                    # Header Details
                    date_tuple = email.utils.parsedate_tz(email_message['Date'])
                    if date_tuple:
                        local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                        local_message_date = "%s" %((local_date.strftime("%a, %d %b %Y %H:%M:%S")))
                    email_from = (email.header.make_header(email.header.decode_header(email_message['From'])))
                    #LOG.debug(email_message['From'])
                    email_to = (email.header.make_header(email.header.decode_header(email_message['To'])))
                    #LOG.debug(email_message['To'])
                    email_subject = (email.header.make_header(email.header.decode_header(email_message['Subject'])))
                    #LOG.debug(email_message['Subject'])
                    # Body details
                    for part in email_message.walk():
                        if part.get_content_type() == "text/plain":
                            body = bytes2str(part.get_payload(decode=True),'utf-8')
                            #LOG.debug("From: %s\nTo: %s\nDate: %s\nSubject: %s\n\nBody: \n\n%s" %(email_from, email_to,local_message_date, email_subject, body))
                            print("From: %s\nTo: %s\nDate: %s\nSubject: %s\n\nBody: \n\n%s" %(email_from, email_to,local_message_date, email_subject, body))
                            file_name = "email_" + bytes2str(num) + ".txt"
                            output_file = open(kwargs.get('_outputdir','') + file_name, 'w')

                            output_file.write("From: %s\nTo: %s\nDate: %s\nSubject: %s\n\nBody: \n\n%s" %(email_from, email_to,local_message_date, email_subject, body))
                            output_file.close()
                        if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
                            open(kwargs.get('_outputdir','') + part.get_filename(), 'wb').write(part.get_payload(decode=True))

                        else:
                            continue
                server.close()
            server.logout()
            del server
            return 200
        else:
            return 401
    except Exception as e:
        tb = sys.exc_info()[2]
        LOG.error('getEmail <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        print('getEmail <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        return 401

def deleteIMAP(*args,**kwargs):
    '''Eliminar todos los correos de IMAP
       @Arguments:
           _user         - str  -  usuario
           _password     - str  -  password
           _imapserver   - str  -  servidor IMAP
           _port         - str  -  puerto
           _folder       - str  -  carpeta a tratar
       @Returns 200|401
    '''

    try:
        if kwargs.get('_imapserver',None) and kwargs.get('_user',None) and kwargs.get('_password',None) and kwargs.get('_folder',None):
            server = IMAP4(_imapserver)
            server.login(_user, _password)
            server.select(_folder)
            typ, data = server.search(None, 'ALL')
            for msgid in data[0].split():
                server.store(msgid, '+FLAGS', '(\\Deleted)')
            server.expunge()
            server.close()
            server.logout()
            del server
            return 200
        else:
            return 401
    except Exception as e:
        tb = sys.exc_info()[2]
        LOG.error('deleteIMAP <%s> in line %s !!!' % (repr(e),tb.tb_lineno))
        return 401

def timeZone(timeZone):
    """Adaptar la hora segun la zona horaria"""
    zone = {'Madrid':2,'Londres':1,'Kabul':4.5}
    nowUTC = datetime.utcnow()
    return nowUTC + timedelta(hours=zone[timeZone])

if __name__ == "__main__":
    print ('''copyright {0}'''.format( __copyright__))
    print ('''license {0}'''.format( __license__))
    print ('''version {0}'''.format( __version__))
    if len(sys.argv) < 2:
        sys.stderr.write("for help use -h o --help")
    elif sys.argv[1]=='-h' or sys.argv[1]=='--help':
        print ('''
        Podra enviar fácilmente mensajes de correo electronico :\n\n''')
    MY_FROM='pymetrick@pymetrick.org'
    MY_TO='javtamvi@gmail.com'
    MY_USER='pymetrick'
    MY_PASSWORD='BETACA96'
    MY_SMTP='smtp.webfaction.com'
    MY_SMTP_PORT=587
    sendMail( _sender = MY_FROM,_to= MY_TO,_subject='mail test',_text='this is a email test',_html='<div>this is a email test</div>',_user=MY_USER,_password=MY_PASSWORD,_smtpserver=MY_SMTP,_port=MY_SMTP_PORT,_files=['C:/TEMP/Libro1.xls','C:/HaxLogs.txt'])
