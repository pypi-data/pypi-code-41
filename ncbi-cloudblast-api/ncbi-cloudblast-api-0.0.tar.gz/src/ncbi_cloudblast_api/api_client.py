from google.protobuf import empty_pb2
from google.protobuf.json_format import MessageToJson, MessageToDict
import grpc
from typing import Any, Dict, List

from ncbi.cloudblast.v1alpha import api_pb2 as cloudblast_pb2
from ncbi.cloudblast.v1alpha import blast_request_pb2
from ._common import (create_stub,
                      open_file,
                      handle_grpc_error,
                      VERBATIM_SEQ_ARG,
                      SEQ_ACCESSION_ARG,
                      InvalidArgumentError)


class APIClient:
    """

    A CloudBlast API client library.

    Provide the interface to get the list of supported databases,
    submit a search job, query for status and get search result.

    """

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

        self._metadata = []
        if self._api_key:
            self._metadata.append(('x-api-key', self._api_key))

        # Default
        self._db_tag = 'nt'
        self._program = blast_request_pb2.BlastRequest.BLASTN

        # TODO provide setters for Blast parameters

    @property
    def host(self):
        return self._host

    @property
    def api_key(self):
        return self._api_key

    @property
    def timeout(self):
        return self._timeout

    def search_by_seq_accession(self, seq_accession) -> str:
        """Submit a Blast search request by sequence id accession

        Parameters:
            seq_accession (str): the accession.version of the query sequence

        Returns:
            str: the job id of this search request

        """
        req = cloudblast_pb2.SubmitRequest()

        if not seq_accession:
            raise InvalidArgumentError(
                f'{SEQ_ACCESSION_ARG} must be specified')
        req.req.seq_accession = seq_accession

        return self.__submit_request(req)

    def search_by_seq_literal(self, verbatim_seq: str,
                              is_file: bool = False) -> str:
        """Submit a Blast search request by verbatim (raw) sequence

        Parameters:
        verbatim_seq (str): the verbatim (raw) sequence
        is_file(bool): when True, verbatim_seq is the file name that
            contains the sequence; when false, verbatim_seq is the
            sequence. (Default is False)

        Returns:
            str: the job id of this search request
        """
        req = cloudblast_pb2.SubmitRequest()

        if not verbatim_seq:
            raise InvalidArgumentError(
                f'{VERBATIM_SEQ_ARG} must be specified')

        if is_file:
            with open_file(verbatim_seq, 'r') as f:
                req.req.verbatim_seq = f.read()
        else:
            req.req.verbatim_seq = verbatim_seq

        return self.__submit_request(req)

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

    def status(self, job_ids: List[str]) -> Dict[str, str]:
        """Query the status of a Blast search job

        Parameters:
            job_id (str): the job id of a search request

        Returns:
            str: the status of the job

        """

        req = cloudblast_pb2.StatusRequest()

        req.job_id.extend(job_ids)

        try:
            response = create_stub(self._host).GetStatus(
                req, self._timeout, metadata=self._metadata)
            res = dict()
            for s in response.status:
                res[s.job_id] = cloudblast_pb2.StatusReply.Status.Name(
                    s.status)
            return res
        except grpc.RpcError as e:
            handle_grpc_error(e)

    def result(self, job_id: str) -> cloudblast_pb2.Resultset:
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

        try:
            return create_stub(self._host).Results(
                req, self._timeout, metadata=self._metadata)
        except grpc.RpcError as e:
            handle_grpc_error(e)

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
