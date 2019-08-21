import re
import time
from pathlib import Path

import pyperclip

schema = (
    r"(aws_access_key_id = )[^\n]+\n"
    r"(aws_secret_access_key = )[^\n]+\n"
    r"(aws_session_token = )[^\n]+"
)


def main():
    recent_value = pyperclip.paste()
    while True:
        tmp_value = pyperclip.paste()
        if tmp_value != recent_value:
            update_credentials(Path.home() / ".aws" / "credentials", tmp_value)
            recent_value = tmp_value
        time.sleep(0.5)


def update_credentials(credentials_file: Path, new_credentials: str):
    new_credentials_match = re.fullmatch(
        re.compile(r"(?P<account>\[\d{12}_\w+\])\n%s" % schema), new_credentials
    )
    if new_credentials_match:
        try:
            with open(credentials_file.as_posix(), "r") as f:
                file_content = f.read()
        except FileNotFoundError:
            append_to_file(credentials_file, new_credentials)
            return
        old_credentials_match = re.search(
            re.compile(
                r"(%s)\n%s" % (re.escape(new_credentials_match["account"]), schema)
            ),
            file_content,
        )
        if old_credentials_match:
            write_to_file(
                credentials_file,
                new_credentials,
                old_credentials_match[0],
                file_content,
            )
        else:
            append_to_file(credentials_file, new_credentials)


def write_to_file(
    credentials_file: Path,
    new_credentials: str,
    old_credentials: str,
    file_content: str,
):
    with open(credentials_file.as_posix(), "w") as f:
        f.write(file_content.replace(old_credentials, new_credentials))


def append_to_file(credentials_file: Path, credentials: str):
    with open(credentials_file.as_posix(), "a") as f:
        f.write(f"\n{credentials}\n")
