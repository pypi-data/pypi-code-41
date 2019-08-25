"""validate inputs"""
import re
import sys
import json
from secretctl.tuples import Secret

DELIM = '/'

# validate user path input
def validate_path(path):
    """validate secret path name: characters, delimeter, lenth"""
    path = path[:-1] if path[-1] == '/' else path
    if not re.match(r"^(?=.{2,256}$)([a-zA-Z0-9_@.-]+\/)*([a-zA-Z0-9_@.-])*[a-zA-Z0-9_@.-]$", path):
        print("secretctl: invalid path/key name. Allowable characters include [A-z0-9_@.-], " \
              "/ for path delimiter, 3 to 256 chars long")
        sys.exit(1)
    return path

# convert cli provided tags into key:value json
def tags_to_json(tags, novalue=False):
    """validate supplied tags and convert to secretsmanager tags json"""
    options = {True: tags_without_values, False: tags_with_values}
    return options[novalue](tags)

def tags_with_values(tags):
    """validate supplied tags-with-values and convert to secretsmanager tags json"""
    tag_list = []
    for tag in tags.split(","):
        if not re.match(r"^(([a-zA-Z0-9\/\+\:_@.-]{3,127})\s*[=]\s*([a-zA-Z0-9\/\+\:_@.-]{1,255}))$", tag.strip()):
            print("secretctl: invalid tags list. Supply tags as \"tag1=value1, tag2=value2, ...\"")
            sys.exit(1)
        tag_list.append({"Key": tag.split("=")[0].strip(), "Value": tag.split("=")[1].strip()})
    return tag_list

def tags_without_values(tags):
    """validate supplied tags-without-values and convert to secretsmanager tags json"""
    tag_list = []
    for tag in tags.split(","):
        if not re.match(r"^([a-zA-Z0-9\/\+\:_@.-]{3,127})$", tag.strip()):
            print("secretctl: invalid remove tags list. Supply tags as \"tag1, tag2, ...\"")
            sys.exit(1)
        tag_list.append(tag.strip())
    return tag_list

# convert json Tags to simple cli formatted
def json_to_tags(tags):
    """format json Tags as simple tag list"""
    tag_list = ""
    for index, _ in enumerate(tags):
        if index == 0:
            tag_list += (tags[index]['Key'] + '=' + tags[index]['Value'])
        else:
            tag_list += (', ' + tags[index]['Key'] + '=' + tags[index]['Value'])
    return tag_list

def read_value(path, value, isjson=False):
    """parse supplied value or response from sys.stdin.read (pipe)"""
    resp = sys.stdin.read() if value == '-' else value
    if isjson:
        try:
            json.loads(resp)
        except ValueError as e:
            print('secretctl: invalid json %s' % e)
            sys.exit(1)
    else:
        resp = json.dumps({path.split(DELIM)[-1]: value})
    return resp

def set_secret(secret):
    """return Secret from list_secret element"""
    secret_kwargs = {}
    secret_kwargs['path'] = secret['Name']
    if 'Description' in secret:
        secret_kwargs['description'] = secret['Description']
    if 'Tags' in secret:
        secret_kwargs['tags'] = secret['Tags']
    return Secret(**secret_kwargs)
