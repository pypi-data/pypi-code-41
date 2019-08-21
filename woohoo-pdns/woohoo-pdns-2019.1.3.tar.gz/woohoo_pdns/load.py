# -*- encoding: utf-8 -*-

import os
import logging
import json
import yaml
# import random

from collections import namedtuple
from dateutil import tz
from pathlib import Path
from datetime import datetime, timezone

from .meta import types
from .util import record_data, sanitise_input


class WoohooImportError(Exception):
    pass


class Importer:
    """
    Importers are used to import new data into the pDNS database.

    This is the super class for all importers. Different importers can import data from different sources. If no
    importer for a specific source is available, woohoo pDNS tries to make it simple to write a new importer for that
    particular source (format).

    The main method of an importer is :meth:`load_batch`. This method reads up to 'batch_size' records from the source,
    processes them into a list of record_data named tuples, adds some statistics and returns it.

    To access the source data it uses a :class:`Source` object. This object's job is to provide a single source record
    at a time to the importer. This can mean reading one or several lines from a file or a record from a Kafka topic or
    whatever produces a source record. The importer then processes this record (possibly into multiple entries, for
    example if the source record contained a single query that produced multiple answers).

    This base class handles the fetching of records from the source (up to a maximum of batch_size), calling the
    respective hooks (:meth:`_inspect_raw_record`, :meth:`_inspect_tokenised_record`, :meth:`_tokenise_record` and
    :meth:`_parse_tokenised_record`) which implement the actual logic for the importer (i.e. these are the methods that
    must be overridden in the child classes), minimal cleansing of the data and handling errors (including writing an
    error logfile).
    """
    load_batch_result = namedtuple("load_batch_result", ["converted", "loaded", "ignored", "records"])
    """A named tuple that is used to pass back some statistics as well as a list of ``record_data``"""
    ILLEGAL_CHARS = ["/", "\\", "&", ":"]
    """If any of these characters is present in ``rname`` the record will not be loaded as these characters are not
    expected in ``rrname`` (they can, however, be present in ``rdata``, for example in TXT records).
    """
    IGNORE_TYPES = [0]
    """DNS types that we want to ignore completely (0 for example does not exist)"""

    def __init__(self, source_name, data_timezone="UTC", strict=False, **kwargs):
        """
        Constructor for an importer.

        Args:
            source_name (str): A name that is passed to the source; can be a file name or directory name for a
                :class:`FileSource` or, for a hypothetical KafkaSource, it could be the name of the Kafka topic to use.
            data_timezone (str): The name of the timezone that should be used if the source data does not provide the
                timezone for the dates and times (first_seen, last_seen).
            strict (bool): If set to true, the importer will throw an exception if something 'odd' is encountered in
                in the source data. If it is set to false, the importer will write an entry in the error log and
                continue loading data.
            kwargs (kwargs): These are mainly to make this a "cooperative class" according to `super() considered
                super`_.

        .. super() considered super: https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
        """
        super().__init__()
        self._logger = logging.getLogger(__name__)

        self.error_filename = os.devnull
        self.source_name = source_name
        self.default_data_timezone = tz.gettz(data_timezone)
        self.strict = strict

        self.source = None
        self.src_config = None
        self._src_state = None
        self._src_has_more_data = True

    @property
    def has_more_data(self):
        """
        Indicating if the importer is (potentially) able to produce more data. Mainly means that the source can fetch
        at least one more record; does not include any validity check(s) of that data though.

        Returns:
            True if there is more source data available, false otherwise.
        """
        return self._src_has_more_data

    def load_batch(self, batch_size, max_failed_inarow=0):
        """
        The workhorse method of :class:`Importer`.

        The source object (self.source) will be initialised with its config (self.src_config) and for subsequent
        iterations the source's state will be restored (to what was returned by :class:`Source.state` in the last
        iteration).
        Then, records will be loaded until either no more data is available or 'batch_size' records are ready for
        loading into the database.

        For the first record in every batch, :meth:`_inspect_raw_record` and :meth:`_inspect_tokenised_record` will
        be called. For every record :meth:`_tokenise_record` and  :meth:`_parse_tokenised_record` are called.

        :meth:`_tokenise_record` is meant to be the place where filtering of source records can occur (return None).

        Args:
            batch_size (int): The maximum number of records to process at once.
            max_failed_inarow (int): The maximum number of records that fail to import in a row before aborting the
                processing of this batch.

        Returns:
            A load_batch_result named tuple. This contains some statistics and a list of record_data named tuples.
        """
        consecutive_fails = 0
        records_converted = 0
        records_loaded = 0
        records_ignored = 0
        records_to_load = []
        with self.source(self.src_config) as src:
            src.state = self._src_state
            while self.has_more_data:
                if records_converted < batch_size:
                    try:
                        rec_to_load = src.get_next_record()
                        if not rec_to_load:
                            self._src_has_more_data = False
                            break
                        if not records_loaded:
                            # this is the first record of a batch
                            self._inspect_raw_record(rec_to_load)
                        tokenised_data = self._tokenise_record(rec_to_load)
                        if tokenised_data:
                            for record in tokenised_data:
                                for t in Importer.IGNORE_TYPES:
                                    if t == record.rrtype:
                                        raise WoohooImportError(
                                            "Ignored rrtype '{}' found, ignoring input line".format(t))
                                for c in Importer.ILLEGAL_CHARS:
                                    if c in record.rrname:
                                        raise WoohooImportError(
                                            "Illegal character in rrname '{}', ignoring input line".format(c))
                            if not records_loaded:
                                # this is still the first record of a batch
                                self._inspect_tokenised_record(tokenised_data)
                            new_entries = self._parse_tokenised_record(tokenised_data)
                            for entry in new_entries:
                                if self._is_valid(entry):
                                    records_to_load.append(entry)
                            records_loaded += 1
                        else:
                            records_ignored += 1
                        records_converted += 1
                        consecutive_fails = 0  # we have successfully converted a record
                    except Exception as e:
                        consecutive_fails += 1
                        self._logger.error("Unexpected exception while importing (see error log): {}".format(e))
                        records_ignored += 1
                        err = {
                            "filename": str(src),
                            "loader": type(self).__name__,
                            "state": src.state,
                            "time": datetime.now(tz=self.default_data_timezone),
                            "error": e,
                            "data": rec_to_load,
                        }
                        with open(self.error_filename, "a") as err_fh:
                            err_fh.write(json.dumps(err, indent=4, default=str))
                            err_fh.write("\n")
                        if self.strict:
                            raise WoohooImportError(e)
                        elif max_failed_inarow and (consecutive_fails > max_failed_inarow):
                            msg_tmpl = "Failed to load '{}' records in a row, aborting."
                            self._logger.error(msg_tmpl.format(max_failed_inarow))
                            raise WoohooImportError(msg_tmpl.format(max_failed_inarow))
                else:
                    break
            self._src_state = src.state
        results = Importer.load_batch_result(records_converted, records_loaded, records_ignored, records_to_load)
        return results

    def _is_valid(self, entry):
        """
        Check if the given entry is considered to be valid.

        Entries with an empty rrname or rdata field are considered invalid, for example.

        Args:
            entry (record_data): the entry to check for validity.

        Returns:
            True if the entry passed validation, False otherwise.
        """
        is_valid = True
        if not entry.rrname or not entry.rdata:
            is_valid = False
        return is_valid

    def _inspect_raw_record(self, raw_record):
        """
        For the first record of every batch this method will be called and the raw record is passed to it. This can be
        used if 'something' must be determined from source data (e.g. the datetime format).

        Note:
            This is a NOP in :class:`Importer` and meant to be overridden by subclasses if required.

        Args:
            raw_record (str): the record as it was returned from the source object.

        Returns:
            Nothing.
        """
        pass

    def _inspect_tokenised_record(self, tokenised_rec):
        """
        For every record that was successfully tokenised (i.e. splitted into the required parts), this method will
        be called. Can be used to decide on further processing for example.

        Note:
            This is a NOP in :class:`Importer` and meant to be overridden by subclasses if required.

        Args:
            tokenised_rec (record_data): The record as it was tokenised by :meth:`_tokenise_record`.

        Returns:
            Nothing.
        """
        pass

    def _tokenise_record(self, rec):
        """
        After a raw record is read from the source object, this method is called and passed the raw record to split it
        into the parts required for a pDNS record.

        Note:
            This method must be implemened by the concrete subclasses of :class:`Importer`.

        Args:
            rec (str): The record as it was returned by the source object. This string must now be splitted into the
            different parts of a record_data named tuple.

        Returns:
            A record_data named tuple that represents the record to load or None if the record could not be parsed (or
            should be ignored).
        """
        raise NotImplementedError("_tokenise_record is not implemented in Importer")

    def _parse_tokenised_record(self, tokenised_rec):
        """
        After a record was tokenised, it is passed to this method for parsing (e.g. turn a unix timestamp into a
        datetime, or similar).

        Note:
            This method must be implemened by the concrete subclasses of :class:`Importer`.

        Args:
            tokenised_rec (record_data): The record as tokenised by :meth:`_tokenise_record`.

        Returns:
            A record_data named tuple representing the final record to load. The importer also works if this method or
            returns None (i.e. nothing is loaded in to the database and the loading process continues) but the record
            is still considered 'loaded' by the statistics.
        """
        raise NotImplementedError("_parse_tokenised_record is not implemented in Importer")


