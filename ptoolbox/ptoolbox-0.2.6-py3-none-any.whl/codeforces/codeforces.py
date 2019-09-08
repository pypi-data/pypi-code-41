import copy

import requests
import tomd
from bs4 import BeautifulSoup
from dsa.dsa_problem import save_problem

from helpers.clog import CLog
from models.general_models import Problem, TestCase


def to_markdown(html):
    html = html.replace("$$$", "$")
    soup = BeautifulSoup(html, 'html.parser')
    bold = soup.select('.tex-font-style-bf')
    for tag in bold:
        tag.name = 'strong'
        tag.attrs = {}
    tt = soup.select('.tex-font-style-tt')
    for tag in tt:
        tag.name = 'code'
        tag.attrs = {}
    tt = soup.select('.tex-font-style-it')
    for tag in tt:
        tag.name = 'i'
        tag.attrs = {}
    return tomd.convert(soup.decode()).strip()


class Codeforces:
    def __init__(self):
        self.s = requests.session()
        self._headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        }
        self.csrf = ''

    def get_problem_list(self, page_index):
        url = f'https://codeforces.com/problemset/page/{page_index}'

        headers = copy.deepcopy(self._headers)
        r = self.s.get(url, headers=headers)

        raw = r.text
        # print(raw)

        soup = BeautifulSoup(raw, 'html.parser')
        self.csrf = soup.select('span.csrf-token')[0]['data-csrf']
        print('CSRF:', self.csrf)

        pagination = soup.select('div.pagination > ul > li')
        last_page = pagination[-2]
        # print(last_page)
        last_page_index = int(last_page.select('span.page-index')[0]['pageindex'])
        if page_index>last_page_index:
            CLog.warn(f'Overpass last page: #{page_index}/{last_page_index}')
            return [], last_page_index
        CLog.info(f'Getting problem list from page: #{page_index}/{last_page_index}')

        problem_tags = soup.select('table.problems > tr')[1:] # remove header line
        print(len(problem_tags))
        # print(problem_tags[0])

        problems = []
        for problem_tag in problem_tags:
            problem = Problem()
            pid = problem_tag.select('td.id a')[0]

            problem.src_id = pid.text.strip()
            problem.src_url = 'https://codeforces.com' + pid['href']

            ptitle = problem_tag.select('td')[1].select('div')[0]
            problem.name = ptitle.select('a')[0].text.strip()

            ptags = problem_tag.select('td')[1].select('div')[1].select('a')
            for ptag in ptags:
                tag = ptag.text.strip()
                problem.tags.append(tag)

            difficulty = problem_tag.select('td')[3].select('span')
            if difficulty:
                difficulty = difficulty[0].text.strip()
                difficulty = int(difficulty) ** 0.5
                dmax = 3800 ** 0.5
                dmin = 250 ** 0.5

                difficulty = (difficulty - dmin)/(dmax-dmin) * 10
            else:
                difficulty = 0

            problem.difficulty = difficulty

            submission_url = problem_tag.select('td')[4].select('a')
            if submission_url:
                problem.src_status_url = 'https://codeforces.com' + submission_url[0]['href']

            problems.append(problem)

            # print(problem.name)
            # print(problem.src_id)
            # print(problem.src_url)
            # print(problem.tags)
            # print(problem.difficulty)
            # break
        return problems, last_page_index

    def get_problem_detail(self, problem):
        url = problem.src_url
        headers = copy.deepcopy(self._headers)
        r = self.s.get(url, headers=headers)
        raw = r.text
        soup = BeautifulSoup(raw, 'html.parser')
        problem_statement = soup.select('div.problem-statement')[0]
        # print(problem_statement)

        limit_time = problem_statement.select('div.time-limit')[0]
        limit_time.select('div')[0].extract()
        problem.limit_time = int(''.join(c for c in limit_time.text if c in '0123456789')) * 1000

        limit_memory = problem_statement.select('div.memory-limit')[0]
        limit_memory.select('div')[0].extract()
        # problem.limit_memory = limit_memory.text
        problem.limit_memory = int(''.join(c for c in limit_memory.text if c in '0123456789'))

        input_type = problem_statement.select('div.input-file')[0]
        input_type.select('div')[0].extract()
        problem.input_type = input_type.text

        output_type = problem_statement.select('div.output-file')[0]
        output_type.select('div')[0].extract()
        problem.output_type = output_type.text

        if problem.input_type.strip() == 'standard input':
            problem.input_type = 'stdin'
        if problem.output_type.strip() == 'standard output':
            problem.output_type = 'stdout'

        problem_statement.select('div.header')[0].extract()

        input_format = problem_statement.select('div.input-specification')[0]
        input_format.select('div.section-title')[0].extract()
        problem.input_format = input_format.decode_contents()
        input_format.extract()


        output_format = problem_statement.select('div.output-specification')[0]
        output_format.select('div.section-title')[0].extract()
        problem.output_format = output_format.decode_contents()
        output_format.extract()

        sample_tests = problem_statement.select('div.sample-tests')[0]
        inputs = [t.text.strip() for t in sample_tests.select('div.input > pre')]
        outputs = [t.text.strip() for t in sample_tests.select('div.output > pre')]
        sample_tests.extract()

        for i in range(len(inputs)):
            testcase = TestCase(inputs[i], outputs[i])
            problem.testcases.append(testcase)

        problem.statement = problem_statement.select('div:not([class])')[0].decode_contents()

        note = problem_statement.select('div.note')
        if note:
            note = note[0]
            note.select('div.section-title')[0].extract()
            explanations = note.select('p')
            for i in range(len(inputs)):
                if i<len(explanations):
                    problem.testcases[i].explanation = to_markdown(explanations[i].decode())

            note.extract()

        problem.statement = to_markdown(problem.statement)
        problem.input_format = to_markdown(problem.input_format)
        problem.output_format = to_markdown(problem.output_format)
        problem.constraints = 'See inline constraints in the input description'

        print(problem.name, problem.limit_time, problem.limit_memory, problem.input_type,
              problem.output_type, problem.src_status_url, sep=' - ')
        # print('=====')
        # print(problem.statement)
        # print('=====')
        # print(problem.input_format)
        # print('=====')
        # print(problem.output_format)
        # print('=====')
        # print(problem.tags)
        # print('=====')
        # print(problem.difficulty)
        # print('=====')
        # for t in problem.testcases:
        #     print(t)
        #     print('----')

        submissions_cpp = self.get_submission_list(problem, 'cpp.g++11')
        submissions_fpc = self.get_submission_list(problem, 'pas.fpc')
        submissions_py3 = self.get_submission_list(problem, 'python.3')

        problem.testcases_sample = problem.testcases
        problem.testcases = []
        if submissions_cpp:
            solution_cpp, testcases = self.get_solution(submissions_cpp[0]['url'], True)
            problem.solutions.append({'lang': '11.cpp', 'code': solution_cpp})
            for testcase in testcases:
                problem.testcases.append(testcase)
            print("Total new testcases:", len(testcases))
            print("Total problem testcases:", len(problem.testcases))
            print("Total problem sample testcases:", len(problem.testcases_sample))
        if submissions_fpc:
            solution_fpc, tmp = self.get_solution(submissions_cpp[0]['url'])
            problem.solutions.append({'lang':'pas', 'code': solution_fpc})
        if submissions_py3:
            submissions_py3, tmp = self.get_solution(submissions_cpp[0]['url'])
            problem.solutions.append({'lang':'py', 'code': submissions_py3})

        print("Solutions:", problem.solutions)

        # save_problem(dsa_problem, '../problems')

        return problem

    def get_submission_list(self, problem, language='anyProgramTypeForInvoker'):
        if not problem.src_status_url:
            return []

        headers = copy.deepcopy(self._headers)
        frameProblemIndex = problem.src_status_url[problem.src_status_url.rfind('/')+1:]
        data = {
            'csrf_token': self.csrf,
            'frameProblemIndex': frameProblemIndex,
            'action': 'setupSubmissionFilter',
            'comparisonType': 'NOT_USED',
            'verdictName': "OK",
            'programTypeForInvoker': language,
            # 'programTypeForInvoker': "pas.fpc",
            # 'programTypeForInvoker': "python.3",
            # 'programTypeForInvoker': "cpp.g++11",
            # 'programTypeForInvoker': "cpp.g++14",
            # 'programTypeForInvoker': "cpp.g++17",
            # 'programTypeForInvoker': "java8",
            # '_tta': 248
        }
        # print(data)
        r = self.s.post(problem.src_status_url, headers=headers, data=data)
        #
        # print(r.status_code)
        # print(r.text)
        #
        # r = self.s.get(problem.src_status_url, headers=headers)

        raw = r.text
        # print(raw)

        soup = BeautifulSoup(raw, 'html.parser')

        submissions = soup.select('table.status-frame-datatable > tr[data-submission-id]')
        # print(submissions)
        # print(len(submissions))
        # problem.solutions
        result = []
        for submit in submissions:
            submission_url = 'https://codeforces.com/' + submit.select('td')[0].select('a')[0]['href']
            submission_problem = submit.select('td')[3].select('a')[0]['href']
            submission_language = submit.select('td')[4].text.strip()
            submission_status = submit.select('td')[5].select('span > span')[0].text.strip()
            submission_time = submit.select('td')[6].text.strip().replace('\xa0', ' ')
            submission_memory = submit.select('td')[7].text.strip().replace('\xa0', ' ')
            submission = {
                'url': submission_url,
                'problem': submission_problem,
                'lang': submission_language,
                'verdict': submission_language,
                'status': submission_status,
                'time': submission_time,
                'memory': submission_memory,
            }
            # print(submission)
            result.append(submission)
            # problem.solutions.append(submission)
        return result

    def get_solution(self, submission_url, get_test_cases=False):
        headers = copy.deepcopy(self._headers)
        r = self.s.get(submission_url, headers=headers)
        raw = r.text
        soup = BeautifulSoup(raw, 'html.parser')
        # print(raw)
        source_code = soup.select('pre#program-source-text')[0].text
        # print(source_code)
        if not get_test_cases:
            return source_code, []

        testcases = []
        testcase_tags = soup.select('div.roundbox')
        for testcase_tag in testcase_tags:
            input_tag = testcase_tag.select('div.input-view')
            if not input_tag:
                continue
            input_data = input_tag[0].select('div.text > pre')[0].text.strip()
            output_data = testcase_tag.select('div.answer-view')[0].select('div.text > pre')[0].text.strip()
            if input_data.endswith('...') or output_data.endswith('...'): # uncompleted test data
                continue
            testcases.append(TestCase(input_data, output_data))

        return source_code, testcases


if __name__ == '__main__':
    cf = Codeforces()
    problems, page_count = cf.get_problem_list(1)
    CLog.info("Number of pages: %s" % page_count)

    for i in range(len(problems)):
        tags = ', '.join(problems[i].tags)
        print(f'#{i+1} - {problems[i].src_id} - {problems[i].name} - {problems[i].difficulty}'
              f' - {problems[i].src_url} - {tags}')
        break

    dsa_problem = cf.get_problem_detail(problems[4])


