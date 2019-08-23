from typing import List, Dict, Union
import enum
import sqlalchemy.orm

from . import iobase
from ..orm import general, cv, organism, pub, sequence


class ChadoClient(iobase.IOClient):

    def query_db(self, name: str) -> sqlalchemy.orm.Query:
        """Queries the db table"""
        return self.session.query(general.Db)\
            .filter(general.Db.name == name)

    def query_dbxref(self, db: str, accession: str) -> sqlalchemy.orm.Query:
        """Queries the dbxref table"""
        return self.session.query(general.DbxRef)\
            .join(general.Db, general.DbxRef.db)\
            .filter(general.Db.name == db)\
            .filter(general.DbxRef.accession == accession)

    def query_cvterm_by_dbxref(self, dbxref_id: int) -> sqlalchemy.orm.Query:
        """Queries the cvterm table, given the dbxref of the required entry"""
        return self.session.query(cv.CvTerm)\
            .filter(cv.CvTerm.dbxref_id == dbxref_id)

    def query_cvterm_by_name_and_namespace(self, name: str, namespace: str) -> sqlalchemy.orm.Query:
        """Queries the cvterm table, given the name and the namespace of the required entry"""
        return self.session.query(cv.CvTerm)\
            .join(cv.Cv, cv.CvTerm.cv)\
            .filter(cv.CvTerm.name == name)\
            .filter(cv.Cv.name == namespace)

    def query_feature_cvterm_properties(self, feature_cvterm_id: int) -> sqlalchemy.orm.Query:
        """Creates a query to select key-value pairs from the 'feature_cvtermprop' table"""
        return self.session.query(cv.CvTerm.name, sequence.FeatureCvTermProp.value)\
            .select_from(sequence.FeatureCvTermProp)\
            .join(cv.CvTerm, sequence.FeatureCvTermProp.type)\
            .filter(sequence.FeatureCvTermProp.feature_cvterm_id == feature_cvterm_id)

    def query_feature_cvterm_pubs(self, feature_cvterm_id: int) -> sqlalchemy.orm.Query:
        """Creates a query to select entries from the 'pub' table associated with a given feature_cvterm"""
        return self.session.query(pub.Pub.uniquename)\
            .select_from(sequence.FeatureCvTerm)\
            .join(pub.Pub, sequence.FeatureCvTerm.pub)\
            .filter(sequence.FeatureCvTerm.feature_cvterm_id == feature_cvterm_id)

    def query_feature_cvterm_secondary_pubs(self, feature_cvterm_id: int) -> sqlalchemy.orm.Query:
        """Creates a query to select entries from the 'pub' table associated with a given feature_cvterm"""
        return self.session.query(pub.Pub.uniquename)\
            .select_from(sequence.FeatureCvTermPub)\
            .join(pub.Pub, sequence.FeatureCvTermPub.pub)\
            .filter(sequence.FeatureCvTermPub.feature_cvterm_id == feature_cvterm_id)

    def query_feature_cvterm_dbxrefs(self, feature_cvterm_id: int) -> sqlalchemy.orm.Query:
        """Creates a query to select dbxrefs associated with a given feature_cvterm"""
        return self.session.query(general.Db.name, general.DbxRef.accession)\
            .select_from(sequence.FeatureCvTermDbxRef)\
            .join(general.DbxRef, sequence.FeatureCvTermDbxRef.dbxref)\
            .join(general.Db, general.DbxRef.db)\
            .filter(sequence.FeatureCvTermDbxRef.feature_cvterm_id == feature_cvterm_id)


class ChadoAccessMode(enum.Enum):
    """Helper class for database connection modes"""
    read = 1
    write = 2


