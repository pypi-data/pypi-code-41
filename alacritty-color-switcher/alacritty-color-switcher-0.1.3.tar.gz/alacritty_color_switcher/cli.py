import click
from pathlib import Path
from ruamel.yaml import YAML
import os
import sys
from itertools import chain
import importlib.resources as resources
from alacritty_color_switcher import templates

yaml = YAML()


def get_color_configs(color_dir):
    configs = dict()
    globs = ["**/*.yaml", "**/*.yml"]

    for conf in chain(*(color_dir.glob(gl) for gl in globs)):
        # TODO catch yaml load exceptions
        with conf.open() as fp:
            configs[conf.stem] = yaml.load(fp)

    return configs


def reset_undefined(color_config, alacritty_config):
    alacritty_colors = alacritty_config["colors"]

    relative_colors = ["cursor", "dim", "selection"]
    for ctype in relative_colors:

        if ctype in color_config["colors"].keys():
            continue

        if ctype not in alacritty_colors.keys():
            continue

        for field in alacritty_colors[ctype].keys():
            alacritty_colors[ctype][field] = None

    return alacritty_config


def apply_color_config(color_config, alacritty_config):
    with alacritty_config.open() as fp:
        alacritty_config = yaml.load(fp)

    alacritty_config = reset_undefined(color_config, alacritty_config)
    alacritty_colors = alacritty_config["colors"]

    for color_type in alacritty_colors:
        for color in alacritty_colors[color_type]:
            try:
                alacritty_colors[color_type][color] = color_config["colors"][
                    color_type
                ][color]
            except KeyError:
                click.echo(f"{color_type}/{color} not found in the color config!")

    return alacritty_config


def set_current_color(color_name, color_dir):
    click.echo(color_name)
    current_color_file = color_dir / "acs.cur"
    with current_color_file.open("w") as f:
        f.write(color_name)


def get_current_color(color_dir):
    current_color_file = color_dir / "acs.cur"
    current_color = None

    if current_color_file.is_file():
        with current_color_file.open() as f:
            current_color = f.read()

    return current_color


def get_next_color(current_color, color_configs):
    color_stems = list(color_configs.keys())

    if current_color is None:
        return color_stems[0]

    current_index = color_stems.index(current_color)
    next_index = (current_index + 1) % len(color_stems)
    return color_stems[next_index]


@click.command()
@click.option("--config", default="$HOME/.config/alacritty/alacritty.yml")
@click.option("-s", "--switch", is_flag=True)
@click.option("-a", "--apply", default="")
@click.option("-c", "--colors", default="$HOME/.config/alacritty-colors")
@click.option(
    "-l",
    "--ls",
    is_flag=True,
    default=False,
    help="List all found color configs and exit.",
)
@click.option("--debug", is_flag=True, default=False)
@click.option("--reset-default", is_flag=True, default=False)
@click.pass_context
def main(ctx, config, switch, apply, colors, ls, debug, reset_default):
    color_dir = Path(os.path.expandvars(colors))
    config = Path(os.path.expandvars(config))

    if not color_dir.is_dir():
        click.echo(click.style(f"{colors} does not exists!", fg="red"))
        ctx.exit(1)

    if not config.is_file():
        click.echo(
            click.style(
                f"{config} does not exists! Is this the right path to your alacritty config?",
                fg="red",
            )
        )
        ctx.exit(1)

    color_configs = get_color_configs(color_dir)
    if ls:
        for color_stem in color_configs.keys():
            click.echo(color_stem)

        ctx.exit(0)

    if apply:
        if apply not in color_configs.keys():
            click.exceptions.BadParameter(
                message=f"'{apply}' not in '{color_configs.keys()}'"
            )
            ctx.exit(1)

        updated_config = apply_color_config(color_configs[apply], config)
        new_color = apply

    if switch:
        current_color = get_current_color(color_dir)
        new_color = get_next_color(current_color, color_configs)
        updated_config = apply_color_config(color_configs[new_color], config)

    if reset_default:
        default_fp = resources.open_text(templates, "default.yaml")
        default_config = yaml.load(default_fp)
        updated_config = apply_color_config(default_config, config)
        new_color = None

    if debug:
        yaml.dump(updated_config, stream=sys.stdout)
    else:
        with config.open("w") as fp:
            yaml.dump(updated_config, stream=fp)

    if new_color:
        set_current_color(new_color, color_dir)


if __name__ == "__main__":
    main()