class FileImporter(Importer):
    """
    An abstract class to handle loading data from files.

    The 'source_name' can be a filename or a directory name on disk. If it is a file name, that file will be read. If it
    is a directory, all files matching the glob pattern in cfg["file_pattern"] will be read.
    An exception will be thrown if the file (or directory) does not exist).

    Note:
        Errors will be written to a file called like the source file, but with '_err' in the name (if 'source_name' is
        a file) or to a file in the parent directory of the directory to load files from, also with an '_err' in the
        name, if 'source_name' is a directory.

    Throws:
        FileNotFoundException if 'source_name' does not exist.
    """
    def __init__(self, source_name, cfg=None, **kwargs):
        """
        To correctly initialise a file source a config dict must be supplied (see 'cfg' argument documentation).

        Args:
            source_name (str): Either the name of a file to be read or the name of a directory to scan for files to
                load.
            cfg (dict): A config dictionary that contains the following two keys:
                * file_pattern (str): The glob pattern to use when reading files from a directory.
                * rename (bool): Whether or not files should be renamed (by appending '.1') after they are read.
        """
        super().__init__(source_name, **kwargs)

        try:
            self.file_pattern = cfg["file_pattern"]
        except KeyError:
            self.file_pattern = "*"
        try:
            self.rename = cfg["rename"]
        except KeyError:
            self.rename = True

        self.src_config = {
            "filename": self.source_name,
            "file_pattern": self.file_pattern,
            "rename": self.rename,
        }

        p = Path(self.source_name)
        if not p.suffix.lower() == ".json":
            err_fname = "{}{}{}.{}".format(p.stem, "_err", p.suffix, "json")
        else:
            err_fname = "{}{}{}".format(p.stem, "_err", p.suffix)

        self.source = FileSource

        self.error_filename = p.parent.joinpath(err_fname)
        self._logger.info("Logging errors to {}".format(self.error_filename))

    def _tokenise_record(self, rec):
        raise NotImplementedError("_tokenise_record is not implemented in FileImporter")

    def _parse_tokenised_record(self, tokenised_rec):
        raise NotImplementedError("_parse_tokenised_record is not implemented in FileImporter")


