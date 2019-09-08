""" The Basic Module delivers the *Basis* for Systems in the Production Systems world."""

import os
import logging
import logging.handlers
import sys
from .package_version import version


from configparser import ConfigParser as SafeConfigParser
from configparser import ParsingError
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import email.encoders
from socket import gethostname

from ps.Patterns import LOGGING_PATTERNS, PATTERN_LANGUAGES

MAX_SIZE_FOR_A_ROTATING_LOGFILE     = 2000000
MAX_NUMBER_OF_OLD_ROTATING_LOGFILES = 10
PATTERN_LANGUAGE                    = "EN"

DEV_STAGES = {'TESTING': {'suffix': '_t', 'logging_port': 9010,
                          'logging_bridge_port': 9011,
                          'logging_level': logging.DEBUG,
                          'l_admin_mail': ['test@somewhere.com'], },
              'DEVELOPMENT': {'suffix': '_d', 'logging_port': 9020,
                              'logging_bridge_port': 9019,
                              'logging_level': logging.DEBUG,
                              'l_admin_mail': ['d_test@somewhere.com'], },
              'INTEGRATION': {'suffix': '_i', 'logging_port': 9022,
                              'logging_bridge_port': 9018,
                              'logging_level': logging.DEBUG,
                              'l_admin_mail': ['itest@somewhere.com'], },
              'PRODUCTION': {'suffix': '', 'logging_port': 9024,
                             'logging_bridge_port': 9017,
                             'logging_level': logging.DEBUG,
                             'l_admin_mail': ['production@somewhere.com'], },
              }


def hms_string(sec_elapsed):
    """Utility to get the hour:minute:seceonds for an 
       elapsed period in seconds"""
    h = int(sec_elapsed / (60 * 60))
    m = int(sec_elapsed % (60 * 60) / 60)
    s = sec_elapsed % 60
    return "%02d:%02d:%02d" % (h, m, s)


class ContextFilter(logging.Filter):
    """ Is used as a logging.filter and merges additional values into the logging message """

    def filter(self, record):
        
        if "package_version" not in record.__dict__: record.package_version        = "undef"
        record.SYSTEM_ID         = os.getenv("SYSTEM_ID", "None")
        record.SUB_SYSTEM_ID     = os.getenv("SUB_SYSTEM_ID", "None")
        record.SUB_SUB_SYSTEM_ID = os.getenv("SUB_SUB_SYSTEM_ID", "None")
        record.PRODUKT_ID        = os.getenv("PRODUKT_ID", "None")
        record.USER_SPEC_1       = os.getenv("USER_SPEC_1", "None")
        record.USER_SPEC_2       = os.getenv("USER_SPEC_2", "None")
        return True


