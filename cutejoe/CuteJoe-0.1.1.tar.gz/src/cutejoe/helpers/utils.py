# TODO improve me, please
import os
import re
import subprocess

import yaml


def command_process(command):
    process = subprocess.run(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if process.stderr:
        raise Exception(process.stderr)
    return process.stdout.decode()


def get_project_url():
    url = command_process("git config --get remote.origin.url")

    if not url.startswith("git@"):
        return url.strip()

    return "https://github.com/" + url.split(":")[1].strip().rstrip(".git")


def get_unreleased_commits(start="master", end="HEAD"):
    return command_process(f"git --no-pager log {start}...{end} --reverse --pretty=format:'%b'")


def get_last_tag():
    try:
        tag = command_process("git describe --tags")
    except Exception:
        return "v0.0.0"

    tag_regex = r"(v\d+\.\d+)(\.\d+)?.*"
    tag_match = re.match(tag_regex, tag)

    tag = tag_match.group(1)
    tag += tag_match.group(2) or ".0"
    return tag


def read_text_file(file_path: str) -> list:
    with open(file_path, "r") as file:
        return file.readlines()


def read_yml_file(file_path: str) -> dict:
    """
    Raises:
        - yaml.YAMLError if invalid yml file
        - FileNotFoundError if file not found
    """
    with open(file_path, "r") as file:
        return yaml.safe_load(file)


def save_text_file(file_path: str, content: list):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as file:
        file.writelines(content)

    return file_path
