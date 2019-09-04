from json import load

from coala_json.reporters.ResultReporter import ResultReporter


class HtmlReporter(ResultReporter):
    """
    Contain methods to produce Html test report from coala-json
    coala_json is coala output in json format, usually produced by
    running coala with --json option
    """

    def to_output(self):
        """
        Convert coala-json output to html table report

        :return: html table report
        """

        output_json = load(self.coala_json)['results']
        table = ('<html><head><title>Test Results Report</title></head><body>'
                 '<table border="1"><h2>Test Result Reports</h2><tr>'
                 '<th>Line</th><th>Column</th><th>Severity</th>'
                 '<th>Message</th><th>Origin</th><th>RuleID</th>'
                 '<th>File</th></tr>')
        for problems in output_json.values():
            for problem in problems:
                line = self.loader.extract_affected_line(problem)
                col = self.loader.extract_affected_column(problem)
                severity = self.loader.extract_severity(problem)
                message = self.loader.extract_message(problem)
                origin = self.loader.extract_origin(problem)
                ruleid = self.loader.extract_error_code(message)
                file = self.loader.extract_file(problem)
                table += ('<tr><td>{}</td><td>{}</td><td>{}</td>'
                          '<td>{}</td><td>{}</td><td>{}</td><td>{}</td>'
                          '</tr>'.format(line, col, severity, message, origin,
                                         ruleid, file))
        table += '</table></body></html>\n'
        return table
