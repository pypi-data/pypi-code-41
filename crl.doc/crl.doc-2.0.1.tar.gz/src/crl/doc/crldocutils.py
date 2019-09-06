import os
import sys
import logging
from contextlib import contextmanager
import traceback
# pylint: disable=import-error
from jinja2 import Template
from lxml import etree, objectify
from robot import libdoc
from .rsttablecreator import RstTableCreator
from .util import convert_xml_to_rst, create_dir
from .robotws_util import create_dir as wscreate_dir
# pylint: enable=import-error


__copyright__ = 'Copyright (C) 2019, Nokia'

LOGGER = logging.getLogger(__name__)


@contextmanager
def error_handling(msg, sys_exit=None):
    try:
        yield None
    except Exception as e:  # pylint: disable=broad-except
        LOGGER.warning('%s: %s: %s\nBacktrace: \n%s',
                       msg,
                       e.__class__.__name__,
                       e,
                       ''.join(traceback.format_list(traceback.extract_tb(
                           sys.exc_info()[2]))))
        if sys_exit is not None:
            sys.exit(exit)


def get_robot_builtin_path():
    return os.path.normpath(os.path.join(libdoc.__file__, "..", "libraries"))


def generate_builtin_doc(builtin_lib_name, templates, xml_dir, rst_dir):
    """Function generate builtin documentation"""
    lib_dir = os.path.normpath(os.path.join(libdoc.__file__, "..",
                                            "libraries"))
    builtin_py_path = os.path.join(lib_dir, builtin_lib_name)
    generate_rflibrary_doc(builtin_py_path, templates, xml_dir, rst_dir)


def generate_rflibrary_doc(lib_path, templates, xml_dir, rst_dir):
    """ Generate Rst file for the provided RobotFramework Library file.

    :param lib_path: The absolute path to the library file
    :param templates: The template to be used for rst file generation
    :param rst_dir: The path to the rst files' folder
    :param xml_dir: The path to the xml files' folder
    """
    LOGGER.debug('Generate RF Lib Doc for %s', lib_path)
    lib_name = os.path.basename(lib_path)
    lib_name_no_ext = os.path.splitext(lib_name)[0]
    xml_file = os.path.join(xml_dir, 'builtin', lib_name_no_ext + '.xml')
    rst_file = os.path.join(rst_dir, 'builtin', lib_name_no_ext + '.rst')
    wscreate_dir(xml_file)
    wscreate_dir(rst_file)
    libdoc.libdoc(lib_path, xml_file)
    if os.path.isfile(xml_file):
        RobotToRstConverter().change_robot_table_to_rst_table(xml_file)
        convert_xml_to_rst(xml_file,
                           rst_file,
                           os.path.join(templates, 'builtin.rst'),
                           'RobotFramework',
                           'RobotFramework',
                           'RobotFramework')
    else:
        LOGGER.warning('Libdoc failed to convert: %s', lib_name)


def crl_convert_xml_to_rst(src_file,
                           dst_file,
                           template_file,
                           author,
                           maintainer,
                           version=None):
    """
    Converts xml file to rst template
    """
    with open(template_file) as f:
        template = Template(f.read())
    with error_handling(
            'Failed to convert {src} to {dst}'.format(src=src_file,
                                                      dst=dst_file)):
        with open(src_file, 'r') as f:
            e = objectify.parse(f).getroot()
            rendered = template.render(e=e,
                                       author=author,
                                       maintainer=maintainer,
                                       version=version)

        with open(dst_file, 'w') as f:
            f.write(rendered)


def generate_rflibrary_doc_from_robotdocsconf(robotdocsconfs,
                                              template_file,
                                              xml_dir,
                                              rst_dir,
                                              relative_path_to_dir):
    for d in [xml_dir, rst_dir]:
        LOGGER.info('Create dir %s', d)
        create_dir(d)
    rconftoxml = RobotconfToXml(robotdocsconfs,
                                xml_dir,
                                rst_dir,
                                relative_path_to_dir)
    for xmlrst in rconftoxml.robot_xml_rst_files():
        RobotToRstConverter().change_robot_table_to_rst_table(xmlrst.xml_file)
        crl_convert_xml_to_rst(src_file=xmlrst.xml_file,
                               dst_file=xmlrst.rst_file,
                               template_file=template_file,
                               author=xmlrst.authorwithemail,
                               maintainer='',
                               version=xmlrst.version)
    return rconftoxml


def generate_xml_doc(dst_file):
    """generates xml file from resource or library"""
    create_dir(dst_file)


class RobotToRstConverter(RstTableCreator):

    def change_robot_table_to_rst_table(self, file_path):
        """Opens file with xml, searches doc nodes, changes Robot XML tables to
        rst tables and saves it as the same xml.

            .. note::

               if the doc is already in ReST format, then no conversion is
               made.


        :param file_path: XML file path
        :type file_path: String
        """
        LOGGER.debug('Changing robot table to reST for file: %s', file_path)
        root = etree.parse(file_path)
        if root.getroot().get('format') == 'REST':
            return

        for i in root.iter('doc'):
            if i.text:
                i.text = self._change_table_to_rst_table(i.text)

        with open(file_path, 'w') as f:
            f.write(etree.tostring(root).decode('utf-8'))


