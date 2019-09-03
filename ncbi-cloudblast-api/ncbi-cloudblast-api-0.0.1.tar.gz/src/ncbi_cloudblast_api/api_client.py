from ncbi.cloudblast.v1alpha import api_pb2 as cloudblast_pb2
from ncbi.cloudblast.v1alpha import blast_request_pb2

from ._common import (create_stub,
                      handle_grpc_error,
                      InvalidArgumentError)
from .converters import convert_resultreply, convert_status
from .result import SearchResult
from .status import Status

from google.protobuf import empty_pb2
import grpc

from typing import List, Optional, Tuple
import time

JobId = str


class APIClient:
    """

    A CloudBlast API client library.

    Provide the interface to get the list of supported databases,
    submit a search job, query for status and get search result.

    """
    __POLL_TIMEOUT = 0.333

    def __init__(self, host: str, api_key: str = "",
                 timeout: float = 30) -> None:
        """Initialize the client

        Parameters:
            host (str): The IP address (including port) of the API service. E.g
                1.2.3.4:12345
            api_key (str): The API key for CloudBlast endpoint (default is
                empty string)
            time_out (float): CloudBlast request timeout, in seconds
                (default is 30 sec)

        """

        if not host:
            raise InvalidArgumentError(
                f'host cannot be empty.'
            )
        self._host = host
        self._api_key = api_key
        self._timeout = timeout

        self._metadata: List[Tuple[str, str]] = []
        if self._api_key:
            self._metadata.append(('x-api-key', self._api_key))

        # Default
        self._db_tag = 'nt'
        self._program = blast_request_pb2.BlastRequest.BLASTN

        # TODO provide setters for Blast parameters

    @property
    def host(self) -> str:
        return self._host

    @property
    def api_key(self) -> str:
        return self._api_key

    @property
    def timeout(self) -> float:
        return self._timeout

    def dblist(self) -> cloudblast_pb2.DBCatalog:
        """Retrieve the list of supported Blast databases

        Returns:
            dict: a dictionary containing a list of supported
                Blast databases.
        """
        try:
            return create_stub(self._host).GetDBCatalog(
                empty_pb2.Empty(), self._timeout, metadata=self._metadata)

        except grpc.RpcError as e:
            handle_grpc_error(e)

    def submit(
            self, *,
            accession: str = None, verbatim_seq: str = None, fasta: str = None,
            from_: Optional[int] = None, to: Optional[int] = None) -> JobId:
        """Submit a Blast search request and get a job id.
        The accepted input types for the query sequence(s) to be used
        for the search are sequence identifier, bare sequence, or FASTA.

        Parameters:
            accession (str): the accession.version of the query sequence
            verbatim_seq (str): the verbatim (raw) sequence
            fasta(str): contains a sequence in FASTA format. The first line
                        must be a description line (defline)
            from_: the start (inclusive) of the sequence coordinates range
                   from 1 to the sequence length
            to: the end of said range (inclusive)

        Returns:
            str: the job id of this search request
        """
        submit_req = cloudblast_pb2.SubmitRequest()

        self.__set_sequence(submit_req, accession, verbatim_seq, fasta)

        if from_:
            submit_req.req.coords.start = from_
        if to:
            submit_req.req.coords.stop = to

        return self.__submit_request(submit_req)

    def search(
            self, *,
            accession: str = None, verbatim_seq: str = None, fasta: str = None,
            from_: Optional[int] = None, to: Optional[int] = None) -> SearchResult:
        """Submit a Blast search request, wait until the search is complete, and
        return the results of said search.
        It is similar to `submit` except that it waits until the search is finished.
        The accepted input types for the query sequence(s) to be used
        for the search are sequence identifier, bare sequence, or FASTA.

        Parameters:
            accession (str): the accession.version of the query sequence
            verbatim_seq (str): the verbatim (raw) sequence
            fasta(str): contains a sequence in FASTA format. The first line
                        must be a description line (defline)
            from_: the start (inclusive) of the sequence coordinates range
                   from 1 to the sequence length
            to: the end of said range (inclusive)

        Returns:
            SearchResult: the job id of this search request
        """
        submit_req = cloudblast_pb2.SubmitRequest()

        self.__set_sequence(submit_req, accession, verbatim_seq, fasta)

        if from_:
            submit_req.req.coords.start = from_
        if to:
            submit_req.req.coords.stop = to

        return self.wait(self.__submit_request(submit_req))

    def __set_sequence(
            self,
            submit_req: cloudblast_pb2.SubmitRequest,
            seq_accession: str = None, verbatim_seq: str = None,
            fasta: str = None) -> None:
        """
        Set the sequence to search in a blast request;
        or throw an error if no sequence was provided by the user

        Parameters:
            submit_req (cloudblast_pb2.SubmitRequest): a request object to which
                       we set a sequence to search
            accession (str): the accession.version of the query sequence
            verbatim_seq (str): the verbatim (raw) sequence
            fasta(str): contains a sequence in FASTA format. The first line
                        must be a description line (defline)

        Returns:
            Nothing
        """
        if seq_accession:
            submit_req.req.seq_accession = seq_accession
        elif verbatim_seq:
            submit_req.req.verbatim_seq = verbatim_seq
        elif fasta:
            submit_req.req.fasta = fasta
        else:
            raise InvalidArgumentError(
                'You must specify a query sequence as one of the following\n'
                'sequence identifier (accession), '
                'bare sequence (verbatim_seq), '
                'or FASTA (fasta)')

    def __submit_request(self, req: cloudblast_pb2.SubmitRequest) -> str:
        """Submit a Blast search request to the API service

        Parameters:
            req (cloudblast_pb2.SubmitRequest): CloudBlast request object

        Returns:
            str: the job id of this search request
        """
        try:
            # TODO set optional parameters (only set required fields now)
            req.req.db_tag = self._db_tag
            req.req.program = self._program
            response = create_stub(self._host).SubmitSearch(
                req, self._timeout, metadata=self._metadata)
            return response.job_id
        except grpc.RpcError as e:
            handle_grpc_error(e)
        return ""

    def wait(self, job_id: str) -> SearchResult:
        """Waits until the result of a Blast search is available and return it.

        Parameters:
            job_id (str): the job id of the search request

        Returns:
            SearchResult: if the search job has completed, the search result
                will be returned; otherwise the method will wait. If the job id
                is invalid, an error is thrown
        """
        try:
            status = self.status(job_id)
            while status not in (Status.SUCCEEDED, Status.FAILED):
                time.sleep(self.__POLL_TIMEOUT)
                status = self.status(job_id)

        except grpc.RpcError as e:
            handle_grpc_error(e)

        return self.__result(job_id)

    def __result(self, job_id: str) -> SearchResult:
        """Get the result of a Blast search

        Parameters:
            job_id (str): the job id of the search request

        Returns:
            SearchResult: if the search job has completed, the search result
                will be returned; otherwise an error message will be
                returned.
        """
        req = cloudblast_pb2.ResultRequest()
        req.job_id = job_id
        result: SearchResult

        try:
            result = convert_resultreply(
                create_stub(self._host).Results(
                    req, self._timeout, metadata=self._metadata))

        except grpc.RpcError as e:
            handle_grpc_error(e)
        return result

    def status(self, job_id: str) -> Status:
        """Query the status of a Blast search job

        Parameters:
            job_id (str): the job id of a search request

        Returns:
            Status(enum): an object with the status of the job plus its id
        """
        req = cloudblast_pb2.StatusRequest()

        req.job_id.append(job_id)

        try:
            response = create_stub(self._host).GetStatus(
                req, self._timeout, metadata=self._metadata)

            status_reply = convert_status(response)

        except grpc.RpcError as e:
            handle_grpc_error(e)

        return status_reply.status[0].status
