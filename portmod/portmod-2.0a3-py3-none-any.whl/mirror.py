# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import shutil
import argparse
import sys
import traceback
from portmod.repo.loader import load_all
from portmod.repo.download import download_mod
from portmod.log import err
from .repo.use import use_reduce
from .repo.metadata import get_license_groups, get_repo_root


def mirror():
    parser = argparse.ArgumentParser(
        description="Command line interface to update a local mirror"
    )
    parser.add_argument("--mirror", metavar="DIR", help="Directory to mirror into")
    parser.add_argument("--debug", help="Enables debug traces", action="store_true")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    if args.mirror:
        os.makedirs(args.mirror, exist_ok=True)
        for mod in load_all():
            # FIXME: Determine which sources have use requirements
            # that don't enable mirror or fetch
            if "mirror" not in mod.RESTRICT and "fetch" not in mod.RESTRICT:
                redis = get_license_groups(get_repo_root(mod.FILE)).get(
                    "REDISTRIBUTABLE"
                )

                def is_license_redis(group):
                    if isinstance(group, str):
                        return group in redis
                    elif group[0] == "||":
                        return any(is_license_redis(li) for li in group)
                    else:
                        return all(is_license_redis(li) for li in group)

                if is_license_redis(
                    use_reduce(mod.LICENSE, opconvert=True, matchall=True)
                ):
                    try:
                        for source in download_mod(mod, True):
                            path = os.path.join(args.mirror, source.name)
                            if not os.path.exists(path):
                                print("Copying {} -> {}".format(source.path, path))
                                shutil.copy(source.path, path)
                    except Exception as e:
                        traceback.print_exc()
                        err("{}".format(e))
