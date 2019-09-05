'''
Define a wrapper class for BLAST
'''
from os import path, environ
import logging
import subprocess
import shlex

from emmtyper.objects.command import Command, FileNotInPathException
from emmtyper.objects.result_row import ResultRow

logging.basicConfig(level=environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)


class BLAST(Command):
    """
    Wrapper class for command-line blastn.
    
    Command-line blastn only allows filtering using e-value, percent identity, and culling limit.
    Additional filter option is given in this wrapper, namely:
    1. Mismatch 
        Regular blastn can do this with perc_identity, but needs to be in percentage of alignment length.
        Specify an integer N, number of mismatches allowed as result. Default = 4.
    2. GapOpen
        Regular blastn cannot do this directly, but you can calculate the resulting e-value from gap open penalty.
        Specify an integer N, number of gap open allowed. Default = 2.
    3. AlignDiff
        This cannot be done only with regular blastn.
        Specify an integer N, which is the maximum allowed difference between subject and alignment length. Default = 5.
    
    Requires user to install blastn on own, and needs ResultRow class.
    
    This class is developed to be used within emmtyper, thus the output format. 
    You need to change the output format AFTER filtering if you want anything other than "6 std slen".
    """

    def __init__(
        self,
        db,
        query,
        dust,
        perc_identity,
        culling_limit,
        output_stream,
        header,
        mismatch,
        align_diff,
        gap,
        tool_path=None,
    ):

        Command.__init__(self, "blastn", tool_path=tool_path)

        self.version = self.get_version()

        self.db = '"\\"' + self.assert_db_and_return(db) + '"\\"'
        self.query = shlex.quote(Command.assert_filepath_and_return(query))

        self.dust = dust
        self.perc_identity = perc_identity
        self.culling_limit = culling_limit

        self.outformat = "6 std slen"
        self.output_stream = output_stream

        self.want_header = header

        # Threshold for ResultRow filtering

        self.mismatch = mismatch
        self.align_diff = align_diff
        self.gap = gap

        self.command_string = self.build_blastn_command()

    def __repr__(self):
        return self.command_string

    def __str__(self):
        string = (
            "{0}\n"
            "Query = {1}\n"
            "DB = {2}\n"
            "Dust filter = {3}\n"
            "% Identity = {4}\n"
            "Culling limit = {5}\n"
            "Outformat = {6}\n"
            "Output to = {7}\n"
            "Mismatch filter = {8}\n"
            "Align difference filter = {9}\n"
            "Gap filter = {10}"
        )

        string = string.format(
            self.version,
            self.query,
            self.db,
            self.dust,
            self.perc_identity,
            self.culling_limit,
            self.outformat,
            self.output_stream,
            self.mismatch,
            self.align_diff,
            self.gap,
        )

        return string

    def get_version(self):
        process = subprocess.Popen(
            args="{} -version".format(self.tool_name),
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = process.communicate()

        return stdout.decode("ascii")

    def assert_db_and_return(self, file_path):
        if not (
            path.isfile(file_path + ".nin")
            and path.isfile(file_path + ".nhr")
            and path.isfile(file_path + ".nsq")
        ):
            raise FileNotInPathException(
                "{} is not a BLAST database!".format(file_path)
            )
            exit(1)

        return file_path

    def build_blastn_command(self):
        string = (
            "{tool_path} -db {db} -query {query} -dust {dust} -perc_identity {perc_id}"
            " -culling_limit {cull_limit} -outfmt \"{outfmt}\""
        )

        command = string.format(
            tool_path=self.tool_path,
            db=self.db,
            query=self.query,
            dust=self.dust,
            perc_id=self.perc_identity,
            cull_limit=self.culling_limit,
            outfmt=self.outformat,
        )

        logger.info(f"Running command {command}")

        return command

    def filter_blastn_results(self, outputs):

        ok_results = [
            ResultRow(output)
            for output in outputs
            if ResultRow(output).filter(self.mismatch, self.align_diff, self.gap)
        ]

        return ok_results

    def result_to_output(self, filtered_outputs):
        string = ""

        for output in filtered_outputs:
            string = "\n".join([repr(output) for output in filtered_outputs])

        # Log if BLAST produces no result
        if not string:
            logger.info("There is no output for {}".format(self.query))

        # Produces header if wanted, attach to string
        if self.want_header and string:
            string = ResultRow.build_header() + string

        # Where to output product
        if self.output_stream in [None, "None", "stdout"]:
            print(string)
        else:
            with open(self.output_stream, "w") as handle:
                handle.write(string)

        return string

    def run_blastn_pipeline(self):
        # logger.info("Running on {}".format(self.query))

        outputs = Command.run(self).split("\n")[:-1]

        filtered_outputs = self.filter_blastn_results(outputs)

        return self.result_to_output(filtered_outputs)