class Basic(object):
    """The Basic Class delivers the *Basis* for Systems in the Production System  world.

       It enforces the same patterns for:
         - logging
	 - configuration files
	 - and maybe more 

       throughout the different development stages.

       **Example Usage**

       >>> from ps.Basic import Basic 
       >>> import os
       >>> project_name='ps'
       >>> dev_stage='DEVELOPMENT'
       >>> os.environ["DEV_STAGE"]=dev_stage    # DEV_STAGE has to be defined in the environment. Error else
       >>> fp=open(os.path.join("/tmp", project_name + "_d.cfg"),"w") # configuration files are built from the projects name
       >>> written = fp.write("[GLOBAL]" + os.linesep)   # and a shortcut for the development stage.
       >>> written = fp.write("pattern_language=EN")     # They follow the ini syle (ms-world) for
       >>> fp.close()                           # configuration files.
       >>> os.environ["BASIC_CONFIGFILE_DIR"] = "/tmp" # you can set the directory, where config files live
       >>> do_not_care=Basic(project_name)
       >>> Basic.config_file_name
       '/tmp/ps_d.cfg'
       >>> assert(Basic.config_file_name == "/tmp/ps_d.cfg")
       >>> my_version="0.0.alpha"
       >>> Basic.logger.info("Will leave an Info level log message in the local log file as in the (DEV_STAGE) central Log-Server/herald",extra={"package_version":my_version})
       >>> Basic.config_parser.sections()      # The application level access should occure via the 
       ['GLOBAL']
       >>> Basic.config_parser.items('GLOBAL')# provided class variables to read the config file
       [('pattern_language', 'EN')]
       >>> Basic.verbose()# put logging messages to stdout too 
       

.. Note::

    If a directory named **LOG** is found in the current working directory, the log file will be put there.
    
.. Note::
    
    The Basic class assumes configuration files to be written within the current working directory of
    the calling process. By setting the environment-variable **BASIC_CONFIGFILE_DIR** to an appropriate
    directory, the Basic class will try to get the corresponding config-file from that directory.
    This way, different systems (and development stages) are able to share a common "configuration" directory.
          
    """
    INSTANCE = None

    suffix                 = "not_yet_defined"  #: e.g are we on d,i or p system
    logging_port           = "not_yet_defined"  #: which port is used to transmit log_messages
    logging_bridge_port    = "not_yet_defined"  #: which port is used to transmit -bridged- log_messages
    logging_level          = "not_yet_defined"  #: current log level
    log_file_name          = "not_yet_defined"  #: name of the local LOG File
    logger                 = "not_yet_defined"  #: provide the logger to other modules
    config_file_name       = "not_yet_defined"  #: the projects config file name
    config_parser          = "not_yet_defined"  #: provide the config File handler to the outside
    dev_stage              = "not_yet_defined"  #: provide the dev_stage to the outside
    herald_sqlite_filename = "not_yet_defined"  #: provide the dev_stage to the outside
    primary_herald_url     = "not yet defined"  #: provide an url where a herald could be reached
    lock_filename          = "not_yet_defined"  #: provide the lock file name
    curr_mail_sender       = "not_yet_defined"
    curr_mail_recipients   = "not_yet_defined" 
    curr_mail_subject      = "not_yet_defined" 
    curr_mail_text         = "not_yet_defined" 
    i_have_lock            = False
    @classmethod
    def get_instance(cls, project_name_p, 
                           init_p=True, 
                           force_usage_of_config_file=False,
                           have_config_file=True, 
                           guarded_by_lockfile=False):
        if Basic.INSTANCE is None:
             Basic.INSTANCE = Basic( project_name_p, 
                                   init_p=init_p, 
                                   force_usage_of_config_file=force_usage_of_config_file,
                                   have_config_file=have_config_file, 
                                   guarded_by_lockfile=guarded_by_lockfile)
             return Basic.INSTANCE
        else:
            if project_name_p != Basic.name: 
                raise KeyError("Reinitialization of the singleton is not allowed")
                     
        return Basic.INSTANCE


    def __init__(self, project_name_p, init_p=True, 
                                       force_usage_of_config_file=False, 
                                       have_config_file=True, 
                                       guarded_by_lockfile=False):
        """
        """

        Basic.name                  = project_name_p
        os.environ["SYSTEM_ID"]     = project_name_p
        os.environ["SUB_SYSTEM_ID"] = gethostname()

        if init_p:
            dev_stage = os.getenv("DEV_STAGE", None)
            if dev_stage == None or dev_stage not in DEV_STAGES.keys():
                sys.stderr.write("DEV_STAGE '%s' Not an Allowed DEVELOPMENT STAGE "%(dev_stage))
                sys.stderr.write("e.g. export DEV_STAGE=DEVELOPMENT")
                sys.stderr.write("Exit Now")
                raise KeyError("DEV_STAGE")

            Basic.dev_stage               = dev_stage
            Basic.suffix                  = DEV_STAGES[dev_stage]['suffix']
            Basic.logging_port            = DEV_STAGES[dev_stage]['logging_port']
            Basic.webserver_port          = DEV_STAGES[dev_stage]['logging_port'] + 1
            Basic.logging_bridge_port     = DEV_STAGES[dev_stage]['logging_bridge_port']
            Basic.logging_level           = DEV_STAGES[dev_stage]['logging_level']
            Basic.l_admin_mail            = DEV_STAGES[dev_stage]['l_admin_mail']
            Basic.herald_sqlite_filename  = os.path.join(os.getcwd(), 'herald.sqlite%s' % Basic.suffix)
            Basic.primary_herald_url      = ""
            Basic.lock_filename           = os.path.join(os.getcwd(), '%s_lock%s' % (project_name_p, Basic.suffix))
            Basic.curr_mail_sender        = ""
            Basic.curr_mail_recipients    = "" 
            Basic.curr_mail_subject       = "" 
            Basic.curr_mail_text          = "" 
            if not os.path.isdir("LOG"):
                try:
                    os.mkdir("LOG")
                except:
                    sys.stderr.write("Error creating LOG DIR in %s: EXIT Now"%(os.getcwd()))
                    sys.stderr.write("Error creating LOG DIR: EXIT Now")
                    sys.exit(1)
            Basic.log_file_name = os.path.join("LOG", Basic.name + Basic.suffix + ".log")
            if Basic.logger ==  "not_yet_defined" :
                Basic.logger = logging.getLogger(project_name_p)
                my_filter = ContextFilter()
                Basic.logger.addFilter(my_filter)
                socket_handler = logging.handlers.SocketHandler('localhost', Basic.logging_port)
                Basic.logger.addHandler(socket_handler)
                logfile_handler = logging.handlers.RotatingFileHandler(Basic.log_file_name,
                                                                   maxBytes=MAX_SIZE_FOR_A_ROTATING_LOGFILE,
                                                                   backupCount=MAX_NUMBER_OF_OLD_ROTATING_LOGFILES)
                formatter = logging.Formatter(
                '%(asctime)s %(PRODUKT_ID)s %(SYSTEM_ID)s %(SUB_SYSTEM_ID)s %(SUB_SUB_SYSTEM_ID)s %(USER_SPEC_1)s %(USER_SPEC_2)s %(levelname)s %(name)-12s %(package_version)s %(lineno)d %(message)s')
                logfile_handler.setFormatter(formatter)
                Basic.logger.addHandler(logfile_handler)

            Basic.logger.setLevel(Basic.logging_level)
            Basic.logger.debug("Logging initialized for pid %s"              % (os.getpid()),extra={"package_version":version})

            if guarded_by_lockfile:
                if not os.path.isfile(Basic.lock_filename):
                    try:
                        fp = open(Basic.lock_filename, "w")
                        fp.write("%s" % os.getpid())
                        fp.close()
                        i_have_lock     = True 
                    except:
                        Basic.logger.exception("Error opening/writing lock File: version %s"%(version))
                        sys.stderr.write("Error open/write lockFile %s: EXIT Now" % (Basic.lock_filename))
                        sys.stderr.write(traceback.format_exc())
                        sys.exit(1)
                    Basic.logger.info("system %s started new lock guarded instance on %s"             % (Basic.name, Basic.lock_filename),extra={"package_version":version})
                else:
                    
                    fp = open(Basic.lock_filename, "r")
                    pid = fp.read().strip()
                    fp.close()
                    st  = os.stat(Basic.lock_filename)
                    age = hms_string(time.time()-st.st_mtime)
                    Basic.logger.info("%s locked by process with pid %s for: %s: version %s" % 
                                              (Basic.lock_filename,pid,age,version))
                    sys.stdout.write("%s locked by process with pid %s for %s" % (Basic.lock_filename,pid,age))
                    
                    try:   
                         os.kill(int(pid), 0)
                         Basic.logger.info("process with pid %s is still alive" % (pid), extra={"package_version":version})
                    except OSError:
                         Basic.logger.error("process with pid %s is not alive: Remove it's lock file" % (pid), extra={"package_version":version})
                         sys.stderr.write("process with pid %s is not alive: Remove it's lock file" % (pid))
                         os.remove(Basic.lock_filename)
                    # In any case exit here -next time the lock-file has been gone ...
                    self.__exit__( 1,2,3)
                    sys.exit(0)
                    #raise SystemExit()

            if have_config_file:
                config_file_directory = os.getenv("BASIC_CONFIGFILE_DIR", False)
                if config_file_directory:
                    if not os.path.isdir(config_file_directory):
                        Basic.logger.fatal("The BASIC_CONFIGFILE_DIR %s does not exist"%(config_file_directory),extra={"package_version":version})
                        sys.stderr.write(
                            "ERROR: The BASIC_CONFIGFILE_DIR %s does not exist. EXIT NOW" % (config_file_directory))
                        self.__exit__( 1,2,3)
                        sys.exit(1)
                    else:
                        Basic.config_file_name = os.path.join(config_file_directory, Basic.name + Basic.suffix + ".cfg")
                        Basic.logger.info("The config_file was forced  to %s " % Basic.config_file_name,extra={"package_version":version})
                else:
                    Basic.config_file_name = os.path.join(os.getcwd(), Basic.name + Basic.suffix + ".cfg")


                Basic.config_parser = SafeConfigParser()
                try:
                    if os.path.isfile(Basic.config_file_name):
                        Basic.config_parser.read(Basic.config_file_name)
                    else:
                        Basic.logger.debug("No config file %s given: version %s " % (Basic.config_file_name,version))
                        if force_usage_of_config_file:
                            sys.stderr.write("No config file %s given but it's usage is mandatory" % (Basic.config_file_name))
                            Basic.logger.fatal("No config file %s given but it's usage is mandatory: version %s" % (Basic.config_file_name,version))
                            self.__exit__( 1,2,3)
                            sys.exit(1)

                except ParsingError:
                    e = sys.exc_info()[1]
                    Basic.logger.exception("Error reading config File: version %s"%(version))
                    sys.stderr.write("Error reading config File: EXIT Now")
                    sys.stderr.write(traceback.format_exc())
                    # import pdb;pdb.set_trace()
                    if Basic.name.startswith("Test"):
                        raise e
                    else:
                        self.__exit__( 1,2,3)
                        sys.exit(1)
                except SystemExit:
                    e = sys.exc_info()[1]
                    self.__exit__( 1,2,3)
                    raise e

                if force_usage_of_config_file:
                    try:
                        Basic.primary_herald_url = Basic.config_parser.get("GLOBAL", 'herald_url')
                    except:
                        Basic.logger.fatal( "Value of herald_url in GLOBAL section of %s not given - but needed. EXIT NOW"%(Basic.config_file_name),extra={"package_version":version})
                        sys.stderr.write("Value of herald_url GLOBAL section of %s not given. EXIT NOW" % Basic.config_file_name)
                        self.__exit__( 1,2,3)
                        sys.exit(1)

                try:
                    PATTERN_LANGUAGE = Basic.config_parser.get("GLOBAL", 'pattern_language')
                    if PATTERN_LANGUAGE not in PATTERN_LANGUAGES:
                        Basic.logger.fatal( "Value of pattern_language in GLOBAL section of %s not allowed. EXIT NOW" % Basic.config_file_name,extra={"package_version":version})
                        sys.stderr.write("Value of pattern_language in GLOBAL section of %s not allowed. EXIT NOW" % Basic.config_file_name)
                        self.__exit__( 1,2,3)
                        sys.exit(1)
                except:
                    PATTERN_LANGUAGE = "EN"
                    Basic.logger.debug( template_writer(LOGGING_PATTERNS, PATTERN_LANGUAGE, "LANGUAGE_PATTERN_FAILED", locals()),extra={"package_version":version})



                # ToDo: Add Trap handler to reread config while running (e.g. switch logging level)
                html_string = "<table>"
                for section_name in Basic.config_parser.sections():
                    html_string += "<tr><td>%s</td></tr>" % (section_name)
                    for name, value in Basic.config_parser.items(section_name):
                        html_string += "<tr><td>%s</td><td>%s</td></tr>" % (str(name), str(value))
                        if name == "LOGGING": Basic.logger.setLevel(int(value))
                html_string += "</table>"
                if html_string != "<table></table>" or Basic.name == "Tests":
                     Basic.logger.debug(html_string,extra={"package_version":version})


    @classmethod
    def verbose(self ):
        """ Print log messages to stdout too """
        ch=logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formater=logging.Formatter('%(asctime)s - %(name)-12s %(lineno)d - %(message)s')
        Basic.logger.addHandler(ch) 

     
    def __exit__(self, exc_type, exc_value, traceback):
        import sys
        #sys.stderr.write("Exit Basic singleton %s"%(version))
        if exc_type ==1 and exc_value == 2 and traceback == 3:
          try:
            import os
            if os.path.isfile(self.lock_filename):
                Basic.logger.debug("remove lock_file %s"%(self.lock_filename), extra={"package_version":version})
                os.unlink(self.lock_filename)
          except:
            Basic.logger.exception("remove log_file: version %s"%(version))
            sys.stdout.write("Unable to remove lock file")
            sys.stderr.write("Unable to remove lock file")
            import traceback
            sys.stderr.write(traceback.print_exc())
        else:
            Basic.logger.error("remove log_file Leave Singleton with nonstandard __exit__", extra={"package_version":version})
            sys.stderr.write("Leave Singleton with nonstandard __exit__")
         

    def __del__(self):
        """ default destructor currently calling __exit__ only if we have a lockfile"""
        if Basic.i_have_lock: self.__exit__(1, 2, 3)


