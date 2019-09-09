"""PMAC Lexer

Token class and lexer class for tokenising a PMAC program
"""

from pygments.lexer import RegexLexer
from pygments.token import Punctuation, Whitespace, Error, Operator, Keyword, Name, Number


class PmacToken(object):

    """Represents a PMAC token."""

    def __init__(self, text=None):
        self.line = ''
        self.text = ''
        self.type = ''
        if text is not None:
            self.text = text

    def set(self, text, line):
        """Set the value and line number of the token."""
        self.text = text
        self.line = line

    def is_int(self):
        """Return true if the token is an integer."""
        return self.text.isdigit()

    def to_int(self):
        """Return the token as an integer."""
        return int(self.text)

    def is_float(self):
        """Return true if the token is a floating point number."""
        result = True
        if not self.is_int():
            result = True
            for char in self.text:
                if char not in '0123456789.':
                    result = False
        return result

    def to_float(self):
        """Return the token as a floating point number."""
        if self.is_int():
            result = self.to_int()
        elif self.is_float():
            result = float(self.text)
        else:
            raise Exception("Float expected, got: %s" % self, self)
        return result

    def __str__(self):
        """Return the token as a string."""
        return self.text

    def __eq__(self, other):
        """Check for equality."""
        return self.text == str(other)

    def __ne__(self, other):
        """Check for inequality."""
        return self.text != str(other)


class PmacLexer(RegexLexer):

    """Turn a list of strings into a PMAC Token list."""

    name = 'pmac'
    aliases = ['pmac']

    def __init__(self):
        super(PmacLexer, self).__init__()
        self.line = 0
        self.lexed_tokens = []
        self.pygment_tokens = []
        self.cur_token = 0
        self.token_list_length = 0

    tokens = {
        'root': [
            (r'[ \n]', Whitespace),
            (r'(IF|ELSE|ENDIF|ENDI|WHILE|ENDWHILE|ENDW|AND|OR)', Keyword.Conditional),
            (r'(ABS|EXP|INT|LN|SIN|COS|TAN|ASIN|ACOS|ATAN2|ATAN|SQRT)', Keyword.Math),
            (r'(RETURN|RET)', Keyword.Control),
            (r'P', Name.VariableP),
            (r'Q', Name.VariableQ),
            (r'I', Name.VariableI),
            (r'M', Name.VariableM),
            (r'\(\d+\+\d+\)', Number.ConstantExpression),
            (r'\d+(\.\d+)?', Number),
            (r'\d+(\.\d+)?', Number),
            (r'(!=)|(!<)|(!>)', Operator),
            (r'[-+/\\*=<>^|&%]', Operator),
            (r'[()]', Punctuation),
            (r'(DISABLE PLC|DIS PLC|DISABLE PLCC|DIS PLCC|DISPLAY|DISP|ENABLE PLC|'
             r'ENA PLC|ENABLE PLCC|ENA PLCC|LOCK|MACROAUXREAD|MXR|MACROAUXWRITE|MXW|'
             r'MACROMSTREAD|MMR|MACROMSTWRITE|MMW|MACROSLVREAD|MSR|MACROSLVWRITE|MSW|'
             r'PAUSE PLC|PAU PLC|RESUME PLC|RES PLC|SETPHASE|UNLOCK)', Error.InvalidPLC),
        ]
    }

    def lex(self, source):
        """Turn the source lines of code into the token list."""
        self.line = 0
        self.lexed_tokens = []
        self.cur_token = 0
        self.token_list_length = 0

        for source_line in source:
            self.line += 1
            # Strip comments from the ends of lines
            code = source_line.split(';', 1)[0].strip().upper()
            self.pygment_tokens = list(self.get_tokens(code))

            for pygment_token in self.pygment_tokens:
                if pygment_token[0] == Error:
                    raise Exception("Unrecognised Token: %s", str(pygment_token[1]))
                if pygment_token[0] != Whitespace:
                    token = PmacToken()
                    token.set(pygment_token[1], self.line)
                    token.type = pygment_token[0]
                    self.lexed_tokens.append(token)

            self.token_list_length = len(self.lexed_tokens)

    def get_token(self, should_be=None):
        """Return the first token and removes it from the list."""
        result = None
        # Skip any newline tokens unless they are wanted
        while self.cur_token < self.token_list_length and self.lexed_tokens[self.cur_token] == '\n':
            self.line += 1
            self.cur_token += 1
        # Get the head token
        if self.cur_token < self.token_list_length:
            result = self.lexed_tokens[self.cur_token]
            self.cur_token += 1
        # Is it the expected one
        if should_be is not None and not should_be == result:
            raise Exception('Expected %s, got %s' % (should_be, result), result)
        return result

    def put_token(self, token):
        """Put a token back onto the list"""
        if token is not None:
            self.cur_token -= 1

    def put_tokens(self, tokens):
        """Put a  list of tokens back on to the list"""
        self.cur_token -= len(tokens)

    def reset(self):
        """Reset the lexer back to the beginning of the list"""
        self.cur_token = 0
