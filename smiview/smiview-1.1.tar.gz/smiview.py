# Command-line program to view some of the syntax of a SMILES string

# Copyright Andrew Dalke, Andrew Dalke Scientific AB (Sweden), 2018
# and distributed under the "MIT license", as follows:
# ============================================================
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# ============================================================


from __future__ import print_function

import re
import sys
from collections import defaultdict
import argparse

__version__ = "1.1"
__version_info__ = (1, 1, 0)


class ASCIISymbols:
    nw_corner = "{("  # these three alternate
    e_side = "{("
    sw_corner = "{("
    single_row = "["
    left_closure = "%"
    right_closure = "%"
    left_closure_atom = "*"
    right_closure_atom = "*"
    open_branch = "("
    close_branch = ")"
    in_branch = "."

class UnicodeSymbols:
    nw_corner = u"\U0000250C"
    e_side = u"\U00002502"
    sw_corner = u"\U00002514"
    single_row = "["
    left_closure = u"\U00002191"
    right_closure = u"\U00002191"
    left_closure_atom = "*"
    right_closure_atom = "*"
    open_branch = "("
    close_branch = ")"
    in_branch = "."
    
# Very hacky way to handle alternating track edge indicators for
# ASCII mode.
def _get_special_symbols(symbols, counter):
    class SpecialSymbols:
        pass
    for attr in ("nw_corner", "e_side", "sw_corner", "single_row"):
        s = getattr(symbols, attr)
        n = len(s)
        c = s[counter % n]
        setattr(SpecialSymbols, attr, c)
    return SpecialSymbols
    

_tokenizer = re.compile(r"""

(?P<atom>
  \*|
  Cl|Br|[cnospBCNOFPSI]|  # organic subset
  \[[^]]+\]               # bracket atom
) |
(?P<bond>
  [=#$/\\:~-]
) |
(?P<closure>
  [0-9]|          # single digit
  %[0-9][0-9]|    # two digits
  %\([0-9]+\)     # more than two digits
) |
(?P<open_branch>
  \(
) |
(?P<close_branch>
  \)
) |
(?P<dot>
  \.
)

""", re.X).match

states = {
    "start": ("atom",),

    # CC, C=C, C(C)C, C(C)C, C.C, C1CCC1
    "atom": ("atom", "bond", "close_branch", "open_branch", "dot", "closure"),

    # C=C, C=1CCC=1
    "bond": ("atom", "closure"),

    # C(C)C, C(C)=C, C(C).C, C(C(C))C, C(C)(C)C
    "close_branch": ("atom", "bond", "dot", "close_branch", "open_branch"),

    # C(C), C(=C), C(.C) (really!)
    "open_branch": ("atom", "bond", "dot"),

    # C.C
    "dot": ("atom",),

    # C1CCC1, C1=CCC1, C12CC1C2, C1C(CC)1, C1(CC)CC1, c1ccccc1.[NH4+]
    "closure": ("atom", "bond", "closure", "close_branch", "open_branch", "dot"),
}

class Token(object):
    def __init__(self, index, state, term, start, end):
        self.index = index
        self.state = state
        self.term = term
        self.start = start
        self.end = end
    def __repr__(self):
        return "Token(%d, %r, %r, %d, %d)" % (
            self.index, self.state, self.term, self.start, self.end)

def _format_state(state):
    if state == "open_branch":
        return "open branch"
    elif state == "close_branch":
        return "close branch"
    return state
def _format_states(states):
    states = [_format_state(state) for state in states]
    if len(states) > 2:
        states[-2:] = ["%s, or %s" % (states[-2], states[-1])]
    return ", ".join(states)
def _format_indefinite(s):
    if s[:1] in "aeiou":
        return "n " + s
    return " " + s

class ParseError(Exception):
    location_msg = "Problem is here"
    def __init__(self, reason, smiles, offset):
        self.reason = reason
        self.smiles = smiles
        self.offset = offset
        
    def __str__(self):
        return self.reason

    def advice(self):
        return ""
    
    def explain(self, prefix="", width=60):
        lines = []
        smiles = self.smiles
        if smiles is None or self.offset is None:
            return ""
        n = len(smiles)
        i = 0
        while i < n:
            lines.append(prefix + smiles[i:i+width] + "\n")
            j = i+width
            if i <= self.offset < j:
                delta = self.offset-i
                errmsg = self.location_msg
                if delta < (len(errmsg) + 4):
                    msg = prefix + " "*delta + "^ " + errmsg + "\n"
                else:
                    msg = prefix + " "*(delta - len(errmsg) - 1) + errmsg + " ^\n"
                lines.append(msg)
            i += width
        return "".join(lines)

class TokenizeError(ParseError):
    location_msg = "Tokenizing stopped here"
    def __init__(self, reason, smiles, offset, state, expected_states):
        super(TokenizeError, self).__init__(reason, smiles, offset)
        self.state = state
        self.expected_states = expected_states

    def advice(self):
        return "A%s must be followed by a%s." % (
            _format_indefinite(_format_state(self.state)),
            _format_indefinite(_format_states(self.expected_states))
            )
        
