from coala_json.reporters.CheckstyleReporter import CheckstyleReporter
from coala_json.reporters.HtmlReporter import HtmlReporter
from coala_json.reporters.JunitReporter import JunitReporter
from coala_json.reporters.TapReporter import TapReporter


class ReporterFactory:
    """
    Use to generate instances of reporters
    """

    def __init__(self, loader, parser, input_file, args):
        self.loader = loader
        self.parser = parser
        self.input_file = input_file
        self.args = args

    def get_reporter(self):
        """
        Get reporter according to args if available else returns error.
        """
        if self.args.checkstyle:
            return CheckstyleReporter(self.loader, self.input_file)

        elif self.args.junit:
            return JunitReporter(self.loader, self.input_file)

        elif self.args.tap:
            return TapReporter(self.loader, self.input_file)

        elif self.args.table:
            return HtmlReporter(self.loader, self.input_file)

        else:
            return self.parser.error("Please check if a single output mode is"
                                     " specified correctly")