class ChadoObject:
    """Generic class for an object in Chado"""

    def __init__(self, parent):
        """Constructs a generic object that holds Chado data"""
        self._id = int()
        self._client = None
        self._mode = None
        self._parent = parent

    def id(self) -> int:
        """Returns the primary id of a Chado object as given by the database"""
        return self._id

    def set_parent(self, parent) -> None:
        """Sets the parent of a Chado object"""
        self._parent = parent

    def parent(self):
        """Returns the parent of a Chado object"""
        return self._parent

    def client(self) -> Union[None, ChadoClient]:
        """Returns the database connector"""
        if self.parent() is not None and isinstance(self.parent(), ChadoObject):
            return self.parent().client()
        else:
            return self._client

    def connect(self, client: ChadoClient, mode: ChadoAccessMode) -> None:
        """Connects a Chado object to a database"""
        if self.parent() is not None:
            raise iobase.DatabaseError("Error: Establish connection on parent object")
        elif self.is_connected():
            raise iobase.DatabaseError("Connection already exists.")
        else:
            self._client = client
            self._mode = mode

    def disconnect(self) -> None:
        """Disconnects a Chado object from a database"""
        if self.parent() is not None:
            raise iobase.DatabaseError("Error: Close connection on parent object")
        elif not self.is_connected():
            raise iobase.DatabaseError("Connection already closed.")
        else:
            self._client = None
            self._mode = None

    def is_connected(self) -> bool:
        """Checks whether a Chado object is connected to a database"""
        if self.parent() is not None and isinstance(self.parent(), ChadoObject):
            return self.parent().is_connected()
        else:
            return self._client is not None

    def connection_mode(self) -> Union[None, ChadoAccessMode]:
        """Returns the mode in which a Chado object is connected to a database (read/write)"""
        if not self.is_connected():
            return None
        else:
            if self.parent() is not None and isinstance(self.parent(), ChadoObject):
                return self.parent().connection_mode()
            else:
                return self._mode


class DbAuthority(ChadoObject):
    """Class for database authorities in Chado"""

    def __init__(self, parent):
        """Initialises an object for a database authority"""
        super().__init__(parent)

        # Primary attributes
        self._name = str()

    def name(self) -> str:
        """Getter for the name of a database authority"""
        return self._name

    def set_name(self, name: str) -> None:
        """Setter for the name of a database authority"""
        self._name = name

    def load(self) -> bool:
        """Loads a database authority from Chado"""

        # Shortcut if the entry has been loaded previously
        if self.id():
            return True

        # Check if a connection to Chado is established
        if not self.is_connected():
            return False

        # Check if all required attributes are set
        if not self.name():
            return False

        # Check if the entry is available in Chado
        db_entry = self.client().query_db(self.name()).first()
        if not db_entry:
            return False
        else:
            self._id = db_entry.db_id
            return True

    def insert(self) -> bool:
        """Import a database authority into Chado"""

        # Check if the correct connection mode is set
        if not self.connection_mode() == ChadoAccessMode.write:
            return False

        # Check if all required attributes are set
        if not self.name():
            return False

        # Insert/update the entry in Chado
        db_entry = general.Db(name=self.name())
        self._id = self.client()._handle_db(db_entry).db_id
        return True


class DbxRef(ChadoObject):
    """Class for database cross references in Chado"""

    def __init__(self, parent):
        """Initialises an object for a database cross reference"""
        super().__init__(parent)

        # Primary attributes
        self._db = str()
        self._accession = str()
        self._version = str()

    def db(self) -> str:
        """Getter for the db of a database cross reference"""
        return self._db

    def set_db(self, db: str) -> None:
        """Setter for the db of a database cross reference"""
        self._db = db

    def accession(self) -> str:
        """Getter for the accession of a database cross reference"""
        return self._accession

    def set_accession(self, accession: str) -> None:
        """Setter for the accession of a database cross reference"""
        self._accession = accession

    def version(self) -> str:
        """Getter for the version of a database cross reference"""
        return self._version

    def set_version(self, version: str) -> None:
        """Setter for the version of a database cross reference"""
        self._version = version

    def to_string(self) -> Union[None, str]:
        """Prints a database cross reference as string"""
        if not self.db or not self.accession:
            return None
        dbxref = self.db() + ":" + self.accession()
        if self.version():
            dbxref = dbxref + ":" + self.version()
        return dbxref

    def from_string(self, dbxref: str) -> None:
        """Parses a string into a database cross reference"""
        split_string = dbxref.split(":")
        if len(split_string) < 2 or len(split_string) > 3:
            raise AttributeError("dbxref must consist of 2 or 3 elements, separated by semicolon")
        self.set_db(split_string[0])
        self.set_accession(split_string[1])
        if len(split_string) == 3:
            self.set_version(split_string[2])

    def load(self) -> bool:
        """Loads a database cross reference from Chado"""

        # Shortcut if the entry has been loaded previously
        if self.id():
            return True

        # Check if a connection to Chado is established
        if not self.is_connected():
            return False

        # Check if all required attributes are set
        if not self.db() or not self.accession():
            return False

        # Check if the dbxref is available in Chado
        dbxref_entry = self.client().query_dbxref(self.db(), self.accession()).first()  # type: general.DbxRef
        if not dbxref_entry:
            return False
        else:
            self._id = dbxref_entry.dbxref_id
            return True

    def insert(self) -> bool:
        """Imports a database cross reference into Chado"""
        # TODO: handle_* functions should be called insert_* and be public

        # Check if the correct connection mode is set
        if not self.connection_mode() == ChadoAccessMode.write:
            return False

        # Check if all required attributes are set
        if not self.db() or not self.accession():
            return False

        # Insert/update the dependencies in Chado
        db_entry = general.Db(name=self.db())
        db_id = self._client._handle_db(db_entry).db_id

        # Insert/update the entry in Chado
        dbxref_entry = general.DbxRef(db_id=db_id, accession=self.accession(), version=self.version())
        self._id = self._client._handle_dbxref(dbxref_entry).dbxref_id
        return True


