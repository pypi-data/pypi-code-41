"""cli commands"""
import json
from invoke import task

from .validators import validate_path
from .validators import tags_to_json
from .validators import set_secret
from .validators import read_value

from .tuples import create_secret
from .tuples import update_secret
from .tuples import get_secret
from .tuples import tag_secret
from .tuples import untag_secret
from .tuples import list_secrets

from .output import print_read, print_list, print_export


@task(optional=['isjson', 'description', 'tags'])
def create(_ctx, path, value, isjson=False, description=None, tags=None):
    """create path/key value | - [--description STRING] [--tags TAG=STRING, ..] [--isjson]

       Flags:

         --description STRING        Add a description to new secret.

         --tags <tag>=<value>, ...   Include tags with new secret.

         - [--isjson]                Read value from stdin. Include --isjson to validate json string.

                                     $> cat <filename> | secretctl create myapp/dev/public-key -
                                     myapp/dev/public-key created
    """
    secret_kwargs = {}
    secret_kwargs['path'] = validate_path(path)
    secret_kwargs['value'] = read_value(path, value, isjson)
    secret_kwargs['description'] = description
    if tags: secret_kwargs['tags'] = tags_to_json(tags)

    resp = create_secret(**secret_kwargs)
    print(f"{resp.path} created")

@task(optional=['isjson', 'description'])
def update(_ctx, path, value, isjson=False, description=None):
    """update path/key value | - [--description STRING] [--isjson]

       Flags:

         --description STRING        Update description of secret.

         - [--isjson]                Read value from stdin. Include --isjson to validate json string.

                                     $> cat <filename> | secretctl update myapp/dev/public-key -
                                     myapp/dev/public-key updated
    """
    secret_kwargs = {}
    secret_kwargs['path'] = validate_path(path)
    secret_kwargs['value'] = read_value(path, value, isjson)
    secret_kwargs['description'] = description
    resp = update_secret(**secret_kwargs)
    print(f"{resp.path} updated")

@task(optional=['quiet', 'info'])
def read(_ctx, path, quiet=False, info=False):
    """read path/key [--quiet] [--info]

       $>  secretctl read myapp/dev/docker_login
       Path/Key                   Version   Value
       myapp/dev/docker_login     1         mydockerlogin

       Flags:

         --quiet            Return only the secret value. Useful for working with secrets in pipelines.
                            Ex: Set DOCKER_LOGIN = to secret

                            $>  export DOCKER_LOGIN=$(secretctl read myapp/dev/docker_login -q)
                            $>  echo $DOCKER_LOGIN
                            mydockerlogin

         --info             Show description and tags.
    """
    print_read(get_secret(validate_path(path)), quiet=quiet, info=info)


# removed from code coverage pending moto support for mocking secretsmanager tags
@task
def tag(_ctx, path, tags):   # pragma: no cover
    """tag key/value 'TAG=STRING, ..'"""
    secret_kwargs = {}
    secret_kwargs['path'] = validate_path(path)
    secret_kwargs['tags'] = tags_to_json(tags)
    resp = tag_secret(**secret_kwargs)
    print(f"{resp.path} tagged")

# removed from code coverage pending moto support for mocking secretsmanager tags
@task
def untag(_ctx, path, tags):   # pragma: no cover
    """untag path/key 'TAG, ..'"""
    secret_kwargs = {}
    secret_kwargs['path'] = validate_path(path)
    secret_kwargs['tags'] = tags_to_json(tags, novalue=True)
    resp = untag_secret(**secret_kwargs)
    print(f"tags removed from {resp.path}")

#pylint: disable=W0622
@task(optional=['path', 'tags'])
def list(_ctx, path=None, tags=None):
    """list [--path STRING] [--tags STRING]

       Flags:

         --path STRING      Returns the subset of secrets with path STRING.
                            Ex: lists all the secrets for the dev environment of myapp

                            $>  secretctl list -p di/dev/
                            Path/Key                Description                             Tags
                            di/dev/docker_username  access credentials for private regis..  team=di
                            di/dev/docker_password  access credentials for private regis..  team=di
                            di/dev/vault_token      team vault token                        team=di
                            Found 3 secrets.

         --tags STRING      Filter secrets by Tag STRING. Will includes tags with Keys or Values that 'contain' STRG.
                            Ex: lists all the secrets with a Tag containing a team's name, "bravo"

                            $ secretctl list -t bravo
                            Path/Key      Description     Tags
                            app/dev/pem   private key     team=bravo
                            app/qa/pem    private key     team=bravo
    """
    secrets = []
    filter_secrets = list_secrets()
    if path: path = validate_path(path)
    filter_secrets = [sec for sec in filter_secrets if not path or (path and sec['Name'].startswith(path))]
    filter_secrets = [sec for sec in filter_secrets if not tags or ('Tags' in sec and tags in json.dumps(sec['Tags']))]
    for secret in filter_secrets:
        secrets.append(set_secret(secret))

    if len(secrets) >= 1:
        print_list(secrets)
        print(f"Found {len(secrets)} secrets.")
    else:
        print('secretctl: no secrets match filter')

@task(optional=['output'])
def export(_ctx, path, output='tfvars'):
    """export path/ [--output json | csv | tfvars(default)]

       $> secretctl export myapp/dev
       docker_login=username123
       docker_password=passwordABC

       Flags:

         --output [option]  Output format options: tfvars(dotenv), json, csv

                            $>  secretctl export myapp/dev -o json > env_vars.json
                            $>  cat env_vars.json
                            {
                            "docker_login": "username123",
                            "docker_password": "passwordABC"
                            }

    """
    if path: path = validate_path(path)
    secrets = []
    for secret in list_secrets():
        if not path or (path and secret['Name'].startswith(path)):
            secrets.append(get_secret(secret['Name']))

    if len(secrets) >= 1:
        print_export(secrets, output=output)
    else:
        print('secretctl: no secrets match filter')