import sys
import time
import logging
from subprocess import Popen, PIPE
import smtplib
import traceback


###########################get_html_string##########################
def get_html_string(var_p ):
   """ return html table structure for a data structure (currently only dict) ."""

   html_string = "<table>"
   for name, value in var_p.items():
     if type(value) is dict:
         html_string += "<tr><td>%s</td><td>%s</td></tr>" % (str(name), get_html_string(value))
     else:
        html_string += "<tr><td>%s</td><td>%s</td></tr>" % (str(name), str(value))
   html_string += "</table>"
   return html_string



###########################ps_shell############################

def ps_shell(cmd_p, env_p=None):
    logger = Basic.logger
    success = "SUCCESS"
    try:
        start_time = time.time()
        child = Popen(cmd_p, shell=True, stdout=PIPE, stderr=PIPE, env=env_p, universal_newlines=True)
        (stdout, stderr) = child.communicate()
        exitcode = child.poll()
        end_time = time.time()

    except Exception:
        sys.stdout.write("%s: Exception while calling %s" % (Basic.name, cmd_p))
        logger.exception("Exception while calling %s" % (cmd_p))
        stdout = "ERROR"
        stderr = traceback.format_exc()
        exitcode = 1
        end_time = time.time()

    time_needed = hms_string(end_time - start_time)
    if exitcode != 0:
        success = "ERROR"
    logger.debug("%s %s %s " % (success, time_needed, cmd_p),extra={"package_version":version})
    if exitcode != 0:
        logger.error("%d %s" % (int(exitcode), stderr),extra={"package_version":version})

    return (
        str(stdout).strip().split("\n"),
        str(stderr).strip().split("\n"),
        exitcode,
        time_needed
    )