class CvTerm(ChadoObject):
    """Class for controlled vocabulary terms in Chado"""

    def __init__(self, parent):
        """Initialises an object for a controlled vocabulary term"""
        super().__init__(parent)

        # Primary attributes
        self.name = str()
        self.is_obsolete = bool()
        self.is_relationship = bool()

        # Secondary attributes
        self._dbxref = DbxRef(self)
        self._vocabulary = str()

        # Helper variables to avoid duplicate loading

    def dbxref(self) -> DbxRef:
        """Getter for the database cross reference of a controlled vocabulary term"""
        return self._dbxref

    def set_dbxref(self, dbxref: DbxRef):
        """Setter for the database cross reference of a controlled vocabulary term"""
        dbxref.set_parent(self)
        self._dbxref = dbxref

    def vocabulary(self) -> str:
        """Getter for the vocabulary of a controlled vocabulary term"""
        return self._vocabulary

    def set_vocabulary(self, vocabulary: str) -> None:
        """Setter for the vocabulary of a controlled vocabulary term"""
        self._vocabulary = vocabulary

    def load(self) -> bool:
        """Loads a controlled vocabulary term from Chado"""

        # Shortcut if the entry has been loaded previously
        if self.id():
            return True

        # Check if a connection to Chado is established
        if not self.is_connected():
            return False

        # Check if the cvterm can be loaded via its dbxref
        if self.dbxref().load():
            cvterm_entry = self.client().query_cvterm_by_dbxref(self.dbxref().id()).first()
            if not cvterm_entry:
                return False
            else:
                self._id = cvterm_entry.cvterm_id
                return True

        # Alternatively, check if the cvterm can be loaded via its name and vocabulary
        elif self.vocabulary() and self.name:
            cvterm_entry = self.client().query_cvterm_by_name_and_namespace(self.name, self.vocabulary())
            if not cvterm_entry:
                return False
            else:
                self._id = cvterm_entry.cvterm_id
                return True
        else:
            return False

    def insert(self) -> bool:
        """Imports a controlled vocabulary term into Chado"""

        # Check if the correct connection mode is set
        if not self.connection_mode() == ChadoAccessMode.write:
            return False

        # Check if all required attributes are set
        if not self.dbxref().load() or not self.vocabulary() or not self.name:
            return False

        # Insert/update the dependencies in Chado
        cv_entry = cv.Cv(name=self.vocabulary())
        cv_id = self.client()._handle_cv(cv_entry)

        # Insert/update the entry in Chado
        cvterm_entry = cv.CvTerm(cv_id=cv_id, dbxref_id=self.dbxref().id(), name=self.name)
        self._id = self.client()._handle_cvterm(cvterm_entry, self.vocabulary()).cvterm_id
        return True


class Publication(ChadoObject):
    """Class for publications in Chado"""

    def __init__(self, parent):
        """Initialises an object for a publication"""
        super().__init__(parent)

        # Primary attributes
        self._systematic_id = str()

    def systematic_id(self) -> str:
        """Getter for the systematic ID of a publication (PMID)"""
        return self._systematic_id

    def set_systematic_id(self, systematic_id: str):
        """Setter for the systematic ID of a publication (PMID)"""
        self._systematic_id = systematic_id


