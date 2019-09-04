import re

from coala_json.loader.JsonLoader import JsonLoader


class coalaJsonLoader(JsonLoader):
    """
    Contains method to extract data from coala-json
    """

    @staticmethod
    def sanitize(error_message):
        """
        Change HTML characters to character entity reference so that
        they are not mixed with XML tags

        :param: string that contains HTML characters
        :return: string with character entity references
        """
        mapping = {'\"': '&quot;', '<': '&lt;', '>': '&gt;'}
        for k, v in mapping.items():
            error_message = error_message.replace(k, v)
        return error_message

    @staticmethod
    def extract_error_code(error_message):
        """
        Return error code from error message or an empty string if
        no error code is found
        """
        try:
            pattern = re.search('[A-Z][0-9]{3,4}', error_message).group()
            return ' {}'.format(pattern)
        except AttributeError:
            return ''

    @staticmethod
    def extract_message(problem):
        return coalaJsonLoader.sanitize(problem['message'])

    @staticmethod
    def extract_raw_message(problem):
        return problem['message']

    @staticmethod
    def extract_affected_line(problem):
        if problem['affected_code']:
            return problem['affected_code'][0]['end']['line']

    @staticmethod
    def extract_affected_column(problem):
        if problem['affected_code']:
            return problem['affected_code'][0]['end']['column']

    @staticmethod
    def extract_file(problem):
        if problem['affected_code']:
            return problem['affected_code'][0]['file']

    @staticmethod
    def extract_origin(problem):
        return problem['origin'].split(" ")[0]

    @staticmethod
    def extract_severity(problem):
        return problem['severity']

    @staticmethod
    def extract_errors(problems):
        return len(problems)
