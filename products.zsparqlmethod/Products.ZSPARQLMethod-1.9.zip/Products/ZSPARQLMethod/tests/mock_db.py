from os import path
from Products.ZSPARQLMethod.Method import sparql

GET_LANGS = """\
SELECT ?lang_url WHERE {
  ?lang_url a <http://rdfdata.eionet.europa.eu/eea/ontology/Language> .
}
"""

GET_LANG_NAMES = """\
PREFIX eea_ontology: <http://rdfdata.eionet.europa.eu/eea/ontology/>
SELECT * WHERE {
  ?lang_url a eea_ontology:Language .
  ?lang_url eea_ontology:name ?name .
  FILTER (lang(?name) = "en") .
}
"""

GET_LANG_BY_NAME = """\
PREFIX eea_ontology: <http://rdfdata.eionet.europa.eu/eea/ontology/>
PREFIX rdf_schema: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?lang_url WHERE {
  ?lang_url a eea_ontology:Language .
  ?lang_url rdf_schema:label ?lang_label .
FILTER (?lang_label = ${lang_name})
}
"""

GET_LANG_BY_NAME_DA = GET_LANG_BY_NAME.replace('${lang_name}', '"Danish"')

def pack(q):
    return q.replace("\n", " ").encode('utf-8')

def read_response_xml(name):
    xml_path = path.join(path.dirname(__file__), 'sparql-%s.xml' % name)
    f = open(xml_path, 'rb')
    data = f.read()
    f.close()
    return data

QUERIES = {
        pack(GET_LANGS): read_response_xml('get_languages'),
        pack(GET_LANG_NAMES): read_response_xml('get_lang_names'),
        pack(GET_LANG_BY_NAME_DA): read_response_xml('get_lang_by_name-da'),
    }

class MockResponse(object):
    def getcode(self):
        return 200


class MockQuery(sparql._Query):
    def _get_response(self, opener, request, buf, timeout):
        self.querystring = request.get_data()
        return MockResponse()

    def _read_response(self, response, buf, timeout):
        try:
            from urlparse import parse_qs
        except ImportError:
            from cgi import parse_qs
        query = parse_qs(self.querystring).get('query', [''])[0]
        buf.write(QUERIES[pack(query)])

class MockSparql(object):
    def start(self):
        self.old_Query = sparql._Query
        sparql._Query = MockQuery

    def stop(self):
        sparql._Query = self.old_Query