class OntologyTerm(ChadoObject):
    """Class for ontology term associations in Chado"""

    default_evidence_code = "NR"

    def __init__(self, parent):
        """Initialises an object for an ontology term association"""
        super().__init__(parent)

        # Primary attributes
        self._systematic_id = DbxRef(self)
        self._isnot = bool()

        # Secondary attributes
        self._feature = self.parent()
        self._cvterm = CvTerm(self)
        self._date = str()
        self._source = str()
        self._evidence = str()
        self._withfrom = List[DbxRef]
        self._publications = List[Publication]

        # Helper variables to avoid duplicate loading
        self._are_properties_queried = False
        self._is_withfrom_queried = False
        self._are_publications_queried = False

    def systematic_id(self) -> DbxRef:
        """Getter for the systematic ID of an ontology term association, i.e. the actual ontology term"""
        # TODO: there should be a query on dbxref for this
        return self._systematic_id

    def set_systematic_id(self, systematic_id: DbxRef):
        """Setter for the systematic ID of an ontology term association, i.e. the actual ontology term"""
        systematic_id.set_parent(self)
        self._systematic_id = systematic_id
        self._cvterm.set_dbxref(systematic_id)

    def date(self) -> str:
        """Getter for the date of an ontology term association"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_properties_queried:
            self._query_properties(self._client)
        return self._date

    def set_date(self, date: str):
        """Setter for the date of an ontology term association"""
        self._date = date

    def source(self) -> str:
        """Getter for the source of an ontology term association"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_properties_queried:
            self._query_properties(self._client)
        return self._source

    def set_source(self, source: str):
        """Setter for the source of an ontology term association"""
        self._source = source

    def evidence(self) -> str:
        """Getter for the evidence code of an ontology term association"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_properties_queried:
            self._query_properties(self._client)
        return self._evidence

    def set_evidence(self, evidence: str):
        """Setter for the evidence code of an ontology term association"""
        self._evidence = evidence

    def _query_properties(self, client: ChadoClient) -> None:
        """Loads all properties of an ontology term association from Chado"""
        for property_type, property_value in client.query_feature_cvterm_properties(self.id()).all():
            if property_type == "date":
                self.set_date(property_value)
            elif property_type == "evidence":
                self.set_evidence(self._convert_text_to_evidence_code(property_value))
            elif property_type == "assigned_by":
                self.set_source(property_value)
        self._are_properties_queried = True

    def withfrom(self) -> List[DbxRef]:
        """Getter for the additional evidence information of an ontology term association"""
        if self.connection_mode() == ChadoAccessMode.read and not self._is_withfrom_queried:
            self._query_withfrom(self._client)
        return self._withfrom

    def set_withfrom(self, withfrom: List[DbxRef]):
        """Setter for the additional evidence information of an ontology term association"""
        for dbxref in withfrom:
            dbxref.set_parent(self)
            self._withfrom.append(dbxref)

    def _query_withfrom(self, client: ChadoClient) -> None:
        """Loads the additional evidence information of an ontology term association from Chado"""
        for db, accession in client.query_feature_cvterm_dbxrefs(self.id()).all():
            dbxref = DbxRef(self)
            dbxref.set_db(db)
            dbxref.set_accession(accession)
            self._withfrom.append(dbxref)
        self._is_withfrom_queried = True

    def publications(self) -> List[Publication]:
        """Getter for the publications of an ontology term association"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_publications_queried:
            self._query_publications(self._client)
        return self._publications

    def set_publications(self, publications: List[Publication]):
        """Setter for the publications of an ontology term association"""
        for publication in publications:
            publication.set_parent(self)
            self._publications.append(publication)

    def _query_publications(self, client: ChadoClient) -> None:
        """Loads the publications of an ontology term association from Chado"""
        for pmid in client.query_feature_cvterm_pubs(self.id()).all():
            publication = Publication(self)
            publication.set_systematic_id(pmid)
            self._publications.append(publication)
        for pmid in client.query_feature_cvterm_secondary_pubs(self.id()).all():
            publication = Publication(self)
            publication.set_systematic_id(pmid)
            self._publications.append(publication)
        self._are_publications_queried = True

    def _convert_evidence_code_to_text(self, evidence_code: str) -> str:
        """Converts the abbreviation for an evidence code into the spelled-out version, if applicable"""
        if evidence_code in self._evidence_codes_to_text():
            return self._evidence_codes_to_text()[evidence_code]
        return ""

    def _convert_text_to_evidence_code(self, text: str) -> str:
        """Converts a spelled-out evidence code into its abbreviation, if applicable"""
        if text.lower() in self._text_to_evidence_codes():
            return self._text_to_evidence_codes()[text.lower()]
        if text.upper() in self._evidence_codes_to_text():
            return text.upper()
        return ""

    @staticmethod
    def _evidence_codes_to_text() -> Dict[str, str]:
        """Lists the GO evidence codes and their respective abbreviations"""
        return {
            "EXP": "Inferred from Experiment",
            "IDA": "Inferred from Direct Assay",
            "IPI": "Inferred from Physical Interaction",
            "IMP": "Inferred from Mutant Phenotype",
            "IGI": "Inferred from Genetic Interaction",
            "IEP": "Inferred from Expression Pattern",
            "HTP": "Inferred from High Throughput Experiment",
            "HDA": "Inferred from High Throughput Direct Assay",
            "HMP": "Inferred from High Throughput Mutant Phenotype",
            "HGI": "Inferred from High Throughput Genetic Interaction",
            "HEP": "Inferred from High Throughput Expression Pattern",
            "ISS": "Inferred from Sequence or structural Similarity",
            "ISO": "Inferred from Sequence Orthology",
            "ISA": "Inferred from Sequence Alignment",
            "ISM": "Inferred from Sequence Model",
            "IGC": "Inferred from Genomic Context",
            "IBA": "Inferred from Biological aspect of Ancestor",
            "IBD": "Inferred from Biological aspect of Descendant",
            "IKR": "Inferred from Key Residues",
            "IRD": "Inferred from Rapid Divergence",
            "RCA": "Inferred from Reviewed Computational Analysis",
            "TAS": "Traceable Author Statement",
            "NAS": "Non-traceable Author Statement",
            "IC": "Inferred by Curator",
            "ND": "No biological Data available",
            "IEA": "Inferred from Electronic Annotation",
            "NR": "Not recorded"
        }

    def _text_to_evidence_codes(self) -> Dict[str, str]:
        """Lists the GO evidence codes and their respective abbreviations"""
        return {
            text.lower(): evidence_code
            for evidence_code, text
            in self._evidence_codes_to_text().items()
        }

    def insert(self) -> bool:
        """Imports an ontology term association into Chado"""

        # Check if the correct connection mode is set
        if not self.connection_mode() == ChadoAccessMode.write:
            return False

        # Check if all required attributes are set
        if not self._cvterm.load() or not self._feature.id():
            return False

        # Insert/update the entry in Chado
        feature_cvterm_entry = sequence.FeatureCvTerm(feature_id=self._feature.id(), cvterm_id=self._cvterm.id(),
                                                      pub_id=1)
        self._id = self.client().insert_feature_cvterm(feature_cvterm_entry).feature_cvterm_id

        # Insert/update additional evidence information
        for withfrom in self.withfrom():
            withfrom.insert()

        return True