def send_a_mail(sent_from, l_send_to_p, subject, text, files=[], server="localhost", test_only=False):
    assert isinstance(l_send_to_p, list)
    assert isinstance(files, list)
    logger = Basic.logger
    logger.debug("TRY send_mail FROM " + sent_from + " TO " + str(l_send_to_p) + " subject " + subject,extra={"package_version":version})

    msg = MIMEMultipart('alternative')
    msg['From'] = sent_from
    msg['To'] = COMMASPACE.join(l_send_to_p)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(text, 'html'))

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        email.encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition', 'attachment; filename="%s"' %
                                   os.path.basename(f))
        msg.attach(part)

    try:
        
        if not test_only and Basic.dev_stage != "TESTING": 
                     smtp = smtplib.SMTP(server)
                     smtp.sendmail(sent_from, l_send_to_p, msg.as_string())
                     smtp.close()
        else:
                     Basic.curr_mail_sender      = sent_from
                     Basic.curr_mail_recipients  = l_send_to_p
                     Basic.curr_mail_subject     = subject
                     Basic.curr_mail_text        = text  

        logger.debug("SUCC send_mail FROM " + sent_from + " TO " + \
                         str(l_send_to_p) + " subject " + \
                         subject,extra={"package_version":version})
    except:
        logger.error("FAILURE send_mail FROM " + sent_from + " TO " + \
                         str(l_send_to_p) + " subject " + subject,
                         exc_info=True,extra={"package_version":version})
        sys.stdout.write("Exception Sending Email")
        try:
             
            logger.debug("Try To send via shell mail", extra={"package_version":version})
            for dst in l_send_to_p:
                cmd = ' echo "%s" | mail -s "%s" %s' % (text, subject, dst)
                logger.debug("Try to send mail via shell %s" % (cmd),extra={"package_version":version})
                o, e, ex, t = ps_shell(cmd)
                if int(ex) > 0:
                    logger.error("FAILURE Mail via shell",extra={"package_version":version})
                else:
                    logger.info("SUCCESS Mail via shell to %s"%(dst),extra={"package_version":version})
        except:
           logger.error("FAILURE send_mail via shell FROM " + send_from + " TO " + str(l_send_to_p) + " subject " + subject)


