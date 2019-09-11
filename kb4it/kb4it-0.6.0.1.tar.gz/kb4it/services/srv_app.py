#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module with the application logic.

# Author: Tomás Vírseda <tomasvirseda@gmail.com>
# License: GPLv3
# Description: module holding the application logic
"""

import os
import shutil
import tempfile
import datetime
from urllib.parse import quote, unquote
from concurrent.futures import ThreadPoolExecutor as Executor
from rdflib import URIRef
from rdflib import Literal
from kb4it.services.srv_rdfdb import RDF, KB4IT
from kb4it.core.mod_env import LPATH, GPATH, SEP
from kb4it.core.mod_env import ADOCPROPS, MAX_WORKERS, EOHMARK
from kb4it.core.mod_srv import Service

EOHMARK = """// END-OF-HEADER. DO NOT MODIFY OR DELETE THIS LINE"""



class Application(Service):
    """Missing class docstring (missing-docstring)."""

    params = None
    target_path = None
    source_path = None
    graph = None
    tmpdir = None
    numdocs = 0

    def initialize(self):
        """Missing method docstring."""
        self.tmpdir = tempfile.mkdtemp()
        self.params = self.app.get_params()
        if self.params.TARGET_PATH is None:
            self.target_path = LPATH['WWW']
        else:
            self.target_path = self.params.TARGET_PATH
        self.source_path = os.path.realpath(self.params.SOURCE_PATH)
        self.get_services()

    def get_temp_dir(self):
        """Missing method docstring."""
        return self.tmpdir

    def get_services(self):
        """Missing method docstring."""
        self.srvutl = self.get_service('Utils')
        self.srvdtb = self.get_service('DB')
        self.srvbld = self.get_service('Builder')

    def get_numdocs(self):
        """Missing method docstring."""
        return self.numdocs

    def process_docs(self):
        """Missing method docstring."""
        TOP_NAV_BAR = self.srvutl.get_template('TPL_TOP_NAV_BAR')
        attributes = self.srvdtb.get_attributes()
        for attribute in attributes:
            self.log.debug("Processing attribute: %s", attribute)
            key = attribute[attribute.rfind('/') + 4:]
            docname = "%s/%s.adoc" % (self.tmpdir, key)
            values = self.srvdtb.objects(None, attribute)
            html = self.srvbld.create_key_page(key, list(values))
            with open(docname, 'w') as fkey:
                TPL_METAKEY = self.srvutl.get_template('TPL_METAKEY')
                fkey.write(TPL_METAKEY % key)
                fkey.write(html)
                for value in values:
                    # Create .adoc from value
                    docname = "%s/%s_%s.adoc" % (self.tmpdir, key, value)
                    with open(docname, 'w') as fvalue:
                        TPL_VALUE = self.srvutl.get_template('TPL_VALUE')
                        fvalue.write(TPL_VALUE % (key, unquote(value)))

                        # Search documents related to this key/value
                        docs = self.srvdtb.subjects(RDF['type'], URIRef(KB4IT['Document']))
                        for doc in docs:
                            objects = self.srvdtb.objects(doc, attribute)
                            if Literal(value) in list(objects):
                                title = self.srvdtb.value(doc, KB4IT['hasTitle'])
                                fvalue.write("* <<%s#,%s>>\n" % (os.path.basename(doc)[:-5], unquote(title)))
                        fvalue.write("\n%s\n" % TOP_NAV_BAR)

                fkey.write("\n%s\n" % TOP_NAV_BAR)

        # ~ self.srvbld.create_recents_page()
        self.srvbld.create_index_all()
        self.srvbld.create_index_page()
        self.srvbld.create_all_keys_page()
        self.log.info("4. Document's metadata processed")

    def compile_docs(self):
        """Missing method docstring."""
        # copy online resources to target path
        resources_dir_source = GPATH['ONLINE']
        resources_dir_target = self.target_path + SEP + 'resources'
        self.log.debug("Copying contents from %s to %s", resources_dir_source, resources_dir_target)
        resources_dir_tmp = self.tmpdir + SEP + 'resources'
        shutil.copytree(resources_dir_source, resources_dir_target)
        shutil.copytree(resources_dir_source, resources_dir_tmp)

        adocprops = ''
        for prop in ADOCPROPS:
            if ADOCPROPS[prop] is not None:
                if '%s' in ADOCPROPS[prop]:
                    adocprops += '-a %s=%s \\\n' % (prop, ADOCPROPS[prop] % self.target_path)
                else:
                    adocprops += '-a %s=%s \\\n' % (prop, ADOCPROPS[prop])
            else:
                adocprops += '-a %s \\\n' % prop
        self.log.debug("\tParameters passed to Asciidoc:\n%s", adocprops)

        with Executor(max_workers=MAX_WORKERS) as exe:
            docs = self.srvutl.get_source_docs(self.tmpdir)
            jobs = []
            jobcount = 0
            num = 0
            for doc in docs:
                cmd = "asciidoctor %s -b html5 -D %s %s" % (adocprops, self.tmpdir, doc)
                #~ self.log.debug(cmd)
                job = exe.submit(self.srvutl.exec_cmd, (doc, cmd, num))
                job.add_done_callback(self.srvutl.job_done)
                self.log.debug("Created job #%2d for document: %s", num, doc)
                jobs.append(job)
                num = num + 1

            for job in jobs:
                res = job.result()
                # ~ self.log.info(dir(job))
                # ~ doc, rc, j = res
                jobcount += 1
                if jobcount % MAX_WORKERS == 0:
                    pct = int(jobcount * 100 / len(docs))
                    self.log.info("\tCompiling: %3s%% done", str(pct))
            self.log.info("\tCompiling: 100% done")
            self.log.info("5. Documents compiled successfully.")

    def preprocessing(self, docs):
        """
        Extract metadata from source docs into a dict.

        Create metadata section for each adoc and insert it after the
        EOHMARK.

        In this way, after being compiled into HTML, final adocs are
        browsable throught its metadata.
        """
        TOP_NAV_BAR = self.srvutl.get_template('TPL_TOP_NAV_BAR')
        docs.sort()
        for source in docs:
            docname = os.path.basename(source)
            self.log.debug("\tProcessing source doc (Part I): %s", docname)

            # Create a new node in the graph (a document)
            self.srvdtb.add_document(docname)

            # Get metadata
            docpath = os.path.join(self.source_path, docname)
            props = self.srvutl.get_metadata(docpath)
            for key in props:
                alist = props[key]
                for elem in alist:
                    self.srvdtb.add_document_attribute(quote(docname), quote(key), quote(elem))

        for source in docs:
            try:
                docname = os.path.basename(source)
                self.log.debug("\tProcessing source doc (Part II): %s", docname)
                # Create metadata section
                meta_section = self.srvbld.create_metadata_section(docname)

                # Replace EOHMARK with metadata section
                with open(source) as source_adoc:
                    srcadoc = source_adoc.read()
                    newadoc = srcadoc.replace(EOHMARK, meta_section, 1)
                    newadoc += TOP_NAV_BAR

                    # Write new adoc to temporary dir
                    target = "%s/%s" % (self.tmpdir, docname)
                    with open(target, 'w') as target_adoc:
                        target_adoc.write(newadoc)
            except Exception as error:
                msgerror = "Source file %s: could not be processed: %s" % (docname, error)
                self.log.error("\t%s", msgerror)
                raise

        self.log.info("3. Preprocessed %d docs", len(docs))


    def run(self):
        """Start script execution following this flow.

        1. Delete contents of target directory (if any)
        2. Get source documents
        3. Preprocess documents (get metadata)
        4. Process documents in a temporary dir
        5. Compile documents to html with asciidoc
        6. Copy all documents to target path
        7. Copy source docs to target directory
        """
        self.log.info("KB4IT - Knowledge Base for IT")

        # 1. Delete contents of target directory (if any)
        self.log.info("1. Delete target contents in: %s", self.target_path)
        self.srvutl.delete_target_contents(self.target_path)

        # 2. Get source documents
        self.log.info("2. Get source documents from: %s", self.source_path)
        docs = self.srvutl.get_source_docs(self.source_path)
        self.numdocs = len(docs)

        # 3. Preprocess documents (get metadata)
        self.log.info("3. Pre-processing source documents")
        self.preprocessing(docs)

        # 4. Process documents in a temporary dir
        self.process_docs()

        # 5. Compile documents to html with asciidoc
        dcomps = datetime.datetime.now()
        self.compile_docs()
        dcompe = datetime.datetime.now()
        totaldocs = len(self.srvutl.get_source_docs(self.tmpdir))
        comptime = dcompe - dcomps
        self.log.info("\tCompilation time: %d seconds", comptime.seconds)
        self.log.info("\tNumber of compiled docs: %d", totaldocs)
        try:
            self.log.info("\tCompilation Avg. Speed: %d docs/sec",
                          int((totaldocs/comptime.seconds)))
        except ZeroDivisionError:
            self.log.info("\tCompilation Avg. Speed: %d docs/sec",
                          int((totaldocs/1)))

        # 6. Copy all documents to target path
        self.srvutl.create_target(self.source_path, self.target_path)
        self.log.info("6. Compiled documents copied to target directory")

        # 7. Copy source docs to target directory
        self.srvutl.copy_docs(docs, self.target_path)
        self.log.info("7. Source docs copied to target directory")
        self.log.info("Execution finished")