class SilkFileImporter(FileImporter):
    """
    Importer to read files produced by the SiLK security suite.

    Note:
        This is a subclass of :class:`FileImporter` as it reads data from files on disk. There are many ways to get
        the files, for example with `the 'rwsender' program`_ included in the SiLK suite.

    .. _the 'rwsender' program: https://tools.netsa.cert.org/silk/rwsender.html
    """
    def __init__(self, source_name, **kwargs):
        super().__init__(source_name, **kwargs)
        self.time_format = "%Y-%m-%d %H:%M:%S"
        self.source = SingleLineFileSource

    def _tokenise_record(self, rec):
        """
        Split a line into tokens::

            2019-05-13 18:12:44.374|2019-05-13 18:12:44.374|28|gateway.fe.apple-dns.net|1|2a01:b740:0a41:0603::0010

        becomes::

            tokens[0] = "2019-05-13 18:12:44.374"    # first_seen
            tokens[1] = "2019-05-13 18:12:44.374"    # last_seen
            tokens[2] = "28"                         # DNS type
            tokens[3] = "gateway.fe.apple-dns.net"   # rrname
            tokens[4] = "1"                          # hitcount
            tokens[5] = "2a01:b740:0a41:0603::0010"  # rdata

        respectively::

            entry.first_seen
            entry.last_seen
            entry.rrtype
            entry.rrname
            entry.hitcount
            entry.rdata

        Args:
            rec (str): A record returned from the source object.

        Returns:
            A single entry list of record_data named tuple.
        """
        tokens = rec.strip().split("|")

        try:
            first_seen = tokens[0]
            last_seen = tokens[1]
            rrtype = int(tokens[2])
            rrname = sanitise_input(tokens[3].strip())
            hitcount = int(tokens[4])
            rdata = sanitise_input(tokens[5].strip())
        except ValueError:
            return None

        entry = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        return [entry]

    def _parse_tokenised_record(self, tokenised_rec):
        """
        Mainly convert the date and time (strings) into aware datetime objects.

        Args:
            tokenised_rec (record_data): The record_data as tokenised by :meth:`_tokenise_record`

        Returns:
            A single element list of record_data named tuple.
        """
        rec = tokenised_rec[0]
        first_seen = datetime.strptime(rec.first_seen, self.time_format).replace(tzinfo=timezone.utc)
        last_seen = datetime.strptime(rec.last_seen, self.time_format).replace(tzinfo=timezone.utc)
        if len(rec.rrname) > 270 or len(rec.rdata) > 300:
            raise WoohooImportError("Record data too long (rrname > 270 or rdata > 300)")
        new_tokens = record_data(first_seen, last_seen, rec.rrtype, rec.rrname, rec.hitcount, rec.rdata, None)
        return [new_tokens]

    def _inspect_tokenised_record(self, tokenised_rec):
        """
        Sometimes, the time in the input as millisecond resolution (for the whole source file). If so, adjust the
        parsing format to account for this.

        Args:
            tokenised_rec (record_data): The record as tokenised by :meth:`_tokenise_record`.

        Returns:
            Nothing.
        """
        if not self.strict:
            rec = tokenised_rec[0]
            dtime_in = rec.first_seen
            try:
                datetime.strptime(dtime_in, self.time_format)
            except ValueError:
                msg_tmpl = "Input date/time is not in expected format ({}), trying alternative"
                self._logger.warning(msg_tmpl.format(self.time_format))
                time_format = "%Y-%m-%d %H:%M:%S.%f"
                datetime.strptime(dtime_in, time_format)
                self.time_format = time_format


