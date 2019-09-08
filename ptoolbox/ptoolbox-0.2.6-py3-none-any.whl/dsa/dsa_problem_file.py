import codecs
import glob
import os
import re
from shutil import copyfile
from jinja2 import Template

from helpers.clog import CLog


def create_problem(folder, problem_code, overwrite=False):
    problem_code = problem_code.replace('-', '_').replace(' ', '_').lower()

    problem_folder = os.path.join(folder, problem_code)

    if os.path.exists(problem_folder):
        if not overwrite:
            CLog.error('Problem folder existed! Delete the folder or use `overwrite` instead.')
            return
        else:
            CLog.warn('Problem folder existed! Content will be overwritten.')

    if not os.path.exists(problem_folder):
        os.makedirs(problem_folder)

    # if not os.path.exists(problem_folder + "/testcases"):
    #     os.makedirs(problem_folder + "/testcases")

    problem_name = (' '.join(problem_code.split('_'))).title()

    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

    with open(os.path.join(template_path, 'statement.md')) as file_:
        template = Template(file_.read())
        statement = template.render(problem_name=problem_name, problem_code=problem_code)
        f = codecs.open(problem_folder + ("/%s.md" % problem_code), "w", "utf-8")
        f.write(statement)
        f.close()

    with open(os.path.join(template_path, 'testcases.txt')) as file_:
        template = Template(file_.read())
        content = template.render()
        f = open(problem_folder + "/testcases.txt", 'w')
        f.write(content)
        f.close()

    with open(os.path.join(template_path, 'testcases_manual.txt')) as file_:
        template = Template(file_.read())
        content = template.render()
        f = open(problem_folder + "/testcases_manual.txt", 'w')
        f.write(content)
        f.close()

    with open(os.path.join(template_path, 'solution.py.j2')) as file_:
        template = Template(file_.read())
        content = template.render(problem_code=problem_code)
        f = open(problem_folder + ("/%s.py" % problem_code), 'w')
        f.write(content)
        f.close()

    with open(os.path.join(template_path, 'generator.py.j2')) as file_:
        template = Template(file_.read())
        content = template.render(problem_code=problem_code)
        f = open(problem_folder + ("/%s_generator.py" % problem_code), 'w')
        f.write(content)
        f.close()

    problem_folder = os.path.abspath(problem_folder)

    CLog.important(f'Problem created at `{problem_folder}`')


def read_testcases_from_file(testcase_file):
    count = 0
    inputi = ""
    outputi = ""
    is_output = False

    testcases = []

    with open(testcase_file, 'r') as fi:
        for line in fi:
            if line.startswith("###"):

                if count > 0:
                    testcases.append({'input': inputi.strip(), 'output': outputi.strip()})

                count += 1

                is_output = False

                inputi = outputi = ""

                continue
            elif line.startswith("---"):
                is_output = True
            else:
                if is_output:
                    outputi += line
                else:
                    inputi += line
        if inputi.strip() or outputi.strip():
            testcases.append({'input': inputi.strip(), 'output': outputi.strip()})

    return testcases


def find_section(pattern, lines, start_index=0, once=False):
    indices = []
    content = {}
    for i in range(start_index, len(lines)):
        if re.match(pattern, lines[i], re.I):
            indices.append(i)
            for j in range(i + 1, len(lines)):
                if lines[j].startswith('#'):
                    break
                content.setdefault(i, [])
                content[i].append(lines[j])
            if once:
                break

    return indices, content


def fix_section_title(name, pattern, lines, replace, once=True):
    found = False
    for i in range(len(lines)):
        if re.match(pattern, lines[i], re.I):
            lines[i] = re.sub(pattern, replace, lines[i])
            CLog.info(f'AUTOFIX: Fix {name} heading style: ' + lines[i])
            found = True
            if once:
                break
    if not found:
        CLog.warn(f'AUTOFIX: {name} is probably missing, don\'t know how to fix it.')


def check_section(name, pattern, lines, proper_line, unique=True, start_index=0, log_error=True):
    lines, content = find_section(pattern, lines, start_index)
    if log_error:
        flog = CLog.error
    else:
        flog = CLog.warn
    if not lines:
        flog(f'{name} is missing or invalid: {name} should has style: `{proper_line}`')
        return None, None
    if unique and len(lines) > 1:
        CLog.error(f'Only one {name} allowed!')

    empty = True
    for isection in content:
        for line in content[isection]:
            if line.strip() and not line.startswith('[//]:'):
                empty = False
    if empty:
        flog(f'{name} is empty!')

    return lines[0], content


