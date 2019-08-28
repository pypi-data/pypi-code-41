import re
import uuid

import benchlingapi
import jdna
import primer3
from benchlingapi.exceptions import InvalidRegistryId

from aqseq.logger import MyLoggable
from pydent import AqSession
from pydent.browser import Browser


class Connector(object):
    def retrieve_sequence(self):
        pass

    @staticmethod
    def dna(sequence, name=None):
        return jdna.Sequence(sequence, name=name)

    @classmethod
    def from_json(cls, json_seq):
        """
        Converts a benchling sequence to a jDNA sequence

        :param json_seq: benchling DNASequence
        :return: jDNA sequence
        """
        return jdna.Sequence.load(json_seq)

    def to_json(self, seq):
        """
        Converts a DNA sequence to a JSON formatted DNA sequence

        :param seq: jDNA sequence
        :return: benchling DNASequence
        """
        return seq.json()


class RegistryConnector(object):
    def __init__(self, api, initials, schema, prefix, folder_id, registry_id):
        self.api = api
        self.initials = initials
        self.schema = schema
        self.prefix = prefix
        self.folder_id = folder_id
        self.registry = self.api.Registry.find(registry_id)

    def format_registry_id(self, uid):
        return "{prefix}{init}{uid}".format(
            prefix=self.prefix, uid=uid, init=self.organization_initials
        )

    def find(self, uid):
        return self.registry.find_in_registry(self.format_registry_id(uid))

    def register(self, seq, uid, overwrite=True):
        seq.folderId = self.folder_id
        if not hasattr(seq, "id") or seq.id is None:
            seq.save()
        seq.set_schema(self.schema)
        try:
            seq.register_with_custom_id(self.format_registry_id(uid))
        except InvalidRegistryId as e:
            if not overwrite:
                raise e
            existing = self.api.DNASequence.find_in_registry(
                self.format_registry_id(uid)
            )
            print(existing)
            seq = self.api.DNASequence.update_model(existing.id, seq.update_json())
        return seq


class BenchlingConnector(MyLoggable, Connector):
    def __init__(self, api):
        self.api = api
        self.init_logger("{}_{}".format(self.__class__.__name__, str(api)))

    @staticmethod
    def extract_sequence_id_from_benchling_weblink(link):
        """
        Extracts a benchling sequence id from a generic benchling URL

        :param link: benchling URL
        :type link: basestring
        :return: the benchling sequence id
        :rtype: basestring
        """
        m = re.search("/seq-(\w+)-", link)
        if m is not None:
            return "seq_{}".format(m.group(1))

    def retrieve_sequence(self, sample):
        """
        Retrieve the jDNA sequence object from an aquarium sample

        :param sample: the Aquarium sample
        :type sample: pydent.Sample
        :return:
        :rtype: jDNA.Sequence
        """
        for seq_key in ["Sequence", "Sequence Verification"]:
            weblink = sample.properties.get(seq_key, None)
            return self.from_benchling(self.get_benchling_sequence(weblink))

    def get_benchling_sequence(self, key):
        seqid = self.extract_sequence_id_from_benchling_weblink(key)
        if seqid is not None:
            return self.api.DNASequence.find(seqid)
        try:
            if key is not None and key != "":
                return self.api.DNASequence.from_share_link(key)
        except benchlingapi.BenchlingAPIException:
            pass

    def benchling_annotation_to_jdna_feature(seq, annotation):
        """
        Converts a benchling annotation to a jDNA feature

        :param seq: jdna sequence
        :param annotation: benchling Annotation
        :return: jDNA feature
        """
        feature = jdna.core.Feature(
            annotation.name,
            type=annotation.type,
            strand=annotation.strand,
            color=annotation.color,
        )
        seq.add_feature(feature=feature, i=annotation.start, j=annotation.end - 1)
        return feature

    def from_benchling(self, benchling_sequence):
        """
        Converts a benchling sequence to a jDNA sequence

        :param benchling_sequence: benchling DNASequence
        :return: jDNA sequence
        """
        s = benchling_sequence
        seq_json = s.save_json()
        return self.from_json(seq_json)

    def to_benchling(self, sequence):
        """
        Converts a jdna Sequence to a Benchling DNASequence object.

        :param sequence: a jdna sequence object
        :type sequence: jdna.Sequence
        :return: benchling DNASequence object
        :rtype: benchlingapi.DNASequence
        """
        seq_json = self.to_json(sequence)
        seq_json["folderId"] = str(uuid.uuid4())
        return self.api.DNASequence.load(seq_json)

    def save_sequence(self, sequence, folder_id=None, folder=None, folder_name=None):
        if folder_id is None and folder is not None:
            folder_id = folder.id
        elif folder_name is not None:
            folder_id = self.api.Folder.find_by_name(folder_name).id
        benchling_seq = self.to_benchling(sequence)
        benchling_seq.folderId = folder_id
        folder = self.api.Folder.find(folder_id)
        response = benchling_seq.save()
        self._info(
            "BENCHLING Saved sequence seqName='{seqName}' seqId='{seqId}' "
            "folderId='{folderId}' folderName='{folderName}'".format(
                seqName=benchling_seq.name,
                seqId=benchling_seq.id,
                folderId=folder_id,
                folderName=folder.name,
            )
        )
        self._info("BENCHLING sequence_url: {}".format(benchling_seq.webURL))
        return benchling_seq


