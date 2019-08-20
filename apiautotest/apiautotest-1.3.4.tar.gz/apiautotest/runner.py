# encoding: utf-8

from unittest.case import SkipTest

from apiautotest import exceptions, logger, response, utils
from apiautotest.client import HttpSession
from apiautotest.context import SessionContext


tmp_extracted_variables = dict()


class Runner(object):
    """ Running testcases.

    Examples:
        >>> tests_mapping = {
                "project_mapping": {
                    "functions": {}
                },
                "testcases": [
                    {
                        "config": {
                            "name": "XXXX",
                            "base_url": "http://127.0.0.1",
                            "verify": False
                        },
                        "teststeps": [
                            {
                                "name": "test description",
                                "variables": [],        # optional
                                "request": {
                                    "url": "http://127.0.0.1:5000/api/users/1000",
                                    "method": "GET"
                                }
                            }
                        ]
                    }
                ]
            }

        >>> testcases = parser.parse_tests(tests_mapping)
        >>> parsed_testcase = testcases[0]

        >>> test_runner = runner.Runner(parsed_testcase["config"])
        >>> test_runner.run_test(parsed_testcase["teststeps"][0])

    """

    def __init__(self, config, http_client_session=None):
        """ run testcase or testsuite.

        Args:
            config (dict): testcase/testsuite config dict

                {
                    "name": "ABC",
                    "variables": {},
                    "setup_hooks", [],
                    "teardown_hooks", []
                }

            http_client_session (instance): requests.Session(), or locust.client.Session() instance.

        """
        self.verify = config.get("verify", True)
        self.output = config.get("output", [])
        self.validation_results = []
        config_variables = config.get("variables", {})

        # testcase setup hooks
        self.testcase_setup_hooks = config.get("setup_hooks", [])
        # testcase teardown hooks
        self.testcase_teardown_hooks = config.get("teardown_hooks", [])

        self.http_client_session = http_client_session or HttpSession()
        self.session_context = SessionContext(config_variables)

    def execute_hooks(self):
        if self.testcase_setup_hooks:
            self.do_hook_actions(self.testcase_setup_hooks, "setup")

    def __del__(self):
        if self.testcase_teardown_hooks:
            self.do_hook_actions(self.testcase_teardown_hooks, "teardown")

    def __clear_test_data(self):
        """ clear request and response data
        """
        if not isinstance(self.http_client_session, HttpSession):
            return

        self.validation_results = []
        self.http_client_session.init_meta_data()

    def __get_test_data(self):
        """ get request/response data and validate results
        """
        if not isinstance(self.http_client_session, HttpSession):
            return

        meta_data = self.http_client_session.meta_data
        meta_data["validators"] = self.validation_results
        return meta_data

    def _handle_skip_feature(self, test_dict):
        """ handle skip feature for test
            - skip: skip current test unconditionally
            - skipIf: skip current test if condition is true
            - skipUnless: skip current test unless condition is true

        Args:
            test_dict (dict): test info

        Raises:
            SkipTest: skip test

        """
        # TODO: move skip to initialize
        skip_reason = None

        if "skip" in test_dict:
            skip_reason = test_dict["skip"]

        elif "skipIf" in test_dict:
            skip_if_condition = test_dict["skipIf"]
            if self.session_context.eval_content(skip_if_condition):
                skip_reason = "{} evaluate to True".format(skip_if_condition)

        elif "skipUnless" in test_dict:
            skip_unless_condition = test_dict["skipUnless"]
            if not self.session_context.eval_content(skip_unless_condition):
                skip_reason = "{} evaluate to False".format(skip_unless_condition)

        if skip_reason:
            raise SkipTest(skip_reason)

    def do_hook_actions(self, actions, hook_type):
        """ call hook actions.

        Args:
            actions (list): each action in actions list maybe in two format.

                format1 (dict): assignment, the value returned by hook function will be assigned to variable.
                    {"var": "${func()}"}
                format2 (str): only call hook functions.
                    ${func()}

            hook_type (enum): setup/teardown

        """
        logger.log_debug("call {} hook actions.".format(hook_type))
        for action in actions:

            if isinstance(action, dict) and len(action) == 1:
                # format 1
                # {"var": "${func()}"}
                var_name, hook_content = list(action.items())[0]
                hook_content_eval = self.session_context.eval_content(hook_content)
                logger.log_debug(
                    "assignment with hook: {} = {} => {}".format(
                        var_name, hook_content, hook_content_eval
                    )
                )
                self.session_context.update_test_variables(
                    var_name, hook_content_eval
                )
            else:
                # format 2
                logger.log_debug("call hook function: {}".format(action))
                # TODO: check hook function if valid
                self.session_context.eval_content(action)

    def _run_test(self, test_dict):
        """ run single teststep.

        Args:
            test_dict (dict): teststep info
                {
                    "name": "teststep description",
                    "skip": "skip this test unconditionally",
                    "times": 3,
                    "variables": [],            # optional, override
                    "request": {
                        "url": "http://127.0.0.1:5000/api/users/1000",
                        "method": "POST",
                        "headers": {
                            "Content-Type": "application/json",
                            "authorization": "$authorization",
                            "random": "$random"
                        },
                        "json": {"name": "user", "password": "123456"}
                    },
                    "extract": {},              # optional
                    "validate": [],             # optional
                    "setup_hooks": [],          # optional
                    "teardown_hooks": []        # optional
                }

        Raises:
            exceptions.ParamsError
            exceptions.ValidationFailure
            exceptions.ExtractFailure

        """
        global tmp_extracted_variables
        # clear meta data first to ensure independence for each test
        self.__clear_test_data()

        # check skip
        self._handle_skip_feature(test_dict)

        # prepare
        test_dict = utils.lower_test_dict_keys(test_dict)
        test_variables = test_dict.get("variables", {})
        # override variables use former extracted_variables
        test_variables.update(tmp_extracted_variables)
        self.session_context.init_test_variables(test_variables)

        # teststep name
        test_name = self.session_context.eval_content(test_dict.get("name", ""))

        # parse test request
        raw_request = test_dict.get('request', {})
        parsed_test_request = self.session_context.eval_content(raw_request)
        self.session_context.update_test_variables("request", parsed_test_request)

        # prepend url with base_url unless it's already an absolute URL
        url = parsed_test_request.pop('url')
        base_url = self.session_context.eval_content(test_dict.get("base_url", ""))
        parsed_url = utils.build_url(base_url, url)

        # setup hooks
        setup_hooks = test_dict.get("setup_hooks", [])
        if setup_hooks:
            self.do_hook_actions(setup_hooks, "setup")

        try:
            method = parsed_test_request.pop('method')
            parsed_test_request.setdefault("verify", self.verify)
            group_name = parsed_test_request.pop("group", None)
        except KeyError:
            raise exceptions.ParamsError("URL or METHOD missed!")

        # TODO: move method validation to json schema
        valid_methods = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
        if method.upper() not in valid_methods:
            err_msg = u"Invalid HTTP method! => {}\n".format(method)
            err_msg += "Available HTTP methods: {}".format("/".join(valid_methods))
            logger.log_error(err_msg)
            raise exceptions.ParamsError(err_msg)

        logger.log_info("{method} {url}".format(method=method, url=parsed_url))
        logger.log_debug("request kwargs(raw): {kwargs}".format(kwargs=parsed_test_request))

        # request
        resp = self.http_client_session.request(
            method,
            parsed_url,
            name=(group_name or test_name),
            **parsed_test_request
        )
        resp_obj = response.ResponseObject(resp)

        # extract
        extractors = test_dict.get("extract", {})
        if extractors:
            extracted_variables_mapping = resp_obj.extract_response(extractors)
            tmp_extracted_variables.update(extracted_variables_mapping)
            self.session_context.update_session_variables(extracted_variables_mapping)
        self.session_context.update_session_variables(tmp_extracted_variables)

        # validate
        validators = test_dict.get("validate") or test_dict.get("validators") or []
        try:
            self.session_context.validate(validators, resp_obj)
        except (exceptions.ParamsError, exceptions.ValidationFailure, exceptions.ExtractFailure):
            err_msg = "{} DETAILED REQUEST & RESPONSE {}\n".format("*" * 32, "*" * 32)

            # log request
            err_msg += "====== request details ======\n"
            err_msg += "url: {}\n".format(parsed_url)
            err_msg += "method: {}\n".format(method)
            err_msg += "headers: {}\n".format(parsed_test_request.pop("headers", {}))
            for k, v in parsed_test_request.items():
                v = utils.omit_long_data(v)
                err_msg += "{}: {}\n".format(k, repr(v))

            err_msg += "\n"

            # log response
            err_msg += "====== response details ======\n"
            err_msg += "status_code: {}\n".format(resp_obj.status_code)
            err_msg += "headers: {}\n".format(resp_obj.headers)
            err_msg += "body: {}\n".format(repr(resp_obj.text))
            logger.log_error(err_msg)

            raise

        finally:
            self.validation_results = self.session_context.validation_results
            # teardown hooks
            teardown_hooks = test_dict.get("teardown_hooks", [])
            if teardown_hooks:
                self.session_context.update_test_variables("response", resp_obj)
                self.do_hook_actions(teardown_hooks, "teardown")

    def _run_testcase(self, testcase_dict):
        """ run single testcase.
        """
        self.meta_datas = []
        config = testcase_dict.get("config", {})

        # each teststeps in one testcase (YAML/JSON) share the same session.
        test_runner = Runner(config, self.http_client_session)

        tests = testcase_dict.get("teststeps", [])
        if test_runner.testcase_setup_hooks:
            test_runner.execute_hooks()
        for index, test_dict in enumerate(tests):

            test_dict.setdefault("variables", {})
            test_runner.session_context.test_variables_mapping.update(test_dict["variables"])
            # override current teststep variables with former testcase output variables
            former_output_variables = self.session_context.test_variables_mapping
            if former_output_variables:
                test_dict.setdefault("variables", {})
                test_dict["variables"].update(former_output_variables)

            test_dict["variables"].update(test_runner.session_context.test_variables_mapping)

            try:
                test_runner.run_test(test_dict)
            except Exception:
                # log exception request_type and name for locust stat
                self.exception_request_type = test_runner.exception_request_type
                self.exception_name = test_runner.exception_name
                raise
            finally:
                _meta_datas = test_runner.meta_datas
                self.meta_datas.append(_meta_datas)

        self.session_context.update_session_variables(
            test_runner.extract_output(test_runner.output)
        )

    def run_test(self, test_dict):
        """ run single teststep of testcase.
            test_dict may be in 3 types.

        Args:
            test_dict (dict):

                # teststep
                {
                    "name": "teststep description",
                    "variables": [],        # optional
                    "request": {
                        "url": "http://127.0.0.1:5000/api/users/1000",
                        "method": "GET"
                    }
                }

                # nested testcase
                {
                    "config": {...},
                    "teststeps": [
                        {...},
                        {...}
                    ]
                }

                # TODO: function
                {
                    "name": "exec function",
                    "function": "${func()}"
                }

        """
        self.meta_datas = None
        if "teststeps" in test_dict:
            # nested testcase
            test_dict.setdefault("config", {}).setdefault("variables", {})
            test_dict["config"]["variables"].update(
                self.session_context.session_variables_mapping)
            self._run_testcase(test_dict)
        else:
            # api
            try:
                self._run_test(test_dict)
            except Exception:
                # log exception request_type and name for locust stat
                self.exception_request_type = test_dict["request"]["method"]
                self.exception_name = test_dict.get("name")
                raise
            finally:
                self.meta_datas = self.__get_test_data()

    def extract_output(self, output_variables_list):
        """ extract output variables
        """
        variables_mapping = self.session_context.session_variables_mapping

        output = {}
        for variable in output_variables_list:
            if variable not in variables_mapping:
                logger.log_warning(
                    "variable '{}' can not be found in variables mapping, failed to output!"\
                        .format(variable)
                )
                continue

            output[variable] = variables_mapping[variable]

        utils.print_info(output)
        return output
