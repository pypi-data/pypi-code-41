#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RDF Graph In Memory database module.

# Author: Tomás Vírseda <tomasvirseda@gmail.com>
# License: GPLv3
# Description: module to allow kb4it create a RDF graph
"""

from urllib.parse import quote, unquote
from rdflib import URIRef
from rdflib import Literal
from rdflib.namespace import Namespace, NamespaceManager
from rdflib import RDF
from rdflib import ConjunctiveGraph
from kb4it.core.mod_env import SEP
from kb4it.core.mod_srv import Service

# Semantic Web Ontologies: W3C and KB4IT
RDF = Namespace(RDF)
KB4IT = Namespace(u"https://t00mlabs.net/ontologies/kb4it/")

NSBINDINGS = {
    u"rdf"   : RDF,
    u"kb4it" : KB4IT
}

EOHMARK = """// END-OF-HEADER. DO NOT MODIFY OR DELETE THIS LINE"""


class KB4ITGraph(Service):
    """RDF graph database class."""

    params = None
    path = None
    graph = None
    source_path = None

    def initialize(self, path=None):
        """Initialize database module."""
        self.get_services()
        if path is not None:
            # Create persistent Graph in disk
            self.path = path
            self.graph = ConjunctiveGraph('Sleepycat', URIRef("kb4it://"))
            graph_path = path + SEP + 'kb4it.graph'
            self.graph.store.open(graph_path)
        else:
            # Create Graph in Memory
            self.graph = ConjunctiveGraph('IOMemory')

        # Assign namespaces to the Namespace Manager of this graph
        namespace_manager = NamespaceManager(ConjunctiveGraph())
        for nsp in NSBINDINGS:
            namespace_manager.bind(nsp, NSBINDINGS[nsp])
        self.graph.namespace_manager = namespace_manager

        self.params = self.app.get_params()
        self.source_path = self.params.SOURCE_PATH

    def get_services(self):
        """Missing docstring."""
        self.srvutl = self.get_service('Utils')

    def get_graph(self):
        """Missing docstring."""
        return self.graph

    def subjects(self, prd, obj):
        """Return a list of sorted and uniques subjects."""
        return self.srvutl.uniq_sort(self.graph.subjects(prd, obj))

    def predicates(self, sbj=None, obj=None):
        """Return a list of sorted and uniques predicates."""
        return self.srvutl.uniq_sort(self.graph.predicates(sbj, obj))

    def objects(self, subject, predicate):
        """Return a list of sorted and uniques objects."""
        return self.srvutl.uniq_sort(self.graph.objects(subject, predicate))

    def value(self, sbj=None, prd=None, obj=None, default=None):
        """Return a value given the subject and the predicate."""
        return self.graph.value(sbj, prd, obj, default, True)

    def add_document(self, doc):
        """Add a new document to the graph."""
        sbj = URIRef(doc)
        prd = RDF['type']
        obj = URIRef(KB4IT['Document'])
        self.graph.add([sbj, prd, obj])

    def add_document_attribute(self, doc, attribute, value):
        """Add a new attribute to a document."""
        prd = 'has%s' % attribute
        prd = KB4IT[prd]
        sbj = URIRef(doc)
        obj = Literal(value)
        self.graph.add([sbj, prd, obj])

    def get_attributes(self):
        """Get all predicates except RFD.type and title."""
        blacklist = set()
        blacklist.add(RDF['type'])
        blacklist.add(KB4IT['hasTitle'])
        alist = list(self.predicates(None, None))
        aset = set(alist) - blacklist
        alist = list(aset)
        alist.sort()
        return alist

    def get_html_values_from_attribute(self, doc, predicate):
        """Return the html link for a value."""
        html = ''

        try:
            values = self.objects(URIRef(doc), predicate)
            for value in values:
                if len(value) > 0:
                    key = predicate[predicate.rfind('/')+4:]
                    html += "<a class=\"metadata\" href=\"%s_%s.html\">\
%s</a> " % (key, quote(value), unquote(value))
                else:
                    html = ''
        except Exception as error:
            self.log.error(error)
            raise
            # ~ self.log.error(tb.format_exc())

        return html

    def get_custom_keys(self, doc):
        """Missing docstring."""
        header_keys = [RDF['type'], KB4IT['hasCategory'],
                       KB4IT['hasScope'], KB4IT['hasStatus'],
                       KB4IT['hasDepartment'], KB4IT['hasTeam'],
                       KB4IT['hasTag'], KB4IT['hasAuthor'],
                       KB4IT['hasRevdate'],
                       KB4IT['hasRevnumber'], KB4IT['hasTitle']]
        custom_keys = []
        keys = self.get_keys(sbj=URIRef(doc))
        for key in keys:
            if key not in header_keys:
                custom_keys.append(key)
        custom_keys.sort()

        return custom_keys

    def get_keys(self, sbj=None, obj=None):
        """Missing docstring."""
        return self.predicates(sbj, obj)

    def serialize(self):
        """Serialize graph to pretty xml format."""
        return self.graph.serialize(format='pretty-xml')

    def close(self):
        """Close the graph if it is persistent."""
        self.graph.store.close()
