import click

from alfa_sdk.common.exceptions import ResourceNotFoundError
from alfa_cli.common.exceptions import AlfaCliError
from alfa_cli.runner import LocalRunner


@click.command()
@click.argument("algorithm-id", type=str)
@click.argument("environment-name", type=str)
@click.argument("problem", type=str)
@click.option(
    "--return-holding-response",
    is_flag=True,
    help="If specified, ALFA will return the identifier of the request but not wait until the algorithm finishes.",
)
@click.option(
    "--include-details",
    is_flag=True,
    help="If specified, ALFA will add additional details to the response in addition to the algorithm result.",
)
@click.option(
    "--can-buffer",
    is_flag=True,
    help="If specified, ALFA will buffer the invocation when busy (instead of returning an error).",
)
@click.pass_obj
def invoke(obj, algorithm_id, environment_name, problem, **kwargs):
    """Invoke a deployed algorithm."""

    client = obj["client"]

    #

    try:
        algorithm = client.get_algorithm(algorithm_id)
    except ResourceNotFoundError:
        raise AlfaCliError(message="Algorithm {} not found.".format(algorithm_id))

    try:
        environment = algorithm.get_environment(environment_name)
    except ResourceNotFoundError:
        raise AlfaCliError(
            message="Environment {} for algorithm {} not found.".format(
                environment_name, algorithm_id
            )
        )

    #

    try:
        problem = open(problem, "r").read()
    except:
        pass

    res = environment.invoke(problem, **kwargs)
    return obj["logger"].result(res)


@click.command()
@click.argument("problem", type=str)
@click.option(
    "--algorithm-id",
    "-a",
    type=str,
    help="If specified, the provided algorith id will be set in the context; defaults to the algorithm id in the alfa.yml configuration file.",
)
@click.option(
    "--environment-name",
    "-e",
    type=str,
    help="If specified, the provided environment name will be set in the context; defaults to the environment name in the alfa.yml configuration file.",
)
@click.pass_obj
def invoke_local(obj, problem, algorithm_id, environment_name):
    """Invoke the algorithm in the working directory locally"""

    try:
        problem = open(problem, "r").read()
    except:
        pass

    runner = LocalRunner(obj, algorithm_id, environment_name)
    res = runner.run(problem)
    return obj["logger"].result(res)
