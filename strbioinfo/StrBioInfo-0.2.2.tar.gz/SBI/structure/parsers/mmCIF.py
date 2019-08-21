# -*-
#
# @author: jaumebonet
# @email:  jaume.bonet@gmail.com
# @url:    jaumebonet.github.io
#
# @date:   2016-02-16 10:27:32
#
# @last modified by:   jaumebonet
# @last modified time: 2016-02-16 19:50:53
#
# -*-
import json

from pynion  import File
from pynion  import accepts
from .Parser import Parser


def specialSplit(content):
    output = [["", False]]
    quote  = False
    length = len(content)

    for c in xrange(length):
        isWS   = content[c] == " " or content[c] == "\t"
        wasWS  = c == 0        or content[c-1] == " " or content[c-1] == "\t"
        willWS = c == length-1 or content[c+1] == " " or content[c+1] == "\t"
        braket = frozenset(["'", '"'])
        if (content[c] in braket) and (wasWS or willWS):
            quote = not quote
        elif not quote and isWS and output[-1][0] != "": output.append(["", False])
        elif not quote and content[c] == "#": break
        elif not isWS or quote:
            output[-1][0] += content[c]
            output[-1][1] = quote
    if output[-1][0] == "": output.pop()
    return output


def nonefy(content):
    if content == "?": return None
    if content == ".": return None
    return content


class mmCIF(Parser):
    """Transforms from a to `mmCIF <http://mmcif.wwpdb.org/>`_ format.
    This parser is based on the one created by `Gert-Jan Bekker
    <http://github.com/gjbekker/cif-parsers>`_ but simplified
    """
    def __init__(self):
        self.multiline  = False
        self.buffer     = ""
        self.data       = {}
        self.loopstatus = False
        self.keyname    = None
        self.lastkey    = None
        self.headers    = frozenset(['loop_', 'save_', 'global_', 'data_'])

    def read(self, file_name):
        with File(file_name, 'r') as fd:
            for line in [l.rstrip() for l in fd]:
                if len(line) == 0: continue
                if self._check_multiline(line):
                    self._assign(specialSplit(self.buffer))
                    self.buffer = ""
        info = self.data
        self._set_default(True)
        return info

    @accepts(json_object="json_dict")
    def write(self, json_object, file_name):
        pass

    def _is_header(self, data):
        for x in self.headers:
            if data[0].startswith(x) and not data[1]:
                return True
        return False

    def _manage_header(self, data):
        if data[0][0] == 'loop_':
            self.loopstatus = True
        elif data[0][0].startswith('data_'):
            self.keyname = data[0][0][5:].strip()
            self.data.setdefault(self.keyname, {})
        elif data[0][0].startswith('save_'):   pass  # TODO
        elif data[0][0].startswith('global_'): pass  # TODO

    def _set_default(self, strong = False):
        self.loopstatus = False
        self.lastkey    = None
        if strong:
            self.multiline  = False
            self.buffer     = ""
            self.data       = {}
            self.keyname    = None

    def _assign(self, data):
        if len(data) == 0:             self._set_default()
        elif self._is_header(data[0]): self._manage_header(data)
        elif not self.loopstatus:      self._no_loop_status(data)
        else:                          self._loop_status(data)

    def _loop_status(self, data):
        if data[0][0].startswith('_'):
            k = data[0][0].split('.')
            if self.lastkey is None: self.lastkey = {}
            self.lastkey.setdefault(k[0], []).append(k[1])
            self.data[self.keyname].setdefault(k[0], {}).setdefault(k[1], [])
        else:
            k = self.lastkey.keys()[0]
            for x in range(len(data)):
                self.data[self.keyname][k][self.lastkey[k][x]].append(nonefy(data[x][0]))

    def _no_loop_status(self, data):
        if data[0][0].startswith('_'):
            self.lastkey = data[0][0].split('.')
            self.data[self.keyname].setdefault(self.lastkey[0], {}).setdefault(self.lastkey[1], [])
            if len(data) == 2:
                d = nonefy(data[1][0])
                self.data[self.keyname][self.lastkey[0]][self.lastkey[1]].append(d)
                self.lastkey = None
        elif self.lastkey is not None:
            if len(data) == 1:
                d = nonefy(data[0][0])
                self.data[self.keyname][self.lastkey[0]][self.lastkey[1]].append(d)
            else:
                d = nonefy(" ".join([x[0] for x in data]))
                self.data[self.keyname][self.lastkey[0]][self.lastkey[1]].append(d)
            self.lastkey = None

    def _check_multiline(self, line):
        if line[0] == ';': self.multiline = not self.multiline
        if self.multiline:
            self.buffer += line.lstrip(';')
            return False
        else:
            if len(self.buffer) == 0: self.buffer = line
            return True
