import copy
import pprint
from enum import Enum


class ProblemType(Enum):
    code = "code"
    bugfix = "bugfix"
    recover = "recover"


class ProblemStatus(Enum):
    draft = 0
    published = 1
    scheduled = 10


class ProgrammingLanguage(Enum):
    python3 = "python3"
    pascal = "pascal"
    cpp = 'cpp'

    unknown = "-1"


class ProblemDifficulty(Enum):
    unknown = "Unknown"
    trivial = "Trivial"
    easy = "Easy"
    easy_medium = "Easy-Medium"
    medium = "Medium"
    medium_hard = "Medium-Hard"
    hard = "Hard"
    super_hard = "Super-Hard"


class JudgeMode(Enum):
    manual = 0
    oj = 1  # input - output
    soj = 2  # special jugde
    unit_test = 3
    quiz = 10  # test question


class MatchingType(Enum):
    flexible = 1
    strict = 2
    regexp = 10


class TestCase:
    def __init__(self, input="", output="", matchingtype=MatchingType.flexible):
        self.name = ""
        self.input = input
        self.output = output
        self.src_id = ""
        self.matching_type = matchingtype
        self.input_size = self.output_size = 0
        self.input_hash = self.output_hash = ''
        self.explanation = ''
        self.sample = False
        self.score = 0

    def __str__(self):
        s = ''
        # s += "src_id: " + str(self.src_id) + "\n"
        # s += "matching type: " + str(self.matching_type) + "\n"
        s += "input:\n" + self.input + "\n"
        s += "output:\n" + self.output + "\n"
        s += "explanation:\n" + self.explanation
        return s


class Problem:
    def __init__(self):
        self.src_id = ""
        self.src_url = ""
        self.src_status_url = ""
        self.src_data = None
        self.input_type = 'stdin'
        self.output_type = 'stdout'
        self.limit_time = 10000 # ms
        self.limit_memory = 256 # MB
        self.name = ""
        self.slug = ""
        self.code = ""
        self.type = ProblemType.code
        self.template = ""  # editor template
        self.preview = ""
        self.statement = self.src_id = ""
        self.input_format = self.constraints = self.output_format = ""
        self.judge_mode = JudgeMode.oj
        self.testcases_sample = []
        self.testcases = []
        self.language = ProgrammingLanguage.unknown
        self.solution = None
        self.hint = None
        self.category = None
        self.editorial = None
        self.contest_slug = None    # hackerrank specific
        self.topics = []
        self.tags = []
        self.experience_gain = 0
        self.difficulty = 0.0
        self.difficulty_level = ProblemDifficulty.easy
        self.total_count = self.solved_count = self.success_ratio = 0

        self.public_test_cases = False
        self.public_solutions = False
        self.languages = []
        self.solutions = []  # list of solution for each language
        self.hints = []  # list of hint for each language
        self.track = None # hackerrank specific

    def prints(self):
        s = ''
        if self.src_url:
            s += '[//]: {}\n'.format(self.src_url)

        s += '\n# {}\n\n'.format(self.name)
        s += '\n{}\n\n'.format(self.slug)

        s += '\n*Type: {}, Difficulty: {} ({})*'.format(str(self.type), self.difficulty, self.difficulty_level)

        s += '\n\n{}'.format(self.statement)
        s += '\n\n## Input'
        s += '\n{}'.format(self.input_format)
        s += '\n\n## Constraints'
        s += '\n{}'.format(self.constraints)
        s += '\n\n## Output'
        s += '\n{}'.format(self.output_format)

        s += '\n\n## Tags'
        s += '\n{}'.format(self.tags)

        s += '\n\n## Testcases: {}'.format(len(self.testcases))

        if self.testcases and len(self.testcases)>0:
            s += '\n\n## Sample Input'
            s += '\n```\n{}\n```'.format(self.testcases[0].input)
            s += '\n\n## Sample Output'
            s += '\n```\n{}\n```\n'.format(self.testcases[0].output)
            if self.testcases[0].explanation:
                s += '\n\n## Explanation'
                s += '\n```\n{}\n```\n'.format(self.testcases[0].explanation)

        if self.solution:
            s += '\n\n## Solution'
            s += '\n```\n{}\n```'.format(self.solution)
        return s

    def __str__(self):
        # s = "src_id: " + str(self.src_id) + "\n"
        # s += "Name: " + self.name + "\n"
        # s += "Judge mode: " + str(self.judge_mode) + "\n"
        # s += "Statement: \n"
        # s += self.statement
        # s += "\nNo of testcases: " + str(len(self.testcases))
        # s += "\nSolution: \n{}\n".format(self.solution)
        self.testcases_count = len(self.testcases)
        tmp = copy.deepcopy(self)
        tmp.testcases = None
        return pprint.pformat(vars(tmp), indent=2)


class Classroom:
    def __init__(self):
        self.src_id = ""
        self.name = ""
        self.language = ProgrammingLanguage.unknown
        self.students = []
        self.student_invites = []
        self.self_learners = []
        self.assignments = []
        self.scheduled_assignments = []
        self.draft_assignments = []

    def __str__(self):
        s = "src_id: " + str(self.src_id) + "\n"
        s += "Name: " + self.name + "\n"
        s += "Language: " + str(self.language)
        s += "\nNo of students: " + str(len(self.students))
        s += "\nNo of student_invites: " + str(len(self.student_invites))
        s += "\nNo of self_learners: " + str(len(self.self_learners))
        s += "\nNo of assignments: " + str(len(self.assignments))
        return s