class Feature(ChadoObject):
    """Generic class for any nucleotide/amino acid sequence in Chado"""

    def __init__(self, parent):
        """Initialises an object for a generic nucleotide/amino acid sequence"""
        super().__init__(parent)

        # Primary attributes
        self.systematic_id = str()
        self.name = str()

        # Secondary attributes
        self._sequence = str()
        self._type = str()
        self._organism = str()
        self._dbxrefs = List[DbxRef]
        self._ontology_terms = List[OntologyTerm]

        # Helper variables to avoid duplicate loading
        self._is_type_queried = False
        self._are_dbxrefs_queried = False
        self._are_ontology_terms_queried = False

    def query(self, client: ChadoClient, systematic_id: str, organism_name: str, lazy_loading=True) -> bool:
        """Loads a feature with a given ID from a Chado database"""
        # TODO: Not sure if this function is needed at all
        self.systematic_id = systematic_id
        self._organism = organism_name
        organism_entry = client.query_first(organism.Organism, abbreviation=organism_name)
        if not organism_entry:
            return False
        feature_entry = client.query_first(sequence.Feature, uniquename=systematic_id,
                                           organism_id=organism_entry.organism_id)
        if not feature_entry:
            return False
        self._id = feature_entry.feature_id
        self.name = feature_entry.name
        self._type = client.query_first(cv.CvTerm, cvterm_id=feature_entry.type_id).name
        self._organism = client.query_first(organism.Organism, organism_id=feature_entry.organism_id).abbreviation
        self._sequence = feature_entry.residues

        if lazy_loading:
            # Save database connection details for future use
            self._client = client
        else:
            # Immediately load all additional attributes
            self._query_dbxrefs(self._client)
        return True

    def sequence(self) -> str:
        """Getter for the nucleotide sequence of a feature"""
        return self._sequence

    def set_sequence(self, sequence: str) -> None:
        """Setter for the nucleotide sequence of a feature"""
        self._sequence = sequence

    def type(self) -> str:
        """Getter for the type of a feature"""
        if self.connection_mode() == ChadoAccessMode.read and not self._is_type_queried:
            self._query_type(self._client)
        return self._type

    def set_type(self, feature_type: str):
        """Setter for the type of a feature"""
        self._type = feature_type

    def _query_type(self, client: ChadoClient):
        """Loads the type of a feature from Chado"""
        # TODO: write a proper query_feature_type function
        self._type = client.query_first(cv.CvTerm, cvterm_id=None).name

    def dbxrefs(self) -> List[DbxRef]:
        """Getter for database cross references associated with a feature"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_dbxrefs_queried:
            self._query_dbxrefs(self._client)
        return self._dbxrefs

    def set_dbxrefs(self, dbxrefs: List[DbxRef]) -> None:
        """Setter for database cross references associated with a feature"""
        for dbxref in dbxrefs:
            dbxref.set_parent(self)
            self._dbxrefs.append(dbxref)

    def _query_dbxrefs(self, client: ChadoClient) -> None:
        """Loads all database cross references associated with a feature from Chado"""
        # TODO: primary dbxref (write query_feature_dbxrefs and query_feature_secondary_dbxrefs)
        for db, accession in client.query_feature_dbxrefs(self._id).all():
            dbxref = DbxRef(self)
            dbxref.set_db(db)
            dbxref.set_accession(accession)
            self._dbxrefs.append(dbxref)
        self._are_dbxrefs_queried = True

    def ontology_terms(self) -> List[OntologyTerm]:
        """Getter for ontology terms associated with a feature"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_ontology_terms_queried:
            self._query_ontology_terms(self._client)
        return self._ontology_terms

    def set_ontology_terms(self, ontology_terms: List[OntologyTerm]) -> None:
        """Setter for ontology terms associated with a feature"""
        for ontology_term in ontology_terms:
            ontology_term.set_parent(self)
            self._ontology_terms.append(ontology_term)

    def _query_ontology_terms(self, client: ChadoClient):
        """Loads all ontology terms associated with a feature from Chado"""
        # TODO: query_feature_ontology_terms should take a db authority string as input
        # TODO: query_feature_ontology_terms should return feature_cvterm objects
        for db, accession in client.query_feature_ontology_terms(self._id, None).all():
            dbxref = DbxRef(self)
            dbxref.set_db(db)
            dbxref.set_accession(accession)
            ontology_term = OntologyTerm(self)
            ontology_term.set_systematic_id(dbxref)
            self._ontology_terms.append(ontology_term)
        self._are_ontology_terms_queried = True


