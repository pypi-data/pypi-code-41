from __future__ import print_function
import os
import sys
import json
from pywebhdfs.webhdfs import PyWebHdfsClient

perm_map = {
    '0': '---',
    '1': '--x',
    '2': '-w-',
    '3': '-wx',
    '4': 'r--',
    '5': 'r-x',
    '6': 'rw-',
    '7': 'rwx',
}


# remove the tailing slash
# foo/ ==> foo
# / ==> EMPTY string
def cut_tail_slash(s):
    while s[-1:] == '/':
        s = s[:-1]
    return s


# add slash to tail if needed
# e.g.: foo ==> foo/
#       foo/ ==> foo/
def add_tail_slash(s):
    s = s.strip()
    if not s.endswith('/'):
        return s + '/'
    return s


# remove the path and only return the filename
# e.g: foo/bar.txt ==> bar.txt
def get_filename(s):
    return cut_tail_slash(s).split("/")[-1]


def permission_to_str(file_summary):
    if len(file_summary["permission"]) not in (3, 4):
        raise Exception("bad permission: {}".format(permission_str))

    if len(file_summary["permission"]) == 4:
        permission_str = file_summary["permission"][1:]
    else:
        permission_str = file_summary["permission"]

    if file_summary["type"] == "DIRECTORY":
        ret = 'd'
    else:
        ret = '-'

    ret += perm_map[permission_str[0:1]]
    ret += perm_map[permission_str[1:2]]
    ret += perm_map[permission_str[2:3]]

    return ret

class DfsToolException(Exception):
    def __init__(self, message, exit_code=1):
        self.message = message
        self.exit_code = exit_code


def fail(message, exit_code=1):
    print(message)
    assert exit_code != 0
    sys.exit(exit_code)


def run_command(action):
    try:
        action()
    except DfsToolException as e:
        print("Error: {}".format(str(e)))
        sys.exit(e.exit_code)
    except Exception as e:
        print("Error: {}".format(str(e)))
        sys.exit(1)

# Parse command line arguments
# ls -al ==> ["ls"], {"a", "l"}
def parse_args():
    args = []
    options = set()

    idx = 1
    while idx < len(sys.argv):
        arg = sys.argv[idx]

        if not arg.startswith("-"):
            args.append(arg)
            idx += 1
            continue

        for ch in arg[1:]:
            if ('a' <= ch <= 'z') or ('A' <= ch <= 'Z'):
                options.add(ch)

        idx += 1

    return args, options


def get_hdfs():
    config_filename = os.environ.get(
        "DFS_TOOL_CFG",
        os.path.expanduser("~/.dfs_tool/config.json")
    )
    with open(config_filename, "r") as f:
        config = json.load(f)

    base_uri_pattern = add_tail_slash(config["api_base_uri"])
    username = config["username"]
    password = config["password"]
    return PyWebHdfsClient(
        base_uri_pattern=base_uri_pattern,
        request_extra_opts={
            'verify': False,
            'auth': (username, password)
        },
    )

def get_config():
    config_filename = os.environ.get(
        "DFS_TOOL_CFG",
        os.path.expanduser("~/.dfs_tool/config.json")
    )
    with open(config_filename, "r") as f:
        return json.load(f)