def tokenize(smiles):
    current_state = "start"
    n = len(smiles)
    start = 0
    index = 0
    while start < n:
        #print("loop from", current_state)
        expected = states[current_state]
        m = _tokenizer(smiles, start)
        if m is None:
            raise TokenizeError("Unexpected syntax", smiles, start, current_state, expected)
        
        for next_state in expected:
            term = m.group(next_state)
            if term:
                end = m.end(next_state)
                break
        else:
            raise TokenizeError("Unexpected term", smiles, start, current_state, expected)

        yield Token(index, next_state, term, start, end)
        index += 1
        current_state = next_state
        start = end

def _parse_closure(term):
    n = len(term)
    if n == 1:
        return int(term)
    elif n == 3:
        return int(term[1:])
    else:
        return int(term[2:-1])

class Closure(object):
    def __init__(self, closure_id,
                 first_atom_index, first_closure_index,
                 second_atom_index, second_closure_index,
                 bond_type):
        self.closure_id = closure_id
        self.first_atom_index = first_atom_index
        self.first_closure_index = first_closure_index
        self.second_atom_index = second_atom_index
        self.second_closure_index = second_closure_index
        self.bond_type = bond_type
    
def match_closures(tokens, smiles):
    closure_table = {}
    atom = None
    for token in tokens:
        if token.state == "atom":
            atom = token
            bond_token = None
        elif token.state == "bond":
            bond_token = token
        elif token.state == "closure":
            closure = _parse_closure(token.term)
            if closure in closure_table:
                prev_atom, prev_closure, prev_bond_token = closure_table[closure]
                if prev_bond_token is None:
                    if bond_token is None:
                        bond_type = None
                    else:
                        bond_type = bond_token.term
                elif bond_token is None:
                    bond_type = prev_bond_token.term
                else:
                    if bond_token.term != prev_bond_token.term:
                        raise ParseError(
                            "Mismatch in closure bond type. Expecting %r or unspecified."
                            % (prev_bond_token.term,), smiles, bond_token.start)
                    bond_type = prev_bond_token.term
                    
                yield Closure(closure, prev_atom.index, prev_closure.index,
                              atom.index, token.index, bond_type)
                del closure_table[closure]
            else:
                closure_table[closure]  = (atom, token, bond_token)
            bond_token = None
        else:
            bond_token = None
            
    if closure_table:
        pair = min(closure_table.values(), key = lambda pair: pair[1].start)
        raise ParseError("Unclosed closure", smiles, pair[1].start)

class GraphAtom(object):
    def __init__(self, index, token):
        self.index = index
        self.token = token
        self.bond_indices = []
        self.neighbor_indices = []
        
class GraphBond(object):
    def __init__(self, index, token):
        self.index = index
        self.token = token
        self.atom_indices = []
        
class Graph(object):
    def __init__(self, atoms, bonds):
        self.atoms = atoms
        self.bonds = bonds
    def dump(self):
        print("%d atom %d bonds" % (len(self.atoms), len(self.bonds)))
        for atom in self.atoms:
            if atom.token is None:
                term = None
            else:
                term = atom.token.term
            print("%d %r %r" % (atom.index, term, atom.bond_indices))
        for bond in self.bonds:
            print("%d %r %r" % (bond.index, bond.atom_indices, bond.token))

# I wanted to include "fragments" in the default output.
# I don't want to require RDKit by default, because I want
# this code to work even if RDKit isn't available.
# Which means I can't use Chem.GetMolFrags(). 
# So I'll make my own. Which means I need a graph-like object.
# Here it is.
def make_graph(tokens):
    closure_table = {}
    prev_graph_atom = None
    prev_bond_token = None
    branch_stack = []
    
    graph_atoms = []
    graph_bonds = []
    
    for token in tokens:
        if token.state == "atom":
            graph_atom = GraphAtom(len(graph_atoms), token)
            graph_atoms.append(graph_atom)
            
            if prev_graph_atom is not None:
                # Then there is a bond, either implicit (prev_bond_token is
                # None) or explicit
                new_bond_index = len(graph_bonds)
                graph_bond = GraphBond(new_bond_index, prev_bond_token)
                graph_bonds.append(graph_bond)
                
                prev_graph_atom.bond_indices.append(new_bond_index)
                graph_atom.bond_indices.append(new_bond_index)
                graph_bond.atom_indices.append(prev_graph_atom.index)
                graph_bond.atom_indices.append(graph_atom.index)

            prev_graph_atom = graph_atom
            prev_bond_token = None
                    
        elif token.state == "bond":
            prev_bond_token = token

        elif token.state == "dot":
            prev_graph_atom = None
            prev_bond_token = None

        elif token.state == "open_branch":
            assert prev_graph_atom is not None, "branch without previous atom?"
            assert prev_bond_token is None, "how did a bond get before the '('?"
            branch_stack.append(prev_graph_atom)

        elif token.state == "close_branch":
            assert prev_bond_token is None, "how did a bond get before the ')'?"
            if branch_stack:
                prev_graph_atom = branch_stack.pop()
            # Ignore an empty stack. It should be caught in match_branches()

        elif token.state == "closure":
            assert prev_graph_atom is not None, "closure without previous atom?"
            closure = _parse_closure(token.term)
            if closure in closure_table:
                closure_graph_atom, closure_graph_bond = closure_table.pop(closure)
                if closure_graph_bond.token is None:
                    closure_graph_bond.token = prev_bond_token
                    # match_closures already verified that the bond types were correct
                # Fill in the other half of the bond
                prev_graph_atom.bond_indices.append(closure_graph_bond.index)
                closure_graph_bond.atom_indices.append(prev_graph_atom.index)
            else:
                # Make a 1/2 bond
                new_bond_index = len(graph_bonds)
                graph_bond = GraphBond(new_bond_index, prev_bond_token)
                graph_bonds.append(graph_bond)
                graph_atom.bond_indices.append(new_bond_index)
                graph_bond.atom_indices.append(graph_atom.index)
                closure_table[closure] = graph_atom, graph_bond
            prev_bond_token = None
        else:
            raise AssertionError(("Unknown token", token))

    # Fill in the missing closures with unspecified atoms
    # (Shouldn't happen if match_closures() did it's job.)
    for closure, (graph_atom, graph_bond) in closure_table.items():
        new_atom_index = len(graph_atoms)
        new_graph_atom = GraphAtom(new_atom_index, None)
        graph_atoms.append(new_graph_atom)
        new_graph_atom.bond_indices.append(graph_bond.index)
        graph_bond.atom_indices.append(new_atom_index)

    # fill in the atom neighbors
    for graph_atom in graph_atoms:
        neighbor_indices = graph_atom.neighbor_indices
        for bond_index in graph_atom.bond_indices:
            graph_bond = graph_bonds[bond_index]
            assert len(graph_bond.atom_indices) == 2
            if graph_bond.atom_indices[0] == graph_atom.index:
                neighbor_indices.append(graph_bond.atom_indices[1])
            else:
                neighbor_indices.append(graph_bond.atom_indices[0])
            
    return Graph(graph_atoms, graph_bonds)


