import os
from inspect import cleandoc
from distutils.cmd import Command
from setuptools_freeze.constant import ENTRY_POINT_TEMPLATE, INNO_TEMPLATE


def guid(dist, keyword, value):
    setattr(dist.metadata, 'guid', value)


class PyInstallerCmd(Command):

    description = 'Freeze the package with pyinstaller'
    user_options = [
        ('addopts=', None, 'Additional options for pyinstaller'),
        ('cleanup', None, 'Delete *.spec and entry files'),
    ]

    def initialize_options(self):
        self.addopts = ''
        self.cleanup = False

    def finalize_options(self):
        pass

    def run(self):
        self._freeze()
        if self.cleanup:
            self._cleanup()

    def _get_console_scripts(self):
        entry_points = getattr(self.distribution, 'entry_points', {})
        console_scripts = entry_points.get('console_scripts', [])
        for entry_point in console_scripts:
            name, entry = [part.strip() for part in entry_point.split("=")]
            module, func = [part.strip() for part in entry.split(":")]
            yield (name, module, func)

    def _freeze(self):
        for (name, module, func) in self._get_console_scripts():
            script = cleandoc(
                ENTRY_POINT_TEMPLATE.format(module, func, func)
            )
            input_file = "build/{}_entry.py".format(name)
            with open(input_file, "w") as outfile:
                outfile.write(script)
            self._pyinstaller(name, input_file)

    def _pyinstaller(self, name, target):
        cmd = "pyinstaller --name {} {} {}".format(name, self.addopts, target)
        if os.system(cmd):
            raise Exception("PyInstaller failed!")

    def _cleanup(self):
        for file in os.listdir('.'):
            if file.endswith('.spec'):
                os.remove(file)

        for file in os.listdir('build'):
            if file.endswith('_entry.py'):
                os.remove(os.path.join('build', file))


class InnoSetupCmd(Command):
    description = 'Creat a setup with "Inno Setup"'
    user_options = [
        ('addopts=', None, 'Additional options for Inno Setup'),
        ('cleanup', None, 'Delete *.iss file'),
        ('guid', None, 'Set the guid'),
    ]

    def initialize_options(self):
        self.addopts = ''
        self.cleanup = False
        self.guid = None

    def finalize_options(self):
        pass

    def run(self):
        self._check()
        self._inno()
        if self.cleanup:
            self._cleanup()

    def _check(self):
        self.data = {
            'author': self.distribution.metadata.author or 'Axel Juraske',
            'url': self.distribution.metadata.url or '',
            'version': self.distribution.metadata.version or '0.0.0',
            'guid': self.guid or self.distribution.metadata.guid or 'ERROR',
        }

    def _inno(self):
        for name in self._dists():
            script = INNO_TEMPLATE.format(name=name, **self.data)
            input_file = "build/{}.iss".format(name)
            with open(input_file, "w") as outfile:
                outfile.write(script)
            cmd = 'compil32 /cc {} "build/{}.iss"'.format(self.addopts, name)
            if os.system(cmd):
                raise Exception("PyInstaller failed!")

    def _dists(self):
        for dir in os.listdir('dist'):
            path = os.path.abspath(os.path.join('dist', dir))
            if os.path.isdir(path):
                if os.path.isfile(os.path.join(path, dir+'.exe')):
                    yield dir

    def _cleanup(self):
        for file in os.listdir('build'):
            if file.endswith('.iss'):
                os.remove(os.path.join('build', file))
