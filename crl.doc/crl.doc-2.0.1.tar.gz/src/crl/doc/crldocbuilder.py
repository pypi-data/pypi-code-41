import logging
import os
import shutil
import subprocess
import errno
from collections import namedtuple
import pkg_resources
from .robotws_util import add_toc_tree  # pylint: disable=import-error
from .util import create_dir
from .crldocutils import (
    get_robot_builtin_path,
    generate_builtin_doc,
    generate_rflibrary_doc_from_robotdocsconf,
    error_handling)
from .robotdocsconfs import EntrypointRobotdocsconf
from .template import (
    TEMPLATE_DIR,
    TOC_TEMPLATE)
from .resource import Resource


LOGGER = logging.getLogger(__name__)


__copyright__ = 'Copyright (C) 2019, Nokia'


class InvalidRobotdocsconfType(Exception):
    pass


class NamespacePath(namedtuple('NamespacePath', ['namespace', 'path'])):

    @property
    def namespacepath(self):
        return os.path.join(self.path, self.namespace)


class CRLDocBuilder():
    # pylint: disable=too-many-instance-attributes
    """ CRLDocBuilder generates Sphinx documentation source from Robot
    Framework test libraries as default. Document type
    can be filtered with argument if not all the 3 types (builtin, api, crl)
    needed

    **Example usage**:

    - CRLDockBuilder().create_doc()

    - CRLDockBuilder().create_doc(['crl', 'builtin'])

    .. note::

        This tool does not generated the final documentation. The Spinx
        configuration files (e.g. conf.py and index.rst) must be strored either
        before or after the generation into **sphinxdocs** directory prior
        Sphinx build.
    """
    invalid_builtinlib_starts = ['__',
                                 'dialogs',
                                 'dialogs_jy',
                                 'dialogs_py',
                                 'Remote',
                                 'Dialogs']

    def __init__(self, args):
        self.static = pkg_resources.resource_filename('crl.doc', 'resource')

        self.template_lib_rst = os.path.join(TEMPLATE_DIR, 'lib.rst')
        self.template_index_rst = os.path.join(TEMPLATE_DIR, 'index.rst')
        self.xml_root = os.path.join('xmldocs')
        self.rst_root = os.path.join('sphinxdocs')
        self.crl_index_rst_file = os.path.join(self.rst_root, 'crl_index.rst')
        self.rst_crl_api = os.path.join(self.rst_root, 'crl_api')
        self.rst_crl = os.path.join(self.rst_root, 'crl')
        self.relative_path_to_crl = 'crl'
        self.rst_builtin = os.path.join(self.rst_root, 'builtin')
        self._args = args

    @property
    def tmpsrc(self):
        return 'tmpsrc'

    def create_doc(self):
        self._clean_temp_files()
        self._generate_auto_index_docs()
        self._generate_special_index_docs()

    def _clean_temp_files(self):
        for directory in self._generated_dirs:
            shutil.rmtree(directory, True)

    def _generate_auto_index_docs(self):
        self._generate_docspec_docs(self._methods_with_auto_index)
        self._generate_resource_docs()
        self._add_toc_tree()

    def _generate_special_index_docs(self):
        self._generate_docspec_docs(self._methods_with_special_index)
        self._generate_robotdocsconfs_docs()

    def _generate_docspec_docs(self, methods):
        for docspec, method in methods:
            if self._docspec_matches(docspec):
                method()

    @property
    def _methods_with_auto_index(self):
        return [('builtin', self._generate_builtin_documentation),
                ('api', self._generate_api_documentation)]

    @property
    def _methods_with_special_index(self):
        return [('crl', self._generate_crl_documentation)]

    def _docspec_matches(self, docspec):
        return set(['all', docspec]) & set(self._args.docspec)

    def _generate_robotdocsconfs_docs(self):
        for robot_conf in self._args.robotdocsconfs:
            self._generate_docs_for_robotdocs(robot_conf)

    def _generate_docs_for_robotdocs(self, robotdocsconf):
        section = robotdocsconf.metadata.get('Name')
        robotconftoxml = generate_rflibrary_doc_from_robotdocsconf(
            robotdocsconfs=[robotdocsconf],
            template_file=self.template_lib_rst,
            xml_dir=self.xml_root,
            rst_dir=self._get_rst_dir_for_section(section),
            relative_path_to_dir=self._get_relative_path_to_section(section))
        robotconftoxml.set_section(section)
        robotconftoxml.generate_index(
            index_template=self._simple_index_template,
            index_rst_file=self._get_index_rst_for_section(section))

    @property
    def _simple_index_template(self):
        return os.path.join(TEMPLATE_DIR, 'simple_index.rst')

    def _get_rst_dir_for_section(self, section):
        return os.path.join(self.rst_root,
                            self._get_relative_path_to_section(section))

    def _get_index_rst_for_section(self, section):
        return os.path.join(self.rst_root,
                            '{}_index.rst'.format(
                                self._get_relative_path_to_section(section)))

    @staticmethod
    def _get_relative_path_to_section(section):
        return section.replace(' ', '_').lower()[:50]

    @property
    def _generated_dirs(self):
        return [self.xml_root,
                self.rst_builtin,
                self.rst_crl_api,
                self.rst_crl,
                self.tmpsrc]

    @property
    def crl_namespaces(self):
        return ['cloudtaf', 'crl']

    def _generate_builtin_documentation(self):
        for builtin_lib in os.listdir(get_robot_builtin_path()):
            if (builtin_lib.endswith('.py') and
                    not self._lib_starts_with_any_invalid(builtin_lib)):
                generate_builtin_doc(builtin_lib, TEMPLATE_DIR,
                                     self.xml_root, self.rst_root)

    def _generate_api_documentation(self):
        self._generate_api_documentation_for_crl_namespaces()

    def _generate_api_documentation_with_filter(
            self, dist_filter, out,
            dist_translate=lambda dist: str(dist)):
        # pylint: disable=unnecessary-lambda
        for libpath in self._dist_paths(dist_filter, dist_translate):
            self._sphinx_apidoc(out=out, source=libpath)

    @staticmethod
    def _sphinx_apidoc(out, source):
        subprocess.call(
            'sphinx-apidoc --implicit-namespaces -o {out} {source}'.format(
                out=out,
                source=source), shell=True)

    @staticmethod
    def _dist_paths(dist_filter, dist_translate):
        for _, dists in pkg_resources.working_set.entry_keys.items():
            for dist in [d for d in dists if dist_filter(dist_translate(d))]:
                yield os.path.dirname(pkg_resources.resource_filename(
                    dist_translate(dist), '__init__.py'))

    def _generate_api_documentation_for_crl_namespaces(self):
        for nspath in self._namespacepaths(self.crl_namespaces):
            self._copy_directories(nspath.namespacepath,
                                   os.path.join(self.tmpsrc, nspath.namespace))
        self._sphinx_apidoc(out=self.rst_crl_api, source=self.tmpsrc)

    @staticmethod
    def _namespacepaths(namespaces):
        for ns in namespaces:
            for path, dists in pkg_resources.working_set.entry_keys.items():
                for d in dists:
                    if str(d).startswith('{}.'.format(ns)):
                        yield NamespacePath(namespace=ns, path=path)
                        break

    @staticmethod
    def _copy_directories(src_dir, dest_dir):
        try:
            shutil.copytree(src_dir, dest_dir)
        except OSError as e:
            if e.errno == errno.ENOTDIR:
                shutil.copy(src_dir, dest_dir)
            else:
                LOGGER.warning('Directory not copied. Error: %s', e)

    def _generate_crl_documentation(self):
        robotconftoxml = generate_rflibrary_doc_from_robotdocsconf(
            robotdocsconfs=self._robotdocsconfs,
            template_file=self.template_lib_rst,
            xml_dir=self.xml_root,
            rst_dir=self.rst_crl,
            relative_path_to_dir=self.relative_path_to_crl)
        robotconftoxml.set_section('Common Robot Libraries')
        robotconftoxml.generate_index(
            index_template=self.template_index_rst,
            index_rst_file=self.crl_index_rst_file)

    @property
    def _robotdocsconfs(self):
        return [r for r in self._robotdocsconf_generator()]

    @staticmethod
    def _robotdocsconf_generator():
        for ep in pkg_resources.iter_entry_points(group='robotdocsconf'):
            with error_handling(
                    'Not generating Robot framework documentation for '
                    'entry point {}'.format(
                        ep)):
                yield EntrypointRobotdocsconf(ep)

    def _generate_resource_docs(self):
        for r in self._args.resource:
            dst_path = os.path.join(self.rst_root, self._flat(r))
            create_dir(dst_path)
            r = Resource(src_path=r, dst_path=dst_path)
            r.generate_rst()

    @staticmethod
    def _flat(path):
        return path.replace(os.sep, '_')[-50:]

    def _lib_starts_with_any_invalid(self, lib):
        return (
            any([lib.startswith(i) for i in self.invalid_builtinlib_starts]) or
            lib.lower().startswith('deprecated'))

    def _add_toc_tree(self):
        add_toc_tree(self.rst_root, TOC_TEMPLATE)