def make_layout(smiles, need_mol=True, sanitize=True, special_symbols=UnicodeSymbols):
    if need_mol:
        from rdkit import Chem
        # Disable sanitizing here to preserve hydrogens.
        # RDKit be default will turn "[H]C" into "C".
        mol = Chem.MolFromSmiles(smiles, sanitize=False)
        if mol is None:
            raise ParseError("RDKit cannot parse the SMILES", smiles, None)
        if sanitize:
            Chem.SanitizeMol(mol)
        else:
            # Don't modify bond orders or charges, which can (e.g.)
            # happen around nitro groups.
            Chem.SanitizeMol(mol,Chem.SANITIZE_ALL^Chem.SANITIZE_CLEANUP^Chem.SANITIZE_PROPERTIES)      
    else:
        mol = None


    tokens = list(tokenize(smiles))
    atoms = [token for token in tokens if token.state == "atom"]
    closures = list(match_closures(tokens, smiles))
    branches = list(match_branches(tokens, smiles))

    graph = make_graph(tokens)
    fragments = get_mol_frags(graph)
    #graph.dump()
    
    layout = Layout(
        smiles, mol, tokens, atoms, closures, branches,
        graph, fragments,
        special_symbols=special_symbols)
    layout.add_above(0, smiles)
    layout.end_track("above", "SMILES")
    return layout

def get_mol_frags(graph):
    graph_atoms = graph.atoms
    graph_bonds = graph.bonds
    
    seen = set()
    fragments = []
    
    for graph_atom in graph_atoms:
        seed = graph_atom.index
        if seed in seen:
            continue
        fragment = [seed]
        stack = [seed]
        seen.add(seed)
        
        while stack:
            atom_idx = stack.pop()
            for neighbor_idx in graph_atoms[atom_idx].neighbor_indices:
                if neighbor_idx in seen:
                    continue
                fragment.append(neighbor_idx)
                stack.append(neighbor_idx)
                seen.add(neighbor_idx)
        fragments.append(tuple(fragment))
    return tuple(fragments)

## def verify_get_mol_frags():
##     from rdkit import Chem
##     filename = "/Users/dalke/databases/chembl_23.rdkit.smi"
##     with open(filename) as infile:
##         for lineno, line in enumerate(infile):
##             if lineno % 1000 == 0:
##                 sys.stderr.write("Processed %d lines.\n" % (lineno,))
##             try:
##                 smiles, id = line.split()
##             except ValueError:
##                 print
##             try:
##                 tokens = list(tokenize(smiles))
##             except ParseError as err:
##                 msg = "Cannot parse SMILES\n"
##                 msg += err.explain(prefix="  ")
##                 msg += err.advice()
##                 print(msg)
##                 continue
            
##             graph = make_graph(tokens)
##             my_mol_frags = get_mol_frags(graph)
##             mol = Chem.MolFromSmiles(smiles)
##             if mol is None:
##                 continue
##             rd_mol_frags = Chem.GetMolFrags(mol)
##             my_mol_frags = list(map(sorted, my_mol_frags))
##             rd_mol_frags = list(map(sorted, rd_mol_frags))
##             if my_mol_frags != rd_mol_frags:
##                 raise AssertionError( (smiles, my_mol_frags, rd_mol_frags) )
## verify_get_mol_frags()


