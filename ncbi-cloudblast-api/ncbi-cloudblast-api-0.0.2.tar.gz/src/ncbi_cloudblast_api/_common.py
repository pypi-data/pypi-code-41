import grpc
from ncbi.cloudblast.v1alpha import api_pb2_grpc as cloudblast_grpc
from typing import Generator, TextIO, cast
from contextlib import contextmanager

from sys import stdin, stdout, stderr, exit
import os


VERBATIM_SEQ_ARG = '--verbatim-seq'
SEQ_ACCESSION_ARG = '--seq-accession'


class InvalidArgumentError(ValueError):
    pass


def create_stub(host: str) -> cloudblast_grpc.CloudBlastStub:
    """
    Create stub for a RPC
    """
    channel = grpc.insecure_channel(host)
    stub = cloudblast_grpc.CloudBlastStub(channel)
    return stub


@contextmanager
def open_file(filename: str, mode: str) -> Generator[TextIO, None, None]:
    """
    Open text file for reading or writing.

    Arguments:
        file_name: Name of file to be opened:
            Name could be "-" and than std stream will be opened based on mode:
                r - will open stdin
                w - will open stdout

        mode: Read write or append:
            r - for read
            w - write

    """
    if mode not in ['r', 'w']:
        raise Exception(f"Wrong file mode '{mode}'")

    if mode == 'r':
        if not filename or (filename != '-' and not os.path.isfile(filename)):
            raise Exception(f'No such file "{filename}"')

    if filename == '-':
        if mode is None or not('a' in mode or 'w' in mode):
            yield cast(TextIO, stdin)
        else:
            yield cast(TextIO, stdout)
    else:
        with open(filename, mode + 't') as fp:
            yield cast(TextIO, fp)


def handle_grpc_error(e: grpc.RpcError) -> None:
    print('A gRPC error has occurred: ', file=stderr)
    print('\tStatus code: ' + str(e.code()), file=stderr)
    details = e.details()
    if (details):
        print('\tMessage from service: ' + str(details), file=stderr)
    exit(1)
