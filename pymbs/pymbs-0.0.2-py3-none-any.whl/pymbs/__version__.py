"""
PyMBS is a Python library for use in modeling Mortgage-Backed Securities.
Copyright (C) 2019  Brian Farrell

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Contact: brian.farrell@me.com
"""

from collections import namedtuple

Version = namedtuple(
    '_version_tuple',
    ['major', 'minor', 'micro', 'pre_tags', 'post_tag']
)

version_pre_tags = []
version_post_tag = ''
version_git_tags = []
version_git_rev = ''


def _basic_version(version):
    """Creates a basic, semantic version string

       For additional information on Semantic Versioning,
       see https://semver.org

        Args:
            version: An instance of a Version namedtuple

        Returns:
            A string created from the Version tuple, formatted using
            basic Smeantic Versioning.
            example:

            '1.2.3'
    """
    v = '.'.join([str(getattr(version, f'{field}'))
                  for field in version._fields
                  if field in
                  ('major', 'minor', 'micro')])

    return v


def _version_to_git_string(version):
    pass


def _version_to_string(version):
    """Creates a version string according to PEP-440

       For additional information, please
       see https://www.python.org/dev/peps/pep-0440/#version-scheme

        Args:
            version: An instance of a Version namedtuple

        Returns:
            A string created from the Version tuple, formatted according
            to PEP-440
            example:

            '0.0.1.dev.b1'
    """
    s1 = '.' if version.pre_tags else ''
    s2 = '.' if version.pre_tags else ''
    v = f'.'.join([str(getattr(version, f'{field}'))
                   for field in version._fields
                   if field in ('major', 'minor', 'micro')]) + \
        f'{s1}' + f'.'.join([tag for tag in version.pre_tags]) + \
        f'{s2}{version.post_tag}'

    return v


# To increment the version, increment it in the Version tuple _version_t_
_version_t_ = Version(0, 0, 2, version_pre_tags, version_post_tag)
_short_version_ = _basic_version(_version_t_)
__version__ = _version_to_string(_version_t_)

_version_min_python_t_ = Version(3, 6, 0, [], '')
_version_min_python_ = _version_to_string(_version_min_python_t_)