import re
import inspect
import pdb


def local_exec(exec_instance_p, local_shell_cmds_p, exec_cmd_shortcut_p, d_vars_p, ret_stdout=False):
    """Helper function with EXEC CLASS"""
    template = local_shell_cmds_p[exec_cmd_shortcut_p]
    exec_instance_p.lexec(template % (d_vars_p))
    if ret_stdout:
        return exec_instance_p.stdout[0]


def remote_exec(exec_instance_p, remote_shell_cmds_p, exec_cmd_shortcut_p, d_vars_p, ret_stdout=False,
                ret_stdoutFull=False):
    """Helper function with EXEC CLASS"""
    template = remote_shell_cmds_p[exec_cmd_shortcut_p]
    exec_instance_p.rexec(template % (d_vars_p))
    if ret_stdoutFull: return exec_instance_p.stdout
    if ret_stdout:     return exec_instance_p.stdout[0]


class EXEC(object):
    """
       The EXEC class is used to ease the usage of patterns for shell commands.
       In order to work for remote commands, a

       >>> A_FILE_NAME="foo"
       >>> LOCAL_SHELL_CMDS = { "L_TOUCH_FILE": "touch /tmp/%(A_FILE_NAME)s",
       ...                      "L_LS_FILE"   : "ls /tmp/%(A_FILE_NAME)s", }
       >>> x=Basic.get_instance("EXEC_Test")
       >>> from ps.Basic import EXEC,local_exec
       >>> DESTINATION_HOST="xx"
       >>> myg = globals().copy()
       >>> myg.update(locals()) 
       >>> r = EXEC(x, dictionary=myg)
       >>> r = EXEC(x, dictionary={"DESTINATION_HOST":DESTINATION_HOST})
       >>> local_exec(r, LOCAL_SHELL_CMDS, "L_TOUCH_FILE", myg)
       >>> r.exitcode
       0
       >>> r.stderr
       ['']
       >>> r.stdout
       ['']
       >>> local_exec(r, LOCAL_SHELL_CMDS, "L_LS_FILE", myg )
       >>> r.exitcode
       0
       >>> r.stderr
       ['']
       >>> r.stdout
       ['/tmp/foo']
        

    """

    def __init__(self, sys_p, dictionary=None):
        # UserDict.__init__(self)
        self.logger = Basic.logger
        self.data = {}
        self.stdout, self.stdin, self.exitcode, self.timings = "", "", -1, ""
        if dictionary is not None:
            for key in dictionary.keys():
                self.data[key] = dictionary[key]
        try:
            self.data['SSH_CMD_PREFIX'] = 'ssh -o "ConnectTimeout 20"  %s' % (self.data["DESTINATION_HOST"])
        except:
            self.logger.exception("DESTINATION_HOST not set. EXEC instance will not be available for remote commands.")

    def __repr__(self):
        return repr(self.data)

    def lexec(self, cmd_p, stop_on_Failure=True):
        self.data['curr_cmd'] = cmd_p

        cmd = "%(curr_cmd)s" % (self.data)

        self.logger.debug("%s execute Command %s" % (Basic.name, cmd),extra={"package_version":version})
        self.stdout, self.stderr, self.exitcode, self.timings = ps_shell(cmd)
        if self.exitcode != 0:
            self.logger.error("%s stdout %s: version %s" % (Basic.name, self.stdout,version))
            self.logger.error("%s stderr %s: version %s" % (Basic.name, self.stderr,version))
            return 1  # ==> indicates error
        return 0  # indicates success

    def rexec(self, cmd_p, stop_on_Failure=True):
        frame, filename, line_number, function_name, lines, index = \
            inspect.getouterframes(inspect.currentframe())[1]
        self.logger.debug(
            "%s remotely execute (line %d) Command %s: version %s" % (Basic.name, line_number, cmd_p,version))
        self.data['curr_cmd'] = cmd_p
        cmd = "%(SSH_CMD_PREFIX)s %(curr_cmd)s" % (self.data)
        return self.lexec(cmd)


