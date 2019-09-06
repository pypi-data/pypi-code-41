from unittest import TestCase

from girepo.arg_parser import create_argparser


class TestCreateArgparser(TestCase):
    def test_create_argparser_without_argument_error(self):
        test_data = [
            ({
                 "args": ["strict", "angular/angular", "facebook/react", "vuejs/vue"],
                 "sort_keys": ["star", "created_at"],
                 "expected": {
                     "names": ["angular/angular", "facebook/react", "vuejs/vue"],
                     "asc_key": None,
                     "desc_key": None,
                 }
             }, "normal arguments without sort option"),
            ({
                 "args": ["strict", "angular/   angular", "facebook   /react", "  vuejs  /  vue  "],
                 "sort_keys": ["star", "created_at"],
                 "expected": {
                     "names": ["angular/angular", "facebook/react", "vuejs/vue"],
                     "asc_key": None,
                     "desc_key": None,
                 }
             }, "arguments which have spaces without sort option"),
            ({
                 "args": ["strict", "angular/  angular", "facebook  /react", " vuejs / vue ", "--asc", "star"],
                 "sort_keys": ["star", "created_at"],
                 "expected": {
                     "names": ["angular/angular", "facebook/react", "vuejs/vue"],
                     "asc_key": "star",
                     "desc_key": None,
                 }
             }, "normal arguments with asc option"),
            ({
                 "args": ["strict", "angular/  angular", "facebook  /react", " vuejs / vue ", "--desc", "star"],
                 "sort_keys": ["star", "created_at"],
                 "expected": {
                     "names": ["angular/angular", "facebook/react", "vuejs/vue"],
                     "asc_key": None,
                     "desc_key": "star",
                 }
             }, "normal arguments with desc option"),

            # need to prepare data....
        ]

        for data, message in test_data:
            with self.subTest(message):
                actual = create_argparser(data['args'], data['sort_keys'])
                self.assertEqual(data['expected']['names'], actual.names)
                self.assertEqual(data['expected']['asc_key'], actual.asc_key)
                self.assertEqual(data['expected']['desc_key'], actual.desc_key)

    def test_create_argparser_with_argument_error(self):
        test_data = [
            ({
                "args": ["strict", "angular/  angular", "--sort"],
                "sort_keys": ["star", "created_at"],
                "expected": {
                    "full_names": ["angular/angular", "facebook/react", "vuejs/vue"],
                    "sort_key": None,
                    "is_asc": False,
                    "is_desc": False,
                }
            }, "There is no such option like sort"),
            ({
                "args": ["strict", "angular/  angular", "facebook  /react", " vuejs / vue ", "-a"],
                "sort_keys": ["star", "created_at"],
                "expected": {
                    "full_names": ["angular/angular", "facebook/react", "vuejs/vue"],
                    "sort_key": "star",
                    "is_asc": True,
                    "is_desc": False,
                }
            }, "the asc option requires a keyword in choices"),
            # need to prepare data....
        ]

        for data, message in test_data:
            with self.subTest(message):
                with self.assertRaises(SystemExit):
                    create_argparser(data['args'], data['sort_keys'])
