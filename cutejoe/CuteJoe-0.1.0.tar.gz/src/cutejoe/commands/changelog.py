"""Generate changelog on /changelog folder for releases"""
import yaml
import click

from cutejoe.helpers import Config, Changelog, save_text_file, read_yml_file


@click.command()
@click.option("--start", help="First commit to log")
@click.option("--end", help="Last commit to log")
@click.option("--save", "-s", is_flag=True, default=False, help="Save to file")
@click.option("--config", "-c", default=".cutejoe.yml", help="Config file")
def changelog(save, config, start=None, end=None):
    """Generate automatic changelog and tag based on commit messages.

    \b
    Commit messages must have this pattern:
        `<kind>:<message>`

    \b
    If you didn't override the config file, default valid kinds are:
        - break: fix or feature that would cause existing functionality to not work as expected;
        - add: non-breaking change that adds functionality;
        - change: non-breaking change that changes existing functionality;
        - deprecate: non-breaking change that deprecates existing functionality;
        - remove: non-breaking change that removes existing functionality;
        - security: non-breaking change that fixes existing vulnerability;
        - fix: non-breaking change that fixes existing issue.
    """
    try:
        content = read_yml_file(config)
    except (yaml.YAMLError, FileNotFoundError):
        click.confirm("Config not found. Would you like to use default config?", abort=True)
        default_config = Config.get_default_file_path()
        content = read_yml_file(default_config)

    config = Config(**content)
    changelog_config = config.changelog

    if start:
        changelog_config.start = start
    if end:
        changelog_config.end = end

    changelog = Changelog(config=changelog_config)

    if save:
        save_text_file(changelog.file_path, changelog.content)
        click.echo(f"Changelog: \"{changelog.file_path}\"")
    else:
        click.echo("Changelog:")
        click.echo("".join(changelog.content))

    click.echo(f"Tag: \"{changelog.tag}\"")
    click.echo(f"Branch: \"{changelog.branch}\"")
