from nifconverter.uri_converter import URIConverter
from nifconverter.dbpedia_sparql import FromDBpediaSparqlConverter
from nifconverter.dbpedia_sparql import ToDBpediaSparqlConverter
from nifconverter.dbpedia_samething import SameThingConverter

class AutoConverter(URIConverter):
    """
    Meta-converter which selects the best converter given the
    desired source and target prefixes.
    """


