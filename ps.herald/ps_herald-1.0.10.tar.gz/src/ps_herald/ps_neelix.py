__doc__="""

  Neelix scans the log and triggers actions.

  It's work is based on two models:
     - Log
     - HeartBeat
 
  First it  analyses the Log-model, which Log.system-id's are available.
  For each system_id, the log is analyzed, if "reactions" should be triggered.
 
  Reactions   are defined in the configuration File. 

  Each system_id has it's own configuration section.

  Within each section currently two values could be defined:

       - MSG
       - AGE

  If either of these values is defined a parameter "MAIL_TO"
  has to be defined. Tho these addresses (a comma seperated list of 
  email recipients Emails will be sent - alerting the error.
  e.g::
 
    [ch2eu]
       MAIL_TO=hedwig@the_othercompany.ch,gottfried@haufe-lexware.com
       MSG="If this text would be found in a logging message would be send."
       #AGE Value is given in seconds
       AGE=60*60*2
    [hu2hu]
       MAIL_TO=hedwig@the_othercompany.ch,gottfried@haufe-lexware.com
       #AGE Value is given in seconds
       AGE=60*60*2
  
  Would consider the only logging-messages from the system-is's ch2eu and hu2hu. No other system_id
  will  be analyzed. Reactions will be triggered, if:

         - either we did not see a log message for the last 2 hours in the two systems
         - or in the ch2eu a logging msg appeared having a text like MSG "


  Usage:
        neelix.py [-v] [-r] [-t]

  Options:

    -h --help     Show this screen.
    -r            reinit model 
    -t            test-only mode 
    -v            verbose

"""

import docopt
import datetime, time
import time
import os
import traceback
import sys
import logging
import pdb
from socket import gethostname

from ps_herald import db,create_app,cli
from ps_herald.models import User, Post, Log,HeartBeat

import ps
from ps.Basic import Basic, send_a_mail
from sqlalchemy import func

class MyConfig(object):
    version = "TBD"

herald_package_version=MyConfig()

ps_basic_singleton = ps.Basic.Basic.get_instance("neelix", guarded_by_lockfile=True)

app = create_app()


TEXT_OF_THE_NOTIFICATION_MESSAGE="""
Dear Madam/Sir, <br>
<br>
 Neelix found a misbehaviour while analyzing the log on %(hostname)s
 The misbehaviour is  on system_id [%(system_id_p)s].
<br>

 The cause of the trigger was: [%(cause_p)s], the firing rule was [%(value_p)s]. 
<br>

 This event will be inserted into the logging messages of system [%(system_id_p)s]
 as an ERROR Event - by neelix.
<br>

 Please consult the Deployment Monitor for further information. 
<br>

 Regards
<br>
  Neelix

<br>
 
In case of questions ... contact  _EP-Produktionsstrecke .
<br>
"""

VERBOSE=False
TEST_ONLY=False


def react(system_id_p, cause_p, value_p, record_p):
   """
      - system_id_p  Name of the system for which we react
      - cause_p      Name of the cause e.g. PATTERN or AGE
      - value_p      Value of the cause                         
      - record_p     table-row of the logging table correlated to the event 

      >>> from ps import Basic
   """
   
   global  VERBOSE
   logger                  = Basic.logger
   hostname = gethostname()
   logger.debug("Neelix reacts sys_id %s: cause %s value %s "%(system_id_p,cause_p,value_p), 
                                  extra={"package_version":herald_package_version.version})
   mail_to=""
   for name,value in Basic.config_parser.items(system_id_p):
      if name=="mail_to": mail_to=value.split(",")
   if mail_to=="":
            mail_to=Basic.l_admin_mail
   message=record_p.message
   send_a_mail("neelix@haufe-lexware.com",\
                mail_to,\
                "neelix %s %s"%(system_id_p,cause_p),\
                TEXT_OF_THE_NOTIFICATION_MESSAGE%(locals()))
   record_p.message     = "Neelix React added Notification %s for %s"%(cause_p, system_id_p)
   record_p.system_id   = system_id_p
   record_p.exc_text    = record_p.message
   record_p.levelno     = 30
   record_p.levelname   = "ERROR"
   record_p.created     = time.strftime("%Y-%m-%d %H:%M:%S")
   di={}
   try:
       for key in record_p.__dict__.keys():
         # skip internal variables and primary key of the table
         if key.startswith("_"): continue 
         if key == "id"        : continue 
         di[key] = record_p.__dict__[key]
       logger.debug("react added new log entry %s "%(str(di)), extra={"package_version":herald_package_version.version})
       row=Log(**di)
       db.session.add(row)
       db.session.commit()
   except:
       print("Start exception ==================================================")
       traceback.print_exc(file=sys.stdout)
       logger.exception("Exception in react", extra={"package_version":herald_package_version.version})
       print("End exception (will rollback transaction now)  ===================")
       db.session.rollback()


