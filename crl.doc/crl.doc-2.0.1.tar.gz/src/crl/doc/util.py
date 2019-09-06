import os
from jinja2 import Template, TemplateError
from lxml import objectify
from lxml.etree import LxmlError


__copyright__ = 'Copyright (C) 2019, Nokia'


def create_dir(directory):
    """Summary line.

    Creates parameter directory if it doesn't exist

    Args:
        directory (string): File path of the directory

    Return:
        Nothing

    """
    if not os.path.isdir(directory):
        os.makedirs(directory)


def convert_xml_to_rst(src_file, dst_file, template_file, author, maintainer,
                       version=None, committer=None):
    """Summary line.

    Converts xml file to rst template

    Args:
        src_file (str): File containing xml to be converted
        dst_file (str): Destination file for the conversion
        template_file (str): File Containing template for the conversion
        auther (str): Name of the author
        maintainer (str): Name of the maintainer
        version (str): Version number
        committer (str): Name of the committer

    Returns:
        Nothing

    """
    template = Template(_read_file(template_file))
    try:
        with open(src_file, 'r') as f:
            e = objectify.parse(f).getroot()
            template_string = template.render(e=e, author=author, maintainer=maintainer,
                                              version=version, committer=committer)
            _write_template_to_file(dst_file, template_string)
    except (TemplateError, LxmlError, OSError, IOError) as e:
        print(e)


def _read_file(path):
    with open(path, 'r') as f:
        return f.read()


def _write_template_to_file(path, template_string):
    with open(path, 'wb') as f:
        f.write(template_string.encode('utf-8'))
