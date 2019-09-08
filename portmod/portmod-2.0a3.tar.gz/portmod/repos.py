# Copyright 2019 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

# File for interacting with PORTMOD_CONFIG/repos.cfg

import sys
import os
import ast
from portmod.globals import env
from portmod.log import warn
import configparser


class Repo:
    def __init__(
        self, name, location, auto_sync, sync_type, sync_uri, masters, priority
    ):
        self.name = name
        self.location = location
        self.auto_sync = auto_sync
        self.sync_type = sync_type
        self.sync_uri = sync_uri
        self.masters = masters
        self.priority = priority


# Parses list of repos from repos.cfg
def get_repos():
    repo_config = configparser.ConfigParser()
    repos = []
    default_repo = Repo(
        "openmw",
        os.path.join(env.PORTMOD_LOCAL_DIR, "openmw"),
        True,
        "git",
        env.REPO,
        [],
        -1000,
    )
    if not os.path.exists(env.REPOS_FILE):
        repos.append(default_repo)
    else:
        repo_config.read(env.REPOS_FILE)

        if "openmw" not in repo_config:
            repos.append(default_repo)

        for name, conf in repo_config.items():
            if name == "DEFAULT":
                # Ignore DEFAULT key, as it is always there. We will not use it
                continue

            # Repo must at least have a location
            if "location" in conf:
                repos.append(
                    Repo(
                        name,
                        os.path.expanduser(conf.get("location")),
                        ast.literal_eval(conf.get("auto_sync", "False")),
                        conf.get("sync_type"),
                        conf.get("sync_uri"),
                        conf.get("masters", "").split(),
                        int(conf.get("priority", 0)),
                    )
                )
            else:
                warn('Repo "{}" is missing a location. Skipping...'.format(name))

    # Sort repos by priority such that the highest priority appears first
    repos.sort(key=lambda x: x.priority, reverse=True)
    # Append the path for each repo to sys.path so that the pyclass dir can
    # be loaded as a module
    for repo in repos:
        sys.path.append(os.path.join(repo.location))

    return repos