def _check_vertical_column(columns, column, n, num_rows):
    if column not in columns:
        return True
    elements = columns[column]
    for m in range(n, n-num_rows, -1):
        if m in elements:
            return False
    return True

# Draw vertical
def V(text, text2=None, location="above"):
    if text2 is None:
        return list(text)
    if location == "above":
        return list(text + text2)
    elif location == "below":
        return list(text2 + text)
    else:
        raise ValueError(location)


class Layout(object):
    def __init__(self, smiles, mol, tokens, atoms, closures, branches,
                 graph, fragments, 
                 special_symbols = UnicodeSymbols):
        self.smiles = smiles
        self.mol = mol
        self.tokens = tokens
        self.atoms = atoms
        self.closures = closures
        self.branches = branches
        self.graph = graph
        self.fragments = fragments
        self.special_symbols = special_symbols

        self.columns = defaultdict(dict)
        self.ceiling = 0
        self.floor = -1

        self.legend_columns = defaultdict(dict)
        self._min_legend_row = self._max_legend_row = 0
        self._min_legend_col = self._max_legend_col = 0
        self._num_above_tracks = 0
        self._num_below_tracks = 0

    def end_track(self, location, track_label, align="center"):
        if location == "above":
            end_row = self.ceiling
            self.set_ceiling()
            start_row = self.ceiling
            if start_row == end_row:
                # Nothing present
                # Create an empty track.
                self.ceiling += 1
                start_row = self.ceiling
            start_row -= 1
            self._num_above_tracks += 1
            track_counter = self._num_above_tracks - 1
                
        elif location == "below":
            start_row = self.floor
            self.set_floor()
            end_row = self.floor
            if start_row == end_row:
                # Nothing present
                # Create an empty track.
                self.floor -= 1
                end_row = self.floor
            end_row += 1
            self._num_below_tracks += 1
            track_counter = self._num_below_tracks
        else:
            raise AssertionError(location)

        if align == "above":
            row = start_row
        elif align == "center":
            delta = start_row - end_row
            if delta % 2 == 1:
                delta -= 1
            delta = delta // 2
            row = start_row - delta
            
        elif align == "below":
            row = end_row
        else:
            raise ValueError(align)

        special_symbols = _get_special_symbols(self.special_symbols, track_counter)
                                                   
        self.add_legend_text(row, -len(track_label)-1, track_label)
        if start_row == end_row:
            self.add_legend_text(start_row, -1, special_symbols.single_row)
        else:
            self.add_legend_text(start_row, -1, special_symbols.nw_corner)
            for row in range(start_row-1, end_row, -1):
                self.add_legend_text(row, -1, special_symbols.e_side)
            self.add_legend_text(end_row, -1, special_symbols.sw_corner)
                      
    def set_level(self, location):
        if location == "above":
            self.set_ceiling()
        elif location == "below":
            self.set_floor()
        else:
            raise AssertionError(location)
        
    def set_ceiling(self):
        ceiling = 0
        for column in self.columns.values():
            ceiling = max(ceiling, max(column))
        if ceiling >= self.ceiling:
            self.ceiling = ceiling + 1

    def set_floor(self):
        floor = 0
        for column in self.columns.values():
            floor = min(floor, min(column))
        if floor <= self.floor:
            self.floor = floor - 1
            
    def find_above_row(self, start_column, end_column=None, num_rows=1):
        assert num_rows >= 1, num_rows
        if end_column is None:
            end_column = start_column + 1
        n = self.ceiling + num_rows-1  # Need enough space for all of the rows
        while 1:        
            for column in range(start_column, end_column):
                if not _check_vertical_column(self.columns, column, n, num_rows):
                    break
            else:
                return n
            n += 1
    
    def find_below_row(self, start_column, end_column=None, num_rows=1):
        assert num_rows >= 1, num_rows
        if end_column is None:
            end_column = start_column + 1
        n = self.floor
        while 1:
            for column in range(start_column, end_column):
                if not _check_vertical_column(self.columns, column, n, num_rows):
                    break
            else:
                return n
            n -= 1

    def add(self, location, start_column, text, row=None):
        if location == "above":
            return self._add(text, start_column, row, self.find_above_row)
        elif location == "below":
            return self._add(text, start_column, row, self.find_below_row)
        else:
            raise ValueError(location)

    def add_above(self, start_column, text, row=None):
        return self._add(text, start_column, row, self.find_above_row)
        
    def add_below(self, start_column, text, row=None):
        return self._add(text, start_column, row, self.find_below_row)

    def draw_text(self, row, start_column, text):
        return self._add(text, start_column, row, None)
    
    def _add(self, text, start_column, row, find_row):
        if isinstance(text, type("")) or isinstance(text, type(u"")):
            lines = [text]
        else:
            lines = text
        num_rows = len(lines)
        num_cols = max(len(line) for line in lines)
        if num_rows == 0:
            return None

        if row is None:
            row = find_row(start_column, start_column+num_cols, num_rows)
        start_row = row

        for line in lines:
            for colno, c in enumerate(line, start_column):
                if not (self.floor == self.ceiling == 0):
                    assert not (self.floor < row < self.ceiling), (self.floor, row, self.ceiling)
                self.columns[colno][row] = c
            row -= 1
        return (start_row, row+1)
        #print(self.columns)

    def add_legend_text(self, row, col, label):
        for i, c in enumerate(label):
            self.legend_columns[col+i][row] = c
        if row < self._min_legend_row:
            self._min_legend_row = row
        elif row > self._max_legend_row:
            self._max_legend_row = row
        if col < self._min_legend_col:
            self._min_legend_col = col
        elif col + len(label) > self._max_legend_row:
            self._max_legend_row = col + len(label)

    def get_legend_size(self):
        return (self._max_legend_col - self._min_legend_col) + 1
    
    def display(self, output=sys.stdout, width=40, legend="all"):
        min_required_width = self.get_legend_size() + 10
        if width < min_required_width:
            raise ValueError("width of %d is too small. Must be at least %d for this layout."
                                 % (width, min_required_width))
        if legend not in ("off", "once", "all"):
            raise ValueError("Unsupported legend style %r" % (legend,))
        MAX_COL = max(self.columns)
        
        MIN_COL = min(self.columns)
        # Find the first column containing a non-space character
        while 1:
            if MIN_COL in self.columns:
                chars = set(self.columns[MIN_COL].values())
                if chars and chars != {" "}:
                    break
            if MIN_COL > MAX_COL:
                # Only spaces found?
                return
            MIN_COL += 1
            
        # Find the last column containing a non-space character
        while 1:
            if MAX_COL in self.columns:
                chars = set(self.columns[MAX_COL].values())
                if chars and chars != {" "}:
                    break
            if MAX_COL < MIN_COL:
                raise AssertionError("Should not get here")
            MAX_COL -= 1
        

        legend_count = 0
        start_col = MIN_COL
        WIDTH = width
        while start_col < MAX_COL + 1:
            if legend == "all" or (legend == "once" and legend_count == 0):
                include_legend = True
                max_row = self._max_legend_row
                min_row = self._min_legend_row
                width = WIDTH - (self._max_legend_col - self._min_legend_col + 1)
            else:
                include_legend = False
                width = WIDTH
                min_row = max_row = 0
            legend_count += 1

            # Find the minimum and maximum row number for this range of columns
            for colno in range(start_col, min(start_col+width, MAX_COL+1)):
                if colno in self.columns:
                    max_row = max(max_row, max(self.columns[colno]))
                    min_row = min(min_row, min(self.columns[colno]))

            for rowno in range(max_row, min_row-1, -1):
                output_line = []
                if include_legend:
                    for colno in range(self._min_legend_col, self._max_legend_col+1):
                        if colno in self.legend_columns:
                            c = self.legend_columns[colno].get(rowno, " ")
                        else:
                            c = " "
                        output_line.append(c)
                        
                for colno in range(start_col, min(start_col+width, MAX_COL+1)):
                    if colno in self.columns:
                        c = self.columns[colno].get(rowno, " ")
                    else:
                        c = " "
                    output_line.append(c)
                output_line.append("\n")
                #print("got", output_line)
                output.write("".join(output_line))
            if colno < MAX_COL:
                # Space between this segment and the next,
                # but not after the last segment
                output.write("\n")

            start_col += width
            
