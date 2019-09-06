import os
import sys
import traceback
import logging
from jinja2 import Template, TemplateError

__copyright__ = 'Copyright (C) 2019, Nokia'

LOGGER = logging.getLogger(__name__)


class TemplateOSError(OSError):
    pass


def create_dir(filename):
    """creates dir for given file"""
    LOGGER.debug("Creating base directory for %s", filename)
    absolute_path = os.path.abspath(filename)
    path_to_dir = os.path.dirname(absolute_path)
    if not os.path.exists(path_to_dir):
        os.makedirs(os.path.dirname(filename))


def add_toc_tree(root_dir, template_toc):
    """creates Table of content tree filenames starting from given directory"""
    try:
        with open(template_toc, 'r') as f:
            template = Template(f.read())
        for dirpath, dirnames, _ in os.walk(os.path.abspath(root_dir)):
            for dirname in dirnames:
                name = os.path.join(dirpath, dirname)
                rendered = template.render(e=dirname)
                new_name = "".join([name, "_index.rst"])
                _write_rendered_template(rendered, new_name)
    except (TemplateOSError, TemplateError) as e:
        msg = '{cls}: {msg}\nTraceback:\n{tb}'.format(
            cls=e.__class__.__name__,
            msg=str(e),
            tb=''.join(traceback.format_list(traceback.extract_tb(sys.exc_info()[2]))))
        LOGGER.debug(msg)


def _template_from_file(template_file):
    try:
        with open(template_file, 'r') as f:
            return Template(f.read())
    except OSError:
        raise TemplateOSError


def _write_rendered_template(rendered_template, target_file):
    try:
        with open(target_file, 'w') as f:
            f.write(rendered_template)
    except OSError:
        raise TemplateOSError
