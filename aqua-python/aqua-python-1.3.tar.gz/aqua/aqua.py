#!/usr/local/bin/python3

import sys

class PEP8:
    """
    Contains methods for formatting Python scripts according to 
    the PEP 8 standards.
    """

    use_tabs = False
    line_length = 72
    
    @staticmethod
    def format_indentation(line):
        """
        Indent lines with tabs or spaces.

        :param line: the line to indent
        :returns: the tokens of the indented line
        """
        if PEP8.use_tabs:
            new_line = [line.num_indents * '\t'] + line.tokens[:]
        else:
            new_line = [line.num_indents * 4 * ' '] + line.tokens[:]
        return new_line[:]

    @staticmethod
    def format_line_length(line):
        code_line = line.tokens[:]
        if len(''.join(code_line)) > PEP8.line_length:
            total_len = 0
            tok = ''
            for token in code_line:
                total_len += len(token) + 1
                if total_len >= PEP8.line_length:
                    tok = token
                    break
            tok_index = code_line.index(tok)
            #print(code_line, tok_index)
            code_line.insert(tok_index - 1, '\\\n' + '\t' * (line.num_indents + len(code_line[0]) // 8 - 1))
        return code_line[:]

    @staticmethod
    def format_member_names(line):
        code_line = line.tokens[:]
        _iter = iter(code_line)
        new_line = []
        for token in _iter:
            #print(token)
            if token == 'class':
                new_line.append(token)
                token = next(_iter)
                new_line.append(token)
                token = next(_iter)
                token = token.capitalize()
            elif token == 'def':
                new_line.append(token)
                token = next(_iter)
                new_line.append(token)
                token = next(_iter)
                token = token.lower()[0] + token[1:]
            new_line.append(token)
            #print(token)
        #for token, new_token in zip(code_line, _iter):
            #token = new_token
        #print(new_line)
        #code_line = ''.join(code_line)
        #prev_token = ''
        '''for token in code_line:
            if token == 'class':
                prev_token = 'class'
                continue
            elif token == 'def':
                prev_token = 'def'
                continue
            elif token == ' ' or token == '\t':
                continue
            else:
                if prev_token == 'class':
                    token = token.capitalize()
                elif prev_token == 'def':
                    token = token[0].lower() + token[1:]
                prev_token = ''
        '''

        '''print(code_line)
        if 'class' in code_line:
            print('class keyword in line')
            new_name = code_line[code_line.index('class') + 1].upper()[0] + code_line[code_line.index('class') + 1][1:]
            code_line[code_line.index('class') + 1] = new_name'''
        return new_line[:]


class Line:
    def __init__(self, tokens=None, num_indents=0):
        self.tokens = tokens
        self.num_indents = num_indents

class File:
    num_indents = 0
    def __init__(self, filename, lines=None):
        self.filename = filename
        self.lines = lines
    def read_lines(self):
        file_handle = open(self.filename, 'r+')
        lines = []
        num_newlines = 0
        unindented = False
        self.num_indents = 0
        for line in file_handle.readlines():
            #tokens = [token + ' ' for token in line.split() if token not in ['\s+', '', '\t' * self.num_indents]]
            #print(line)
            tokens = line.split()
            spaced_tokens = []
            for index in range(len(tokens)):
                spaced_tokens.append(tokens[index])
                spaced_tokens.append(' ')
            tokens = spaced_tokens[:]
            tokens.append('\n')
            #print(tokens)

            '''if self.num_indents > 0 and num_newlines >= 1:
                self.num_indents -= 1
                #lines.append(Line(['\n'], self.num_indents))
                num_newlines = 0'''
            '''else:
                self.num_indents = 0
                num_newlines = 0'''
            #print(tokens)
            if self.num_indents > 0 and tokens[0] == '\n':
                #self.num_indents = 0
                #if not unindented:
                self.num_indents -= 1
                unindented = True
                num_newlines += 1
            #if self.num_indents > 0 and num_newlines >= 1:# and not unindented:
                #self.num_indents -= 1
                #unindented = True
                #num_newlines = 0
            if 'else' in line:
                num_newlines = 0
                self.num_indents -= 1
            line_object = Line(tokens, self.num_indents)
            if ':' in line and 'input' not in line:
                num_newlines = 0
                self.num_indents += 1
                unindented = False
            elif line is 'pass' or line is 'return' or 'return' in line:
                num_newlines = 0
                self.num_indents -= 1
            lines.append(line_object)
        return lines
    def write(self, string):
        file_handle = open(self.filename, 'w')
        file_handle.write(string)


def fix_indentation_and_blank_lines(f):
    lines = f.read_lines()
    new_code = []
    if '--use-tabs' in sys.argv:
        PEP8.use_tabs = True
    elif '--PEP8' in sys.argv:
        PEP8.use_tabs = False
    else:
        PEP8.use_tabs = False
    for line in lines:
        line.tokens = PEP8.format_indentation(line)
        #print(line.tokens)
        new_code += line.tokens
    return new_code
    #f.write(''.join(new_code))

def fix_line_length(f):
    lines = f.read_lines()
    new_code = []
    if '--line-length' in sys.argv:
        PEP8.line_length = sys.argv[sys.argv.index('--line-length') + 1]
    prev_line = Line([], 0)
    for line in lines:
        #print(line.tokens)
        new_line = PEP8.format_line_length(line)
        #l = []
        #for i in range(len(new_line)):
            #l.append(new_line[i])
            #l.append(' ')
        line.tokens = new_line[:]
        #line.tokens.append('\n')
        #print(line.tokens)
        line.tokens = PEP8.format_indentation(line)
        if "\\" in prev_line.tokens:
            line.tokens.insert(0, len(line.tokens[0]) * " ")
        #print(line.tokens)
        new_code += line.tokens
        prev_line = line
    return new_code

def fix_member_names(f):
    lines = f.read_lines()
    new_code = []
    for line in lines:
        #print(line.tokens)
        #new_line = PEP8.format_line_length(line)
        #line.tokens = new_line[:]
        #new_line = PEP8.format_indentation(line)
        #line.tokens = new_line[:]

        #new_line = PEP8.format_member_names(line)
        #line.tokens = new_line[:]
        new_line = PEP8.format_line_length(line)
        line.tokens = new_line[:]
        new_line = PEP8.format_indentation(line)
        line.tokens = new_line[:]
        line.tokens = PEP8.format_member_names(line)
        #print(line.tokens)
        #else:
        #new_line = line.tokens[:]
        #line.tokens = new_line[:]
        new_code += line.tokens
    return new_code

def main():
    f = File(sys.argv[1])
    #fix_member_names(f)
    fix_indentation_and_blank_lines(f)
    new_code = fix_line_length(f)
    new_code = fix_member_names(f)
    #new_code = fix_indentation_and_blank_lines(f)
    f.write(''.join(new_code))
    #new_code = fix_member_names(f)
    #f.write(''.join(new_code))

if __name__ == '__main__':
    main()