def draw_bar(layout, start, end, start_text, end_text, c, label,
             left_label = None, right_label=None, location="below", row=None):
    assert len(start_text) == 1, start_text
    assert len(end_text) == 1, end_text
    assert len(c) == 1, c
    if left_label is None:
        left_label = " " + label
    if right_label is None:
        right_label = label
    
    delta = end - start
    assert delta > 0, "cannot reverse direction"
    text = start_text + c*(delta-1) + end_text

    repeat_len = max(len(label) * 1.4, len(label) + 8)
    text_len = len(text)
    if label and text_len > repeat_len:
        inline_len = len(label) + 2
        num_terms = text_len // repeat_len
        for i in range(1, num_terms):
            offset = int(text_len * (i / float(num_terms)) - inline_len/2.0)
            text = text[:offset] + " " + label + " " + text[offset+inline_len:]
    
    return layout.add(location, start-len(left_label), left_label + text + right_label,
                          row=row)

class Branch(object):
    def __init__(self, atom_index, first_index, second_index):
        self.atom_index = atom_index
        self.first_index = first_index
        self.second_index = second_index
        
def match_branches(tokens, smiles):
    paren_stack = []
    atom = None
    for token in tokens:
        if token.state == "atom":
            atom = token
        elif token.state == "open_branch":
            paren_stack.append((atom, token))
        elif token.state == "close_branch":
            if not paren_stack:
                raise ParseError("Close branch without an open branch",
                                 smiles, token.start)
            atom, open_branch = paren_stack.pop()
            yield Branch(atom.index, open_branch.index, token.index)
    if paren_stack:
        raise ParseError("Open branch without a close branch",
                         smiles, paren_stack[0][1].start)


_letters = "ABCDEFGHJKLMNPQRSTUVWXYZ"
def base24(value):
    s = ""
    while 1:
        n = value % 24
        s = _letters[n] + s
        value = value // 24
        if value == 0:
            return s

