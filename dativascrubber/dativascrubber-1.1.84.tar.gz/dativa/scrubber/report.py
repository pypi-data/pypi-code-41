# (c) 2012-2018 Dativa, all rights reserved
# -----------------------------------------
#  This code is licensed under MIT license (see license.txt for details)

import datetime
import pandas as pd
from dativa.tools.pandas import CSVHandler
import json


class ReportEntry:
    """
    An individual report entry.

    Parameters
    ----------
    rule: the name of the rule that produced this entry
    field: the field being processed when the entry was produced
    df: the DataFrame containing the invalid records
    category: the type of entry, one of:
        HistoryCategory.IGNORED - the records were not altered
        HistoryCategory.REPLACED - the records were replaced with other values
        HistoryCategory.REMOVED - the records have been removed
        HistoryCategory.MODIFIED - the records have been modified
        HistoryCategory.INSERTED - new records have been inserted
    description: a textual description of the changes made (if any)
    """

    date = ""
    field = ""
    df = None
    category = ""
    description = ""
    number_records = ""

    def __init__(self, rule, field, df, category, description):
        self.date = datetime.datetime.now()
        self.field = field
        self.df = pd.DataFrame(df)
        self.number_records = df.shape[0]
        self.category = category
        self.description = description
        self.rule = rule

    def __str__(self):
        return "{0}, Field {1}({2}): #{3} {4}/|{5}".format(self.date,
                                                           self.field,
                                                           self.rule,
                                                           self.number_records,
                                                           self.category,
                                                           self.description)

    def get_log_dict(self):
        """
        Returns a dict containing the log entries
        """
        return {"date": self.date,
                "field": self.field,
                "rule": self.rule,
                "number_records": self.number_records,
                "category": self.category,
                "description": self.description}

    def get_records(self):
        """
        returns the DataFrame containing the values
        """
        return self.df


class DefaultReportWriter:
    """
    A default implementation of the ReportWriter that stores ReportEntries
    and returns them.
    """

    report = []

    def reset_report(self):
        self.report = []

    def log_history(self,
                    rule,
                    field,
                    df,
                    category,
                    description
                    ):
        """
        Logs a report entry
        """

        assert isinstance(df, pd.DataFrame), "df passed to log_history is not a DataFrame"

        self.report.append(ReportEntry(rule=rule,
                                       field=field,
                                       df=df,
                                       category=category,
                                       description=description
                                       ))

        return

    def get_report(self):
        """
        Returns an array of all ReportEntries created
        """
        return self.report


class PersistentFieldLogger:

    def __init__(self, logger, persistent_fields):
        self.logger = logger
        self.persistent_fields = persistent_fields

    def _get_args(self, **kwargs):
        args = self.persistent_fields.copy()
        for arg in kwargs:
            if arg in self.persistent_fields:
                self.persistent_fields[arg] = kwargs[arg]
            args[arg] = kwargs[arg]

        return args

    def debug(self, **kwargs):
        self.logger.debug(json.dumps(self._get_args(**kwargs)))

    def info(self, **kwargs):
        self.logger.info(json.dumps(self._get_args(**kwargs)))

    def warning(self, **kwargs):
        self.logger.warning(json.dumps(self._get_args(**kwargs)))

    def error(self, **kwargs):
        self.logger.error(json.dumps(self._get_args(**kwargs)))


class LoggingReportWriter(DefaultReportWriter):
    """
    A class to log all reports to the python log file
    """

    def __init__(self, logger, quarantine_path, error_severities=None, warning_severities=None):
        self.logger = logger
        self.csv = CSVHandler(base_path=quarantine_path)
        self.error_severities = [] if error_severities is None else error_severities
        self.warning_severities = [] if warning_severities is None else warning_severities

    def log_history(self,
                    rule,
                    field,
                    df,
                    category,
                    description
                    ):
        """
        Logs out the report details and saves the dataframe to the specified path
        """

        if df is not None and df.shape[0] > 0:
            filename = "{field}-{rule}-{date:%Y%m%d%H%M%S}.csv".format(
                field=field,
                rule=rule,
                date=datetime.datetime.now()).lower()
            self.csv.save_df(df, filename)

            if type(self.logger) is PersistentFieldLogger:
                if category in self.error_severities:
                    self.logger.error(category=category,
                                      field=field,
                                      description=description,
                                      filename=filename,
                                      number=df.shape[0])
                elif category in self.warning_severities:
                    self.logger.warning(category=category,
                                        field=field,
                                        description=description,
                                        filename=filename,
                                        number=df.shape[0])
                else:
                    self.logger.info(category=category,
                                     field=field,
                                     description=description,
                                     filename=filename,
                                     number=df.shape[0])
            else:
                message = "{category}: #{number} from {field} : {description} [{filename}]".format(
                    category=category,
                    field=field,
                    description=description,
                    filename=filename,
                    number=df.shape[0]
                )

                if category in self.error_severities:
                    self.logger.error(message)
                elif category in self.warning_severities:
                    self.logger.warning(message)
                else:
                    self.logger.info(message)
