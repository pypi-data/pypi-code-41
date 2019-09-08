import copy
import json
import pprint
import shutil
import time
from zipfile import ZipFile
import os

import requests
from dsa import dsa_problem_file
from dsa.dsa_problem import load_problem
from helpers.clog import CLog
from models.general_models import Problem


def chomp(s):
    # if s.endswith("\r\n"): return s[:-2]
    # if s.endswith("\n"): return s[:-1]
    return s.strip()


def save_testcase_file(testcase_folder, tc_number, tc_input, tc_output):
    inp_folder = os.path.join(testcase_folder, "input")
    out_folder = os.path.join(testcase_folder, "output")

    if not os.path.exists(inp_folder):
        os.makedirs(inp_folder)

    CLog.echo(f"Writing testcase #{tc_number}")
    CLog.echo("   input...")

    f = open(os.path.join(inp_folder, "input%02d.in" % tc_number), "w")
    f.write(tc_input)
    f.close()

    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    CLog.echo("   output...")
    f = open(os.path.join(out_folder, "output%02d.out" % tc_number), "w")
    f.write(tc_output)
    f.close()


def prepare_testcases_from_file(tc_file, testcase_output_folder, start_number=0):
    testcases = dsa_problem_file.read_testcases_from_file(tc_file)

    for i in range(len(testcases)):
        save_testcase_file(testcase_output_folder, start_number+i, testcases[i]['input'], testcases[i]['output'])

    return start_number + len(testcases)


def prepare_testcases(problem_folder, keep_zip_file_only=True):
    zipfilename = 'testcases_hackerrank.zip'
    testcase_output_folder = os.path.abspath(os.path.join(problem_folder, "testcases"))

    if os.path.exists(os.path.join(testcase_output_folder, zipfilename)):
        CLog.warn('`testcases.zip` file existed, will be overwritten.')

    testcase_file = os.path.abspath(os.path.join(problem_folder, "testcases_manual.txt"))

    count = 0
    if not os.path.exists(testcase_file):
        CLog.warn(f'`{testcase_file}` file not existed, skipping...')
    else:
        count = prepare_testcases_from_file(testcase_file, testcase_output_folder, count)

    testcase_file = os.path.abspath(os.path.join(problem_folder, "testcases.txt"))
    if not os.path.exists(testcase_file):
        CLog.warn(f'`{testcase_file}` file not existed, skipping...')
    else:
        count = prepare_testcases_from_file(testcase_file, testcase_output_folder, count)

    print("DONE")

    if count:
        zip_test_cases(problem_folder, count, zipfilename)

        if keep_zip_file_only:
            CLog.echo(f"Deleting intermediate files...")
            shutil.rmtree(testcase_output_folder)
            print("DONE")
    else:
        CLog.error(f'No testcases found in {os.path.abspath(problem_folder)}')

    return count


def zip_test_cases(problem_folder, count, zipfilename):
    problem_folder = os.path.abspath(os.path.join(problem_folder, "testcases"))
    zipfile = os.path.join(problem_folder, '..', zipfilename)
    print(f"creating `{os.path.abspath(zipfile)}`")

    os.chdir(problem_folder)
    with ZipFile(zipfile, 'w') as myzip:
        for i in range(count):
            myzip.write("input/input%02d.in" % i)
            myzip.write("output/output%02d.out" % i)

    print("DONE")


