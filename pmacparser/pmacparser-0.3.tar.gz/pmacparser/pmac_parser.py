"""PMAC Parser

Library for parsing and running PMAC programs
"""

import numpy as np

from pygments.token import Number
from pmacparser.pmac_lexer import PmacLexer


class ParserError(Exception):

    """Parser error exception."""

    def __init__(self, message, token):
        super(ParserError, self).__init__()
        self.message = message
        self.line = token.line

    def __str__(self):
        return '[Line %s] %s' % (self.line, self.message)


class Variables(object):

    """Represents a PMAC Variable (I, M, P, Q)."""

    def __init__(self):
        self.variable_dict = {}

    def get_i_variable(self, var_num):
        """Return the value of the specified I variable."""
        return self.get_var('I', var_num)

    def get_p_variable(self, var_num):
        """Return the value of the specified P variable."""
        return self.get_var('P', var_num)

    def get_q_variable(self, var_num):
        """Return the value of the specified Q variable."""
        return self.get_var('Q', var_num)

    def get_m_variable(self, var_num):
        """Return the value of the specified M variable."""
        return self.get_var('M', var_num)

    def set_i_variable(self, var_num, value):
        """Set the value of the specified I variable."""
        self.set_var('I', var_num, value)

    def set_p_variable(self, var_num, value):
        """Set the value of the specified P variable."""
        self.set_var('P', var_num, value)

    def set_q_variable(self, var_num, value):
        """Set the value of the specified Q variable."""
        self.set_var('Q', var_num, value)

    def set_m_variable(self, var_num, value):
        """Set the value of the specified M variable."""
        self.set_var('M', var_num, value)

    def get_var(self, var_type, var_num):
        """Return the value of the specified variable type and number."""
        addr = '%s%s' % (var_type, var_num)
        if addr in self.variable_dict:
            result = self.variable_dict[addr]
        else:
            result = 0
        npvalue = np.array(result)
        return npvalue.astype(float)

    def set_var(self, var_type, var_num, value):
        """Set the value of the variable type and number with the value specified."""
        addr = '%s%s' % (var_type, var_num)
        self.variable_dict[addr] = value

    def populate_with_dict(self, dictionary):
        """Copy the input dictionary into the local variable dictionary."""
        self.variable_dict = dictionary.copy()

    def to_dict(self):
        """Return the variables as a dictionary."""
        return self.variable_dict


