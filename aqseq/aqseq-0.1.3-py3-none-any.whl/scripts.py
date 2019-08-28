from benchlingapi.exceptions import InvalidRegistryId
from pydent.browser import Browser
from pydent.planner import Planner
from pydent.models import Sample
from pydent.utils import make_async
from aqseq.logger import MyLoggable
from jdna import Reaction
import tempfile
import re
import os


class SequenceScripts(MyLoggable):
    def __init__(self, aqsession, dna_factory):
        self.session = aqsession
        self.dna = dna_factory
        self.init_logger("SequenceScripts")

    def new_browser(self):
        return Browser(self.session)

    def new_plan(self):
        return Planner(self.session)

    def gibson_to_assembly(self, opid, print_assembly=True):
        op = self.session.Operation.find(opid)

        browser = self.new_browser()
        browser.recursive_retrieve([op], {"field_values": "sample"})

        output_dna = self.dna.new(op.outputs[0].sample)
        try:
            if output_dna.from_registry():
                self._info(
                    "Gibson assembly unnecessary as there is already a registered sequence."
                )
                output_dna.sequence_as_api().open()
                return output_dna.sequence
        except InvalidRegistryId:
            pass

        input_fragments = [fv.sample for fv in op.input_array("Fragment")]
        input_dnas = [self.dna.new(f) for f in input_fragments]
        input_sequences = [d.sequence() for d in input_dnas]

        assemblies = Reaction.cyclic_assemblies(input_sequences)
        if not assemblies:
            self._error("NO CYCLIC ASSEMBLIES FOUND")
            linear_assemblies = Reaction.linear_assemblies(input_sequences)
            if linear_assemblies:
                self._error("Linear assemblies found...")
                print(linear_assemblies)
                for a in linear_assemblies:
                    print(a.header)
                return linear_assemblies
            else:
                self._error("NO LINEAR ASSEMBLIES FOUND")
            return

        return output_dna, input_dnas, assemblies

    @staticmethod
    def _parse_sequence_upload_name(upload_name):
        m = re.search(
            "(?P<miniprep>\d+)-(?P<user>\w+)-(?P<primer>\d+).(?P<format>\w+)",
            upload_name,
        )
        return m.groupdict()

    @make_async(1, as_classmethod=True)
    def _download(self, uploads, outdir=None):
        sequence_files = []
        for u in uploads:
            msg = "Downloading '{}' to '{}'"
            if outdir is None:
                filepath = tempfile.mkstemp()[1]
                self._info(msg.format(u.name, filepath))
                sequence_files.append(u.download(filepath=filepath))
            else:
                filepath = os.path.join(outdir, u.name)
                self._info(msg.format(u.name, filepath))
                u.download(filepath=filepath)
                sequence_files.append(filepath)
        return sequence_files

    def download_sequence_files(self, sample, outdir=None):
        browser = self.new_browser()
        if isinstance(sample, str):
            sample = browser.find_by_name(sample)
        if not isinstance(sample, Sample):
            raise Exception(
                "Type {} not recognized. Please use a sample name or Sample".format(
                    sample
                )
            )

        self._info("Pulling sanger sequencing files...")
        ot = browser.find_by_name(
            "Upload Sequencing Results", model_class="OperationType"
        )
        ft = ot.field_types[0]
        fvs = browser.where(
            {"field_type_id": ft.id, "child_sample_id": sample.id},
            model_class="FieldValue",
        )
        browser.recursive_retrieve(fvs, {"operation": "jobs"})

        uploads = []
        for fv in fvs:
            for job in fv.operation.jobs:
                for upload in job.uploads:
                    parsed = self._parse_sequence_upload_name(upload.name)
                    item = self.session.Item.find(parsed["miniprep"])
                    item_sample_id = item.sample_id
                    if item_sample_id == sample.id:
                        uploads.append(upload)

        return self._download(uploads, outdir)

    def find_alignments(self, plasmid_name):
        dna = self.dna.new(self.session.Sample.find_by_name(plasmid_name))
        dna_seq = dna.sequence()
        if dna_seq is None:
            raise Exception("No sequence attached to sample '{}'".format(plasmid_name))
        sequence_files = self.download_sequence_files(plasmid_name)
        alignments = dna_seq.align.sanger_reads(sequence_files)
        return alignments
