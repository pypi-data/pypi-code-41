#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Utils service.

# File: srv_utils.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Generic functions service
"""

import os
import glob
import time
import shutil
import random
import threading
import subprocess
from urllib.parse import quote, unquote
from kb4it.core.mod_srv import Service
from kb4it.core.mod_env import LPATH, GPATH, SEP, EOHMARK



class Utils(Service):
    """
    Missing class docstring (missing-docstring)
    """
    def initialize(self):
        self.get_services()

    def get_services(self):
        self.srvapp = self.get_service('App')

    def copy_docs(self, docs, target):
        for doc in docs:
            shutil.copy(doc, target)
        # ~ log.debug("\t%d docs copied to %s" % (len(docs), target))

    def copydir(self, source, dest):
        """Copy a directory structure overwriting existing files
        https://gist.github.com/dreikanter/5650973#gistcomment-835606
        """
        for root, dirs, files in os.walk(source):
            if not os.path.isdir(root):
                os.makedirs(root)

            for file in files:
                rel_path = root.replace(source, '').lstrip(os.sep)
                dest_path = os.path.join(dest, rel_path)

                if not os.path.isdir(dest_path):
                    os.makedirs(dest_path)

                shutil.copyfile(os.path.join(root, file), os.path.join(dest_path, file))

    def get_source_docs(self, path):
        if path[:-1] != os.path.sep:
            path = path + os.path.sep

        pattern = os.path.join(path) + '*.adoc'
        docs = glob.glob(pattern)
        self.log.info("\tFound %d asciidoc documents", len(docs))

        return docs

    def get_template(self, template):
        DIR_SCRIPT = os.path.dirname(__file__)
        TEMPLATE_PATH = GPATH['TEMPLATES'] + template + '.tpl'
        return open(TEMPLATE_PATH, 'r').read()

    def exec_cmd(self, data):
        """
        Execute an operating system command an return:
        - document
        - True if success, False if not
        - res is the output
        """
        doc, cmd, res = data
        process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
        outs, errs = process.communicate()
        if errs is None:
            return doc, True, res
        else:
            log.debug("Command: %s", cmd)
            log.debug("Compiling %s: Error: %s", (doc, errs))
            return doc, False, res

    def set_max_frequency(self, dkeyurl):
        """
        Calculate and set max frequency
        """
        max_frequency = 1
        for keyword in dkeyurl:
            cur_frequency = len(dkeyurl[keyword])
            if cur_frequency > max_frequency:
                max_frequency = cur_frequency

        return max_frequency


    def get_font_size(self, frequency, max_frequency):
        """
        Get font size for a word based in its frequency
        """
        if frequency > 1:
            proportion = int((frequency * 100) / max_frequency)
        else:
            proportion = 1

        size = 8
        if proportion < 2: size = 8
        elif proportion >= 2 and proportion < 10: size = 10
        elif proportion in range(10, 19): size = 12
        elif proportion in range(20, 29): size = 14
        elif proportion in range(30, 39): size = 18
        elif proportion in range(40, 49): size = 26
        elif proportion in range(50, 59): size = 30
        elif proportion in range(60, 69): size = 36
        elif proportion in range(70, 79): size = 42
        elif proportion in range(80, 89): size = 48
        elif proportion in range(90, 99): size = 54
        elif proportion == 100: size = 72

        return size


    def nosb(self, alist, lower=False):
        """
        return a new list of elements, forcing them to lowercase if
        necessary.
        """
        newlist = []
        for item in alist:
            if len(item) > 0:
                if lower:
                    item = item.lower()
                newlist.append(item.strip())
        newlist.sort()

        return newlist


    def job_done(self, future):
        time.sleep(random.random())
        x = future.result()
        cur_thread = threading.current_thread().name
        if (cur_thread != x):
            # ~ print(x) #cur_thread) #, x)
            doc, rc, j = x
            self.log.debug("Job %2d: %s compiled", j, doc)

    def create_directory(self, directory):
        """Create a given directory path."""

        if not os.path.exists(directory):
            os.makedirs(directory)
            self.log.debug("Creating directory '%s'", directory)

    def create_target(self, source_path, target_path):
        tmpdir = self.srvapp.get_temp_dir()
        pattern = source_path + SEP + '*.adoc'
        files = glob.glob(pattern)
        for filename in files:
            shutil.copy(filename, target_path)

        pattern = tmpdir + SEP + '*.html'
        files = glob.glob(pattern)
        for filename in files:
            shutil.copy(filename, target_path)

    def delete_target_contents(self, target_path):
        if not os.path.exists(target_path):
            self.log.info("\tTarget directory '%s' does not exists", target_path)
        else:
            for file_object in os.listdir(target_path):
                file_object_path = os.path.join(target_path, file_object)
                if os.path.isfile(file_object_path):
                    os.unlink(file_object_path)
                else:
                    shutil.rmtree(file_object_path)
            self.log.info("\tContents of directory '%s' deleted successfully", target_path)

    def get_metadata(self, docpath):
        props = {}
        try:
            # Get lines
            line = open(docpath, 'r').readlines()

            # Add document title (first line) to graph
            title = line[0][2:-1]
            props['Title'] = [title]

            # read the rest of properties until watermark
            for n in range(1, len(line)):
                if line[n].startswith(':'):
                    key = line[n][1:line[n].rfind(':')]
                    alist = self.nosb(line[n][len(key)+2:-1].split(','))
                    props[key] = alist
                    # ~ for elem in alist:
                        # ~ self.add_document_attribute(doc, key, elem)
                elif line[n].startswith(EOHMARK):
                    # Stop processing if EOHMARK is found
                    break
        except Exception as error:
            self.log.error(error)
            self.log.error("Document %s could not be processed" % docpath)
        return props

    def uniq_sort(self, result):
        """Missing docstring."""
        alist = list(result)
        aset = set(alist)
        alist = list(aset)
        alist.sort()
        return alist