from json import load

from coala_json.reporters.ResultReporter import ResultReporter


class TapReporter(ResultReporter):
    """
    Contain methods to produce TAP test report from coala-json.
    coala_json is coala output in json format, usually produced by
    running coala with --json option
    """

    def to_output(self):
        """
        Convert coala-json output to coala-TAP test result report

        :return: TAP test result report
        """

        output_json = load(self.coala_json)['results']
        report = ''
        tests = '1'
        for problems in output_json.values():
            for test_no, problem in enumerate(problems):
                file_name = self.loader.extract_file(problem)
                message = self.loader.extract_raw_message(problem)
                error_message = message.replace(':', ' -')
                severity = self.loader.extract_severity(problem)
                affected_line = self.loader.extract_affected_line(problem)
                affected_col = self.loader.extract_affected_column(problem)
                rule_id = self.loader.extract_error_code(message)
                tests = self.loader.extract_errors(problems)
                # severity 0 is for errors related to INFO, the coala-ci build
                # still passes
                status = 'ok' if severity == 0 else 'not ok'
                report += ('{} {} - {}\n  ---\n  message: {}\n  severity: '
                           '{}\n  data:\n    line: {}\n    column: {}\n    '
                           'ruleId:{}\n  ...\n'.format(status, test_no + 1,
                                                       file_name,
                                                       error_message, severity,
                                                       affected_line,
                                                       affected_col, rule_id))
        head = 'TAP version 13\n1..{}\n'.format(tests)
        if report:
            output = head + report
        else:
            output = head + 'ok 1 - coala\n...'
        return output
