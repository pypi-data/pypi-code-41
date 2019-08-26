# -*- coding: utf-8 -*-

from rdflib import Namespace, Graph
import os
import pathlib

from orbis_eval import app
from orbis_plugin_aggregation_dbpedia_entity_types import Main as dbpedia_entity_types


class Convert(object):
    """docstring for Convert"""

    def __init__(self):
        super(Convert, self).__init__()
        self.nif_namespace = Namespace("http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#")
        self.itsrdf_namespace = Namespace("http://www.w3.org/2005/11/its/rdf#")

    def convert(self, download_destination, corpus_dir, download_name):
        g = Graph()
        g.parse(download_destination, format="turtle")
        self.extract_files_from_nif_corpus(g, os.path.join(corpus_dir, "corpus"))
        self.extract_entities_from_nif_corpus(g, os.path.join(corpus_dir, "gold"), f"{download_name}.gs")

    def extract_files_from_nif_corpus(self, g, folder):
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

        for subject, predicate, object_ in g.triples((None, self.nif_namespace.isString, None)):
            document_number = (subject.split("/")[-1]).split("#")[0]
            filename = os.path.join(folder, document_number + ".txt")

            if not os.path.exists(filename):
                with open(filename, "w", encoding="utf-8") as open_file:
                    open_file.write(object_)

    def extract_entities_from_nif_corpus(self, g, folder, file_name):
        pathlib.Path(folder).mkdir(parents=True, exist_ok=True)

        with open(os.path.join(folder, file_name), "w") as open_file:
            lines = set()

            for subject, predicate, object_ in g.triples((None, self.nif_namespace.anchorOf, None)):

                """
                print("\n", 42 * "", "\n")
                print(f"subject: {subject}")
                print(f"predicate: {predicate}")
                print(f"object: {object_}")
                print(f"\n")
                # """

                subject_id = subject.split("/")[-1]
                document_number, postition = subject_id.split("#")
                start, end = postition.split("=")[-1].split(",")
                surfaceForm = object_
                subject_2 = subject

                for subject_2, predicate_2, object_2 in g.triples((subject, self.itsrdf_namespace.taIdentRef, None)):
                    type_ = dbpedia_entity_types.get_dbpedia_type(object_2)

                    """
                    print(f"\n")
                    print(f"subject_2: {subject_2}")
                    print(f"predicate_2: {predicate_2}")
                    print(f"object_3: {object_2}")
                    print(f"\n")
                    # """

                    line = "\t".join([document_number, start, end, object_2.strip(), "1", type_, surfaceForm])
                    # open_file.write(line + "\n")
                    lines.add(line)

                for subject_2, predicate_2, object_2 in g.triples((subject, self.itsrdf_namespace.taClassRef, None)):

                    """
                    print(f"\n")
                    print(f"subject_2: {subject_2}")
                    print(f"predicate_2: {predicate_2}")
                    print(f"object_22: {object_2}")
                    print(f"\n")
                    # """

                    for subject_3, predicate_3, object_3 in g.triples((subject_2, self.nif_namespace.taMsClassRef, None)):

                        types = ['http://dbpedia.org/ontology/Person', 'http://xmlns.com/foaf/0.1/Person', 'http://dbpedia.org/ontology/Organisation', 'http://dbpedia.org/class/yago/Organization108008335', 'http://dbpedia.org/ontology/PopulatedPlace', 'http://dbpedia.org/ontology/Place', 'http://dbpedia.org/ontology/TelevisionShow', 'http://dbpedia.org/ontology/Work', 'http://dbpedia.org/ontology/Work', 'http://www.w3.org/2002/07/owl#Thing']
                        if object_2.strip() in types:
                            type_ = self.define_type(object_2)

                            """
                            print(f"\n")
                            print(f"subject_3: {subject_3}")
                            print(f"predicate_3: {predicate_3}")
                            print(f"object_3: {object_3}")
                            print(f"\n")
                            # """

                            """
                            line = self.write_entity_to_file(
                                open_file,
                                document_number,
                                start,
                                end,
                                subject_3,
                                type_,
                                surfaceForm
                            )
                            print(line)
                            """
                            line = "\t".join([document_number, start, end, object_3.strip(), "1", type_, surfaceForm])
                            # open_file.write(line + "\n")
                            lines.add(line)
            for line in lines:
                open_file.write(line + "\n")

    def write_entity_to_file(self, open_file, document_number, start, end, object_2, type_, surfaceForm, separator="\t"):
        line = "\t".join([document_number, start, end, object_2.strip(), "1", type_, surfaceForm])
        open_file.write(line + "\n")
        return line

    def define_type(self, object_):

        types = {
            'http://dbpedia.org/ontology/Person': 'Person',
            'http://xmlns.com/foaf/0.1/Person': 'Person',
            'http://dbpedia.org/ontology/Organisation': 'Organization',
            'http://dbpedia.org/class/yago/Organization108008335': 'Organization',
            'http://dbpedia.org/ontology/PopulatedPlace': 'Location',
            'http://dbpedia.org/ontology/Place': 'Location',
            'http://dbpedia.org/ontology/TelevisionShow': 'TV',
            'http://dbpedia.org/ontology/Work': 'TV',
            'http://dbpedia.org/ontology/Work': 'Work',
        }

        return types.get(object_.strip(), 'http://www.w3.org/2002/07/owl#Thing')
