#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Builder service.

# File: srv_builder.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: Create KB4IT pages
"""

import os
import datetime as dt
from datetime import datetime
from urllib.parse import quote, unquote
from rdflib import URIRef
from rdflib import Literal
from kb4it.core.mod_srv import Service
from kb4it.services.srv_rdfdb import RDF, KB4IT

class Builder(Service):
    """Missing class docstring (missing-docstring)."""

    tmpdir = None

    def initialize(self):
        """Missing method docstring."""
        self.get_services()
        self.tmpdir = self.srvapp.get_temp_dir()

    def get_services(self):
        """Missing method docstring."""
        self.srvdtb = self.get_service('DB')
        self.srvutl = self.get_service('Utils')
        self.srvapp = self.get_service('App')

    def create_tagcloud_from_key(self, key):
        """Missing method docstring."""
        dkeyurl = {}
        docs = list(self.srvdtb.subjects(RDF['type'], URIRef(KB4IT['Document'])))
        for doc in docs:
            predicate = KB4IT['has%s' % key]
            tags = self.srvdtb.objects(doc, predicate)
            url = os.path.basename(doc)[:-5]
            for tag in tags:
                try:
                    urllist = dkeyurl[tag]
                    surllist = set(urllist)
                    surllist.add(url)
                    dkeyurl[tag] = list(surllist)
                except KeyError:
                    surllist = set()
                    surllist.add(url)
                    dkeyurl[tag] = list(surllist)


        max_frequency = self.srvutl.set_max_frequency(dkeyurl)
        lwords = []

        for word in dkeyurl:
            if len(word) > 0:
                lwords.append(word)

        if len(lwords) > 0:
            lwords.sort()

            html = "<div class=\"tagcloud\">"
            for word in lwords:
                frequency = len(dkeyurl[word])
                size = self.srvutl.get_font_size(frequency, max_frequency)
                url = "%s_%s.html" % (key, quote(word))
                chunk = "<div class=\"tagcloud-word\"><a \
style=\"text-decoration: none;\" href=\"%s\"> \
<span style=\"font-size:%dpt;\">%s</span></a></div>" % (url, size, unquote(word))
                html += chunk
            html += "</div>"
        else:
            html = ''

        return html

    def create_index_all(self):
        """Missing method docstring."""
        docname = "%s/all.adoc" % (self.tmpdir)
        TPL_METAKEY = self.srvutl.get_template('TPL_METAKEY')
        TOP_NAV_BAR = self.srvutl.get_template('TPL_TOP_NAV_BAR')
        with open(docname, 'w') as fall:
            fall.write(TPL_METAKEY % "All documents")
            doclist = []
            docs = self.srvdtb.subjects(RDF['type'], URIRef(KB4IT['Document']))
            for doc in docs:
                doclist.append(doc)
            doclist.sort()
            for doc in doclist:
                title = self.srvdtb.value(doc, KB4IT['hasTitle'])
                fall.write(". <<%s#,%s>>\n" % (os.path.basename(doc)[:-5], unquote(title)))
            fall.write("\n%s\n" % TOP_NAV_BAR)

    def create_index_page(self):
        """Missing method docstring."""
        TPL_INDEX = self.srvutl.get_template('TPL_INDEX')
        TOP_NAV_BAR = self.srvutl.get_template('TPL_TOP_NAV_BAR')
        total = 0
        cats = self.srvdtb.objects(None, KB4IT['hasCategory'])
        cols = '^,'*len(cats)
        tblcats = """[options="header", width="100%%", cols="%s"]\n""" % cols[:-1]
        tblcats += """[.pure-table pure-table-bordered]\n"""
        tblcats += "|===\n"
        for cat in cats:
            tblcats += "|%s\n" % cat
        for cat in cats:
            tblcats += "|<<Category_%s.adoc#,%d>>\n" % (
                cat, len(self.srvdtb.subjects(KB4IT['hasCategory'], quote(cat))))
        tblcats += "|===\n"
        tblareas = self.create_tagcloud_from_key('Scope')
        tagcloud = self.create_tagcloud_from_key('Tag')
        tblkeys = """[options="header", width="100%", cols="80%,>"]\n"""
        tblkeys += "|===\n"
        tblkeys += "|Key\n"
        tblkeys += "|Docs\n"
        for attribute in self.srvdtb.get_attributes():
            key = attribute[attribute.rfind('/')+4:]
            values = self.srvdtb.objects(None, attribute)
            tblkeys += "|<<%s#,%s>>\n" % (key, quote(key))
            tblkeys += "|<<%s.adoc#,%d>>\n\n" % (key, len(values))
            total += len(values)
        tblkeys += "|==="
        numdocs = self.srvapp.get_numdocs()
        with open('%s/index.adoc' % self.tmpdir, 'w') as findex:
            content = TPL_INDEX % (numdocs, tblcats, tblareas, tagcloud, tblkeys)
            findex.write(content)
            findex.write(TOP_NAV_BAR)

    def create_all_keys_page(self):
        """Missing method docstring."""
        TPL_KEYS = self.srvutl.get_template('TPL_KEYS')
        TOP_NAV_BAR = self.srvutl.get_template('TPL_TOP_NAV_BAR')
        with open('%s/keys.adoc' % self.tmpdir, 'w') as fkeys:
            fkeys.write(TPL_KEYS)
            all_keys = self.srvdtb.get_attributes()
            for swkey in all_keys:
                key = swkey[swkey.rfind('/')+4:]
                cloud = self.create_tagcloud_from_key(key)
                if len(cloud) > 0:
                    fkeys.write("\n\n== %s\n\n" % key)
                    fkeys.write("\n++++\n%s\n++++\n" % cloud)
            fkeys.write("\n%s\n" % TOP_NAV_BAR)

    def create_recents_page(self):
        """Create recents page.

        In order this page makes sense, this script should be
        executed periodically from crontab.
        """
        TOP_NAV_BAR = self.srvutl.get_template('TPL_TOP_NAV_BAR')
        docname = "%s/%s" % (self.tmpdir, 'recents.adoc')
        with open(docname, 'w') as frec:
            relset = set()
            today = datetime.now()
            lastweek = today - dt.timedelta(weeks=1)
            lastmonth = today - dt.timedelta(days=31)
            strtoday = "%d-%02d-%02d" % (today.year, today.month, today.day)

            # TODAY
            docs = self.srvdtb.subjects(RDF['type'], URIRef(KB4IT['Document']))
            for doc in docs:
                revdate = self.srvdtb.value(doc, KB4IT['hasRevdate'])
                if revdate == Literal(strtoday):
                    relset.add(doc)

            page = '= Last documents added\n\n'
            page += '== Today (%d)\n\n' % len(relset)
            page += """[options="header", width="100%", cols="60%,20%,20%"]\n"""
            page += "|===\n"
            page += "|Document |Category | Status\n"

            for doc in relset:
                title = self.srvdtb.value(doc, KB4IT['hasTitle'])
                category = self.srvdtb.value(doc, KB4IT['hasCategory'])
                status = self.srvdtb.value(doc, KB4IT['hasStatus'])
                page += "|<<%s#,%s>>\n" % (doc, quote(title))
                page += "|<<Category_%s.adoc#,%s>>\n" % (category, quote(category))
                page += "|<<Status_%s.adoc#,%s>>\n" % (status, status)

            page += "|==="

            # WEEK
            for doc in docs:
                revdate = datetime.strptime(self.srvdtb.value(doc, KB4IT['hasRevdate']), "%Y-%m-%d")
                if revdate <= today and revdate >= lastweek:
                    relset.add(doc)

            page += '\n\n== This week (%d)\n\n' %  len(relset)
            page += """[options="header", width="100%", cols="60%,20%,20%"]\n"""
            page += "|===\n"
            page += "|Document |Category | Status\n"
            for doc in relset:
                title = self.srvdtb.value(doc, KB4IT['hasTitle'])
                category = self.srvdtb.value(doc, KB4IT['hasCategory'])
                status = self.srvdtb.value(doc, KB4IT['hasStatus'])
                page += "|<<%s#,%s>>\n" % (doc, quote(title))
                page += "|<<%s#,%s>>\n" % (doc, quote(category))
                page += "|<<%s#,%s>>\n" % (doc, quote(status))
            page += "|==="

            # MONTH
            for doc in docs:
                revdate = datetime.strptime(self.srvdtb.value(doc, KB4IT['hasRevdate']), "%Y-%m-%d")
                if revdate <= today and revdate >= lastmonth:
                    relset.add(doc)

            page += '\n\n== This month (%d)\n\n' % len(relset)
            page += """[options="header", width="100%", cols="60%,20%,20%"]\n"""
            page += "|===\n"
            page += "|Document |Category | Status\n"
            for doc in relset:
                title = self.srvdtb.value(doc, KB4IT['hasTitle'])
                category = self.srvdtb.value(doc, KB4IT['hasCategory'])
                status = self.srvdtb.value(doc, KB4IT['hasStatus'])
                page += "|<<%s#,%s>>\n" % (doc, quote(title))
                page += "|<<%s#,%s>>\n" % (doc, quote(category))
                page += "|<<%s#,%s>>\n" % (doc, quote(status))
            page += "|===\n\n"

            page += TOP_NAV_BAR
            frec.write(page)

    def create_key_page(self, key, values):
        """Missing method docstring."""
        html = self.srvutl.get_template('TPL_KEY_PAGE')
        tagcloud = self.create_tagcloud_from_key(key)
        alist = ''
        for value in values:
            alist += "* <<%s_%s.adoc#,%s>>\n" % (key, value, unquote(value))

        return html % (tagcloud, alist)

    def create_metadata_section(self, doc):
        """Return a html block for displaying key and custom attributes."""
        try:
            html = self.srvutl.get_template('TPL_METADATA_SECTION_HEADER')
            author = self.srvdtb.get_html_values_from_attribute(doc, KB4IT['hasAuthor'])
            revdate = self.srvdtb.get_html_values_from_attribute(doc, KB4IT['hasRevdate'])
            revnumber = self.srvdtb.get_html_values_from_attribute(doc, KB4IT['hasRevnumber'])
            category = self.srvdtb.get_html_values_from_attribute(doc, KB4IT['hasCategory'])
            scope = self.srvdtb.get_html_values_from_attribute(doc, KB4IT['hasScope'])
            status = self.srvdtb.get_html_values_from_attribute(doc, KB4IT['hasStatus'])
            dept = self.srvdtb.get_html_values_from_attribute(doc, KB4IT['hasDepartment'])
            team = self.srvdtb.get_html_values_from_attribute(doc, KB4IT['hasTeam'])
            tags = self.srvdtb.get_html_values_from_attribute(doc, KB4IT['hasTag'])
            METADATA_SECTION_BODY = self.srvutl.get_template('TPL_METADATA_SECTION_BODY')
            # ~ tc_author = self.create_tagcloud_from_key('Author')
            # ~ tc_revdate = self.create_tagcloud_from_key('Revdate')
            # ~ tc_revision = self.create_tagcloud_from_key('Revnumber')
            # ~ tc_category = self.create_tagcloud_from_key('Category')
            # ~ tc_scope = self.create_tagcloud_from_key('Scope')
            # ~ tc_status = self.create_tagcloud_from_key('Status')
            # ~ tc_department = self.create_tagcloud_from_key('Department')
            # ~ tc_team = self.create_tagcloud_from_key('Team')
            # ~ tc_tag = self.create_tagcloud_from_key('Tag')
            html += METADATA_SECTION_BODY % (author, revdate, revnumber, \
                                            category, scope, status, \
                                            dept, team, tags)

            custom_keys = self.srvdtb.get_custom_keys(doc)
            custom_props = ''
            for key in custom_keys:
                values = self.srvdtb.get_html_values_from_attribute(doc, key)
                if len(values) > 0:
                    swkey = key[key.rfind('/')+4:]
                    row = """<tr><td class="mdkey"><a href=\"%s.html">\
%s</a></td><td class="mdval" colspan="3">%s</td></tr>\n""" % (swkey, swkey, values)
                    custom_props += row

            if len(custom_props) > 0:
                html += "[TIP]\n"
                html += "====\n\n"
                html += "++++\n"
                html += """<table class="metadata">\n"""
                html += custom_props
                html += "</table>\n"
                html += "++++\n\n"
                html += "====\n"

            METADATA_SECTION_FOOTER = self.srvutl.get_template('TPL_METADATA_SECTION_FOOTER')
            html += METADATA_SECTION_FOOTER % doc
        except Exception as error:
            msgerror = "%s -> %s" % (doc, error)
            self.log.error("\t%s", msgerror)
            html = ''
            raise
            # ~ self.log.error(tb.format_exc())

        return html
