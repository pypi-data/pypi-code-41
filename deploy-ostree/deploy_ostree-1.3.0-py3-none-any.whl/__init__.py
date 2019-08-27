# Copyright 2018, 2019 Felix Krull
# Licensed under the MIT license, see LICENSE for details.

import argparse
from pathlib import Path
import sys

from .config_source import open as cfg_open
from .config import Config, InvalidConfigError
from .run import ProcessError
from .steps import get_deploy_steps


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='deploy-ostree',
        description='deploy and configure an OSTree commit'
    )

    parser.add_argument(
        '--sysroot',
        metavar='SYSROOT',
        dest='sysroot',
        type=Path,
        help='root directory to work in (default: /)'
    )
    parser.add_argument(
        '--karg-root',
        metavar='ROOT',
        dest='root_filesystem',
        type=str,
        help='root partition to pass to the kernel (default: autodetect)'
    )
    parser.add_argument(
        '--fstab',
        metavar='FSTAB',
        dest='fstab',
        type=Path,
        help='fstab to copy into the deployment (default: /etc/fstab)'
    )
    parser.add_argument(
        'config',
        metavar='CONFIG',
        type=str,
        help='the path to the configuration file'
    )

    return parser


def parse_config(filename_or_url: str, **kwargs) -> Config:
    with cfg_open(filename_or_url) as cfg_source:
        if cfg_source.has_extension('.toml'):
            return Config.parse_toml(cfg_source.stream, base_dir=cfg_source.base_dir, **kwargs)
        else:
            return Config.parse_json(cfg_source.stream, base_dir=cfg_source.base_dir, **kwargs)


def main():
    parser = build_argument_parser()
    args = parser.parse_args(sys.argv[1:])

    try:
        cfg = parse_config(
            args.config,
            sysroot=args.sysroot,
            root_filesystem=args.root_filesystem,
            fstab=args.fstab
        )
    except OSError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    except InvalidConfigError as exc:
        print('Invalid configuration:', exc, file=sys.stderr)
        sys.exit(1)

    steps = get_deploy_steps(cfg)
    try:
        steps.run()
    except ProcessError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    finally:
        steps.cleanup()
