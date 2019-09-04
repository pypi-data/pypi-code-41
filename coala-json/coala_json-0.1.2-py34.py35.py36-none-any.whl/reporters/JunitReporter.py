import datetime
from json import load

from coala_json.reporters.ResultReporter import ResultReporter


class JunitReporter(ResultReporter):
    """
    Contain methods to produce Junit test report from coala-json
    coala_json is coala output in json format, usually produced by
    running coala with --json option
    """

    def to_output(self):
        """
        Convert coala-json output to coala-junit test result report

        :return: junit test result report
        """

        timestamp = datetime.datetime.utcnow().isoformat()
        output_json = load(self.coala_json)['results']
        junit = ''
        for problems in output_json.values():
            for problem in problems:
                message = self.loader.extract_message(problem)
                affected_line = self.loader.extract_affected_line(problem)
                affected_col = self.loader.extract_affected_column(problem)
                testsuite_name = self.loader.extract_file(problem)
                testsuite_package = self.loader.extract_origin(problem)
                failures = self.loader.extract_errors(problems)
                testcase_name = self.loader.extract_error_code(message)
                error_message = "line: {}, Column: {}, {}".format(
                    affected_line, affected_col, message)
                junit += ('<testsuite package="{}" timestamp="{}" tests="{}" '
                          'failures="{}" name="{}">\n<testcase name="{}{}">\n'
                          '<failure message="{}"></failure>\n</testcase>\n'
                          '</testsuite>\n'.format(testsuite_package, timestamp,
                                                  failures, failures,
                                                  testsuite_name,
                                                  testsuite_package,
                                                  testcase_name,
                                                  error_message))
        if junit:
            head = '<?xml version="1.0" encoding="utf-8"?>\n<testsuites>\n'
            output = head + junit + '</testsuites>'
        else:
            output = ('<?xml version="1.0" encoding="utf-8"?>\n<testsuites>\n'
                      '<testsuite timestamp="{}" '
                      'tests="1" failures="0" name="coala">\n'
                      '<testcase time="0" name="None"></testcase>\n'
                      '</testsuite>\n'
                      '</testsuites>'.format(timestamp))
        return output
