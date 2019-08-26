'''Utilities to bump version'''
from json import load, dump
from datetime import datetime
from dataclasses import dataclass, asdict
from invoke.exceptions import Exit

from rscli.utils import abcfp


@dataclass
class Version:
    year: int
    build: int
    release: str
    release_number: int

    @classmethod
    def load(cls, kwargs):
        return cls(**kwargs)

    @classmethod
    def dummy(cls):
        '''Create a initial dummy version'''
        return cls(
            year=datetime.now().year, build=1, release='a', release_number=1)

    @property
    def version_string(self) -> str:
        v = f'{self.year}.{self.build}'
        release_str = self.release
        if release_str == 'f':
            release_str = ''
        elif release_str == 'p':
            release_str = '.post'
        if self.release_number != 0:
            v = f'{v}{release_str}'
            v = f'{v}{self.release_number}'
        return v

    def bump_build(self):
        self.build += 1
        self.release = 'a'
        self.release_number = 1
        return self.version_string

    def bump(self, release: str, force_year_bump: bool = True) -> str:
        if release not in abcfp:
            raise ValueError(f'Not a valid release: {release}!')

        year = datetime.now().year
        if force_year_bump and year != self.year:
            # Happy new year! Let's reset the build number!!
            self.year = year
            self.build = 0
            return self.bump_build()

        if release in set('abc'):
            if release == self.release:
                self.release_number += 1
            elif release > self.release:
                self.release = release
                self.release_number = 1
            else:
                raise ValueError('Can\'t Downgrade! try bump_build maybe?')

        elif release == 'f':
            if self.release in set('fp'):
                raise ValueError('Can\'t do a final release! Try bump_build?')
            else:
                self.release = release
                self.release_number = 0

        elif release == 'p':
            if self.release == 'p':
                self.release_number += 1
            elif self.release == 'f':
                self.release = release
                self.release_number = 1
            else:
                raise ValueError(
                    'Post releases can be made only on final / post release')

        return self.version_string

    def __lt__(self, other) -> bool:
        attrs = ['year', 'build', 'release', 'release_number']
        for attr in attrs:
            self_val = getattr(self, attr)
            other_val = getattr(other, attr)
            if self_val < other_val:
                return True
            if self_val > other_val:
                return False
        return False

    def __le__(self, other) -> bool:
        return self < other or self == other

    def __gt__(self, other) -> bool:
        return not self <= other

    def __ge__(self, other) -> bool:
        return self > other or self == other


def _get_currnet_version():
    version_json = load(open('.version.json'))
    current_kwargs = version_json['version']
    return Version.load(current_kwargs), version_json['files']


def bump_version(
        release=None, build: bool = False, force_year_bump: bool = True):
    current_version, files = _get_currnet_version()
    current_version_str = current_version.version_string
    if build:
        new_version_str = current_version.bump_build()
    else:
        new_version_str = current_version.bump(release, force_year_bump)
    for file in files:
        content = open(file).read()
        if current_version_str not in content:
            raise Exit(
                f'Version `{current_version_str}` not found in {file}', 1)
        content = content.replace(current_version_str, new_version_str)
        with open(file, 'w') as f:
            f.write(content)
        dump(
            {"version": asdict(current_version), "files": files},
            open('.version.json', 'w'), indent=4)
    # TODO: Find and replace version in files
    # Tag commit
    # Push tag
    return current_version_str, new_version_str
