#!/usr/bin/python3

# simple expression parser and evaluator
# Copyright 2016, 2019 Eric Smith <spacewar@gmail.com>
# SPDX-License-Identifier: GPL-3.0

# This program is free software: you can redistribute it and/or modify
# it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__version__ = '1.0.10'
__author__ = 'Eric Smith <spacewar@gmail.com>'

__all__ = ['__version__', '__author__',
           'M5Expr', 'UndefinedSymbol']           

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import sys
from typing import Callable, Dict, List, Union

from pyparsing import Combine, Forward, Literal, OneOrMore, Optional, \
    ParseException, ParserElement, ParseResults, StringEnd, Word, \
    ZeroOrMore, \
    infixNotation, oneOf, \
    alphas, alphanums, hexnums, nums, opAssoc

assert sys.version_info >= (3, 7, 0)


class UndefinedSymbol(Exception):
    def __init__(self, s):
        self.symbol = s
        super().__init__(f'Undefined symbol "{s}"')


class _RPNItem(ABC):
    @abstractmethod
    def eval(self, symtab: Dict[str, int]) -> int:
        pass

_IorRPN = Union[int, _RPNItem]

@dataclass
class _RPNInteger(_RPNItem):
    value: int

    def eval(self, symtab: Dict[str, int] = { }) -> int:
        return self.value

    def __str__(self):
        return str(self.value)

@dataclass
class _RPNIdentifier(_RPNItem):
    identifier: str

    def eval(self, symtab: Dict[str, int] = { }) -> int:
        if self.identifier not in symtab:
            raise UndefinedSymbol(self.identifier)
        return symtab[self.identifier]

    def __str__(self):
        return self.identifier

@dataclass
class _UnaryOp(_RPNItem):
    name: str
    op1: Union[_RPNItem, int]

    def eval(self, symtab: Dict[str, int] = { }) -> int:
        if isinstance(self.op1, _RPNItem):
            op1 = self.op1.eval(symtab)
        else:
            op1 = self.op1
        return {
            '+': lambda x: x,
            '-': lambda x: -x,
            '~': lambda x: ~x,
            '!': lambda x: not x,
        } [self.name] (op1)

    def __str__(self):
        return str(self.op1) + ' u' + self.name

@dataclass
class _BinaryOp(_RPNItem):
    name: str
    op1: Union[_RPNItem, int]
    op2: Union[_RPNItem, int]

    def eval(self, symtab: Dict[str, int] = { }) -> int:
        if isinstance(self.op1, _RPNItem):
            op1 = self.op1.eval(symtab)
        else:
            op1 = self.op1
        if isinstance(self.op2, _RPNItem):
            op2 = self.op2.eval(symtab)
        else:
            op2 = self.op2
        return {
            '+':  lambda x, y: x + y,
            '-':  lambda x, y: x - y,
            '*':  lambda x, y: x * y,
            '/':  lambda x, y: x // y,
            '&':  lambda x, y: x & y,
            '|':  lambda x, y: x | y,
            '^':  lambda x, y: x ^ y,
            '<<': lambda x, y: x << y,
            '>>': lambda x, y: x >> y,
        } [self.name] (op1, op2)

    def __str__(self):
        return ' '.join([str(x) for x in [self.op1, self.op2, self.name]])


# Convert pyparsing infixNotation output with multiple instances of same
# operator in one list into nested form.
# Based on:
#   https://web.archive.org/web/20151207073412/http://pyparsing.wikispaces.com:80/share/view/73472016
def _nest_operand_pairs(tokens: List[str]) -> List[_RPNItem]:
    tokensf = tokens[0]
    ret = ParseResults(tokensf[:3])
    remaining = iter(tokensf[3:])
    while True:
        next_pair = (next(remaining,None), next(remaining,None))
        if next_pair == (None, None):
            break
        ret = ParseResults([ret])
        ret += ParseResults(list(next_pair))
    return [ret]

def _infix_to_tree(pe: Union[int, str, ParseResults]) -> _RPNItem:
    if isinstance(pe, int):
        return _RPNInteger(pe)
    if isinstance(pe, str):
        return _RPNIdentifier(pe)
    assert isinstance(pe, ParseResults)
    assert 2 <= len(pe) <= 3
    if len(pe) == 2:
        return _UnaryOp(pe[0],
                        _infix_to_tree(pe[1]))
    return _BinaryOp(pe[1], 
                     _infix_to_tree(pe[0]),
                     _infix_to_tree(pe[2]))


class M5Expr:
    def __init__(self):
        ParserElement.enablePackrat()
        decimal_integer = Word(nums).setName('decimal integer') \
                          .setParseAction(lambda t: int(''.join(t)))

        hexadecimal_integer = Combine(Word(nums, hexnums) + Word('hH')) \
                              .setName('hexadecimal integer') \
                              .setParseAction(lambda t: int((''.join(t))[:-1], 16))

        identifier = Word(alphas, alphanums + '_@?') \
                     .setName('identifier')

        baseExpr = (hexadecimal_integer |
                    decimal_integer |
                    identifier
                   )
    
        operators = [
                      (oneOf('+ - ~ !'), 1, opAssoc.RIGHT, _nest_operand_pairs),
                      (oneOf('* /'),     2, opAssoc.LEFT,  _nest_operand_pairs),
                      (oneOf('+ -'),     2, opAssoc.LEFT,  _nest_operand_pairs),
                      (oneOf('<< >>'),   2, opAssoc.LEFT,  _nest_operand_pairs),
                      (oneOf('&'),       2, opAssoc.LEFT,  _nest_operand_pairs),
                      (oneOf('^'),       2, opAssoc.LEFT,  _nest_operand_pairs),
                      (oneOf('|'),       2, opAssoc.LEFT,  _nest_operand_pairs),
                    ]

        self._expr = infixNotation(baseExpr, operators) + StringEnd()

    def parse(self, s: str) -> _RPNItem:
        e = self._expr.parseString(s)[0]
        #print('before:', e)
        e = _infix_to_tree(e)
        #print('after:', e)
        return e

    def eval(self, s, symtab = { }) -> int:
        tree = self.parse(s)
        return tree.eval(symtab)


def main():
    ep = M5Expr()

    symtab = { 'a': 3,
               'b': 5 }

    while True:
        try:
            estr = input('> ')
        except EOFError:
            break
        tree = ep.parse(estr)
        print(str(tree))
        print(tree.eval(symtab))


if __name__ == '__main__':
    main()
