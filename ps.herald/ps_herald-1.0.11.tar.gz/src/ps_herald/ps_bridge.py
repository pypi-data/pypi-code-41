doc_rest="""
"""
__doc__="""

 The Bridge module receives messages emited with the Standard Python logging StreamHandler.
 These messages are stored in a database. 
 The logging events lateron can be analyzed e.g. with the herald Server.

 To use the bridge-functionality, it might be needed to establish a tunnel to another machine,
 another bridge is listening e.g:

   ssh -f -oExitOnForwardFailure=yes   -R 9019:localhost:9024 hr2dev@vl-knecht-ci1.haufe-ep.de  -N
Usage:
  bridge.py [-v] [-b] [-p] [-s AGE ] [-r ROUND ]  

Option:
  -h, --help       Show this screen.
  -v, --verbose    verbose
  -b, --bridge     bridge the received logging event additionaly on the bridge-port 
  -s AGE           delete messages older than age seconds while running ( a week are 604800 seconds)
  -r ROUND         check for messages to delete after that amount of inserts
"""


import docopt
import asyncio
import struct
#import herald_package_version 
herald_package_version ="tBD"
from pickle import loads
import pickle
import time
import os
import sys 
import traceback
import socket
import sys
import logging
import datetime 
import requests
import json
import ps
from ps.Basic import Basic

# make sure we can import from app directory
l = os.path.split(os.path.dirname(os.path.abspath(__file__)))[:-1]
print(l[0])
sys.path.append(l[0])
for i in sys.path:print(i)
sys.stdout.flush()
#base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
#sys.path.append(base_dir)
from ps_herald import db,create_app,cli
from ps_herald.models import User, Post, Log

class MyConfig(object):
    version = "TBD"

herald_package_version=MyConfig()


ps_basic_singleton = ps.Basic.Basic.get_instance("bridge", guarded_by_lockfile=True)
sys.stdout.flush()
app = create_app()
#cli.register(app)

sys.stdout.flush()


CLIENTS = {} # asynchronous tasks are "remembered here"

VERBOSE                      = False
BRIDGE_MODE                  = False
AGE                          = False 
ROUND                        = 1024 

def init_database():
    """ The "None" value in the fields is a placeholder for any-value in the web interface. We ensure, that at least one entry is in the database"""

    with app.app_context():
      try:
        log=Log(produkt_id="None",system_id="None",sub_system_id="None",sub_sub_system_id="None",user_spec_1="None", user_spec_2="None",summary="None")
        db.session.add(log)
        db.session.commit()
      except:
         print(traceback.format_exc())
         Basic.logger.exception("error init database")
         sys.exit(1)



def client_connected_handler(client_reader, client_writer):
    """ Start a new asyncio.Task to handle this specific client connection"""
    task = asyncio.Task(handle_client(client_reader, client_writer))
    CLIENTS[task] = (client_reader, client_writer)
 
    def client_done(task):
        """When the tasks that handles the specific client connection is done"""
        del CLIENTS[task]
 
    # Add the client_done callback to be run when the future becomes done
    task.add_done_callback(client_done)

 
