#!/usr/bin/env python

import os
import sys
import time
import json
import sh
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from snap import common

PIPELINE_CMD = '{pipeline_dir}/pipeline.sh'

class Watcher:
    def __init__(self, target_dir):
        self.target_directory = target_dir
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

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)
            if not event.src_path.find('pipeline'):
                return None
            #print(event)
            jobdata = None
            with open(event.src_path) as f:
                raw_jobdata = f.readline()
                jobdata = json.loads(raw_jobdata)

            print(common.jsonpretty(jobdata))
            
            pipeline_command_string = PIPELINE_CMD.format(pipeline_dir=os.getcwd())
            print(pipeline_command_string)
            
            source_schema = jobdata['source_schema']
            target_schema = jobdata['target_schema']
            pcmd = sh.Command(pipeline_command_string)
            for line in pcmd('assets_qdm.txt', source_schema, target_schema, _err=sys.stdout, _iter=True):
                print(line)
            

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s." % event.src_path)
            print(event)


if __name__ == '__main__':
    w = Watcher('/tmp')
    w.run()
