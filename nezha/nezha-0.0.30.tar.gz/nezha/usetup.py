import re


def update_version(file: str, version: str):
    with open(file, encoding='utf-8', mode='r') as f:
        content = f.read()
        pattern = re.compile("\d+\.\d+\.\d+")
        subbed = pattern.sub(version, content)
        with open(file, encoding='utf-8', mode='w') as fl:
            fl.write(subbed)