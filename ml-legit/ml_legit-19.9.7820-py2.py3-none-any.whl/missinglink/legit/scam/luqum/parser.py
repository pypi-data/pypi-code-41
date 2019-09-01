# -*- coding: utf-8 -*-
"""The Lucene Query DSL parser based on PLY
"""

# see : https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html
# https://lucene.apache.org/core/3_6_0/queryparsersyntax.html
import logging
import ply.lex as lex
import ply.yacc as yacc
from .tree import *


class ParseError(ValueError):
    """Exception while parsing a lucene statement
    """
    pass


# the case of : which is used in date is problematic because it is also a delimiter
# lets catch those expressions appart
# Note : we must use positive look behind, because regexp engine is eager,
# and it's only arrived at ':' that it will try this rule
TIME_RE = r'''
    (?<=T\d{2}):  # look behind for T and two digits: hours
    \d{2}         # minutes
    (:\d{2})?     # seconds
'''
# this is a wide catching expression, to also include date math.
# Inspired by the original lucene parser:
# https://github.com/apache/lucene-solr/blob/master/lucene/queryparser/src/java/org/apache/lucene/queryparser/surround/parser/QueryParser.jj#L189
# We do allow the wildcards operators ('*' and '?') as our parser doesn't deal with them.

TERM_RE = r'''
(?P<term>  # group term
  (?:
   [^\s:^~(){{}}[\],\"'\\] # first char is not a space neither some char which have meanings
                             # note: escape of "-" and "]"
                             #       and doubling of "{{}}" (because we use format)
   |                         # but
   \\.                       # we can start with an escaped character
  )
  ([^\s:^\\~(){{}}[\]]       # following chars
   |                       # OR
   \\.                     # an escaped char
   |                       # OR
   {time_re}               # a time expression
  )*
)
'''.format(time_re=TIME_RE)
# phrase
PHRASE_RE = r'''
(?P<phrase>  # phrase
  "          # opening quote
  (?:        # repeating
    [^\\"]   # - a char which is not escape or end of phrase
    |        # OR
    \\.      # - an escaped char
  )*
  "          # closing quote
)'''


# r'(?P<phrase>"(?:[^\\"]|\\"|\\[^"])*")' # this is quite complicated to handle \"
# modifiers after term or phrase


