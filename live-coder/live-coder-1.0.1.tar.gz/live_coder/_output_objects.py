
class OutputLoop:

    def __init__(self, iterations):
        self.iterations = iterations

    def len(self):
        return max([output_object.len() for output_object in self.iterations])

    def render(self):
        html_iterations = []
        for output_object in self.iterations:
            html_iterations.append(
                '<div class="iteration">{0}</div>'.format(output_object.render())
            )
        return '<div class="loop">{0}</div>'.format(''.join(html_iterations))


class OutputLines:

    def __init__(self, lines):
        self.lines = lines
        self._linenos_for_lines = []
        self._setup_line_number_map()

    def _setup_line_number_map(self):
        pointer = 0
        for obj in self.lines:
            if type(obj) is OutputLoop:
                pointer += obj.len()
            else:
                self._linenos_for_lines.append(pointer)
                pointer += 1

    def len(self):
        length = 0
        for obj in self.lines:
            if type(obj) is OutputLoop:
                length += obj.len()
            else:
                length += 1
        return length

    def _in_loop_lines(self, lineno):
        return lineno not in self._linenos_for_lines and lineno < self.len()

    def _add_missing_lines(self, max_lineno):
        for i in range(self.len(), max_lineno + 1):
            self._linenos_for_lines.append(i)
            self.lines.append('')

    def _i_for_relative_lineno(self, lineno):
        if self._in_loop_lines(lineno):
            raise RuntimeError('Trying to get the lines index of a line in an OutputLoop.')
        if lineno in self._linenos_for_lines:
            return self._linenos_for_lines.index(lineno)
        self._add_missing_lines(lineno)
        return len(self.lines) - 1

    def _insert(self, lineno, line):
        i = self._i_for_relative_lineno(lineno)
        if self.lines[i] and line:
            self.lines[i] = '{0} {1}'.format(line, self.lines[i])
        elif line:
            self.lines[i] = line

    def set(self, start_i, lines):
        for i, line in enumerate(lines):
            lineno = start_i + i
            self._insert(lineno, line)

    def _format_line(self, line):
        return '<div style="height:18px;" class="view-line"><span>{0}</span></div>'.format(line)

    def render(self):
        html = ''
        for line in self.lines:
            if type(line) is OutputLoop:
                html += line.render()
            else:
                html += self._format_line(line)
        return html
