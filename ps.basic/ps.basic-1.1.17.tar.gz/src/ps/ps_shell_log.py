# psf: ta=4, -*-Python-*-, vi: set et ts=4: coding: utf-8
__doc__ = """ps_shell_log writes strings to the ps logging of the DEV_STAGE 

  Usage: ps_shell_log [-v] [ --level=LEVEL ] [ --service_name=name ] TEXT ...

  Arguments:
    TEXT  Message to be printed

  Options:
    -h --help             Show this screen.
    -v                    verbose
    --level=LEVEL         LogLevel (DEBUG,INFO,ERROR,WARNING,FATAL) 
    -service_name=value   the system_id of the message  

"""
import sys
import docopt
import re, os
import urllib2, base64
from   ps.Basic import Basic
from package_version import version

def main():
    level="info"
    service_name="shell_log"
    options = docopt.docopt(__doc__, version=1)
    sys.stdout.write(options)
    if options["-v"]:                     VERBOSE = True
    if options["--level"] != None:        level=options["--level"]
    if options["--service_name"] != None: service_name=options["--service_name"]

    the_singleton = Basic.get_instance(service_name, have_config_file=False)
    try:
       exec('Basic.logger.%s("%s",extra={"package_version":"%s")'%(level.lower(),options['TEXT'],str(version)))
    except:
       Basic.logger.exception("Exception while calling ps_shell_log")