def add_byte_offset_track(layout, location="above"):
    n = len(layout.smiles)
    for i in range(0, n-1, 5):
        if i % 5 == 0:
            layout.add(location, i, V(str(i)))
    layout.add(location, n-1, V(str(n-1)))
    layout.end_track(location, "byte offsets")
        
def add_atom_index_track(layout, location="above"):
    for atom_index, atom in enumerate(layout.atoms):
        layout.add(location, atom.start, V(str(atom_index), "|", location))
    layout.end_track(location, "atoms")


_state_aliases = {
    "atom": "a",
    "bond": "b",
    "open_branch": "(",
    "close_branch": ")",
    "dot": ".",
    "closure": "%",
    }
def add_token_label_track(layout, location="above"):
    for token in layout.tokens:
        layout.add(location, token.start, _state_aliases[token.state])
    layout.end_track(location, "token types")

## def add_branch_track(layout, location="above"):
##     tokens = layout.tokens
##     for branch_index, branch in enumerate(layout.branches):
##         label = base24(branch_index)
##         draw_bar(layout,
##                  tokens[branch.first_index].start,
##                  tokens[branch.second_index].start,
##                  "(", ")", ".", label, label, label,
##                  location=location)
        
##     layout.end_track(location, "branches")
def add_branch_track(layout, location="above"):
    tokens = layout.tokens
    base_atoms = defaultdict(list)
    for branch in layout.branches:
        base_atoms[branch.atom_index].append(branch)

    for atom_index, branches in sorted(base_atoms.items()):
        atom_token = tokens[atom_index]
        
        # Find out where I can place this section
        # I have a leading space to keep things from bunching up.
        spaces = " " * (tokens[branches[-1].second_index].end - atom_token.start)
        start_row, end_row = layout.add(location, atom_token.start-1, spaces)
        
        gap = (tokens[branches[0].first_index].start - atom_token.start) - 1
        layout.draw_text(start_row, atom_token.start, "*" + "-"*gap)
        label = str(layout.atoms.index(atom_token))
        for branch in branches:
            draw_bar(layout,
                     tokens[branch.first_index].start,
                     tokens[branch.second_index].end-1,
                     layout.special_symbols.open_branch,
                     layout.special_symbols.close_branch,
                     layout.special_symbols.in_branch,
                     label, "", "",
                     row = start_row)
                     
    layout.end_track(location, "branches")
        
def add_closure_track(layout, location="below"):
    tokens = layout.tokens
    closures = layout.closures
    
    for closure_index, closure in enumerate(closures, 1):
        start_row, end_row = draw_bar(
            layout,
            tokens[closure.first_atom_index].start,
            tokens[closure.second_closure_index].start,
            layout.special_symbols.left_closure_atom,
            layout.special_symbols.right_closure, "-",
            str(closure.closure_id),
            location = location)
        # This isn't clean. If there are enough closures,
        # or large closures like %(000000001) before it,
        # then this may overright the in-bar label. Oh well.
        layout.draw_text(
            start_row,
            tokens[closure.first_closure_index].start,
            layout.special_symbols.left_closure)
        layout.draw_text(
            start_row,
            tokens[closure.second_atom_index].start,
            layout.special_symbols.right_closure_atom)
        
    layout.end_track(location, "closures")

def add_smiles_track(layout, location="below"):
    layout.add(location, 0, layout.smiles)
    layout.end_track(location, "SMILES")
    

def add_smarts_match_tracks(layout, pattern, uniquify=True, useChirality=False,
                            maxMatches=1000, match_style=None, location="below"):
    mol = layout.mol
    matches = mol.GetSubstructMatches(pattern, uniquify=uniquify, useChirality=useChirality,
                                      maxMatches=maxMatches)
    if match_style == "simple" or match_style is None:
        def style(atom_index, pattern_index):
            return "*"
    elif match_style == "pattern-index":
        def style(atom_index, pattern_index):
            return V(str(pattern_index))
    elif match_style == "atom-index":
        def style(atom_index, pattern_index):
            return V(str(atom_index))
    else:
        raise ValueError("Unknown match_style: %r" % (match_style,))
        
        
    atoms = layout.atoms
    for matchno, atom_indices in enumerate(matches, 1):
        for pattern_index, atom_index in enumerate(atom_indices):
            layout.add(location, atoms[atom_index].start, style(atom_index, pattern_index))
        layout.end_track(location, "match %d" % (matchno,))

_bond_type_labels = None
def _init_bond_type_labels():
    global _bond_type_labels
    from rdkit import Chem
    _bond_type_labels = {
        Chem.BondType.SINGLE: "-",
        Chem.BondType.DOUBLE: "=",
        Chem.BondType.AROMATIC: ":",
        Chem.BondType.TRIPLE: "#",
        }

def _get_symbol(atom):
    symbol = atom.GetSymbol()
    if atom.GetIsAromatic():
        symbol = symbol.lower()
    return symbol
        