#
# The following writer functions are used together with xxx_pattern.py files
# in a project.
# param1 ==> xxx_patterns: dictionary with patterns for different languages
# e.g. LOGGING_PATTERNS = {
#    "DE": {
#        "RSYNC_FAILED": "Der rsync Aufruf/transfer hatte einen Fehler. Abort now.",
#        "RSYNC_SUCC": "SUCCESS rsync uebermittelte %(asia_cloud_host)s/%(srcdir_on_asia_host)s ==>%(PATH_TO_LOCAL_MIRROR_DIR)s",
#
#    },
#    "EN": {
#        "RSYNC_FAILED": "The rsync transfer exited with an error. Abort now.",
#        "RSYNC_SUCC": "SUCCESS rsync transfered %(asia_cloud_host)s/%(srcdir_on_asia_host)s ==>%(PATH_TO_LOCAL_MIRROR_DIR)s",
#
#    },
# }
# param2 ==> pattern_language: string e.g. DE or EN
# param3 ==> name of the pattern to use e.g. RSYNC_SUCC 
# param4 ==> dictionary  with name value pairs to be substituted in pattern

# The functions return the corresponding string in the defined language with the variables substituted.

def template_writer(patterns_p, pattern_offset_p, pattern_p, d_vars_p):
    """
      A helper function for writing strings  from patterns 
    """

    try:
        template = patterns_p[pattern_offset_p][pattern_p]
        return template % (d_vars_p)
    except:
        Basic.logger.exception("unable to generate string in %s from template %s" % (pattern_offset_p, pattern_p))
        time.sleep(2)  # give logging a little time to write the message
        raise KeyError(pattern_offset_p)
