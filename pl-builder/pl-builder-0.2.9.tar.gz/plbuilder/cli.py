from typing import Optional
import fire
import shutil
import os
from plbuilder.config import CREATED_DIRECTORY

from plbuilder.builder import (
    build_all,
    build_by_file_path,
    create_presentation_template,
    create_document_template
)


def build(file_path: Optional[str] = None):
    """
    Create slides and handout PDFs from plbuilder pyexlatex templates.
    Passing no arguments will build all templates.

    :param file_path: path of template from which to build PDFs
    :return: None
    """
    if file_path is None:
        build_all()
    else:
        build_by_file_path(file_path)



def create(doc_type: str, name: str):
    """
    Creates a slide template using the passed name

    :param doc_type: 'presentation' or 'document'
    :param name: Display name, will be standardized to snakecase and lowercase for use in the file name
    :return:
    """
    doc_type = doc_type.lower().strip()
    if doc_type == 'presentation':
        create_presentation_template(name)
    elif doc_type == 'document':
        create_document_template(name)
    else:
        raise ValueError(f'must pass document or presentation as first argument, got {doc_type}')


def init():
    """
    Creates a plbuilder project in the current directory


    :return:
    """
    if os.path.exists(CREATED_DIRECTORY):
        raise ProjectExistsException(f'{os.getcwd()}')

    os.makedirs(CREATED_DIRECTORY)

    pl_builder_source_path = os.path.dirname(os.path.abspath(__file__))

    templates_source = os.path.join(pl_builder_source_path, 'templates')
    templates_out_path = os.path.join(CREATED_DIRECTORY, 'templates')
    shutil.copytree(templates_source, templates_out_path)

    paths_source = os.path.join(pl_builder_source_path, 'paths.py')
    shutil.copy(paths_source, CREATED_DIRECTORY)

    sources_path = os.path.join(CREATED_DIRECTORY, 'sources')
    presentation_sources_path = os.path.join(sources_path, 'presentation')
    document_sources_path = os.path.join(sources_path, 'document')
    os.makedirs(presentation_sources_path)
    os.makedirs(document_sources_path)

    assets_path = os.path.join(CREATED_DIRECTORY, 'assets')
    images_path = os.path.join(assets_path, 'images')
    os.makedirs(images_path)


class ProjectExistsException(Exception):
    pass

def main():
    return fire.Fire({
        'build': build,
        'create': create,
        'init': init
    })

if __name__ == '__main__':
    main()