def add_neighbor_track(layout, atom_index, location="below"):
    if _bond_type_labels is None:
        _init_bond_type_labels()

    atom_tokens = layout.atoms
    mol = layout.mol
    if atom_index >= mol.GetNumAtoms():
        layout.add(location, 0, "No atom with index %d" % (atom_index,))
    else:
        center_atom = mol.GetAtomWithIdx(atom_index)
        start = atom_tokens[atom_index].start

        layout.add(location, start, "X")
        
        terms = []
        for other_atom, bond in zip(
                center_atom.GetNeighbors(), center_atom.GetBonds()):
            terms.append("%s%s%d" % (_bond_type_labels[bond.GetBondType()],
                                     _get_symbol(other_atom), other_atom.GetIdx()))
                                          
        description = _get_symbol(center_atom) + "".join("(" + term + ")" for term in terms)

        layout.add(location, start, description)
        
        for bond_idx, other_atom in enumerate(center_atom.GetNeighbors()):
            other_atom_idx = other_atom.GetIdx()
            other_atom_start = atom_tokens[other_atom_idx].start
            layout.add(location, other_atom_start, "^")

    layout.end_track(location, "neighbors")

def add_fragment_track(layout, fragments, location="below"):
    atoms = layout.atoms
    tokens = layout.tokens
    for fragment_index, atom_indices in enumerate(fragments):
        text = str(fragment_index)
        text2 = " " * fragment_index # stagger fragments each on its own line
        for atom_index in atom_indices:
            atom_token = atoms[atom_index]
            for i in range(atom_token.start, atom_token.end):
                layout.add(location, i, V(text, text2, location))

        atom_indices = set(atom_indices)
        # Also highlight the branches
        for branch in layout.branches:
            # ... XXX the atom token should know its index in the atom list
            atom_token_index = branch.atom_index
            atom_index = atoms.index(tokens[atom_token_index])
            if atom_index in atom_indices:
                for index in (branch.first_index, branch.second_index):
                    layout.add(
                        location,
                        tokens[index].start,
                        V(text, text2, location))
            
        # And the closures
        for closure in layout.closures:
            atom_token_index = closure.first_atom_index
            atom_index = atoms.index(tokens[atom_token_index])
            if atom_index in atom_indices:
                for index in (closure.first_closure_index, closure.second_closure_index):
                    for i in range(tokens[index].start, tokens[index].end):
                        layout.add(location, i, V(text, text2, location))
        # And the bonds
        for graph_bond in layout.graph.bonds:
            if graph_bond.token is None:
                continue
            if graph_bond.atom_indices[0] in atom_indices:
                for i in range(graph_bond.token.start, graph_bond.token.end):
                    layout.add(location, i, V(text, text2, location))
                
    layout.end_track(location, "fragments")

TRACKS = """\
atoms - display the index number of each atom term
tokens - display the index number of each term
offsets - display the offset of every 5th byte in the SMILES string, and the last byte
branches - show the start and end location of each pair of branches
closures - show the start and end location of each pair of closures
fragments - show which atoms are in each connected fragment
matches - show which atoms match a given SMARTS match (--smarts is required)
neighbors - show which atoms are connected to a given atom index (--atom-index is required)
smiles - add another copy of the SMILES
none - show nothing
"""
track_names = [line.split()[0] for line in TRACKS.splitlines() if line.strip()]

epilog = """
The available tracks are:
""" + "".join("  " + line for line in TRACKS.splitlines(True))

epilog += """
If no tracks are specified then the default --above is ["atoms"].

If no tracks are specified and neither --smarts nor --atom-index are
defined, then the default --below is ["branches", "closures"].

Otherwise, if one of --smarts or --atom-index is specified, then the
default --below is ["matches"] or ["neighbors"], respectively, or
["matches", "neighbors"] if both are specified.

Use "none" to disable tracks. For example:
  %(prog)s 'CCO' -a none --use-rdkit
will only verify the syntax and display the SMILES string

Examples:

  %(prog)s 'Cc1c(OC)c(C)cnc1CS(=O)c2nc3ccc(OC)cc3n2'
  %(prog)s 'O/N=C/5C.F5' -a offsets -b closures
  %(prog)s 'CC1CC2C3CCC4=CC(=O)C=CC4(C)C3(F)C(O)CC2(C)C1(O)C(=O)CO' --smarts '[R]'
  %(prog)s 'CN1C(=O)CN=C(c2ccccc2)c2cc(Cl)ccc21' --atom-index 2

"""


class ListTracksAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(ListTracksAction, self).__init__(option_strings, dest, nargs=0, **kwargs)
    def __call__(self, parser, namespace, values, option_string=None):
        sys.stdout.write(TRACKS)
        raise SystemExit(0)

_kwargs = dict(
    description = "Show details of the SMILES string",
    allow_abbrev = False,
    epilog = epilog,
    formatter_class = argparse.RawDescriptionHelpFormatter,
    )
if sys.version_info[0] == 2:
    _kwargs.pop("allow_abbrev") # Not available in older Pythons
parser = argparse.ArgumentParser(**_kwargs)
del _kwargs

parser.add_argument(
    "--above", "-a", action="append", metavar="TRACK", choices=track_names,
    help="Specify a track to show above the SMILES. Repeat this option once for each track.")
parser.add_argument(
    "--below", "-b", action="append", metavar="TRACK", choices=track_names,
    help="Specify a track to show below the SMILES. Repeat this option once for each track.")

parser.add_argument(
    "--list-tracks", "-l", action=ListTracksAction,
    help="List the available tracks.")
                        