class RobotXmlRstFile():

    def __init__(self,
                 xml_file,
                 rst_file,
                 metadata):
        self.xml_file = xml_file
        self.rst_file = rst_file
        self.metadata = metadata

    @property
    def authorwithemail(self):
        return ' '.join(
            [a for a in [self.author, self.authoremailinbrackets] if a])

    @property
    def authoremailinbrackets(self):
        return ('<{email}>'.format(
            email=self.authoremail) if self.authoremail else '')

    @property
    def author(self):
        return self.metadata.get('Author', '')

    @property
    def authoremail(self):
        return self.metadata.get('Author-email', '')

    @property
    def version(self):
        return self.metadata.get('Version', None)


class RobotXmlFileNotFound(Exception):
    pass


class RobotLibrary():
    def __init__(self, library, synopsis, relative_path_to_dir):
        self.ref = os.path.join(relative_path_to_dir, library)
        self.synopsis = synopsis


class RobotdocsConf():
    def __init__(self, robotdocsentrypoint, relative_path_to_dir):
        self._robotdocsentrypoint = robotdocsentrypoint
        self._relative_path_to_dir = relative_path_to_dir

    @property
    def nameanddescr(self):
        return '{name}{descr}'.format(name=self.name,
                                      descr=self.summarywithhyphen)

    @property
    def name(self):
        return self._robotdocsentrypoint.metadata.get('Name')

    @property
    def summarywithhyphen(self):
        return ' - {}'.format(self.summary) if self.summary else ''

    @property
    def summary(self):
        return self._robotdocsentrypoint.metadata.get('Summary', '')

    @property
    def description(self):
        return self.summary

    def _use_summary(self):
        return (self.long_description.startswith('UNKNOWN') or
                len(self.summary) > len(self.long_description))

    @property
    def long_description(self):
        return self._robotdocsentrypoint.metadata.get_payload()

    @property
    def libraries(self):
        for library, args in sorted(
                self._robotdocsentrypoint.robotdocsconf.items(),
                key=lambda t: str.lower(t[0])):
            yield RobotLibrary(
                library=library,
                synopsis=args['synopsis'],
                relative_path_to_dir=self._relative_path_to_dir)


class RobotconfToXml():

    def __init__(self, robotdocsentrypoints,
                 xml_dir, rst_dir, relative_path_to_dir):
        self._robotdocsentrypoints = robotdocsentrypoints
        self._xmldir = xml_dir
        self._rstdir = rst_dir
        self._relative_path_to_dir = relative_path_to_dir
        self._section = None

    def set_section(self, section):
        self._section = section

    def robot_xml_rst_files(self):
        for r in self._robotdocsentrypoints:
            for library, args in r.robotdocsconf.items():
                with error_handling(
                        'Failed to generate Robot documentation for library {}'.format(
                            library)):
                    yield self._generate_xml_with_libdoc(
                        r.metadata, library, args)

    def _generate_xml_with_libdoc(self, metadata, library, args):
        xmlrst = RobotXmlRstFile(xml_file=self._get_xml_doc_file(library),
                                 rst_file=self._get_rst_doc_file(library),
                                 metadata=metadata)
        libdoc.LibDoc().execute(
            '{library}{args}'.format(
                library=library,
                args=self._get_flattened_args(args)),
            xmlrst.xml_file,
            version=xmlrst.version,
            docformat=args.get('docformat', 'ROBOT'))
        LOGGER.info('libdoc.LibDoc(%s, %s, version=%s, docformat=%s)',
                    '{library}{args}'.format(
                        library=library,
                        args=self._get_flattened_args(args)),
                    xmlrst.xml_file,
                    xmlrst.version,
                    args.get('docformat', 'ROBOT'))

        if not os.path.isfile(xmlrst.xml_file):
            raise RobotXmlFileNotFound(
                'Failed to generate xml file with libdoc from {}'.format(
                    library))
        self._update_synopsis(args, xmlrst.xml_file)
        return xmlrst

    def _get_xml_doc_file(self, library):
        return '{path}.xml'.format(path=os.path.join(self._xmldir,
                                                     self._replace_path_sep(library)))

    def _get_rst_doc_file(self, library):
        return '{path}.rst'.format(path=os.path.join(self._rstdir,
                                                     self._replace_path_sep(library)))

    @staticmethod
    def _replace_path_sep(library):
        return library.replace(os.sep, '_')[-80:]

    @staticmethod
    def _update_synopsis(args, xml_file):
        if 'synopsis' not in args:
            root = etree.parse(xml_file).getroot()
            args['synopsis'] = root.find('doc').text.split('\n')[0]

    @staticmethod
    def _get_docformat(args):
        return args.get('docformat', None)

    @staticmethod
    def _get_flattened_args(args):
        try:
            flattened = '::'.join(arg for arg in args['args'])
            return '::' + flattened if flattened else ''
        except KeyError:
            return ''

    def generate_index(self,
                       index_template,
                       index_rst_file):
        with open(index_template) as f:
            template = Template(f.read())

        with open(index_rst_file, 'w') as f:
            f.write(template.render(
                section=self._section,
                robotdocsconfs=self.robotdocsconfs))

    @property
    def robotdocsconfs(self):
        for r in sorted(self._robotdocsentrypoints,
                        key=lambda r: r.metadata.get('Name', '')):
            yield RobotdocsConf(r, self._relative_path_to_dir)