class DNSLogFileImporter(FileImporter):
    """
    Importer capable of reading a different source file format (JSON based).
    """
    def __init__(self, source_name, **kwargs):
        super().__init__(source_name, **kwargs)
        self.source = SingleLineFileSource

    def _tokenise_record(self, rec):
        """
        Split a line into tokens::

            {"rrclass": "IN", "ttl": 3600, "timestamp": "1562845812", "rrtype": "PTR", "rrname": "24.227.156.213.in-addr.arpa.", "rdata": "mx2.mammut.ch.", "sensor": 37690}

        becomes::

            tokens[0] = "1562845812"                     # first_seen
            tokens[1] = "1562845812"                     # last_seen
            tokens[2] = "PTR"                            # DNS type
            tokens[3] = "24.227.156.213.in-addr.arpa."   # rrname
            tokens[4] = "1"                              # hitcount
            tokens[5] = "mx2.mammut.ch."                 # rdata

        respectively::

            entry.first_seen
            entry.last_seen
            entry.rrtype
            entry.rrname
            entry.hitcount
            entry.rdata

        Args:
            rec (str): A record returned from the source object.

        Returns:
            A single entry list of record_data named tuple.
        """

        try:
            j = json.loads(rec)
            first_seen = j["timestamp"]
            last_seen = j["timestamp"]
            rrtype = j["rrtype"]
            rrname = sanitise_input(j["rrname"])
            hitcount = 1
            rdata = sanitise_input(j["rdata"].strip())
        except ValueError:
            return None

        entry = record_data(first_seen, last_seen, rrtype, rrname, hitcount, rdata, None)
        return [entry]

    def _parse_tokenised_record(self, tokenised_rec):
        """
        Convert unix timestamps into aware datetime objects and convert string-type rrtype into their integer based
        pendants.

        Args:
            tokenised_rec (record_data): The record_data as tokenised by :meth:`_tokenise_record`

        Returns:
            A single element list of record_data named tuple.
        """
        rec = tokenised_rec[0]
        first_seen = datetime.fromtimestamp(int(rec.first_seen), tz=self.default_data_timezone)
        last_seen = datetime.fromtimestamp(int(rec.last_seen), tz=self.default_data_timezone)
        rrtype = types[rec.rrtype]
        if len(rec.rrname) > 270 or len(rec.rdata) > 300:
            raise WoohooImportError("Record data too long (rrname > 270 or rdata > 300)")
        new_tokens = record_data(first_seen, last_seen, rrtype, rec.rrname, rec.hitcount, rec.rdata, None)
        return [new_tokens]