class QueryParser(object):
    reserved = {
        'AND': 'AND_OP',
        'OR': 'OR_OP',
        'NOT': 'NOT',
        'TO': 'TO',
        '@SPLIT': 'SPLIT_FUNCTION'
    }

    # tokens of our grammar
    tokens = (['TERM', 'PHRASE', 'SEPARATOR', 'COLUMN', 'LPAREN', 'RPAREN', 'LBRACKET', 'RBRACKET', 'QUOTATION_MARK'] + sorted(list(reserved.values())))  # we sort to have a deterministic order, so that gammar signature does not changes

    # text of some simple tokens
    t_NOT = r'NOT'
    t_AND_OP = r'AND'
    t_OR_OP = r'OR'
    t_COLUMN = r':'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'(\[|\{)'
    t_RBRACKET = r'(\]|\})'
    t_QUOTATION_MARK = r'"'

    # precedence rules
    precedence = (
        ('left', 'OR_OP',),
        ('left', 'AND_OP'),
        ('nonassoc', 'LPAREN', 'RPAREN'),
        ('nonassoc', 'LBRACKET', 'TO', 'RBRACKET'),
        ('nonassoc', 'PHRASE'),
        ('nonassoc', 'TERM'),
    )

    def __init__(self, debug_mode=False, write_tables=True):
        logger = logging.getLogger('ply')

        if not debug_mode:
            logger.addHandler(logging.NullHandler())
            logger.disabled = True

        debug_log = logger
        error_log = logger

        self._parser = yacc.yacc(module=self, debug=debug_mode, write_tables=write_tables, errorlog=error_log, debuglog=debug_log)
        self._lexer = lex.lex(module=self)

    def parse(self, query, debug=False):
        return self._parser.parse(query, lexer=self._lexer, debug=debug)

    def t_SEPARATOR(self, t):
        r"""\s+"""
        pass  # discard separators

    @lex.TOKEN(TERM_RE)
    def t_TERM(self, t):
        # check if it is not a reserved term (an operation)
        t.type = self.reserved.get(str(t.value).upper(), 'TERM')
        # it's not, make it a Word
        if t.type == 'TERM':
            m = re.match(TERM_RE, t.value, re.VERBOSE)
            value = m.group("term")
            t.value = Word(value)

        return t

    @lex.TOKEN(PHRASE_RE)
    def t_PHRASE(self, t):
        m = re.match(PHRASE_RE, t.value, re.VERBOSE)
        value = m.group("phrase")
        t.value = Phrase(value)
        return t

    @classmethod
    def t_error(cls, t):  # pragma: no cover
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    @classmethod
    def p_expression_or(cls, p):
        """expression : expression OR_OP expression"""
        p[0] = create_operation(OrOperation, p[1], p[3])

    @classmethod
    def p_expression_not(cls, p):
        """expression : NOT expression"""
        p[0] = Not(p[2])

    @classmethod
    def p_expression_and(cls, p):
        """expression : expression AND_OP expression"""
        p[0] = create_operation(AndOperation, p[1], p[len(p) - 1])

    @classmethod
    def p_expression_implicit(cls, p):
        """expression : expression expression"""
        p[0] = create_operation(UnknownOperation, p[1], p[2])

    @classmethod
    def p_grouping(cls, p):
        """expression : LPAREN expression RPAREN"""
        p[0] = Group(p[2])  # Will p_field_search will transform as FieldGroup if necessary

    @classmethod
    def p_range(cls, p):
        """unary_expression : LBRACKET phrase_or_term TO phrase_or_term RBRACKET"""
        include_low = p[1] == "["
        include_high = p[5] == "]"
        p[0] = Range(p[2], p[4], include_low, include_high)

    @classmethod
    def p_expression_unary(cls, p):
        """expression : search_field"""
        p[0] = p[1]

    @classmethod
    def p_split_function_3(cls, p):
        """search_field : SPLIT_FUNCTION COLUMN unary_expression COLUMN unary_expression COLUMN unary_expression"""
        expr = Word('%s:%s:%s' % (p[3], p[5], p[7]))
        p[0] = SearchField(p[1], expr)

    @classmethod
    def p_split_function_2(cls, p):
        """search_field : SPLIT_FUNCTION COLUMN unary_expression COLUMN unary_expression"""
        expr = Word('%s:%s' % (p[3], p[5]))
        p[0] = SearchField(p[1], expr)

    @classmethod
    def p_split_function_1(cls, p):
        """search_field : SPLIT_FUNCTION COLUMN unary_expression"""
        expr = Word('%s' % p[3])
        p[0] = SearchField(p[1], expr)

    @classmethod
    def p_search_field(cls, p):
        """search_field : TERM COLUMN unary_expression"""
        if isinstance(p[3], Group):
            p[3] = group_to_fieldgroup(p[3])

        # for field name we take p[1].value for it was captured as a word expression
        p[0] = SearchField(p[1].value, p[3])

    @classmethod
    def p_phrases_or_terms(cls, p):
        """
        phrases_or_terms : phrases_or_terms phrase_or_term
        phrases_or_terms : phrase_or_term
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = create_operation(OrOperation, p[1], p[2])

    @classmethod
    def p_search_field_grouped(cls, p):
        """search_field : TERM COLUMN LPAREN phrases_or_terms RPAREN"""
        # for field name we take p[1].value for it was captured as a word expression
        if isinstance(p[4], Group):
            p[4] = group_to_fieldgroup(p[4])

        p[0] = SearchField(p[1].value, p[4])

    @classmethod
    def p_quoting(cls, p):
        """unary_expression : PHRASE"""
        p[0] = p[1]

    @classmethod
    def p_terms_quotation_mark(cls, p):
        """unary_expression : QUOTATION_MARK TERM QUOTATION_MARK"""
        p[0] = p[2]

    @classmethod
    def p_terms(cls, p):
        """unary_expression : TERM"""
        p[0] = p[1]

    # handling a special case, TO is reserved only in range
    @classmethod
    def p_to_as_term(cls, p):
        """unary_expression : TO"""
        p[0] = Word(p[1])

    @classmethod
    def p_phrase_or_term(cls, p):
        """phrase_or_term : TERM
                          | PHRASE"""
        p[0] = p[1]

    @classmethod
    def p_error(cls, p):
        if p is None:
            error_msg = "end of of query"
        else:
            error_msg = str(p.lexpos)

        full_error_msg = "Syntax error at %s" % error_msg
        raise ParseError(full_error_msg)


def parser(debug_mode=False, write_tables=True):
    return QueryParser(debug_mode=debug_mode, write_tables=write_tables)