class HackerRank:
    def __init__(self):
        self.username = None
        self.csrf_token = None
        self.s = requests.session()
        self._headers = {
            'origin': 'https://www.hackerrank.com',
            'referer': 'https://www.hackerrank.com/dashboard',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/70.0.3538.77 Safari/537.36',
        }

    @staticmethod
    def get_csrf(html):
        s = 'name="csrf-token"'
        i = html.find(s)
        if i < 0:
            raise ValueError('Cannot get csrf token')

        i = html[:i].rfind('<meta')
        i = html.find('content="', i + 1)
        i += len('content="')
        j = html.find('"', i + 1)
        csrf = html[i: j]
        if not csrf:
            raise ValueError('Cannot get csrf token')
        return csrf

    def login(self, username, password):
        url = 'https://www.hackerrank.com/rest/auth/login'

        headers = copy.deepcopy(self._headers)
        # headers['content-type'] = 'application/json' # automatically overwrite when set json = python dict

        r = self.s.get('https://www.hackerrank.com/auth/login', headers=headers)

        data = {
            "login": username,
            "password": password,
            "remember_me": False,
            "fallback": False
        }
        self.csrf_token = HackerRank.get_csrf(r.text)
        # print("csrf:", self.csrf_token)
        headers['x-csrf-token'] = self.csrf_token
        r = self.s.post(url, json=data, headers=headers)

        print(r.status_code)
        # print(r.headers)
        # print(r.text)
        raw = r.json()
        print(raw)

        if raw['status']:
            # print('Login succeeded, csrf token: {}'.format(raw['csrf_token']))
            CLog.important('Login succeeded')
            self.username = username
            self.csrf_token = raw['csrf_token']
        else:
            raise ValueError("Login failed with user: {}".format(username))

        # res = r.json()origin
        # print(res)

        return True

    def get_raw_track(self, track_url, offset=0, limit=10, save_to_file=None):
        # hackkerrank chi co lay 50 cai 1
        size = min(limit, 50)
        i = 0
        print(size, limit)

        raw_track = None
        while i < limit:
            url = track_url + '?offset={}&limit={}'.format(offset, min(limit - i, size))
            headers = copy.deepcopy(self._headers)
            print("get url: " + url)
            r = self.s.get(url, headers=headers)

            # print(r.text)

            raw = r.json()
            if len(raw['models']) < 1:
                break

            if i == 0:
                raw_track = raw
            else:
                raw_track['models'].extend(raw['models'])

            offset += 50
            i += min(limit - i, size)

        if save_to_file:
            with open(save_to_file, 'w') as outfile:
                json.dump(raw_track, outfile)

        return raw_track

    @staticmethod
    def load_raw_track_from_file(filename):
        with open(filename) as f:
            return json.load(f)

    @staticmethod
    def parse_track(raw_track):
        hkr_track = HackerRankTrack()
        hkr_track.total = raw_track['total']
        if 'current_track' in raw_track:
            d = raw_track['current_track']
            hkr_track.src_id = d['id']
            hkr_track.name = d['name']
            hkr_track.slug = d['slug']
            hkr_track.descriptions = d['descriptions']

        hkr_track.problems = raw_track['models']
        hkr_track.problems = []
        for raw_prob in raw_track['models']:
            problem = Problem()
            problem.src_id = raw_prob['id']
            problem.name = raw_prob['name']
            problem.slug = raw_prob['slug']
            problem.category = raw_prob['category']
            problem.type = raw_prob['kind']
            problem.preview = raw_prob['preview']
            problem.tags = raw_prob['tag_names']
            problem.topics = raw_prob['topics']
            problem.hints = raw_prob['hints']
            problem.difficulty = raw_prob['difficulty']
            problem.difficulty_level = raw_prob['difficulty_name']
            problem.contest_slug = raw_prob['contest_slug']
            problem.total_count = raw_prob['total_count']
            problem.solved_count = raw_prob['solved_count']
            problem.success_ratio = raw_prob['success_ratio']
            problem.track = HackerRankTrack('', raw_prob['track']['id'], raw_prob['track']['name'],
                                            raw_prob['track']['slug'])

            hkr_track.problems.append(problem)
        return hkr_track

    def get_problem(self, problem_slug):
        url = 'https://www.hackerrank.com/rest/contests/master/challenges/{}/'.format(problem_slug)
        headers = copy.deepcopy(self._headers)
        r = self.s.get(url, headers=headers)

        print(r.text)

        raw = r.json()
        # problem = self.parse_problem(raw)
        return raw

    def submit(self, problem_slug, language, code, compile_test=True, custominput=None):
        contest_slug = 'master'  # TODO: change this
        if compile_test:
            url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}/compile_tests'.format(contest_slug,
                                                                                                   problem_slug)
        else:
            url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}/submissions'.format(contest_slug,
                                                                                                 problem_slug)

        headers = copy.deepcopy(self._headers)
        headers['x-csrf-token'] = self.csrf_token
        # TODO: https://www.hackerrank.com/contests/{}/challenges/{}.format(contest_slug, problem_slug)
        headers['referer'] = 'https://www.hackerrank.com/challenges/{}/problem'.format(problem_slug)

        data = {
            "code": code,
            "language": language,
            "playlist_slug": '',
        }

        if compile_test:
            if custominput:
                data["customtestcase"] = True
                data['custominput'] = custominput
            else:
                data["customtestcase"] = False
        else:  # real submission
            data["contest_slug"] = 'master'

        print('sending submission:', url)
        print(headers)

        r = self.s.post(url, json=data, headers=headers)

        print(r.text)

        raw = r.json()
        if not raw['status']:
            return None
        # problem = self.parse_problem(raw)
        return raw['model']['id']

    def check_submission_result(self, problem_slug, submission_id, compile_test=True, interval=1):
        contest_slug = 'master'  # TODO: change this

        count = 0
        while count < 10:
            time.sleep(interval)
            count += 1
            if compile_test:
                url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}/compile_tests/{}' \
                    .format(contest_slug, problem_slug, submission_id)
            else:
                url = 'https://www.hackerrank.com/rest/contests/{}/challenges/{}/submissions/{}' \
                    .format(contest_slug, problem_slug, submission_id)

            headers = copy.deepcopy(self._headers)
            print('Checking %d... %s' % (count, url))
            r = self.s.get(url, headers=headers)

            print(r.text)

            raw = r.json()
            # see hackerrank-sample-compile-result-*.json for examples
            if compile_test and raw['model']['status'] == 1:  # compile_test mode
                return raw

            if not compile_test and raw['model']['status_code'] == 1:  # judge mode
                return raw

        return None

    def create_problem(self, problem):
        url = 'https://www.hackerrank.com/rest/administration/challenges'

        headers = copy.deepcopy(self._headers)
        headers['x-csrf-token'] = self.csrf_token
        headers['referer'] = 'https://www.hackerrank.com/administration/challenges/create'

        data = {
            "name": problem.name,
            "preview": problem.preview,
            "problem_statement_fields": {
                'problem_statement': problem.statement,
                'input_format': problem.input_format,
                'constraints': problem.constraints,
                'output_format': problem.output_format,
            },
            # "tags": ["basic"],
            "tags": problem.tags,
        }

        print('creating problem:')
        print(data)

        r = self.s.post(url, json=data, headers=headers)
        print(r.status_code)
        print(r.headers)
        print(r.text)

        raw = r.json()
        if not raw['status']:
            print(raw['errors'])
            raise ValueError("Cannot create challenge")
        # problem = self.parse_problem(raw)
        problem.src_id = raw['model']['id']
        problem.slug = raw['model']['slug']
        CLog.important(f'Hackerrank problem created: {problem.src_id} slug: {problem.slug}')
        return raw['model']

    @staticmethod
    def parse_problem(raw_problem):
        r = raw_problem['model']
        problem = Problem()
        problem.src_id = r['id']
        problem.name = r['name']
        problem.slug = r['slug']
        problem.preview = r['preview']
        problem.type = r['kind']
        problem.languages = r['languages']
        problem.public_test_cases = r['public_test_cases']
        problem.public_solutions = r['public_solutions']
        problem.difficulty = r['difficulty']
        return problem

    def update_problem(self, problem_id, problem):
        url = 'https://www.hackerrank.com/rest/administration/challenges/{}'.format(problem_id)

        headers = copy.deepcopy(self._headers)
        headers['x-csrf-token'] = self.csrf_token
        headers['referer'] = 'https://www.hackerrank.com/administration/challenges/create'

        data = {
            "name": problem.name,
            "id": problem_id,
            'difficulty': problem.difficulty,
            "preview": problem.preview,
            "problem_statement_fields": {
                'problem_statement': problem.statement,
                'input_format': problem.input_format,
                'constraints': problem.constraints,
                'output_format': problem.output_format,
            },
            'slug': problem.slug,
            "tags": problem.tags,
            'public_solutions': problem.public_solutions,
            'public_test_cases': problem.public_test_cases,
            'translation_language': 'English'
        }

        print('updating problem:')
        print(data)

        r = self.s.put(url, json=data, headers=headers)

        print(r.text)

        raw = r.json()
        if not raw['status']:
            print(raw['errors'])
            raise ValueError("Cannot create challenge")
        # problem = self.parse_problem(raw)

        if problem.languages:
            url = 'https://www.hackerrank.com/rest/administration/challenges/{}/allowed_languages'\
                .format(problem.src_id)
            data = []
            for lang in problem.languages:
                data.append(('languages[]', lang))
            print('updating languages:')
            print(data)
            r1 = self.s.put(url, data=data, headers=headers)
            if r1.json()[0] != 'ok':
                print(r1.text)
                raise ValueError('Cannot set allowed languages')
        return raw['model']

    def upload_testcases(self, problem_id, zip_file_path):
        """

        :param problem_id:
        :param zip_file_path:
        :return: list of created hackerrank testcases
        [
           {
              "id":1161797,
              "challenge_id":113357,
              "input":"input00.txt",
              "output":"output00.txt",
              "score":10.0,
              "sample":false,
              "tag":null,
              "input_size":10,
              "output_size":2,
              "additional":null,
              "h_input_size":"10 Bytes",
              "h_output_size":"2 Bytes",
              "explanation":null
           },
           {
              "id":1161798,
              "challenge_id":113357,
              "input":"input01.txt",
              "output":"output01.txt",
              "score":10.0,
              "sample":false,
              "tag":null,
              "input_size":9,
              "output_size":1,
              "additional":null,
              "h_input_size":"9 Bytes",
              "h_output_size":"1 Byte",
              "explanation":null
           }
        ]
        """
        url = 'https://www.hackerrank.com/rest/administration/challenges/{}/test_cases/upload_zip'.format(problem_id)

        headers = copy.deepcopy(self._headers)
        headers['x-csrf-token'] = self.csrf_token
        headers['referer'] = 'https://www.hackerrank.com/administration/challenges/edit/{}/testcases'.format(problem_id)

        files = {'zip_file': ('testcases.zip', open(zip_file_path, 'rb'), 'application/zip')}
        print('uploading file: ', files)
        r = self.s.post(url, files=files, headers=headers)

        print(r.text)
        raw = r.json()
        if not raw['status']:
            print(raw['errors'])
            raise ValueError("Error uploading test cases")
        return raw['models']

    def update_testcases_score(self, problem_id, testcase_ids, score=100, sample_ids=None):
        """

        :param problem_id:
        :param testcase_ids:
        :param score:
        :param sample_ids: list of testcase ids to mark as sample
        :return:
        """
        url = 'https://www.hackerrank.com/rest/administration/challenges/{}/test_cases/{}'\
            .format(problem_id, ','.join([str(t) for t in testcase_ids]))
        print('Updating testcase score... {}'.format(url))

        changes = {
            'auto_generate_sample_cases': True,
            'test_cases': dict()
        }

        for t in testcase_ids:
            is_sample = True if t in sample_ids else False
            changes['test_cases'][t] = {
                'sample': is_sample,
                'additional': False,
                'score': 0 if is_sample else score
            }

        data = {
            'changes': json.dumps(changes)
        }

        print(data)

        headers = copy.deepcopy(self._headers)
        headers['x-csrf-token'] = self.csrf_token
        headers['referer'] = 'https://www.hackerrank.com/administration/challenges/edit/{}/testcases'.format(problem_id)

        r = self.s.put(url, data=data, headers=headers)
        print(r.text)

        raw = r.json()
        if not raw['status']:
            print(raw['errors'])
            raise ValueError("Error updating testcases")
        return raw['models']

    def upload_testcases_and_set_score(self, problem_id, zip_file_path, score=100, sample_test_count=1):
        testcases = self.upload_testcases(problem_id, zip_file_path)
        testcase_ids = [t['id'] for t in testcases]
        sample_ids = [testcase_ids[i] for i in range(min(len(testcase_ids), sample_test_count))]
        print('testcase_ids:', testcase_ids)
        print('sample_ids:', testcase_ids)
        return self.update_testcases_score(problem_id, testcase_ids, score, sample_ids)