class DNSTapFileImporter(FileImporter):
    """
    An importer capable of reading YAML based dnstap log files.
    """
    def __init__(self, source_name, **kwargs):
        super().__init__(source_name, **kwargs)
        self.time_format = "%Y-%m-%dT%H:%M:%SZ"
        self.source = YamlFileSource

    def _tokenise_record(self, rec):
        """
        Extract from YAML document::

            type: MESSAGE
            identity: dns.host.example.com
            version: BIND 9.11.3-RedHat-9.11.3-6.el7.centos
            message:
              type: RESOLVER_RESPONSE
              message_size: 89b
              socket_family: INET6
              socket_protocol: UDP
              query_address: 203.0.113.56
              response_address: 203.0.113.53
              query_port: 49824
              response_port: 53
              response_message_data:
                opcode: QUERY
                status: NOERROR
                id:  44174
                flags: qr aa
                QUESTION: 1
                ANSWER: 2
                AUTHORITY: 0
                ADDITIONAL: 0
                QUESTION_SECTION:
                  - clients6.google.com. IN AAAA
                ANSWER_SECTION:
                  - clients6.google.com. 300 IN CNAME clients.l.google.com.
                  - clients.l.google.com. 300 IN AAAA 2a00:1450:4002:807::200e
              response_message: |
                ;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id:  44174
                ;; flags: qr aa    ; QUESTION: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 0
                ;; QUESTION SECTION:
                ;clients6.google.com.       IN  AAAA

                ;; ANSWER SECTION:
                clients6.google.com.    300 IN  CNAME   clients.l.google.com.
                clients.l.google.com.   300 IN  AAAA    2a00:1450:4002:807::200e

        becomes::

            tokens[0] = "2018-06-18T19:22:56Z"   # first_seen
            tokens[1] = "2018-06-18T19:22:56Z"   # last_seen
            tokens[2] = "CNAME"                  # DNS type
            tokens[3] = "clients6.google.com."   # rrname
            tokens[4] = "1"                      # hitcount
            tokens[5] = "clients.l.google.com."  # rdata

        respectively::

            entry.first_seen
            entry.last_seen
            entry.rrtype
            entry.rrname
            entry.hitcount
            entry.rdata

        Args:
            rec (str): A record (YAML document as string) returned from the source object.

        Returns:
            A list of record_data named tuple.
        """
        entries = []
        try:
            y = yaml.safe_load(rec)
            first_seen = y["message"]["response_time"]
            last_seen = y["message"]["response_time"]
        except ValueError:
            return None

        for ans in y["message"]["response_message_data"]["ANSWER_SECTION"]:
            try:
                rrname, ttl, cls, rrtype, rdata = ans.split()
                entry = record_data(first_seen,
                                    last_seen,
                                    rrtype,
                                    sanitise_input(rrname),
                                    1,
                                    sanitise_input(rdata),
                                    None)
                entries.append(entry)
            except ValueError:
                return None

        return entries

    def _parse_tokenised_record(self, tokenised_rec):
        """
        Loop through all answers in the record and turn the datetimes into aware objects (using the default timezone).

        Args:
            tokenised_rec (record_data): The record_data as tokenised by :meth:`_tokenise_record`

        Returns:
            A list of record_data named tuple.
        """
        new_tokens_list = []
        for rec in tokenised_rec:
            self._logger.debug(("rec: {}".format(rec)))
            # first_seen = rec.first_seen.replace(tzinfo=timezone.utc)
            # last_seen = rec.last_seen.replace(tzinfo=timezone.utc)
            first_seen = rec.first_seen.replace(tzinfo=self.default_data_timezone)
            last_seen = rec.last_seen.replace(tzinfo=self.default_data_timezone)
            rrtype = types[rec.rrtype]
            rrname = rec.rrname
            rdata = rec.rdata
            if len(rec.rrname) > 270 or len(rec.rdata) > 300:
                raise WoohooImportError("Record data too long (rrname > 270 or rdata > 300)")
            new_tokens = record_data(first_seen, last_seen, rrtype, rrname, rec.hitcount, rdata, None)
            new_tokens_list.append(new_tokens)
        return new_tokens_list


