import xml.etree.ElementTree as ET
import sys

class bcolors:
    OKGREEN = '\033[92m'
    FAIL = '\033[91m'
    OKBLUE = '\033[94m'
    BOLD = '\033[1m'
    HEADER = '\033[95m'
    NORMAL = '\033[0m'


class Yatrep():
    def parse_xml(file_path):
        print("Parsing file '{0}'".format(file_path))
        root = ET.parse(file_path).getroot()
        return TestResults(root)


class TestResults():
    def __init__(self, xml_root):
        self.failed_tests = int(xml_root.attrib['failed'])
        self.passed_tests = int(xml_root.attrib['passed'])
        self.inconclusive_tests = int(xml_root.attrib['inconclusive'])
        self.total_tests = int(xml_root.attrib['total'])
        self.test_duration = float(xml_root.attrib['duration'])
        self.failed_tests_details = self.fetch_details(xml_root)
        self.check_success()

    def check_success(self):
        if (self.failed_tests == 0 and self.total_tests == self.passed_tests):
            self.success = True
        else:
            self.success = False

    def fetch_details(self, xml_root):
        details = {}
        for test_case in xml_root.findall(".//failure/..[@result='Failed']"):
            if (test_case.tag == 'test-case'):
                name = test_case.attrib['name']
                details[name] = {}
                msg = test_case.find('failure').find('message').text
                std_out = test_case.find('output').text
                stack_trace = test_case.find('failure').find('stack-trace').text

                details[name]['stack_trace'] = stack_trace
                details[name]['message'] = msg
                details[name]['std_out'] = std_out
        return details


def main():
    if (len(sys.argv) < 1):
        print("Invalid usage.")
        print("Example: .'/bin/yatrep.sh path_to_file'")
        sys.exit(-1)
    else:
        result = Yatrep.parse_xml(sys.argv[1])
        exit_code = 0
        if result.success == False:
            exit_code = -1
            print("{0}Tests failed!".format(bcolors.FAIL))
        else:
            print("{0}Tests passed!".format(bcolors.OKGREEN))
        print(bcolors.NORMAL)
        print("{0}Total: {1}".format(bcolors.BOLD, result.total_tests))
        print("{0}Passed: {1}".format(bcolors.BOLD, result.passed_tests))
        print("{0}Inconclusive: {1}".format(bcolors.BOLD, result.inconclusive_tests))

        error_color = bcolors.NORMAL
        if (result.failed_tests > 0):
            error_color = bcolors.FAIL

        print("{2}{0}Failed: {1}".format(bcolors.BOLD, result.failed_tests, error_color))

        print("{0} ---".format(bcolors.NORMAL))
        for case_id, details in result.failed_tests_details.items():
            print("Test "+bcolors.BOLD+"{0} Failed.".format(case_id)+bcolors.NORMAL)
            print(bcolors.FAIL+"{0}".format(details['message']))
            print(bcolors.OKBLUE+bcolors.BOLD+"Stack Trace:"+bcolors.NORMAL)
            print(details['stack_trace'])
            print(bcolors.OKBLUE+bcolors.BOLD+"Std.Out:"+bcolors.NORMAL)
            print(details['std_out'])
            print("{0} ---".format(bcolors.NORMAL))
        sys.exit(exit_code)
