#!/usr/bin/env python

'''
Usage:
    dirwatch --config <configfile> --target <target_command>
    dirwatch --dir <directory> --filter <filter_exp> --command <cmd> --log <logfile>

'''

import os
import sys
import time
import json
import sh
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import docopt
from snap import common


PIPELINE_CMD = '{pipeline_dir}/pipeline.sh {asset_list} {source_schema} {target_schema}'
'''
class HandlerConfig(object):
    template = None
    logfile = None
    payload = {}
'''


class Watcher:
    def __init__(self, target_dir, filename_filter, command_template, logfile, **kwargs):
        self.target_directory = target_dir
        Handler.command_template = command_template
        Handler.logfile = logfile
        Handler.payload = kwargs
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.target_directory, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except Exception as err:
            self.observer.stop()
            print("Error handling filesystem evemt: %s" % err)

        self.observer.join()


class Handler(FileSystemEventHandler):
    command_template = None
    logfile = None
    payload = {}
    @classmethod
    def on_any_event(cls, event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)

            filename = os.path.basename(event.src_path)
            print('filename: %s' % filename)
            
            if not filename.startswith('pipeline'):
                return None
            
            jobdata = {}
            with open(event.src_path) as f:
                raw_jobdata = f.readline()
                if raw_jobdata:
                    jobdata = json.loads(raw_jobdata)

            print(common.jsonpretty(jobdata))
            
            pipeline_command_string = PIPELINE_CMD.format(pipeline_dir=os.getcwd(),
                                                          asset_list='assets_pdm.txt',
                                                          source_schema=jobdata['source_schema'],
                                                          target_schema=jobdata['target_schema'])
            print(pipeline_command_string)
            
            #source_schema = jobdata['source_schema']
            #target_schema = jobdata['target_schema']
            pcmd = sh.Command(pipeline_command_string)
            for line in pcmd(_err=sys.stdout, _iter=True):
                print(line)
            

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)
            print(event)


def main(args):
    
    print(common.jsonpretty(args))

    # dirwatch --dir <directory> --filter <filter_exp> --command <cmd> --log <logfile>
    if args['--config'] == True: # read config params from file
        configfile = args['<configfile>']
        yaml_config = common.read_config_file(configfile)
    else: # read config params from the command line
        target_dir = args['<directory>']
        filename_filter = args['<filter_exp>']
        command = args['<cmd>']
        logfile = args['<logfile>']

        w = Watcher(target_dir, filename_filter, command, logfile)
        w.run()


if __name__ == '__main__':
    args = docopt.docopt(__doc__)    
    main(args)