class Source:
    """
    Source object(s) abstract the logic of fetching a 'single record' from a source.

    For files, this can mean reading one or several lines (e.g. a YAML document), for other sources (e.g. an imaginary
    Kafka source) this could mean querying a service or calling an API or ...
    """
    def __init__(self, config, **kwargs):
        """

        Args:
            config (dict): A dictionary that can hold data the source requires to configure itself.
            kwargs (kwargs): These are mainly to make this a "cooperative class" according to `super() considered
                super`_.

        .. super() considered super: https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
        """
        super().__init__(**kwargs)
        self._logger = logging.getLogger(__name__)
        self._config = config

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc_val, exc_tb):
        raise NotImplementedError

    @property
    def state(self):
        """
        A source can have 'state' which allows it to resume at the correct next record after a batch of data was
        processed.

        Note:
            Importers will request state from the source when a batch is about to be finished and will pass whatever
            the source provided back to the source before starting the next batch.

            For a source reading from a file this can for example mean to return the value of :meth:`tell` and then
            :meth:`seek` to this position when state is passed in again.
        """
        raise NotImplementedError

    @state.setter
    def state(self, value):
        raise NotImplementedError

    def get_next_record(self):
        """
        This method is called by the importer whenever it is ready to load the next record. What is returned will be
        passed into :meth:`Importer._tokenise_record`.

        Note:
            Subclasses must implement this method as it is not implemented here.

        Returns:
            A raw record from the source as string.
        """
        raise NotImplementedError


