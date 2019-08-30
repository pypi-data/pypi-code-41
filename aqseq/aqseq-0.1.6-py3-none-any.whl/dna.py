from benchlingapi.exceptions import InvalidRegistryId
import jdna
from pydent.utils import make_async
from aqseq.exceptions import AqSeqException
import pydent
from aqseq.logger import logger


class AquariumDNA(object):
    class DEFAULTS:
        MIN_ASSEMBLY_BASES = 12
        MAX_ASSEMBLY_BASES = 200
        LINEAR_ASSEMBLY_KEY = "Fragment Mix Array"
        CYCLIC_ASSEMBLY_KEY = None
        FORWARD_PRIMER_KEY = "Forward Primer"
        REVERSE_PRIMER_KEY = "Reverse Primer"
        TEMPLATE_KEY = "Template"
        PRIMER_SEQUENCE_KEYS = ["Overhang Sequence", "Anneal Sequence"]

    ########################################
    # Initializers
    ########################################

    def __init__(self, aquarium_sample, connector, interactive=True):
        self.sample = aquarium_sample
        if not isinstance(self.sample, pydent.models.Sample):
            raise AqSeqException("Expects a Sample, not a {}".format(type(self.sample)))
        self.__sequence = None
        self.connector = connector
        self.logger = logger(self)
        self.interactive = interactive

    def new(self, sample):
        """
        Return a new AquariumDNA instance from an Aquarium sample.

        :param sample: Aquarium sample
        :return: AquariumDNA instance
        """
        return self.__class__(sample, self.connector)

    def new_sequence(self, *args, **kwargs):
        """
        Create a new jdna.Sequence instance and add to this AquariumDNA instance.
        This will also update the metadata of the jdna.Sequence from the sample
        attached to this AquariumDNA.

        :param args: creation args
        :param kwargs: creation kwargs
        :return:
        """
        sequence = jdna.Sequence(*args, **kwargs)
        self._update_sequence_info(sequence)
        return sequence

    def _update_sequence_info(self, sequence):
        sequence.name = self.sample.name
        sequence.metadata["webURL"] = self.sample.properties.get("Sequence", None)
        sequence.metadata["aquarium_id"] = self.sample.id
        sequence.metadata["sample_type"] = self.sample.sample_type.name
        return sequence

    ########################################
    # Getters
    ########################################

    def from_link(self, key="Sequence"):
        """
        Return the sequence from a weblink. The weblink should be attached to the
        Sample properties via 'key' (default is 'Sequence').

        To get a sequence from a weblink directly, use `self.connector.fetch(weblink)`

        :param key: property key containing weblink.
        :return:
        """
        weblink = self.sample.properties.get(key, "")
        if weblink is None:
            weblink = ""
        else:
            weblink = weblink.strip()
        self.logger.info(
            "Fetching sequence '{sample}' from weblink '{link}'".format(
                link=weblink, sample=self.sample.name
            )
        )
        seq = self.connector.fetch(weblink)
        return seq

    def is_registered(self):
        """
        Returns whether the AquariumDNA has a registered sequence.

        :return:
        """
        if self.from_registry() is not None:
            return True
        return False

    def from_registry(self):
        """
        Get the jdna.Sequence from the register. Conventionally, the registry id is unique to the attatched
        Aquarium sample.

        :return:
        """
        self.logger.info("Attempting to find '{}' in registry".format(self.sample.name))
        try:
            return self.connector.find(self.sample.id)
        except InvalidRegistryId:
            return None
        except TypeError:
            return None

    def sequence_as_api(self):
        """
        Return the sequence in the format the Connector api expects (i.e. not jdna.Sequence).

        Will try to get sequence in the following order:

        1. from the registry
        2. from the weblink

        :return: dna (from Connector model)
        """
        seq = self.from_registry()
        if seq is None:
            try:
                return self.from_link()
            except ValueError:
                pass
        return seq

    def sequence_from_api(self):
        """
        Return the sequence as a jdna.Sequence.

        Will try to get sequence in the following order:

        1. from the registry
        2. from the weblink

        :return: jDNA.Sequence
        """
        sequence = self.sequence_as_api()
        if sequence:
            sequence = self.connector.from_api(sequence)
            self._update_sequence_info(sequence)
            return sequence

    @classmethod
    def get_sequences(cls, samples, registry):
        """
        Return list of sequences from a list of samples.

        :param samples: list of samples
        :param registry: connector registry
        :return:
        """
        dnas = []
        for sample in samples:
            if isinstance(sample, cls):
                dnas.append(sample)
            else:
                dnas.append(cls(sample, registry))
        sequences = []
        for dna in dnas:
            sequences.append(dna.sequence())
        return sequences

    @classmethod
    @make_async(1, as_classmethod=True)
    def batch_get_sequences(cls, samples, registry):
        """
        Async get sequences. See `get_sequences`.

        :param samples:
        :param registry:
        :return:
        """
        dnas = [cls(sample, registry) for sample in samples]
        sequences = []
        for dna in dnas:
            sequences.append(dna.sequence())
        return sequences

    def url(self):
        """
        Return the webURL of the linked sequence.

        :return:
        """
        seq = self.sequence_as_api()
        return seq.webURL

    def open(self):
        """
        Open the webURL of the linked sequence.

        :return:
        """
        seq = self.sequence_as_api()
        if seq:
            seq.open()
        else:
            print("No sequence found...")

    def registry_id(self):
        """
        Return the connector registry id of the sequence.

        :return:
        """
        seq = self.sequence_as_api()
        return seq.entityRegistryId

    ########################################
    # Setters
    ########################################

    def register(self, sequence=None):
        """
        Register the sequence with the connector registry.

        :param sequence:
        :return:
        """
        if sequence is None:
            sequence = self.sequence()
        if sequence is None:
            raise AqSeqException(
                "Cannot find a sequence for '{}'".format(self.sample.name)
            )
        self._update_sequence_info(sequence)
        api_seq = self.connector.to_api(sequence)
        return self.connector.register(api_seq, self.sample.id, overwrite=True)

    ########################################
    # Reactions returning multiple
    # products/assemblies
    ########################################

    def linear_assemblies(self, fragments=None, key=None):
        """
        Produce a sequence from a linear assembly of fragments. If fragments are not provided,
        a 'key' can be provided to get the fragments from the properties of the sample.

        :param fragments:
        :param key:
        :return:
        """
        if key is None:
            key = self.DEFAULTS.LINEAR_ASSEMBLY_KEY
        if fragments is None:
            fragments = self.sample.properties[key]
        if not fragments:
            return None
        sequences = self.get_sequences(fragments, self.connector)
        assemblies = jdna.Reaction.linear_assemblies(
            sequences,
            min_bases=self.DEFAULTS.MIN_ASSEMBLY_BASES,
            max_bases=self.DEFAULTS.MAX_ASSEMBLY_BASES,
        )
        return assemblies

    def cyclic_assemblies(self, fragments=None, key=None):
        """
        Produce a sequence from a cyclic assembly of fragments. If fragments are not provided,
        a 'key' can be provided to get the fragments from the properties of the sample.

        :param fragments:
        :param key:
        :return:
        """
        if key is None:
            key = self.DEFAULTS.LINEAR_ASSEMBLY_KEY
        if fragments is None:
            fragments = self.sample.properties[key]
        sequences = self.get_sequences(fragments, self.connector)
        assemblies = jdna.Reaction.cyclic_assemblies(
            sequences,
            min_bases=self.DEFAULTS.MIN_ASSEMBLY_BASES,
            max_bases=self.DEFAULTS.MAX_ASSEMBLY_BASES,
        )
        return assemblies

    # TODO: autoregister
    def pcr_products(self):
        """
        Produce a sequence as a pcr product. If fragments are not provided,
        a 'key' can be provided to get the fragments from the properties of the sample.

        :param fragments:
        :param key:
        :return:
        """
        self.logger.info("Building sequence from template and primers")
        self.logger.info(self.sample.properties)
        template, p1, p2 = [
            self.sample.properties[key]
            for key in [
                self.DEFAULTS.TEMPLATE_KEY,
                self.DEFAULTS.FORWARD_PRIMER_KEY,
                self.DEFAULTS.REVERSE_PRIMER_KEY,
            ]
        ]

        if None in [template, p1, p2]:
            self.logger.info(
                "Cannot find pcr products since one of the following is none: {}".format(
                    {"p1": p1 is None, "p2": p2 is None, "template": template is None}
                )
            )
            return []

        self.logger.info("Finding primer sequences")
        p1_sequence = self.new(p1).sequence()
        p2_sequence = self.new(p2).sequence()
        self.logger.info("Forward primer: '{}'".format(p1_sequence))
        self.logger.info("Reverse primer: '{}'".format(p2_sequence))

        self.logger.info("Finding template sequence")
        template_sequence = self.new(template).sequence()
        self.logger.info("Template sequence:: {}".format(template_sequence.__repr__()))

        if template_sequence is None:
            self._error("Template sequence {} was not found".format(template.name))

        if p1_sequence is None:
            self._error("Primer sequence {} was not found".format(p1.name))

        if p2_sequence is None:
            self._error("Primer sequence {} was not found".format(p2.name))

        products = jdna.Reaction.pcr(template_sequence, [p1_sequence, p2_sequence])
        return products

    ########################################
    # Reactions returning single
    # products/assemblies
    ########################################

    def _only_one(self, arr, more_than_one_err, none_err):
        if len(arr) > 1:
            self._error(more_than_one_err)
        elif len(arr) == 0:
            self._error(none_err)
        else:
            return arr[0]

    def linear_assembly(self, fragments=None, key=None):
        assemblies = self.linear_assemblies(fragments, key)
        return self._only_one(
            assemblies,
            "More than one linear assembly found",
            "No linear assembly found",
        )

    def cyclic_assembly(self, fragments=None, key=None):
        assemblies = self.cyclic_assemblies(fragments, key)
        return self._only_one(
            assemblies,
            "More than one cyclic assembly found",
            "No cyclic assembly found",
        )

    def linear_product(self, fragments=None, key=None):
        return self._update_sequence_info(self.linear_assembly(fragments, key).product)

    def cyclic_product(self, fragments=None, key=None):
        return self._update_sequence_info(self.cyclic_assembly(fragments, key).product)

    def pcr_product(self):
        products = self.pcr_products()
        if products:
            return self._update_sequence_info(
                self._only_one(
                    products,
                    "There was more than one pcr product",
                    "There were no pcr products",
                )
            )

    ########################################
    # Dispatching methods
    ########################################

    def _sequence_from_parts(self, keys):
        sequence = ""
        for key in keys:
            seq = self.sample.properties[key]
            sequence += seq.strip().upper()
        return self.new_sequence(sequence)

    def request_sequence_from_link(self):
        s = input(
            "Could not find a sequence for Sample '{}'. Would you "
            "like to provide an alternative weblink (Y/N)?".format(self.sample.name)
        )
        if s.lower().startswith("y"):
            weblink = input("  Enter weblink: ")
            api_seq = self.connector.fetch(weblink)
            return self.connector.from_api(api_seq)

    def sequence(self, interactive=None):
        """
        Catch all to find the sequence from a sample. Tries the following:

        1. Sequence from the registry
        2. Sequence from the weblink
        3. If sample is a fragment, tries to make a pcr_product
        4. If sample is a primer, builds sequence from keys (self.DEFAULTS.PRIMER_SEQUENCE_KEYS)
        5. Finally, asks user to provide a web link for the sequence.

        :return:
        """
        # If PRIMER, build sequence from keys
        if self.sample is None:
            return None
        if self.sample.sample_type.name == "Primer":
            return self._sequence_from_parts(self.DEFAULTS.PRIMER_SEQUENCE_KEYS)
        else:
            seq = self.sequence_from_api()
            if seq is None:
                if self.sample.sample_type.name == "Fragment":
                    self.logger.info("Attempting pcr product...")
                    seq = self.pcr_product()
                    if seq is not None:
                        return seq

                    self.logger.info("Attempting linear product...")
                    seq = self.linear_product(key=self.DEFAULTS.LINEAR_ASSEMBLY_KEY)
                    if seq is not None:
                        return seq
            else:
                return seq
        if interactive is None:
            interactive = self.interactive
        if interactive:
            return self.request_sequence_from_link()
        else:
            raise AqSeqException(
                "Could not find sequence. Use 'interactive=True' if you would like "
                "to provide a link to the sequence."
            )


class AquariumDNAFactory(object):
    """AquariumDNAFactory that produces AquariumDNA instances."""

    def __init__(self, connector, interactive=True):
        self.connector = connector
        self.logger = logger(self)
        self.interactive = interactive

    def new(self, sample, interactive=None):
        if interactive is None:
            interactive = self.interactive
        dna = AquariumDNA(sample, self.connector, interactive=interactive)
        # dna.set_verbose(dna._verbose)
        return dna