class CDS(Feature):
    """Class for a CDS feature in Chado"""
    types = ["CDS"]


class UTR(Feature):
    """Class for a UTR feature in Chado"""
    types = ["three_prime_UTR", "five_prime_UTR"]


class Protein(Feature):
    """Class for a protein/polypeptide feature in Chado"""
    types = ["polypeptide"]


class Transcript(Feature):
    """Class for a transcript feature in Chado"""
    types = ["mrna", "rrna", "trna", "snrna", "ncrna", "scrna", "snorna", "pseudogenic_transcript"]

    def __init__(self, parent):
        """Initialises an object for a transcript feature"""
        super().__init__(parent)

        # Attributes
        self._coding_sequences = List[CDS]
        self._untranslated_regions = List[UTR]
        self._polypeptides = List[Protein]

        # Helper variables to avoid duplicate loading
        self._are_coding_sequences_queried = False
        self._are_untranslated_regions_queried = False
        self._are_polypeptides_queried = False

    def coding_sequences(self) -> List[CDS]:
        """Getter for the coding sequences of a transcript"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_coding_sequences_queried:
            self._query_coding_sequences(self._client)
        return self._coding_sequences

    def set_coding_sequences(self, coding_sequences: List[Protein]) -> None:
        """Setter for the coding sequences of a transcript"""
        for coding_sequence in coding_sequences:
            coding_sequence.set_parent(self)
            self._coding_sequences.append(coding_sequence)

    def _query_coding_sequences(self, client: ChadoClient):
        """Loads all coding sequences of a given transcript from Chado"""
        # TODO: query_child_features should be able to optionally filter by relationship_type and feature_type
        for feature_entry in client.query_child_features(self._id, None).all():         # type: sequence.Feature
            coding_sequence = CDS(self)
            coding_sequence._id = feature_entry.feature_id
            coding_sequence.systematic_id = feature_entry.uniquename
            coding_sequence.name = feature_entry.name
            coding_sequence._sequence = feature_entry.residues
            self._coding_sequences.append(coding_sequence)
        self._are_coding_sequences_queried = True

    def untranslated_regions(self) -> List[UTR]:
        """Getter for the untranslated regions of a transcript"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_untranslated_regions_queried:
            self._query_untranslated_regions(self._client)
        return self._untranslated_regions

    def set_untranslated_regions(self, untranslated_regions: List[Protein]) -> None:
        """Setter for the untranslated regions of a transcript"""
        for untranslated_region in untranslated_regions:
            untranslated_region.set_parent(self)
            self._untranslated_regions.append(untranslated_region)

    def _query_untranslated_regions(self, client: ChadoClient):
        """Loads all untranslated regions of a given transcript from Chado"""
        # TODO: query_child_features should be able to optionally filter by relationship_type and feature_type
        for feature_entry in client.query_child_features(self._id, None).all():         # type: sequence.Feature
            untranslated_region = UTR(self)
            untranslated_region._id = feature_entry.feature_id
            untranslated_region.systematic_id = feature_entry.uniquename
            untranslated_region.name = feature_entry.name
            untranslated_region._sequence = feature_entry.residues
            self._untranslated_regions.append(untranslated_region)
        self._are_untranslated_regions_queried = True

    def polypeptides(self) -> List[Protein]:
        """Getter for the polypeptides of a transcript"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_polypeptides_queried:
            self._query_polypeptides(self._client)
        return self._polypeptides

    def set_polypeptides(self, polypeptides: List[Protein]) -> None:
        """Setter for the polypeptides of a transcript"""
        for polypeptide in polypeptides:
            polypeptide.set_parent(self)
            self._polypeptides.append(polypeptide)

    def _query_polypeptides(self, client: ChadoClient):
        """Loads all polypeptides of a given transcript from Chado"""
        # TODO: query_child_features should be able to optionally filter by relationship_type and feature_type
        for feature_entry in client.query_child_features(self._id, None).all():         # type: sequence.Feature
            polypeptide = Protein(self)
            polypeptide._id = feature_entry.feature_id
            polypeptide.systematic_id = feature_entry.uniquename
            polypeptide.name = feature_entry.name
            polypeptide._sequence = feature_entry.residues
            self._polypeptides.append(polypeptide)
        self._are_polypeptides_queried = True


class Gene(Feature):
    """Class for a gene feature in Chado"""
    types = ["gene", "pseudogene"]

    def __init__(self, parent):
        """Initialises an object for a transcript feature"""
        super().__init__(parent)

        # Attributes
        self._transcripts = List[Transcript]

        # Helper variables to avoid duplicate loading
        self._are_transcripts_queried = False

    def transcripts(self) -> List[Transcript]:
        """Getter for the transcripts of a gene"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_transcripts_queried:
            self._query_transcripts(self._client)
        return self._transcripts

    def set_transcripts(self, transcripts: List[Transcript]) -> None:
        """Setter for the transcripts of a gene"""
        for transcript in transcripts:
            transcript.set_parent(self)
            self._transcripts.append(transcript)

    def _query_transcripts(self, client: ChadoClient):
        """Loads all transcripts of a given gene from Chado"""
        # TODO: query_child_features should be able to optionally filter by relationship_type and feature_type
        for feature_entry in client.query_child_features(self._id, None).all():         # type: sequence.Feature
            transcript = Transcript(self)
            transcript._id = feature_entry.feature_id
            transcript.systematic_id = feature_entry.uniquename
            transcript.name = feature_entry.name
            transcript._sequence = feature_entry.residues
            self._transcripts.append(transcript)
        self._are_transcripts_queried = True

    def polypeptides(self) -> List[Protein]:
        """Getter for the proteins coded by a gene (shortcut)"""
        all_polypeptides = []
        for transcript in self.transcripts():
            all_polypeptides.extend(transcript.polypeptides())
        return all_polypeptides


