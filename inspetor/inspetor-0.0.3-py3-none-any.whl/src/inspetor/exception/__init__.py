from flask         import (request, jsonify)
from flask_restful import (Api, Resource)
import re
import logging

def json_response(data, code, headers={}):
    """Flask response with a JSON encoded body
    """
    headers['Server'] = 'Ingresse EventAPI/1.0.0'

    response = jsonify(data)

    response.status_code = code
    response.headers.extend(headers)

    return response

def get_exception_response(error):
    """Transform the Exception in a JSON ready for response

    Keyword arguments:
    error -- Exception
    """
    formatter = Error()
    response  = json_response(formatter.format(error), error.status_code)

    return response


def parse_integrity_error_message(error):
    """Parse IntegrityError message

    Keyword arguments:
    error -- IntegrityError
    """
    content = re.search('\((.*?)\)=\((.*?)\){1,}(.*)', str(error))

    if content:
        field       = content.group(1).title().replace('_', '')
        formatted   = ''.join([field[0].lower(), field[1:]])
        explanation = 'already exists' if ('already exists' in content.group(3)) else 'does not exist'

        return {
            'field'  : formatted,
            'value'  : content.group(2),
            'message': ' '.join([formatted, content.group(2), explanation]),
        }

    return None

class Error:
    def format(self, error):
        """Formats a Error Response Dict

        Keyword arguments:
        error -- api.exception.EventException
        """
        base            = self.__format_basic_format()
        base['code']    = error.code
        base['message'] = error.message
        base['info']    = error.payload

        return base

    def __format_basic_format(self):
        """Basic Response Dict
        """
        return {
            'code'   : None,
            'message': None,
            'info'   : None
        }

