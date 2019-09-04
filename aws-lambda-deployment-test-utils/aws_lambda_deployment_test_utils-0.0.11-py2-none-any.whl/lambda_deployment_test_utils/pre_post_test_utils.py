import dataclasses
import functools
import importlib
import json
import logging
import os
import pprint
from typing import Any, Callable, Mapping, MutableMapping, Sequence, Type

import boto3

log = logging.getLogger(__name__)

log.setLevel(os.getenv("LOG_LEVEL") or logging.INFO)

ALL_LAMBDA_TESTS: MutableMapping[str, MutableMapping[str, Callable]] = {}

StringKeyedMapping = Mapping[str, Any]


def get_full_function_arn() -> str:
    return os.getenv("FUNCTION_VERSION")


class LambdaFailed(RuntimeError):
    """Raised when a lambda fails."""


class ARNHasNotBeenSet(Exception):
    """Raised when this class is invoked with """


@dataclasses.dataclass
class LambdaInfo:
    function_arn: str
    version_number: str

    @classmethod
    def from_arn(cls, arn: str) -> "LambdaInfo":
        try:
            function_arn, _, version_number = arn.rpartition(":")
        except AttributeError:
            raise ARNHasNotBeenSet()
        return cls(function_arn, version_number)


def lambda_test(test_group: str, expected_status_code: int = 200)->"LambdaTest":
    return LambdaTest(test_group, get_full_function_arn(), expected_status_code)


@dataclasses.dataclass
class LambdaTest:
    test_group: str
    arn: str
    expected_status_code: int

    def __call__(self, fn)->Mapping[str,Any]:
        lambda_info = self.get_lambda_info()

        def the_lambda(event, context=None):
            aws_lambda = boto3.client("lambda")
            log.debug(f"Invoking lambda: {lambda_info.function_arn}")
            try:
                response = aws_lambda.invoke(
                    FunctionName=self.arn,
                    InvocationType="RequestResponse",
                    LogType="Tail",
                    Payload=json.dumps(event),
                    Qualifier=lambda_info.version_number,
                )
                statuscode = response["StatusCode"]
                log.debug(f"Full response from lambda invoke: {response}")
                fn_assert(
                    statuscode == self.expected_status_code,
                    f"StatusCode: {statuscode} is not as expected: {self.expected_status_code}",
                )
                response_payload = json.loads(
                    response["Payload"].read().decode("utf-8")
                )
                log.debug(f"Payload: {response_payload}")
                return response_payload
            except RuntimeError:
                raise LambdaFailed(fn.__name__)

        @functools.wraps(fn)
        def wrapped():
            return fn(the_lambda)

        ALL_LAMBDA_TESTS.setdefault(self.test_group, {})[fn.__name__] = wrapped

        wrapped._original_function = fn

        return wrapped

    def get_lambda_info(self) -> LambdaInfo:
        return LambdaInfo.from_arn(self.arn)


def run_all_my_tests(test_group: str) -> bool:
    log.info(f"Running {test_group} tests.")
    all_tests = ALL_LAMBDA_TESTS[test_group].values()

    test_results = {}

    for test in all_tests:
        log.info(f"Running test: {test.__name__}")
        try:
            test()
        except AssertionError:
            log.exception(f"Test {test.__name__} has failed")
            test_results[test.__name__] = False
        except Exception:
            log.exception(f"Test {test.__name__} has raised an unrecoverable error")
            test_results[test.__name__] = False
            break
        else:
            log.info(f"Test {test.__name__} has succeeded")
            test_results[test.__name__] = True

    return all(test_results.values())


def push_deployment_status(
    status: bool, deployment_id, lifecycle_event_hook_execution_id
):
    aws_codedeploy = boto3.client("codedeploy")
    deployment_status: str = "Succeeded" if status else "Failed"
    log.debug(f"Setting status codedeploy to {deployment_status}")
    response = aws_codedeploy.put_lifecycle_event_hook_execution_status(
        deploymentId=deployment_id,
        lifecycleEventHookExecutionId=lifecycle_event_hook_execution_id,
        status=deployment_status,
    )
    log.debug(f"CodeDeploy response: {response}")


def fn_assert(
    value: bool, message: str, error_base_class: Type = AssertionError
) -> None:
    if not value:
        raise error_base_class(message)


def handler(test_group, event, context):
    log.info(f"Event: {pprint.pformat(event)}")
    log.info(f"Context: {pprint.pformat(context)}")

    push_deployment_status(
        run_all_my_tests(test_group),
        event["DeploymentId"],
        event["LifecycleEventHookExecutionId"],
    )


def handler_factory(
    test_group: str, modules: Sequence[str]
) -> Callable[[StringKeyedMapping, StringKeyedMapping], StringKeyedMapping]:
    # Ensure that all of the modules the test group requires are imported prior to buiding the handler.
    for m in modules:
        print(f"Attempting to import {m}")
        importlib.import_module(m)
        # __import__(m)

    return functools.partial(handler, test_group)
