from json import load

from coala_json.reporters.ResultReporter import ResultReporter


class CheckstyleReporter(ResultReporter):
    """
    Contain methods to produce Checkstyle test report from coala-json.
    coala_json is coala output in json format, usually produced by
    running coala with --json option
    """

    def to_output(self):
        """
        Convert coala-json output to coala-checkstyle test result report

        :return: checkstyle test result report
        """
        output_json = load(self.coala_json)['results']
        report = ''
        for problems in output_json.values():
            for problem in problems:
                """
                map RESULT_SEVERITY of coala to Checkstyle severity options
                coala: INFO = 0, NORMAL = 1, MAJOR = 2
                checkstyle options: error, warning, info, ignore
                """
                severity = self.loader.extract_severity(problem)
                severity_map = {0: 'info', 1: 'warning', 2: 'error'}
                message = self.loader.extract_message(problem)
                error_line = self.loader.extract_affected_line(problem)
                error_col = self.loader.extract_affected_column(problem)
                file_name = self.loader.extract_file(problem)
                source = self.loader.extract_origin(problem)
                error_code = self.loader.extract_error_code(message)
                report += ('<file name="{}">\n<error severity="{}" line="{}" '
                           'column="{}" message="{}" source="{} {}">\n</error>'
                           '\n</file>\n'.format(file_name,
                                                severity_map[severity],
                                                error_line, error_col, message,
                                                error_code, source))
        head = ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<checkstyle version="4.3">\n')
        output = head + report + '</checkstyle>\n'
        return output