class Chromosome(Feature):
    """Class for a chromosome/contig feature in Chado"""
    types = ["chromosome", "contig", "supercontig"]

    def __init__(self, parent):
        """Initialises an object for a chromosome feature"""
        super().__init__(parent)

        # Attributes
        self._genes = List[Gene]

        # Helper variables to avoid duplicate loading
        self._are_genes_queried = False

    def genes(self) -> List[Gene]:
        """Getter for the genes located on a chromosome"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_genes_queried:
            self._query_genes(self._client)
        return self._genes

    def set_genes(self, genes: List[Gene]) -> None:
        """Setter for the genes located on a chromosome"""
        for gene in genes:
            gene.set_parent(self)
            self._genes.append(gene)

    def _query_genes(self, client: ChadoClient):
        """Loads all genes located on a given chromosome from Chado"""
        # TODO: query_features_by_srcfeature should be able to optionally filter by feature_type
        for feature_entry in client.query_features_by_srcfeature(self._id).all():       # type: sequence.Feature
            gene = Gene(self)
            gene._id = feature_entry.feature_id
            gene.systematic_id = feature_entry.uniquename
            gene.name = feature_entry.name
            gene._sequence = feature_entry.residues
            self._genes.append(gene)
        self._are_genes_queried = True


class Organism(ChadoObject):
    """Class for an organism in Chado"""

    def __init__(self):
        """Initialises an object for an organism"""
        super().__init__(None)

        # Primary attributes
        self.abbreviation = str()
        self.genus = str()
        self.species = str()
        self.strain = str()

        # Secondary attributes
        self._genome_version = str()
        self._taxon_id = str()
        self._wikidata_id = str()
        self._chromosomes = List[Chromosome]

        # Helper variables to avoid duplicate loading
        self._are_properties_queried = False
        self._are_dbxrefs_queried = False
        self._are_chromosomes_queried = False

    def load(self) -> bool:
        """Loads an organism from Chado"""
        # TODO: _load_organism should be public
        if self.connection_mode() == ChadoAccessMode.read:
            try:
                organism_entry = self._client._load_organism(self.abbreviation)        # type: organism.Organism
                self._id = organism_entry.organism_id
                self.abbreviation = organism_entry.abbreviation
                self.genus = organism_entry.genus
                self.species = organism_entry.species
                self.strain = organism_entry.infraspecific_name
                return True
            except iobase.DatabaseError:
                return False

    def genome_version(self) -> str:
        """Getter for the version of a genome assembly"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_properties_queried:
            self._query_properties(self._client)
        return self._genome_version

    def set_genome_version(self, version: str):
        """Setter for the version of a genome assembly"""
        self._genome_version = version

    def taxon_id(self) -> str:
        """Getter for the taxon ID of a genome assembly"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_properties_queried:
            self._query_properties(self._client)
        return self._taxon_id

    def set_taxon_id(self, taxon_id: str):
        """Setter for the taxon ID of a genome assembly"""
        self._taxon_id = taxon_id

    def _query_properties(self, client: ChadoClient) -> None:
        """Loads all properties of an organism from Chado"""
        # TODO: query_organism_properties still needs writing
        for property_type, property_value in client.query_organism_properties(self._id).all():
            if property_type == "taxonId":
                self.set_taxon_id(property_value)
            elif property_type == "version":
                self.set_genome_version(property_value)
        self._are_properties_queried = True

    def wikidata_id(self) -> str:
        """Getter for the Wikidata ID of an organism"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_dbxrefs_queried:
            self._query_dbxrefs(self._client)
        return self._wikidata_id

    def set_wikidata_id(self, wikidata_id: str):
        """Setter for the Wikidata ID of an organism"""
        self._wikidata_id = wikidata_id

    def _query_dbxrefs(self, client: ChadoClient) -> None:
        """Loads all dbxrefs of an organism from Chado"""
        # TODO: query_organism_dbxrefs still needs writing
        for db, accession in client.query_organism_dbxrefs(self._id).all():
            if db == "Wikidata":
                self.set_wikidata_id(accession)
        self._are_dbxrefs_queried = True

    def chromosomes(self):
        """Getter for the chromosomes of an organism"""
        if self.connection_mode() == ChadoAccessMode.read and not self._are_chromosomes_queried:
            self._query_chromosomes(self._client)
        return self._chromosomes

    def set_chromosomes(self, chromosomes: List[Chromosome]) -> None:
        """Setter for the chromosomes of an organism"""
        for chromosome in chromosomes:
            chromosome.set_parent(self)
            self._chromosomes.append(chromosome)

    def _query_chromosomes(self, client: ChadoClient):
        """Loads all genes located on a given chromosome from Chado"""
        # TODO: query_features_by_property_type should take a property type as string
        for feature_entry in client.query_features_by_property_type(self._id, None).all():  # type: sequence.Feature
            chromosome = Chromosome(self)
            chromosome._id = feature_entry.feature_id
            chromosome.systematic_id = feature_entry.uniquename
            chromosome.name = feature_entry.name
            chromosome._sequence = feature_entry.residues
            self._chromosomes.append(chromosome)
        self._are_chromosomes_queried = True


def convert_organism_object(chado_object: organism.Organism, natural_object: Organism):
    """Helper function to convert objects describing organisms from different classes into each other"""
    natural_object.abbreviation = chado_object.abbreviation
    natural_object.genus = chado_object.genus
    natural_object.species = chado_object.species
    natural_object.strain = chado_object.infraspecific_name
