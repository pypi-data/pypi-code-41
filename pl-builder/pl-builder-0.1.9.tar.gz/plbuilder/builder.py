from typing import Sequence, List, Optional, Union
import importlib.util
import os
import sys
sys.path.append(os.path.abspath(os.getcwd()))  # needed to be able to import local plbuild directory

IGNORED_FILES = [
    '__init__.py',
]


def get_all_source_files() -> List[str]:
    from plbuild.paths import (
        SLIDES_SOURCE_PATH,
        slides_source_path,
        DOCUMENTS_SOURCE_PATH,
        documents_source_path,
    )
    slide_sources = [file for file in next(os.walk(SLIDES_SOURCE_PATH))[2] if file not in IGNORED_FILES]
    slide_sources = [slides_source_path(file) for file in slide_sources]
    doc_sources = [file for file in next(os.walk(DOCUMENTS_SOURCE_PATH))[2] if file not in IGNORED_FILES]
    doc_sources = [documents_source_path(file) for file in doc_sources]
    return slide_sources + doc_sources


def create_presentation_template(name: str):
    from plbuild.paths import (
        slides_source_path,
    )
    base_file_name = get_file_name_from_display_name(name)
    full_file_name = f'{base_file_name}.py'
    file_path = slides_source_path(full_file_name)
    create_template(
        [
            'general',
            'author',
            'presentation'
        ],
        out_path=file_path
    )


def create_document_template(name: str):
    from plbuild.paths import (
        documents_source_path,
    )
    base_file_name = get_file_name_from_display_name(name)
    full_file_name = f'{base_file_name}.py'
    file_path = documents_source_path(full_file_name)
    create_template(
        [
            'general',
            'author',
            'document'
        ],
        out_path=file_path
    )


def create_template(template_names: Sequence[str], out_path: str):
    from plbuild.paths import (
        templates_path_func
    )
    template_paths = [templates_path_func(template + '.py') for template in template_names]
    template_str = _create_template_str(template_paths)
    with open(out_path, 'w') as f:
        f.write(template_str)


def _create_template_str(template_paths: Sequence[str]) -> str:
    template_str = ''
    for path in template_paths:
        with open(path, 'r') as f:
            template_str += f.read()
    template_str += '\n'
    return template_str



def get_file_name_from_display_name(name: str) -> str:
    """
    Converts name to snake case and lower case for use in file name

    :param name: display name, can have spaces and capitalization
    :return:
    """
    return name.replace(' ', '_').lower()


def build_all():
    files = get_all_source_files()
    [create_presentation_by_file_path(file) for file in files]


def create_presentation_by_file_path(file_path: str):
    print(f'Creating presentation for {file_path}')
    mod = _module_from_file(file_path)

    build_from_content(
        mod.get_content(),
        pl_class=mod.DOCUMENT_CLASS,
        outfolder=mod.OUTPUT_LOCATION,
        title=getattr(mod, 'TITLE', None),
        short_title=getattr(mod, 'SHORT_TITLE', None),
        subtitle=getattr(mod, 'SUBTITLE', None),
        handouts_outfolder=getattr(mod, 'HANDOUTS_OUTPUT_LOCATION', None),
        index=getattr(mod, 'ORDER', None),
        author=getattr(mod, 'AUTHOR', None),
        short_author=getattr(mod, 'SHORT_AUTHOR', None),
        institutions=getattr(mod, 'INSTITUTIONS', None),
        short_institution=getattr(mod, 'SHORT_INSTITUTION', None),
    )


def build_from_content(content, pl_class, outfolder: str, title: str, short_title: str, subtitle: str,
                       handouts_outfolder: Optional[str] = None,
                       index: Optional[int] = None, author: Optional[str] = None,
                       short_author: Optional[str] = None, institutions: Optional[Sequence[Sequence[str]]] = None,
                       short_institution: Optional[str] = None,
                       ):
    out_name = f'{index} {title}' if index is not None else title
    kwargs = dict(
        title=title,
        short_title=short_title,
        subtitle=subtitle,
        author=author,
        short_author=short_author,
        institutions=institutions,
        short_institution=short_institution
    )
    fmp = pl_class(
        content,
        **kwargs
    )
    fmp.to_pdf(
        outfolder,
        out_name
    )
    if handouts_outfolder is not None:
        fmp_handout = pl_class(
            content,
            handouts=True,
            **kwargs
        )
        fmp_handout.to_pdf(
            handouts_outfolder,
            out_name
        )


def _module_from_file(file_path: str):
    mod_name = os.path.basename(file_path).strip('.py')
    return _module_from_file_and_name(file_path, mod_name)


def _module_from_file_and_name(file_path: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


if __name__ == '__main__':
    build_all()