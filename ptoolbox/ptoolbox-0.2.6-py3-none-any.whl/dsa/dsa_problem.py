import os

from dsa.dsa_problem_file import check_problem, find_section
from models.general_models import Problem, TestCase


def join_lines(lines):
    return ''.join([l+'\n' for l in lines]).strip()


def load_problem(problem_folder):
    problem_code = check_problem(problem_folder)
    statement_file = os.path.join(problem_folder, f"{problem_code}.md")

    problem = Problem()
    problem.slug = problem_code.replace('_', '-')
    problem.code = problem_code
    problem.preview = f'[//]: # ({problem_code})'

    with open(statement_file) as fi:
        statement = fi.read()
        lines = statement.splitlines()

        source_link = None
        s = lines[0]
        if not s.strip():
            s = lines[1]
        if s.startswith('[//]:'):
            o = s.find('(')
            if o:
                source_link = s[o+1:s.find(')')].strip()
            else:
                source_link = s[5:].strip()
        problem.src_url = source_link

        statement_i, statement_c = find_section('#\s+.*', lines)
        if statement_i:
            title = lines[statement_i[0]][1:].strip()
            problem.name = title

            s = lines[statement_i[0]+1].strip()
            if not s.strip():
                s = lines[statement_i[0]+2]
            if s.startswith('[//]:'):
                problem.preview = s
                o = s.find('(')
                if o:
                    code = s[o + 1:s.find(')')].strip()
                else:
                    code = s[5:].strip()
                problem.code = code
                problem.slug = problem.code.replace('_', '-')

        if statement_i:
            problem.statement = join_lines(statement_c[statement_i[0]])

        input_i, input_c = find_section('(#+\s*Input|Input\s*$)', lines)
        if input_i:
            problem.input_format = join_lines(input_c[input_i[0]])

        output_i, output_c = find_section('(#+\s*Output.*|Output\s*$|#+\s*Ouput.*|Ouput\s*$)', lines)
        if output_i:
            problem.output_format = join_lines(output_c[output_i[0]])

        constraints_i, constraints_c = find_section('(#+\s*Constraint.*|Constraints\s*$|#+\s*Giới hạn.*)', lines)
        if constraints_i:
            problem.constraints = join_lines(constraints_c[constraints_i[0]])

        tags_i, tags_c = find_section('#+\s*Tag.*', lines)
        if tags_i:
            tags = []
            for t in tags_c[tags_i[0]]:
                t = t.strip()
                if t:
                    if t.startswith('-'):
                        tags.append(t[1:].strip())
                    else:
                        tags.append(t)
            problem.tags = problem.topics = tags

        difficulty_i, difficulty_c = find_section('#+\s*Difficulty.*', lines)
        if difficulty_i:
            problem.difficulty = float(difficulty_c[difficulty_i[0]][0])

        sample_input_i, sample_input_c = find_section('#+\s*Sample input(.*)', lines)
        sample_output_i, sample_output_c = find_section('#+\s*Sample (ou|Ou|out|Out)put(.*)', lines)
        explanation_i, explanation_c = find_section('#+\s*Explanation(.*)', lines)
        if sample_input_i:
            for i in range(len(sample_input_i)):
                testcase = TestCase()
                testcase.input = join_lines(sample_input_c[sample_input_i[i]]).strip('`').strip()
                testcase.output = join_lines(sample_output_c[sample_output_i[i]]).strip('`').strip()
                if len(explanation_i)>i:
                    testcase.explanation = join_lines(explanation_c[explanation_i[i]]).strip('`').strip()

                problem.testcases.append(testcase)

    solution_file = os.path.join(problem_folder, f"{problem_code}.py")
    if os.path.isfile(solution_file):
        with open(solution_file) as f:
            problem.solution = f.read()
    return problem


def save_problem(problem, base_folder):
    """
    :param problem:
    :param base_folder: the parent folder that will contain the problem folder
    :return:
    """


if __name__ == "__main__":
    # load_problem('/home/thuc/teko/online-judge/dsa-problems/number_theory/num001_sumab')
    # load_problem('/home/thuc/teko/online-judge/dsa-problems/unsorted/minhhhh/m010_odd_to_even')
    # problem = load_problem('/home/thuc/teko/online-judge/ptoolbox/problems/array001_counting_sort3')
    dsa_problem = load_problem('/home/thuc/teko/online-judge/dsa-problems/number_theory/num001_sumab')
    print(dsa_problem.prints())