class SequenceManager(MyLoggable, object):
    """Manages sequences and sequence simulations like PCR"""

    def __init__(self, browser, connector, registry=None):
        self.browser = browser
        self.connector = connector
        self.registry = registry
        self.rebase = None
        self.init_logger("SeqManager@{}".format(browser.session.url))

    @classmethod
    def load_from_config(cls, config, session_name, login, password):
        session_info = config["sessions"][session_name]
        connector_info = config["connectors"][session_info["connector"]]
        registry_info = connector_info["registry"]
        session = AqSession(login, password, session_info["url"])

        benchapi = benchlingapi.Session(connector_info["api_key"])

        connector = BenchlingConnector(benchapi)
        registry = RegistryConnector(
            benchapi,
            registry_id=registry_info["id"],
            folder_id=registry_info["folder_id"],
            prefix=registry_info["prefix"],
            initials=registry_info["initials"],
            schema=registry_info["schema"],
        )
        return cls(Browser(session), connector, registry=registry)

    def register_sequence(self, sample, sequence=None):
        if sequence is None:
            sequence = self.retrieve_sequence(sample)
        bseq = self.connector.to_json(sequence)
        self.registry.register(sample.id, bseq, overwrite=True)

    def get_registered_sequence(self, sample):
        return self.connector.from_json(self.registry.find(sample.id))

    def set_verbose(self, verbose):
        super().set_verbose(verbose)
        self.connector.set_verbose(verbose)

    @staticmethod
    def _attach_sequence(sample, sequence):
        sample.seq = sequence

    @staticmethod
    def _get_attached_sequence(sample):
        return sample.__dict__.get("seq", None)

    # def get_rebase(self):
    #     if self.rebase is None:
    #         self.rebase = coral.database.Rebase()

    def dna(self, sequence, name=None):
        return self.connector.new(sequence, name=name)

    def get_primer_sequence(self, primer):
        """Returns a complete and sanitized primer sequence from an Aquarium Primer Sample"""
        sequence_parts = []
        for key in self.model_keys["Primer"]["keys"]["sequence_parts"]:
            seqpart = primer.properties.get(key, "")
            if seqpart is None:
                seqpart = ""
            sequence_parts.append(seqpart)
        sequence = "".join(sequence_parts)
        return re.sub("\s+", "", sequence).upper()

    def retrieve_sequence(self, sample):
        """

        :param sample:
        :type sample: pydent.models.Sample
        :return:
        :rtype:
        """
        seq = self._get_attached_sequence(sample)
        if seq is None:
            seq = self.connector.retrieve_sequence(sample)
            self._attach_sequence(sample, seq)
        return seq

    def _pcr(self, template, primers):
        """

        :param template: template sequence
        :type template: jdna.Sequence
        :param primers: list of jdna.Sequence
        :type primers: list
        :return:
        :rtype:
        """
        return jdna.Reaction.pcr(template, primers)

    def pcr_from_fragment(self, fragment, template_sequence=None):
        """
        Produces a jdna Sequence from a template

        :param fragment: an Aquarium fragment sample
        :type fragment: Sample
        :param template_sequence: Optional template sequence. If not provided, the sequence must
        be accessible through Benchling
        :type template_sequence: jdna.Sequence
        :return: list of jdna.Sequences
        :rtype: list
        """

        primer1 = fragment.properties["Forward Primer"]
        primer2 = fragment.properties["Reverse Primer"]
        template = fragment.properties["Template"]

        p1 = self.dna(self.get_primer_sequence(primer1), primer1.name)
        p2 = self.dna(self.get_primer_sequence(primer2), primer2.name)

        if template_sequence is None:
            template_sequence = self.retrieve_sequence(template)

        products = self._(template_sequence, [p1, p2])
        return products

    def _update_sequence_helper(self, fragment, sequence, length_key="Length"):
        if length_key:
            fragment.update_properties({length_key: len(sequence)})
        self._info(
            "updated Fragment '{}' with Length={}".format(fragment.name, len(sequence))
        )
        sequence.name = fragment.name
        self._attach_sequence(fragment, sequence)

    def update_fragment_with_sequence(self, fragment, template_sequence=None):
        """
        Produces a jdna Sequence from a template and updates the fragment Length.
        Attatches the 'seq' jdna.Sequence attribute to the fragment.

        :param fragment: an Aquarium fragment sample
        :type fragment: Sample
        :param template_sequence: Optional template sequence. If not provided, the sequence must
        be accessible through Benchling
        :type template_sequence: jdna.Sequence
        :return: list of jdna.Sequences
        :rtype: list
        """
        products = self.pcr_from_fragment(fragment, template_sequence=template_sequence)
        self._info(
            "Fragment '{}' produced {} pcr products".format(
                fragment.name, len(products)
            )
        )
        if len(products) == 0:
            raise Exception("There were no products for {}".format(fragment.name))
        elif len(products) > 1:
            raise Exception(
                "There were more than one product for {}".format(fragment.name)
            )

        product = products[0]
        self._update_sequence_helper(fragment, product)
        return fragment

    def new_pcr_fragment(self, p1, p2, template, name, description="", project=""):
        """
        Produces a new Aquarium sample from primers and a template sample.

        :param p1: Aquarium sample
        :type p1: pydent.models.Sample
        :param p2: Aquarium sample
        :type p2: pydent.models.Sample
        :param template: Aquarium sample
        :type template: pydent.models.Sample
        :return: new Aquarium sample
        :rtype: Aquarium sample
        """

        self._info(
            "Generating fragment '{name}' from primers '{fwd}' & '{rev}' and template '{template}'".format(
                name=name, fwd=p1.name, rev=p2.name, template=template.name
            )
        )
        template_sequence = self.retrieve_sequence(template)
        if template_sequence is None:
            raise Exception("Template sequence is missing")
        new_fragment = self.browser.new_sample(
            "Fragment",
            name,
            description,
            project,
            properties={
                "Forward Primer": p1,
                "Reverse Primer": p2,
                "Template": template,
            },
        )
        self.update_fragment_with_sequence(new_fragment)
        return new_fragment

    def check_registry(self, aquarium_sample):
        return
        self.registry.check_url(aquarium_sample.session.url)

    def register_sample(self, aquarium_sample, sequence):
        self.check_registry(aquarium_sample)
        uid = aquarium_sample.id
        if not uid:
            raise Exception("Cannot register. Aquarium sample must have an id")
        sequence.name = aquarium_sample.name
        bseq = self.connector.to_benchling(sequence)
        self.registry.register(bseq, uid)

    def get_registered_sample(self, aquarium_sample):
        self.connector

    @staticmethod
    def parse_primer3_results(results_dict):
        num_pairs = results_dict["PRIMER_PAIR_NUM_RETURNED"]
        pairs = {}
        for i in range(num_pairs):
            pairs.setdefault(i, {})
        key_pattern = "PRIMER_(?P<label>[a-zA-Z]+)_(?P<pair_id>\d+)_(?P<key>.+)"
        for k in results_dict:
            m = re.match(key_pattern, k)
            if m:
                groupdict = m.groupdict()
                pair_id = int(groupdict["pair_id"])
                label = groupdict["label"]
                key = groupdict["key"]
                pairdict = pairs[pair_id]
                pairdict.setdefault(label, {})
                pairdict[label][key] = results_dict[k]
        return pairs

    def _primer3(self, seq_args, global_args):
        return primer3.bindings.designPrimers(dict(seq_args), dict(global_args))

    def primer3_example(self):
        return dict(
            seq_args={
                "SEQUENCE_TEMPLATE": "AGTAGA...",
                "SEQUENCE_TARGET": [(10000, 1500)],
            },
            global_args={
                "PRIMER_OPT_SIZE": 20,
                "PRIMER_MIN_SIZE": 16,
                "PRIMER_MAX_SIZE": 30,
                "PRIMER_OPT_TM": 60.0,
                "PRIMER_MIN_TM": 52.0,
                "PRIMER_MAX_TM": 75.0,
                "PRIMER_MIN_GC": 20.0,
                "PRIMER_MAX_GC": 80.0,
                "PRIMER_PRODUCT_SIZE_RANGE": [[500, 4000]],
                "PRIMER_PRODUCT_OPT_SIZE": 2000,
            },
        )

    def primer3_help(self):
        print("http://primer3.sourceforge.net/primer3_manual.htm")

    def design_primers(self, seq_args, global_args):
        results = self._primer3(seq_args, global_args)
        return self.parse_primer3_results(results)
