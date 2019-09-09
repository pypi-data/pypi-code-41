"""
Plunger - A tool to inspect and clean gitlab's docker registry.
Copyright (C) 2019 Bearstech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import sys
import os
import argparse
import logging
import textwrap
from fnmatch import fnmatch
from datetime import datetime
from operator import itemgetter

import texttable
import requests
from .sentry_script import with_sentry
from .jwt_token import get_token
from plunger import version


class Plunger:

    def __init__(self, registry, key, payload):
        self.registry = registry.rstrip('/')
        self.key = key
        self.payload = payload
        self.session = requests.Session()
        self.broken_repos = {}
        self.failed = []
        self.log = logging.getLogger('plunger')

    def set_token_header(self, repositories=None):
        """generate the correct token and use it as a session header"""
        if self.key:
            token = get_token(self.key, repositories, **self.payload)
            self.session.headers.update({
                'Authorization': 'Bearer {}'.format(token)
            })
            return self.session.headers

    def check_version(self):
        """ensure we can login"""
        self.set_token_header()
        resp = self.session.get(self.registry + '/v2/')
        if resp.status_code != 200:
            raise RuntimeError(resp)
        return True

    def get_repo_tags(self, name):
        """get all available tags for a repo"""
        url = self.registry + '/v2/{0}/tags/list'.format(name)
        resp = self.session.get(url)
        data = resp.json()
        if isinstance(data, dict):
            return data.get('tags') or []
        return []

    def get_tag_manifest(self, name, tag):
        """get repos manifest v2"""
        url = self.registry + '/v2/{0}/manifests/{1}'.format(name, tag)
        resp = self.session.get(url, headers={
            'Accept': 'application/vnd.docker.distribution.manifest.v2+json',
            'Content-Type': 'application/json'})
        data = resp.json()
        layers = {layer['digest']: layer['size'] for layer in data['layers']}
        digest = resp.headers['docker-content-digest']

        # get config manifest for created date
        path = '/v2/{0}/blobs/{1}'.format(name, data['config']['digest'])
        url = self.registry + path
        resp = self.session.get(url, headers={
            'Content-Type': 'application/json'})
        data = resp.json()
        created = datetime.strptime(
            data['created'].split('.')[0],
            '%Y-%m-%dT%H:%M:%S')

        # return usefull data to show sizes / delete tag
        manifest = {
            'digest': digest,
            'created': created,
            'layers': layers,
            'size': sum(layers.values()),
        }
        return manifest

    def get_full_catalog(self, pattern=''):
        """get all repositories filtered (if any filter provided"""
        self.set_token_header()

        resp = self.session.get(self.registry + '/v2/_catalog')
        data = resp.json()
        names = data['repositories']

        # filter names
        if '*' not in pattern:
            pattern += '*'
        names = [name for name in names if fnmatch(name, pattern)]

        if self.key:
            self.set_token_header(names)

        for rname in names:
            repo = {'name': rname, 'tags': []}
            tags = self.get_repo_tags(rname)
            for name in tags:
                tag = {'name': name}
                try:
                    data = self.get_tag_manifest(rname, tag['name'])
                except Exception as e:
                    self.log.exception('error while fetching manifest')
                    self.broken_repos[rname] = str(e)
                    break
                tag.update(data)
                repo['tags'].append(tag)
            if rname not in self.broken_repos:
                repo['tags'] = sorted(repo['tags'],
                                      key=itemgetter('created'))
                yield repo

    def delete_tags(self, name, tags, dry_run=False):
        """delete tags for repository name"""
        if not tags:
            self.log.info('Nothing to delete')
            return
        for tag in tags:
            path = '/v2/{0}/manifests/{1[digest]}'.format(name, tag)
            url = self.registry + path
            self.log.info('DELETE ' + url)
            if not dry_run:
                resp = self.session.delete(url)
                if resp.status_code != 202:
                    self.log.error(str(resp))
                    self.failed.append((url, resp))


@with_sentry
def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent("""
        A toot to inspect and clean gitlab's docker registry.
        """),
        epilog=textwrap.dedent("""
        Examples
        --------

        First export some env var to avoid reapeating command line arguments:

            $ export PLUNGER_REGISTRY=https://your.gitlab.registry/
            $ export PLUNGER_KEY_FILE=/path/to/your/key

        Inspect the registry:

            $ # show size used by images, grouped by gitlab group
            $ plunger --list 1

            $ # show sizes only for a group
            $ plunger --list 2 --filter repository/

            $ # show sizes of all tags
            $ plunger --list 0 --filter repository/path/

        Remove some images:

            $ # keep 4 latest tags for each repos
            $ plunger --keep 4
            $ # keep 2 latest tags for repos starting with 'repository/'
            $ plunger --keep 2 --filter repository/
        """)
    )
    parser.add_argument(
        '--version', action='store_true', default=False,
        help='show version')
    parser.add_argument('--basic-auth', default=None,
                        help='username:password (useless if you use key file)')
    key_file = os.environ.get('PLUNGER_KEY_FILE')
    parser.add_argument('--key-file', default=key_file,
                        help=('full path to the private .key file '
                              'to use for token generation'))
    registry = os.environ.get('PLUNGER_REGISTRY', 'http://localhost:5000')
    parser.add_argument('-r', '--registry', metavar='URL',
                        default=registry,
                        help=('Full url of the registry. '
                              'Default: %s') % registry)
    parser.add_argument('--issuer',
                        default='gitlab-issuer',
                        help='Issuer. Default: gitlab-issuer')
    parser.add_argument('--audience',
                        default='container_registry',
                        help='Audience. Default: container_registry')
    parser.add_argument('-l', '--list', action='store', type=int,
                        metavar='DEPTH', default=-1,
                        help=(
                            'Just list images size, by depth. '
                            '-l 0 show all tags. -l 1 show first level.'
                            '-l 2 show second level. Etc.'
                        ))
    parser.add_argument('-f', '--filter', action='store',
                        default='',
                        help=(
                            'Filter images based on pattern. '
                            'Example: -f myrepo/'
                        ))
    parser.add_argument('-k', '--keep', metavar='N', type=int, default=4,
                        help=('Number of tags to keep per repository. '
                              'Default: 4'))
    parser.add_argument('--dry-run', action='store_true', default=False,
                        help='Just print DELETE actions')
    args = parser.parse_args()

    if args.version:
        version.main()
        return

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    plunger = Plunger(
        registry=args.registry,
        key=args.key_file,
        payload={
            'aud': args.audience,
            'iss': args.issuer,
        },
    )
    plunger.check_version()

    if args.list >= 0:
        table = texttable.Texttable()
        total = 0

        if args.list == 0:
            # show size of all images / tags
            table.set_cols_dtype(['t', 't', 't', 'f'])
            table.set_cols_align(['l', 'c', 'c', 'r'])
            table.set_cols_width([35, 41, 20, 10])
            table.add_row(['Repository path', 'Tag', 'Date', 'Size (MiB)'])
            total_layers = {}
            for repo in plunger.get_full_catalog(pattern=args.filter):
                # store table rows
                rows = []
                # store layers size
                layers = {}

                # sort tags by date
                tags = sorted(repo['tags'], key=itemgetter('created'),
                              reverse=True)

                for tag in tags:
                    rows.append([
                        '',
                        tag['name'],
                        tag['created'],
                        tag['size'] / 1024 / 1024,
                    ])
                    for layer, size in tag['layers'].items():
                        layers[layer] = size
                        total_layers[layer] = size
                # repo row
                size = sum(layers.values())
                table.add_row([repo['name'], '', '', size / 1024 / 1024])

                # tags rows
                for row in rows:
                    table.add_row(row)

            total += sum(total_layers.values())
            table.add_row(['Total', '', '', total / 1024 / 1024])
        else:
            # show sizes grouped by path

            # store grouped data: name: {layer: size, ...}
            groups = {}
            for repo in plunger.get_full_catalog(pattern=args.filter):
                # group name, splitted on -l first slashes
                name = '/'.join(
                    repo['name'].split('/', args.list)[0:args.list]
                )
                # group layers
                layers = groups.setdefault(name, {})
                for tag in repo['tags']:
                    for layer, size in tag['layers'].items():
                        layers[layer] = size

            # results
            table = texttable.Texttable()
            table.set_cols_dtype(['t', 'f'])
            table.set_cols_align(['l', 'r'])
            table.add_row(['Repository path', 'Size (MiB)'])
            for name in sorted(groups):
                size = sum(groups[name].values())
                total += size
                table.add_row([name, size / 1024 / 1024])

            # draw table
            table.add_row(['Total', total / 1024 / 1024])
        print(table.draw())

        # done listing
        sys.exit(0)

    # deleting tags when needed
    for repo in plunger.get_full_catalog(pattern=args.filter):
        plunger.log.info('Checking %s' % repo['name'])
        # store tags to delete
        tags = []
        # a digest can be used by more than one tag
        # ensure digest are deleted only once
        digests = []
        for tag in repo['tags']:
            digest = tag['digest']
            if digest not in digests:
                digests.append(digest)
                tags.append(tag)
        plunger.delete_tags(
            repo['name'],
            tags[:-args.keep] if args.keep > 0 else tags,
            dry_run=args.dry_run)

    # show errors if any
    for name, err in plunger.broken_repos.items():
        logging.error('%s is broken: %s' % (name, err))
    for failed in plunger.failed:
        logging.error(failed)
    if plunger.failed or plunger.broken_repos:
        sys.exit(1)
