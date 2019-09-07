import json
from ruamel import yaml
import logging
import sys
from datetime import datetime, timedelta

import click
from html2text import html2text

from recodex.api import ApiClient
from recodex.decorators import pass_api_client


@click.group()
def cli():
    """
    Tools for working with exercises
    """


@cli.command()
@click.option("--json/--yaml", "useJson", default=None)
@pass_api_client
def list_all(api: ApiClient, useJson):
    """
    List all exercises (as ID and name) in JSON, Yaml, or as a plain list.
    """
    exercises = api.get_exercises()
    if useJson is True:
        json.dump(exercises, sys.stdout, sort_keys=True, indent=4)
    elif useJson is False:
        yaml.dump(exercises, sys.stdout)
    else:
        for exercise in exercises:
            click.echo("{} {}".format(exercise["id"], exercise["name"])) 


@cli.command()
@click.argument("exercise_id")
@click.option("--json/--yaml", "useJson", default=True)
@pass_api_client
def get(api: ApiClient, exercise_id, useJson):
    """
    Get exercise data and print it in JSON or Yaml.
    """
    exercise = api.get_exercise(exercise_id)
    if useJson:
        json.dump(exercise, sys.stdout, sort_keys=True, indent=4)
    else:
        yaml.dump(exercise, sys.stdout)


@cli.command()
@click.argument("exercise_id")
@click.option("--json/--yaml", "useJson", default=None)
@pass_api_client
def get_ref_solutions(api: ApiClient, exercise_id, useJson):
    """
    List all reference solutions of given exercise in JSON, Yaml, or as a plain list.
    """
    solutions = api.get_reference_solutions(exercise_id)
    if useJson is True:
        json.dump(solutions, sys.stdout, sort_keys=True, indent=4)
    elif useJson is False:
        yaml.dump(solutions, sys.stdout)
    else:
        for solution in solutions:
            ts = int(solution["solution"]["createdAt"])
            date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            click.echo("{} {} {} {}".format(solution["id"], solution["runtimeEnvironmentId"],
                                            date, solution["description"]))


@cli.command()
@click.argument("ref_solution_id")
@click.option("--json/--yaml", "useJson", default=None)
@pass_api_client
def get_ref_solution_evaluations(api: ApiClient, ref_solution_id, useJson):
    """
    Get reference solution evaluations and print them all in JSON or Yaml, or as a plain list.
    """
    evaluations = api.get_reference_solution_evaluations(ref_solution_id)
    if useJson is True:
        json.dump(evaluations, sys.stdout, sort_keys=True, indent=4)
    elif useJson is False:
        yaml.dump(evaluations, sys.stdout)
    else:
        for evaluation in evaluations:
            ts = int(evaluation["submittedAt"])
            date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            click.echo("{} {} {} {}".format(evaluation["id"], evaluation["evaluationStatus"], evaluation["isCorrect"], date))


@cli.command()
@click.argument("evaluation_id")
@pass_api_client
def delete_ref_solution_evaluation(api: ApiClient, evaluation_id):
    """
    Delete referenece solution evaluation and all the results and logs.
    """
    api.delete_reference_solution_evaluation(evaluation_id)


@cli.command()
@click.argument("ref_solution_id")
@click.option('--debug', is_flag=True)
@pass_api_client
def resubmit_ref_solution(api: ApiClient, ref_solution_id, debug):
    """
    Resubmit reference solution for another evaluation.
    """
    api.resubmit_reference_solution(ref_solution_id, debug)


@cli.command()
@click.argument("language")
@click.argument("exercise_id")
@pass_api_client
def add_localization(api: ApiClient, language, exercise_id):
    """
    Add a localized text to an exercise.
    The text is read from the standard input. HTML and Markdown are accepted.
    """
    exercise = api.get_exercise(exercise_id)
    exercise["localizedTexts"].append({
        "locale": language,
        "text": html2text(sys.stdin.read())
    })

    api.update_exercise(exercise_id, exercise)


@cli.command()
@click.argument("files", nargs=-1)
@click.option("exercise_id", "-e")
@click.option("note", "-n", default="")
@click.option("runtime_environment", "-r", required=True)
@pass_api_client
def add_reference_solution(api: ApiClient, exercise_id, note, runtime_environment, files):
    solution = api.create_reference_solution(exercise_id, {
        "note": note,
        "runtimeEnvironmentId": runtime_environment,
        "files": [api.upload_file(file, open(file, "r")) for file in files]
    })
    click.echo(solution["id"])


@cli.command()
@click.option("config_path", "-c")
@pass_api_client
def evaluate_all_rs(api: ApiClient):
    """
    Request evaluation for all reference solutions
    """
    with click.progressbar(api.get_exercises()) as bar:
        for exercise in bar:
            try:
                api.evaluate_reference_solutions(exercise["id"])
            except Exception as e:
                logging.error("Error in exercise {}: {}".format(exercise["id"], str(e)))


@cli.command()
@click.option("threshold", "-t")
@pass_api_client
def check_rs_evaluations(api: ApiClient, threshold):
    """
    Find exercises that had no successful reference solution evaluation in
    a given number of days
    """
    for exercise in api.get_exercises():
        solutions = api.get_reference_solutions(exercise["id"])
        if not solutions:
            logging.error("Exercise %s has no reference solutions", exercise["id"])
            continue

        found = False
        found_recent = False

        for solution in solutions:
            for evaluation in api.get_reference_solution_evaluations(solution["id"]):
                status_ok = evaluation["evaluationStatus"] == "done"
                submission_timestamp = int(evaluation["submittedAt"])
                submission_timestamp = max(0, submission_timestamp)
                submission_date = datetime.fromtimestamp(submission_timestamp)
                threshold_date = datetime.utcnow() - timedelta(days=int(threshold))
                recent = submission_date >= threshold_date
                if status_ok:
                    found = True
                    if recent:
                        found_recent = True
                        break

        if not found_recent:
            if found:
                logging.error("Exercise %s has no recent successful evaluations", exercise["id"])
            else:
                logging.error("Exercise %s has never had any successful evaluations", exercise["id"])


@cli.command()
@click.argument("exercise_id")
@pass_api_client
def delete(api: ApiClient, exercise_id):
    api.delete_exercise(exercise_id)


@cli.command()
@click.argument("exercise_id")
@click.option("--json/--yaml", "useJson", default=True)
@pass_api_client
def get_config(api: ApiClient, exercise_id, useJson):
    """
    Get exercise configuration in JSON (or possibly yaml) format
    """
    config = api.get_exercise_config(exercise_id)
    if useJson:
        json.dump(config, sys.stdout, sort_keys=True, indent=4)
    else:
        yaml.dump(config, sys.stdout)


@cli.command()
@click.argument("exercise_id")
@click.argument("file_name")
@click.option("--json/--yaml", "useJson", default=True)
@pass_api_client
def set_config(api: ApiClient, exercise_id, file_name, useJson):
    """
    Load a JSON or YAML from a file and set it as configuration.
    """
    with open(file_name, 'r') as stream:
        if useJson:
            config = json.load(stream)
        else:
            config = yaml.safe_load(stream)
    api.update_exercise_config(exercise_id, config)