@asyncio.coroutine
def handle_client(client_reader, client_writer):
    """ Runs for each client connected. 
        The protocol used is:  first 4 bite define the len of the message. 
        Hence in the first step, the first four byte are read and the the test of the message.
        This "rest" of the message is depickled and stored in the database.
        If the "bridge-mode" is enable, the "byte-buffer" (first 4 bytes plus the rest of the
        message is also sent to another socket - the bridge socket.
    """
    global socke, VERBOSE, BRIDGE_MODE, AGE, ROUND 
    current_round = 0
    while True:
        current_round += 1
        data1 = yield from (client_reader.read(4))
        if not data1: break
        if len(data1) < 4:
           print ("Did not receive First 4 Bytes of message")
           raise
        slen = struct.unpack('>L', data1)[0]
        data2=yield from (client_reader.read(slen))
        if BRIDGE_MODE: print_to_tunnel(data1 +  data2)    
        obj = loads(data2)
        dt = datetime.datetime.now()
        obj['created'] = dt.strftime("%Y-%m-%d %H:%M:%S.%f")   

        lowered_obj={}
        try:
            # While migrating, there may be pakets without the additional info -  
            lowered_obj["summary"]=str(None)
            lowered_obj["produkt_id"]=str(None)
            lowered_obj["system_id"]=str(None)
            lowered_obj["sub_system_id"]=str(None)
            lowered_obj["sub_sub_system_id"]=str(None)
            lowered_obj["user_spec_1"]=str(None)
            lowered_obj["user_spec_2"]=str(None)
            lowered_obj["api_version"]=str(None)
            lowered_obj["package_version"]=str(None)
            for name,value in obj.items():
                 #: obselete if everything switched to ps.basic > 0.4
                 if name == "PID": name = "produkt_id"
                 #:?? sometimes message appears here ?
                 if name == "msg": 
                                name = "message"
                                value = value.replace(u"\u2018", " ").replace(u"\u2019", " ")
                                value=str(value).replace("'"," ").replace('"'," ")
                 if name == "args": value = ""
                 if value is None: lowered_obj[name.lower()] = str(value)
                 else:             lowered_obj[name.lower()] = value
                 if VERBOSE: print (name.lower() ,"    ", value)
            #
            # The summary Attribute of the model eases searching in the database 
            # later.
            lowered_obj["summary"] = str("None") + lowered_obj["produkt_id"]  \
                                 +lowered_obj["system_id"] \
                                 +lowered_obj["sub_system_id"] +lowered_obj["sub_sub_system_id"] \
                                 +lowered_obj["user_spec_1"]   +lowered_obj["user_spec_2"] 
            row=Log(**lowered_obj)
            with app.app_context():
                 db.session.add(row)
                 db.session.commit()
        #except ConnectionError as e:
        #        Basic.logger.exception("Exception: trying to connect to elastic_search server. ", extra={"package_version":herald_package_version.version})
        #        sys.exit(1) 
        except:
            Basic.logger.exception("Error: while writing to database/elasticsearch", extra={"package_version":"XXX"}) #herald_package_version.version})
            print (lowered_obj)
            traceback.print_exc(file=sys.stderr)
            with app.app_context():
                db.session.rollback()
            continue 
        if VERBOSE: print ("Added a row")
        if AGE and 0 == (current_round % ROUND) :
          current_round = 0
          start_date = str(datetime.datetime.now() -  datetime.timedelta(seconds=AGE)) 
          to_del     = Log.query.filter(Log.created < start_date).delete()
          sys.stdout.write("OK: %s rows deleted"%(to_del))
  
    


socke = None

def print_to_tunnel(data_p):
    global socke
    try:
        socke.sendall(data_p) 
    except AttributeError:
       import pdb
       #pdb.set_trace()
       #Basic.logger.error("Error: while writing to bridge-tunnel ", extra={"package_version":herald_package_version.version})
       socke=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
       socke.connect(("",Basic.logging_bridge_port))
       sys.stderr.write("Attribute Error: while writing to bridge-tunnel ")
    except:
       sys.stderr.write("Error: while writing to bridge-tunnel ")
       #Basic.logger.exception("Error: while writing to bridge-tunnel " )
       traceback.print_exc(file=sys.stdout)
       #reset socket descriptor, so that it will be initialized in the 
       #next round
       import pdb
       socke.close()
       socke=None 

def main():
  """ """
  global  VERBOSE, BRIDGE_MODE, AGE, ROUND  
  options = docopt.docopt(__doc__, version=1 )
  #ps.Basic.Basic.logger.debug("started", extra = {"package_version":herald_package_version.version})
  ps.Basic.Basic.logger.debug("started", extra = {"package_version":herald_package_version})
  print(options)

  sys.stdout.flush()
  if options["--verbose"]: VERBOSE                      = True
  if options["--bridge"] : BRIDGE_MODE                  = True
  if options["-s"]       : AGE                          = int(options["-s"])
  if options["-r"]       : ROUND                        = int(options["-r"])


  init_database()
  sys.stdout.flush()
  loop = asyncio.get_event_loop()
  sys.stdout.flush()
  print("will listen on %d"%(Basic.logging_port))
  loop.run_until_complete(asyncio.start_server(client_connected_handler, '0.0.0.0', Basic.logging_port))
  sys.stdout.flush()
  try:
    loop.run_forever()
  finally:
    loop.close()



if __name__ == "__main__":
     main()