parser.add_argument(
    "--smarts", metavar="PATTERN",
    help="Define the SMARTS pattern to use for the 'matches' track.")
                        
parser.add_argument(
    "--max-matches", type=int, metavar="N", default=1000,
    help="The maximum number of matches to display. (default: 1000)")

parser.add_argument(
    "--all-matches", action="store_false", dest="uniquify",
    help="Show all matches. The default only shows unique matches.")
                        
parser.add_argument(
    "--use-chirality", action="store_true",
    help="Enable the use of stereochemistry during matching.")
    
parser.add_argument(
    "--match-style", choices=("simple", "pattern-index", "atom-index"),
    help="Change the display style from a simple '*' to something which also shows "
         "the pattern or atom index")

parser.add_argument(
    "--atom-index", "--idx", type=int, metavar="N",
    help="Define the atom to use for the 'neighbors' track.")

parser.add_argument(
    "--use-rdkit", action="store_true",
    help="Always use RDKit to verify that the SMILES is valid.")
parser.add_argument(
    "--no-sanitize", action="store_true",
    help="Do not let RDKit sanitize/modify the bond orders and charges")

parser.add_argument(
    "--width", type=int, default=72, metavar="W",
    help="Number of columns to use in the output. Must be at least 40. (default: 72)")

parser.add_argument(
    "--legend", choices=("off", "once", "all"), default="all",
    help="The default of 'all' shows the legend for each output segment. "
    "Use 'once' to only show it in the first segment, or 'off' for no legend.")
                        
parser.add_argument(
    "--ascii", action="store_true",
    help="Use pure ASCII for the output, instead of Unicode box characters")

parser.add_argument(
    "--version", action='version', version='%(prog)s ' + __version__)

parser.add_argument(
    "smiles", metavar="SMILES", nargs="?",
    help = "SMILES string to show (if not specified, use caffeine)"
    )

def die(msg):
    sys.stderr.write(msg)
    if not msg.endswith("\n"):
        sys.stderr.write("\n")
    sys.stderr.flush()
    raise SystemExit(1)

def main(argv=None):
    args = parser.parse_args(argv)

    if args.smiles is None:
        sys.stderr.write("No SMILES specified. Using caffeine.\n")
        args.smiles = "Cn1c(=O)c2c(ncn2C)n(C)c1=O"
    
    need_mol = (args.smarts or args.atom_index or args.use_rdkit)

    default_above_list = ["atoms"]
    
    default_below_list = []
    
    pattern = None
    if args.smarts is not None:
        from rdkit import Chem
        pattern = Chem.MolFromSmarts(args.smarts)
        if pattern is None:
            die("Cannot parse the --smarts pattern")
        if args.max_matches < 1:
            die("--max-matches must be a positive integer")
        if args.uniquify is None:
            args.uniquify = True

        default_below_list.append("matches")

    atom_index = args.atom_index
    if atom_index is not None:
        if atom_index < 0:
            die("--atom-index must be a non-negative integer")
        default_below_list.append("neighbors")

    if not default_below_list:
        default_below_list.append("branches")
        default_below_list.append("closures")
        default_below_list.append("fragments")
            
    if args.ascii:
        special_symbols = ASCIISymbols
    else:
        special_symbols = UnicodeSymbols

    width = args.width
    if width < 40:
        die("--width is too narrow. Must be at least 40.")
        
    above_list = args.above
    below_list = args.below
    if above_list is None:
        if below_list is None:
            # Put in the defaults
            above_list = default_above_list
            below_list = default_below_list
        else:
            above_list = []
    else:
        if below_list is None:
            below_list = []
        
    try:
        layout = make_layout(
            args.smiles, need_mol=need_mol,
            sanitize = not args.no_sanitize,
            special_symbols=special_symbols)
    except ParseError as err:
        msg = err.explain(prefix="  ")
        msg += err.advice()
        die("Cannot parse --smiles: %s\n%s" % (err.reason, msg))

            
    for location, track_list in (
            ("above", above_list[::-1]),
            ("below", below_list),
            ):
        for track in track_list:
            if track == "atoms":
                add_atom_index_track(layout, location)
            elif track == "tokens":
                add_token_label_track(layout, location)
            elif track == "offsets":
                add_byte_offset_track(layout, location)
            elif track == "branches":
                add_branch_track(layout, location)
            elif track == "closures":
                add_closure_track(layout, location)
            elif track == "matches":
                if pattern is None:
                    die("Must specify --smarts to show a 'match' track")
                add_smarts_match_tracks(
                    layout, pattern, uniquify=args.uniquify, useChirality=args.use_chirality,
                    maxMatches = args.max_matches, match_style=args.match_style,
                    location=location)
            elif track == "neighbors":
                if atom_index is None:
                    die("Must specify --atom-index to show neighbors of a given atom")
                add_neighbor_track(layout, atom_index, location)
            elif track == "fragments":
                add_fragment_track(layout, layout.fragments, location)
            elif track == "none":
                pass
            elif track == "smiles":
                add_smiles_track(layout, location)
            else:
                raise AssertionError(track)

    layout.display(width=width, legend=args.legend)

if __name__ == "__main__":
    main()
