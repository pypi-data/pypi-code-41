from typing import List, Set, Dict, Union
from Bio.UniProt import GOA
from .experiment import Feature, DbxRef, DbAuthority, CvTerm, Chromosome, Gene, Organism, Transcript
from . import iobase
from .. import utils


class GafImporter:
    """Class to import GAF files into Chado"""

    def __init__(self, uri: str, verbose=False, test_environment=False):
        """Constructor"""

        # Connect to database
        if test_environment:
            self.client = utils.EmptyObject()
        else:
            self.client = iobase.ChadoClient(uri, verbose)

    def load(self, filename: str, organism_name: str, annotation_level: str):
        """Import data from a GAF file into a Chado database"""

        # Loop over all records in the GAF file
        with open(filename) as f:
            for gaf_record in GOA.gafiterator(f):

                # Import this record into the database
                self._load_gaf_record(gaf_record, default_organism, annotation_level, features_with_product)

