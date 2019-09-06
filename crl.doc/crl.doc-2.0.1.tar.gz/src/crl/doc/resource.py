import os
import shutil
from jinja2 import Template
from .util import create_dir
from .template import TEMPLATE_DIR


__copyright__ = 'Copyright (C) 2019, Nokia'


class Resource():
    def __init__(self, src_path, dst_path):
        self._src_path = self._get_path_with_trailing_slash(src_path)
        self._dst_path = dst_path
        self._template = self._create_template()

    @staticmethod
    def _get_path_with_trailing_slash(path):
        return os.path.join(path, '')

    @staticmethod
    def _create_template():
        with open(os.path.join(TEMPLATE_DIR, 'resource.rst')) as f:
            return Template(f.read())

    def generate_rst(self):
        for d, _, fs in os.walk(self._src_path):
            dst_parent = os.path.join(self._dst_path, d[len(self._src_path):])
            for f in fs:
                if os.path.splitext(f)[1] == '.robot':
                    create_dir(dst_parent)
                    r = ResourceFile(os.path.join(d, f), self._template)
                    r.generate_rst(dst_parent)


class ResourceFile():
    def __init__(self, path, template):
        self._path = path
        self._template = template
        self._lines = self._read()

    def generate_rst(self, dst_path):
        # copying the robot file to destination to make download path easy
        self._copy_resource_to_dst(dst_path)
        with open(os.path.join(dst_path, self._rstpath), 'w') as f:
            f.write(self._template.render(resourcefile=self))

    def _copy_resource_to_dst(self, dst_path):
        shutil.copy2(self._path, dst_path)

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def has_variables(self):
        return self._contains('*** Variables ***')

    @property
    def has_keywords(self):
        return self._contains('*** Keywords ***')

    @property
    def has_testcases(self):
        return self._contains('*** Test Cases ***')

    @property
    def _rstpath(self):
        return os.path.basename(self._path) + '.rst'

    def _contains(self, s):
        return any([line.strip().startswith(s) for line in self._lines])

    def _read(self):
        with open(self._path) as f:
            return f.readlines()
