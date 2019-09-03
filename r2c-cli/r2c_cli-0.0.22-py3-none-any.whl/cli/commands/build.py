import os

import click

from r2c.cli.commands.cli import cli
from r2c.cli.logger import abort_on_build_failure, print_msg
from r2c.cli.run import build_docker
from r2c.cli.util import find_and_open_analyzer_manifest, parse_remaining


@cli.command()
@click.option(
    "-A",
    "--analyzer-directory",
    default=os.getcwd(),
    help="The directory where the analyzer is located, defaulting to the current directory.",
)
@click.argument("env-args-string", nargs=-1, type=click.Path())
@click.pass_context
def build(ctx, analyzer_directory, env_args_string):
    """Builds an analyzer without running it.
    """

    manifest, analyzer_directory = find_and_open_analyzer_manifest(
        analyzer_directory, ctx
    )

    print_msg("🔨 Building docker container")

    abort_on_build_failure(
        build_docker(
            manifest.analyzer_name,
            manifest.version,
            os.path.relpath(analyzer_directory, os.getcwd()),
            env_args_dict=parse_remaining(env_args_string),
        )
    )