def check_problem(problem_folder, auto_fix=False):
    problem_code = os.path.basename(problem_folder.rstrip(os.path.sep))

    statement_file = os.path.join(problem_folder, f"{problem_code}.md")
    if not os.path.isfile(statement_file):
        statement_files = glob.glob(os.path.join(problem_folder, "*.md"))
        if len(statement_files) < 1:
            raise SyntaxError(f'Problem statement file `{problem_code}.md` is missing!')
        elif len(statement_files) == 1:
            statement_file = statement_files[0]
            problem_code = os.path.splitext(os.path.basename(statement_file))[0]
        else:
            bak_files = glob.glob(os.path.join(problem_folder, "*bak*.md"))
            print(bak_files)
            if len(statement_files) - 1 > len(bak_files):
                raise SyntaxError('Problem folder contains more than one .md files, '
                                  'and no files has same name as the containing folder, don\'t know what to do.')
            else:
                t = set(statement_files) - set(bak_files)
                statement_file = list(t)[0]
                problem_code = os.path.splitext(os.path.basename(statement_file))[0]
                CLog.info('Auto detect .md file: %s' % statement_file)

    solution_file = os.path.join(problem_folder, f"{problem_code}.py")
    test_generator_file = os.path.join(problem_folder, f"{problem_code}_generator.py")
    testcase_file = os.path.join(problem_folder, f"testcases.txt")
    testcase_manual_file = os.path.join(problem_folder, f"testcases_manual.txt")

    if not os.path.isfile(solution_file):
        CLog.error(f"Solution file `{problem_code}.py` is missing!")
    if not os.path.isfile(test_generator_file):
        CLog.error(f"Testcase generator file `{problem_code}_generator.py` is missing!")
    if not os.path.isfile(testcase_file):
        CLog.error(f"Testcases file `testcases.txt` is missing!")
    else:
        file_size = os.stat(testcase_file).st_size
        if file_size > 50 * 1024 * 1024:
            CLog.error(f"Testcases file `testcases.txt` should not be > 50MB!")

    if not os.path.isfile(testcase_manual_file):
        CLog.warn(f"Manual testcases file `testcases_manual.txt` is missing!")

    with open(statement_file) as fi:
        statement = fi.read()
        # print(statement)
        lines = statement.splitlines()

        if not lines[0].startswith('[//]: # ('):
            CLog.error('The first line should be the source of the problem, ex. `[//]: # (http://source.link)`')
            if auto_fix:
                i = 0
                while not lines[i].strip():
                    i += 1
                lines = lines[i:]
                if lines[0].startswith('[//]:'):
                    lines[0] = '[//]: # (%s)' % lines[0][5:].strip()
                    CLog.info("AUTOFIX: convert source info to: " + lines[0])
                else:
                    CLog.warn("AUTOFIX: Source info may be missed. Don't know how to fix it.")
                    lines.insert(0, '[//]: # ()')

        title_line, statement = check_section('Title', '# \S*', lines, '# Problem Title (heading 1)')
        if auto_fix and not title_line:
            heading_line, content = find_section(f'#.*{problem_code}', lines)
            proper_title = (' '.join(problem_code.split('_'))).title()
            if not heading_line:
                CLog.info('AUTOFIX: Problem title is probably missing, adding one...')
                title1 = f'# {proper_title}'
                title2 = f'[//]: # ({problem_code})'
                lines.insert(1, '')
                lines.insert(2, title1)
                lines.insert(3, title2)
                print(*lines[:4], sep='\n')
            else:  # has Title but wrong format
                lines[heading_line[0]] = f'# {proper_title}'
                if not lines[heading_line[0] + 1].startswith("[//]:"):
                    lines.insert(heading_line[0] + 1, f'[//]: # ({problem_code})')
                CLog.info('AUTOFIX: Fix Title style and problem code')

        if title_line:
            title = lines[title_line]
            proper_title = (' '.join(title.split('_'))).title()
            if title != proper_title:
                CLog.warn(f'Improper title: `{title}`, should be `{proper_title}`')
            # proper_problem_code = f'[//]: # ({problem_code})'
            if not lines[title_line + 1].startswith('[//]: # ('):
                CLog.error(f'Title should be followed by proper problem code: `problem_code`')

            if lines[title_line + 3].startswith("[//]:") and lines[0] == '[//]: # ()':
                CLog.warn('Detect source link in statement: %s' % lines[title_line + 3])
                if auto_fix:
                    CLog.info('AUTOFIX: Detect source link in statement: %s, moving to first line'
                              % lines[title_line + 3])
                    lines[0] = '[//]: # (%s)' % lines[title_line + 3][5:].strip()
                    lines.pop(title_line + 3)

        input_line, input = check_section('Input', '## Input\s*$', lines, '## Input')
        if input_line and title_line and input_line < title_line:
            CLog.error('Input should go after the Problem Statement.')

        if auto_fix and input_line is None:
            fix_section_title('Input', f'(#+\s*Input|Input\s*$)', lines, f'## Input')

        constraints_line, constraints = check_section('Constraints', '## Constraints\s*$',
                                                      lines, '## Constraints')
        if constraints_line and input_line and constraints_line < input_line:
            CLog.error('Constraints should go after the Input.')

        if auto_fix and constraints_line is None:
            fix_section_title('Constraints', f'(#+\s*Constraint.*|Constraints\s*$|#+\s*Giới hạn.*)', lines,
                              f'## Constraints')

        output_line, output = check_section('Output', '## Output\s*$', lines, '## Output')
        # if output_line and constraints_line and output_line < constraints_line:
        #     CLog.error('Output should go after the Constraints.')

        if auto_fix and output_line is None:
            fix_section_title('Output', f'(#+\s*Output.*|Output\s*$|#+\s*Ouput.*|Ouput\s*$)', lines, f'## Output')

        tag_line, tag = check_section('Tags', '## Tags\s*$', lines, '## Tags')
        if tag_line and output_line and tag_line < output_line:
            CLog.error('Tags should go after the Output.')

        if auto_fix and tag_line is None:
            fix_section_title('Tags', f'#+\s*Tag.*', lines, f'## Tags')

        difficulty_line, difficulty = check_section('Difficulty', '## Difficulty\s*$', lines, '## Difficulty')
        if difficulty_line:
            try:
                difficulty = float(difficulty[difficulty_line][0])
                if difficulty < 1 or difficulty > 10:
                    CLog.error('Difficulty should be a number between 1 and 10, found: ' + str(difficulty))
            except ValueError:
                CLog.error('Difficulty should be a number between 1 and 10, found: ' + difficulty[difficulty_line][0])

        if auto_fix and difficulty_line is None:
            fix_section_title('Difficulty', f'#+\s*Difficulty.*', lines, f'## Difficulty')

        list_lines, list_content = find_section('- .*', lines)
        for i in list_lines[::-1]:
            if i > 0:
                prev_line = lines[i - 1]
                if prev_line.strip() and not prev_line.startswith('- '):
                    CLog.error(f'There should be an empty line before the list, line {i}: {lines[i]}')
                    if auto_fix:
                        CLog.info('AUTOFIX: Added new line before list')
                        lines.insert(i, '')

        lines2, tmp = check_section('Sample input', '## Sample input', lines, '## Sample input 1', unique=False)
        if auto_fix and not lines2:
            fix_section_title('Sample Input', '#+\s*Sample input(.*)', lines, r'## Sample Input\1', once=False)

        lines2, tmp = check_section('Sample output', '## Sample output', lines, '## Sample output 1', unique=False)
        if auto_fix and not lines2:
            fix_section_title('Sample Output', '#+\s*Sample (ou|Ou|out|Out)put(.*)', lines, r'## Sample Output\2',
                              once=False)

        lines2, tmp = check_section('Explanation', '## Explanation', lines, '## Explanation 1',
                                    unique=False, log_error=False)
        if auto_fix and not lines2:
            fix_section_title('Explanation', '#+\s*Explanation(.*)', lines, r'## Explanation\1', once=False)

        if auto_fix:
            statement_file_bak = os.path.join(problem_folder, f"{problem_code}_bak.md")
            i = 1
            while os.path.exists(statement_file_bak):
                statement_file_bak = os.path.join(problem_folder, f"{problem_code}_bak{i}.md")
                i += 1
            copyfile(statement_file, statement_file_bak)
            with open(statement_file, 'w') as f:
                f.write('\n'.join(lines))
    return problem_code


if __name__ == '__main__':
    create_problem('../problems', 'Array001 Counting-Sort3', overwrite=True)

    # check_problem('/home/thuc/teko/online-judge/ptoolbox/problems/array001_counting_sort3')
    # check_problem('/home/thuc/teko/online-judge/dsa-problems/array1d/arr001_counting_sort', auto_fix=True)
    # check_problem('/home/thuc/teko/online-judge/dsa-problems/array1d/arr002_football', auto_fix=True)

    # print(re.sub('#+\s*Sample input(.*)', r'## Sample Input\1', '# Sample input 2'))

    # tcs = read_testcases_from_file('../problems/prob1/testcases.txt')
    # print(*tcs, sep='\n')