class FileSource(Source):
    """
    A source that reads data from files on disk.

    This source can either read a single file or scan a directory for files that match a glob pattern and process all
    matching files from the given directory. If the ``filename`` passed in is a file, this file will be processed. If
    ``filename`` is a directory, the glob pattern in ``file_pattern`` will be used to find files to process in that
    directory.

    If the optional configuration option ``rename`` is set to true (the default), :attr:`RENAME_APPENDIX` will be
    appended to the current file name after processing.

    Note:
        The config dictionary (``config``) must contain the following keys:

        * filename

        And the following keys are optional in the ``config`` dictionary:

        * file_pattern
        * rename
    """
    RENAME_APPENDIX = "1"
    """If files should be renamed after processing, this is what is appended to the current filename."""

    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        self.filename = self._config["filename"]
        self.file_pattern = self._config["file_pattern"]
        self.rename = self._config["rename"]
        self._file_list = []
        self._curr_filename = None
        self._fh = None

    def __enter__(self):
        p = Path(self.filename)
        if p.is_dir():
            self._file_list = list(p.glob(self.file_pattern))
            self._logger.info("File list: {}".format(self._file_list))
            try:
                self._curr_filename = self._file_list.pop()
            except IndexError:
                self._logger.warning("No files matching '{}' in directory '{}'".format(self.file_pattern, self.filename))
                self._curr_filename = None
                self._curr_file_has_more_data = False
        else:
            self._file_list = []
            self._curr_filename = self.filename

        try:
            self._fh = open(self._curr_filename, "r")
        except TypeError:
            # happens when there are no files that match file_pattern
            self._fh = open(os.devnull, "r")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fh:
            self._fh.close()

    def __str__(self):
        if self._fh:
            return self._fh.name
        elif self.filename:
            return self.filename
        else:
            return __name__

    @property
    def state(self):
        """
        Return a dictionary that describes the current state of the source.

        The setter of this property expects a dictionary that was created by this getter and then restores the state of
        the source to what it was when ``state`` was retrieved.

        Returns:
            A dictionary containing the current file list ``file_list`` (list of all files pending processing, excluding
            the current file), the name of the currently being processed file ``file_name`` and the offset (index) into
            the currently being processed file (as retrieved by :meth:`tell`).
        """
        try:
            idx = self._fh.tell()
        except ValueError:
            idx = 0
        state = {
            "file_list": self._file_list,
            "file_name": self._curr_filename,
            "file_idx": idx,
        }
        return state

    @state.setter
    def state(self, state):
        if state:
            self._file_list = state["file_list"]
            self._curr_filename = state["file_name"]
            idx = state["file_idx"]
            self._logger.debug("Seeking in file {} to position {}".format(self._curr_filename, idx))
            if self._curr_filename:
                if not self._fh.name == self._curr_filename:
                    self._fh.close()
                    self._fh = open(self._curr_filename, "r")
                self._fh.seek(idx)

    def get_next_record(self):
        raise NotImplementedError

    def _open_next_file(self):
        """
        Try to open the next file to process.

        First, the currently open file will be closed and renamed, if requested. After this, the next file in the list
        is opened (if any).

        Raises:
            :exc:`IndexError` if no files are left to process.

        Returns:
            Nothing.
        """
        self._fh.close()
        # self._curr_filename is None if no matching files were found in a folder
        if self._curr_filename and self.rename:
            curr_p = Path(self._curr_filename)
            filename_renamed = Path("{}.{}".format(curr_p, FileSource.RENAME_APPENDIX))
            self._logger.debug("Renaming {} to {}".format(curr_p, filename_renamed))
            curr_p.rename(filename_renamed)
        self._curr_filename = self._file_list.pop()
        self._fh = open(self._curr_filename, "r")


class SingleLineFileSource(FileSource):
    """A file source that reads a single line from a file at a time."""
    def get_next_record(self):
        """
        Read a single line from a source file (skipping empty lines).

        If no line is left, try to open the next file (if available) and read a line from there.

        Returns:
            see :meth:`FileSource.get_next_record`.
        """
        line = None
        while not line:
            line = self._fh.readline()
            if line:
                # we have read something, but it could be an empty line
                line = line.strip()
                if line:
                    # non-empty line
                    break
            else:
                # EOF
                try:
                    self._open_next_file()
                except IndexError:
                    # no more files to read
                    self._curr_filename = None
                    line = None
                    break
        return line


class YamlFileSource(FileSource):
    """Read a YAML document from a file on disk."""
    def get_next_record(self):
        line = None
        yaml_doc = ""
        while not line == "---":
            line = self._fh.readline()
            if line:
                if not line.strip() == "---":
                    # we have read something which is not a document separator
                    yaml_doc = "".join([yaml_doc, line])
                else:
                    break
            else:
                # EOF
                if yaml_doc:
                    # we have read the last document in the file
                    break
                else:
                    # we are trying to read something after the last document in the file
                    try:
                        self._open_next_file()
                        yaml_doc = ""
                    except IndexError:
                        # no more files to read
                        self._curr_filename = None
                        yaml_doc = None
                        break
        return yaml_doc