class PMACParser(object):

    """Parses a PMAC program, and runs an emulator for forward kinematic programs

    Uses the PMAC Lexer to tokenise a list of strings, and then parses the tokens,
    using an input dictionary or variables to evaluate the expressions in the code,
    populating a dictionary with the results of the program operations.
    It is a modification of the dls_pmacanalyse code developed by J Thompson.
    """

    def __init__(self, program_lines):
        self.lexer = PmacLexer()
        self.lines = program_lines
        self.lexer.lex(self.lines)
        self.variable_dict = Variables()
        self.if_level = 0
        self.while_level = 0
        self.while_dict = {}
        self.pre_process()

    def pre_process(self):
        """Evaluate and replace any Constants Expressions (e.g. 4800+17)."""
        token = self.lexer.get_token()
        while token is not None:
            if token.type == Number.ConstantExpression:
                token_text = str(token)
                token_text = token_text.replace("(", "")
                token_text = token_text.replace(")", "")
                tokens = token_text.split("+")
                int1 = int(tokens[0])
                int2 = int(tokens[1])
                val = int1 + int2
                token.set(str(val), token.line)
                token.type = Number

            token = self.lexer.get_token()
        self.lexer.reset()

    def parse(self, variable_dict):
        """Top level kinematic program parser."""
        self.variable_dict.populate_with_dict(variable_dict)

        token = self.lexer.get_token()
        while token is not None:
            if token == 'Q':
                self.parseQ()
            elif token == 'P':
                self.parseP()
            elif token == 'I':
                self.parseI()
            elif token == 'M':
                self.parseM()
            elif token == 'IF':
                self.parseIf()
            elif token == 'ELSE':
                self.parseElse(token)
            elif token in ('ENDIF', 'ENDI'):
                self.parseEndIf(token)
            elif token == 'WHILE':
                self.parseWhile(token)
            elif token in ('ENDWHILE', 'ENDW'):
                self.parseEndWhile(token)
            elif token in ('RETURN', 'RET'):
                self.parseReturn(token)
            else:
                raise ParserError('Unexpected token: %s' % token, token)
            token = self.lexer.get_token()

        self.lexer.reset()
        return self.variable_dict.to_dict()

    def parseM(self):
        """Parse an M expression - typically an assignment."""
        num = self.lexer.get_token()
        if num.is_int():
            num = num.to_int()
            token = self.lexer.get_token()
            if token == '=':
                val = self.parseExpression()
                self.variable_dict.set_m_variable(num, val)
            else:
                self.lexer.put_token(token)
                # Report M variable values (do nothing)
        else:
            raise ParserError('Unexpected statement: M %s' % num, num)

    def parseI(self):
        """Parse an I expression - typically an assignment."""
        num = self.lexer.get_token()
        if num.is_int():
            num = num.to_int()
            token = self.lexer.get_token()
            if token == '=':
                val = self.parseExpression()
                self.variable_dict.set_i_variable(num, val)
            else:
                self.lexer.put_token(token)
                # Report I variable values (do nothing)
        elif num == '(':
            num = self.parseExpression()
            self.lexer.get_token(')')
            token = self.lexer.get_token()
            if token == '=':
                val = self.parseExpression()
                self.variable_dict.set_i_variable(num, val)
            else:
                self.lexer.put_token(token)
                # Report I variable values (do nothing)
        else:
            raise ParserError('Unexpected statement: I %s' % num, num)

    def parseP(self):
        """Parse a P expression - typically an assignment."""
        num = self.lexer.get_token()
        if num.is_int():
            num = num.to_int()
            token = self.lexer.get_token()
            if token == '=':
                val = self.parseExpression()
                self.variable_dict.set_p_variable(num, val)
            else:
                self.lexer.put_token(token)
                # Report P variable values (do nothing)
        elif num == '(':
            num = self.parseExpression()
            self.lexer.get_token(')')
            token = self.lexer.get_token()
            if token == '=':
                val = self.parseExpression()
                self.variable_dict.set_p_variable(num, val)
            else:
                self.lexer.put_token(token)
                # Report P variable values (do nothing)
        else:
            self.lexer.put_token(num)
            # Do nothing

    def parseQ(self):
        """Parse a Q expression - typically an assignment."""
        num = self.lexer.get_token()
        if num.is_int():
            num = num.to_int()
            token = self.lexer.get_token()
            if token == '=':
                val = self.parseExpression()
                self.variable_dict.set_q_variable(num, val)
            else:
                self.lexer.put_token(token)
                # Report Q variable values (do nothing)
        elif num == '(':
            num = self.parseExpression()
            self.lexer.get_token(')')
            token = self.lexer.get_token()
            if token == '=':
                val = self.parseExpression()
                self.variable_dict.set_q_variable(num, val)
            else:
                self.lexer.put_token(token)
                # Report Q variable values (do nothing)
        else:
            self.lexer.put_token(num)
            # Do nothing

    def parseCondition(self):
        """Parse a condition, return the result of the condition."""
        has_parenthesis = True
        token = self.lexer.get_token()
        if token != '(':
            self.lexer.put_token(token)
            has_parenthesis = False

        value1 = self.parseExpression()
        token = self.lexer.get_token()
        comparator = token
        value2 = self.parseExpression()

        if comparator == '=':
            result = value1 == value2
        elif comparator == '!=':
            result = value1 != value2
        elif comparator == '>':
            result = value1 > value2
        elif comparator == '!>':
            result = value1 <= value2
        elif comparator == '<':
            result = value1 < value2
        elif comparator == '!<':
            result = value1 >= value2
        else:
            raise ParserError('Expected comparator, got: %s' % comparator, comparator)

        # Take ) or AND or OR
        token = self.lexer.get_token()
        if token == 'AND' or token == 'OR':
            self.lexer.put_token(token)
            result = self.parseConditionalOR(result)
            if has_parenthesis:
                self.lexer.get_token(')')
        elif token == ')':
            if not has_parenthesis:
                self.lexer.put_token(token)
        elif token != ')':
            raise ParserError('Expected ) or AND/OR, got: %s' % comparator, comparator)

        return result

    def parseConditionalOR(self, current_value):
        """Parse a conditional OR token, return the result of the condition."""
        result = self.parseConditionalAND(current_value)
        token = self.lexer.get_token()
        if token == 'OR':
            condition_result = self.parseCondition()
            result = self.parseConditionalOR(condition_result) or current_value
        elif token == 'AND':
            self.lexer.put_token(token)
            result = self.parseConditionalOR(result)
        else:
            self.lexer.put_token(token)

        return result

    def parseConditionalAND(self, current_value):
        """Parse a conditional AND token, return the result of the condition."""
        token = self.lexer.get_token()
        if token == 'AND':
            result = self.parseCondition() and current_value
        else:
            self.lexer.put_token(token)
            result = current_value
        return result

    def parseIf(self):
        """Parse an IF token, skipping to after the else if necessary."""
        condition = self.parseCondition()

        if_condition = self.parseConditionalOR(condition)

        # Condition could be numpy array, check and throw if not all True or all False
        if np.all(if_condition):
            if_condition = True
        elif not np.any(if_condition):
            if_condition = False
        else:
            raise Exception('If conditions is an array with not all the same value')

        self.if_level += 1
        if not if_condition:
            this_if_level = self.if_level
            token = self.lexer.get_token()
            while (token != 'ELSE' and token not in ('ENDIF', 'ENDI')) or this_if_level != self.if_level:
                if token in ('ENDIF', 'ENDI'):
                    self.if_level -= 1
                token = self.lexer.get_token()
                if token == 'IF':
                    self.if_level += 1

            if token in ('ENDIF', 'ENDI'):
                self.parseEndIf(token)

    def parseElse(self, token):
        """Parse an ELSE token, skipping to ENDIF if necessary."""
        if self.if_level > 0:
            this_if_level = self.if_level
            while token not in ('ENDIF', 'ENDI') or this_if_level != self.if_level:
                if token in ('ENDIF', 'ENDI'):
                    self.if_level -= 1

                token = self.lexer.get_token()

                if token == 'IF':
                    self.if_level += 1
        else:
            raise ParserError('Unexpected ELSE', token)

    def parseEndIf(self, t):
        """Parse an ENDIF token, closing off the current IF level."""
        if self.if_level > 0:
            self.if_level -= 1
        else:
            raise ParserError('Unexpected ENDIF/ENDI', t)

    def parseWhile(self, token):
        """Parse a WHILE token, skipping to the ENDWHILE the condition is false."""
        self.while_level += 1

        # Get all tokens up to the ENDWHILE
        while_tokens = []
        this_while_level = self.while_level
        while_tokens.append(token)

        while (token not in ('ENDWHILE', 'ENDW')) or this_while_level != self.while_level:
            if token in ('ENDWHILE', 'ENDW'):
                self.while_level -= 1

            token = self.lexer.get_token()
            while_tokens.append(token)

            if token == 'WHILE':
                self.while_level += 1

        # Put the tokens back on
        self.lexer.put_tokens(while_tokens)

        # Get the WHILE
        token = self.lexer.get_token()

        condition = self.parseCondition()

        condition = self.parseConditionalOR(condition)

        # Condition could be numpy array, check and throw if not all True or all False
        if np.all(condition):
            condition = True
        elif not np.any(condition):
            condition = False
        else:
            raise Exception('While conditions is an array with not all the same value')

        if condition:
            self.while_dict[this_while_level] = while_tokens
        else:
            while (token not in ('ENDWHILE', 'ENDW')) or this_while_level != self.while_level:
                if token in ('ENDWHILE', 'ENDW'):
                    self.while_level -= 1

                token = self.lexer.get_token()
                while_tokens.append(token)

                if token == 'WHILE':
                    self.while_level += 1
            self.while_level -= 1

    def parseEndWhile(self, t):
        """Parse an ENDWHILE statement, placing the tokens within the while back on to the list to be executed."""
        if self.while_level > 0:

            while_tokens = self.while_dict[self.while_level]

            # Put the tokens back on
            self.lexer.put_tokens(while_tokens)

            self.while_level -= 1
        else:
            raise ParserError('Unexpected ENDWHILE/ENDW', t)

    def parseReturn(self, t):
        """Parse a RETURN statement, which can just be ignored."""
        pass

    def parseExpression(self):
        """Return the result of the expression."""
        # Currently supports syntax of the form:
        #    <expression> ::= <e1> { <sumop> <e1> }
        #    <e1> ::= <e2> { <multop> <e2> }
        #    <e2> ::= [ <monop> ] <e3>
        #    <e3> ::= '(' <expression> ')' | <constant> | 'P'<integer> | 'Q'<integer> | 'I'<integer> | 'M' <integer>
        #                  | <mathop><float>
        #    <sumop> ::= '+' | '-' | '|' | '^'
        #    <multop> ::= '*' | '/' | '%' | '&'
        #    <monop> ::= '+' | '-'
        #    <mathop> ::= 'SIN' | 'COS' | 'TAB' | 'ASIN' | 'ACOS' | 'ATAN' | 'ATAN2'
        #                  | 'SQRT' | 'ABS' | 'EXT' | 'IN' | 'LN'
        result = self.parseE1()
        going = True
        while going:
            token = self.lexer.get_token()
            if token == '+':
                result = result + self.parseE1()
            elif token == '-':
                result = result - self.parseE1()
            elif token == '|':
                result = np.bitwise_or(np.array(result).astype(int), np.array(self.parseE1()).astype(int))
            elif token == '^':
                result = np.bitwise_xor(np.array(result).astype(int), np.array(self.parseE1()).astype(int))
            else:
                self.lexer.put_token(token)
                going = False
        return result

    def parseE1(self):
        """Return the result of a sub-expression containing multiplicative operands."""
        result = self.parseE2()
        going = True
        while going:
            token = self.lexer.get_token()
            if token == '*':
                result = result * self.parseE2()
            elif token == '/':
                result = result / self.parseE2()
            elif token == '%':
                result = result % self.parseE2()
            elif token == '&':
                result = np.bitwise_and(np.array(result).astype(int), np.array(self.parseE2()).astype(int))
            else:
                self.lexer.put_token(token)
                going = False
        return result

    def parseE2(self):
        """Return the result of a sub-expression containing monadic operands."""
        monop = self.lexer.get_token()
        if monop not in ['+', '-']:
            self.lexer.put_token(monop)
            monop = '+'
        result = self.parseE3()
        if monop == '-':
            result = -result
        return result

    def parseE3(self):
        """Return the result of a sub-expression containing a value.

        This could be an I,P,Q or M variable, or a constant or a
        parenthesised expression, or a mathematical operation.
        """
        token = self.lexer.get_token()
        if token == '(':
            result = self.parseExpression()
            self.lexer.get_token(')')
        elif token == 'Q':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = self.variable_dict.get_q_variable(value)
        elif token == 'P':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = self.variable_dict.get_p_variable(value)
        elif token == 'I':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = self.variable_dict.get_i_variable(value)
        elif token == 'M':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = self.variable_dict.get_m_variable(value)
        elif token == 'SIN':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            I15 = self.variable_dict.get_i_variable(15)
            if I15 == 0:
                value = np.radians(value)
            result = np.sin(value)
        elif token == 'COS':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            I15 = self.variable_dict.get_i_variable(15)
            if I15 == 0:
                value = np.radians(value)
            result = np.cos(value)
        elif token == 'TAN':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            I15 = self.variable_dict.get_i_variable(15)
            if I15 == 0:
                value = np.radians(value)
            result = np.tan(value)
        elif token == 'ASIN':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = np.arcsin(value)
            I15 = self.variable_dict.get_i_variable(15)
            if I15 == 0:
                result = np.degrees(result)
        elif token == 'ACOS':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = np.arccos(value)
            I15 = self.variable_dict.get_i_variable(15)
            if I15 == 0:
                result = np.degrees(result)
        elif token == 'ATAN':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = np.arctan(value)
            I15 = self.variable_dict.get_i_variable(15)
            if I15 == 0:
                result = np.degrees(result)
        elif token == 'ATAN2':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token

            # PMAC uses the value in Q0 as the cosine argument
            Q0 = self.variable_dict.get_q_variable(0)

            result = np.arctan2(value, Q0)
            I15 = self.variable_dict.get_i_variable(15)
            if I15 == 0:
                result = np.degrees(result)
        elif token == 'SQRT':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = np.sqrt(value)
        elif token == 'ABS':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = np.abs(value)
        elif token == 'EXP':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = np.exp(value)
        elif token == 'INT':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = np.floor(value)
        elif token == 'LN':
            token = self.lexer.get_token()
            if token == '(':
                value = self.parseExpression()
                self.lexer.get_token(')')
            else:
                value = token
            result = np.log(value)
        else:
            result = token.to_float()
        return result