class HackerRankTrack:
    def __init__(self, url=None, track_id=None, name=None, slug=None, descriptions=None):
        self.src_id = track_id
        self.name = name
        self.slug = slug
        self.descriptions = descriptions
        self.url = url
        self.problems = []
        self.problem_count = 0
        self.total = 0

    def __str__(self):
        self.problem_count = len(self.problems)
        tmp = copy.deepcopy(self)
        tmp.problems = None
        return pprint.pformat(vars(tmp), indent=2)

    @staticmethod
    def track_list():
        tracks = [
            HackerRankTrack('https://www.hackerrank.com/rest/contests/master/tracks/algorithms/challenges'),
            HackerRankTrack('https://www.hackerrank.com/rest/contests/master/tracks/data-structures/challenges')
        ]
        return tracks


if __name__ == "__main__":
    # prepare_testcases("../problems/prob1", True)
    hr = HackerRank()
    hr.login('thucngch', '15041985')

    problem_dir = '/home/thuc/teko/online-judge/ptoolbox/problems/array001_counting_sort3'

    problem1 = load_problem(problem_dir)

    problem1 = hr.update_problem('113357', problem1)
    # problem1 = hr.create_problem(problem1)
    # print('HackerrankID:', problem1.src_id)
    # 113357

    prepare_testcases(problem_dir)
    testcase_zip = os.path.join(problem_dir, 'testcases_hackerrank.zip')
    created_testcases = hr.upload_testcases_and_set_score('113357', testcase_zip, 50, 4)

