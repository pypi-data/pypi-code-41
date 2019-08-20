# system modules
import logging
import re

# internal modules

# external modules
import click

logger = logging.getLogger(__name__)


@click.group(
    help="Store MQTT data",
    context_settings={
        "help_option_names": ["-h", "--help"],
        "auto_envvar_prefix": "MQTTSTORE",
    },
)
@click.option("-q", "--quiet", help="decrease the loglevel", count=True)
@click.option(
    "-v",
    "--verbose",
    help="increase the loglevel. "
    "Specifying this option more than 2 times "
    "enables all mqttstore log messages. More than 3 times doesn't limit "
    "logging to only mqttstore.",
    count=True,
)
@click.version_option(help="show version and exit")
@click.pass_context
def cli(ctx, quiet, verbose):
    # set up logging
    loglevel_choices = dict(
        enumerate(
            (
                logging.CRITICAL + 1,
                logging.CRITICAL,
                logging.WARNING,
                logging.INFO,
                logging.DEBUG,
            ),
            -2,
        )
    )
    loglevel = loglevel_choices.get(
        min(max(loglevel_choices), max(min(loglevel_choices), verbose - quiet))
    )
    logging.basicConfig(
        level=loglevel,
        format="[%(asctime)s] %(levelname)-8s"
        + (" (%(name)s)" if verbose >= 3 else "")
        + " %(message)s",
    )
    for n, l in logger.manager.loggerDict.items():
        if (
            not re.match(
                r"mqttstore\." if verbose >= 4 else r"mqttstore.cli(?!\w)", n
            )
            and not verbose > 4
        ):
            l.propagate = False
            if hasattr(l, "setLevel"):
                l.setLevel(logging.CRITICAL + 1)