def notify(system_id_p,starting_at_p,till_p):
  """
  """
  global  VERBOSE, TEST_ONLY
  if not system_id_p in Basic.config_parser.sections(): return 
  logger                  = Basic.logger
  msg_pattern="Not defined yet"
  allowed_age=9999999999999999999999999
  logger.debug("notify: check %s from %s to %s "%(system_id_p, starting_at_p,till_p), 
                           extra={"package_version":herald_package_version.version})
  for name,value in Basic.config_parser.items(system_id_p):
      #logger.debug("For %s configured : name %s value %s "%(system_id_p, name,value))
      if name=="msg": msg_pattern=value
      if name=="age": allowed_age=eval(value)

  
  #print "notify called with ", system_id_p, "  ", starting_at_p , " pattern ", msg_pattern, " allowed_age ", allowed_age
  #print "notify called with ", system_id_p, "  ", starting_at_p , " pattern ", msg_pattern
  with app.app_context():
      try:
            #ctx = herald_app.test_request_context()
            #ctx.push()
            records = Log.query.filter( Log.created    >=  starting_at_p,
                                               Log.created    <   till_p,
                                               Log.system_id  == system_id_p  ).all()

            for record in records:
              if msg_pattern in str(record.message): 
                   logger.debug("For %s found a PATTERN Log Entry %s "%(str(record)), 
                             extra={"package_version":herald_package_version.version})
                   react(system_id_p,"PATTERN FOUND","msg_pattern", record)
        
            newest = Log.query.filter(Log.system_id  == system_id_p).order_by(Log.created.desc()).first()
            try:
              time_created = time.strptime(newest.created,"%Y-%m-%d %H:%M:%S.%f")
              seconds_newest=time.mktime(time.strptime(newest.created,"%Y-%m-%d %H:%M:%S.%f"))
              seconds_now=time.mktime(time.strptime(str(till_p),"%Y-%m-%d %H:%M:%S.%f"))
            except:
              time_created = time.strptime(newest.created,"%Y-%m-%d %H:%M:%S")
              seconds_newest=time.mktime(time.strptime(newest.created,"%Y-%m-%d %H:%M:%S"))
              seconds_now=time.mktime(time.strptime(str(till_p),"%Y-%m-%d %H:%M:%S.%f"))

            
            real_age = seconds_now - seconds_newest
            logger.debug("For %s the last log message is aged %s seconds: allowed are %s \
                            seconds"%(system_id_p, real_age, allowed_age), 
                        extra={"package_version":herald_package_version.version})
        
            if allowed_age < (seconds_now - seconds_newest):
                   logger.debug("For %s found an AGE Log Entry %s "%(system_id_p, str(newest)), 
                                      extra={"package_version":herald_package_version.version})
                   react(system_id_p,"SYSTEM HEARTBEAT FAILURE", "age", newest)
            if TEST_ONLY:
                 if system_id_p=="neelix": react(system_id_p,"HURZ", "test", newest)

      except:
            print("Start exception ==================================================")
            traceback.print_exc(file=sys.stdout)
            logger.exception("Exception in notify", extra={"package_version":herald_package_version.version})
            print("End exception (will rollback transaction now)  ===================")
            db.session.rollback()


def check():
  """ """
  global  VERBOSE
  initial_heart_beat_date = "0000-01-01 14:05:39" 
  NOW                     = datetime.datetime.now()
  logger                  = Basic.logger
  with app.app_context():
      try:
            #ctx = herald_app.test_request_context()
            #ctx.push()
            system_ids = db.session.query(Log.system_id.distinct().label("system_id")).all()
            for system_id in system_ids:
                system_id  = system_id[0] # system_id is a tuple here, we only want the first value
                try:
                  old_heartbeat_entry = HeartBeat.query.filter(HeartBeat.system_id==system_id).all()[0]
                  newest_heartbeat    = old_heartbeat_entry.newest_heartbeat
                except:
                  newest_heartbeat = initial_heart_beat_date

                # Handle the with notify registered functions
                notify(system_id, newest_heartbeat,NOW)


                try:
                   # Delete the old HeartBeat Entry if such one was available
                   if not newest_heartbeat == initial_heart_beat_date:
                      db.session.delete(old_heartbeat_entry)
                      db.session.commit()
                   #Create the NewHearBeat Entry
                   di={}
                   di['newest_heartbeat'] = NOW
                   di['system_id']        = system_id
                   row=HeartBeat(**di)

                   #Commit
                   db.session.add(row)
                   db.session.commit()
                except:
                   print("Start exception ==================================================")
                   traceback.print_exc(file=sys.stdout)
                   print("End exception (will rollback transaction now)  ===================")
                   db.session.rollback()
                   print ("Except update")
                   pass
        
      except:
            print("Start exception ==================================================")
            traceback.print_exc(file=sys.stdout)
            logger.exception("Exception in check", extra={"package_version":herald_package_version.version})
            print("End exception (will rollback transaction now)  ===================")
            db.session.rollback()

def main():
  """ """
  global  VERBOSE, TEST_ONLY
  options = docopt.docopt(__doc__, version=1 )
  import ps
  retval = 0
  #ps_basic_singleton = ps.Basic.Basic.get_instance("neelix", guarded_by_lockfile=True)
  ps.Basic.Basic.logger.debug("started", extra={"package_version":herald_package_version.version})

  try:
    if options["-v"]: VERBOSE    = True
    if options["-t"]: 
                      VERBOSE    = True
                      TEST_ONLY  = True


    if options["-r"]:     db.create_all()
    else:                 check()
  
  except SystemExit as e:
      ps.Basic.Basic.logger.exception("Exit in main: system exit handler",
                                       extra = {"package_version":herald_package_version.version})
      retval = e.code
  except:
     ps.Basic.Basic.logger.exception("Exception in main: outer handler", 
                                     extra = {"package_version":herald_package_version.version})
     retval = 4

  ps_basic_singleton.__exit__(1, 2, 3)
  return(retval)


if __name__ == "__main__": 
    main()
