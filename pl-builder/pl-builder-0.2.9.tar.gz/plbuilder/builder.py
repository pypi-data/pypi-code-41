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
            'general_imports',
            'presentation_imports',
            'author',
            'presentation',
            'general',
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
            'general_imports',
            'document_imports',
            'author',
            'document',
            'general',
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
    [build_by_file_path(file) for file in files]


def build_by_file_path(file_path: str):
    mod = _module_from_file(file_path)
    print(f'Creating {mod.DOCUMENT_CLASS.__name__} for {file_path}')

    optional_attrs = dict(
        title='TITLE',
        short_title='SHORT_TITLE',
        subtitle='SUBTITLE',
        handouts_outfolder='HANDOUTS_OUTPUT_LOCATION',
        index='ORDER',
        authors='AUTHORS',
        short_author='SHORT_AUTHOR',
        institutions='INSTITUTIONS',
        short_institution='SHORT_INSTITUTION',
        output_name='OUTPUT_NAME',
    )

    kwargs = dict(
        pl_class=mod.DOCUMENT_CLASS,
        outfolder=mod.OUTPUT_LOCATION,
    )

    for kwarg, mod_attr in optional_attrs.items():
        value = getattr(mod, mod_attr, None)
        if value is not None:
            kwargs.update({kwarg: value})

    passed_kwargs = getattr(mod, 'DOCUMENT_CLASS_KWARGS', None)
    if passed_kwargs:
        kwargs.update(passed_kwargs)

    build_from_content(
        mod.get_content(),
        **kwargs
    )


def build_from_content(content, pl_class, outfolder: str,
                       handouts_outfolder: Optional[str] = None,
                       index: Optional[int] = None, **kwargs):
    if 'output_name' in kwargs:
        out_name = kwargs.pop('output_name')
    else:
        out_name = 'untitled'

    out_name = f'{index} {out_name}' if index is not None else out_name

    if not os.path.exists(outfolder):
        os.makedirs(outfolder)

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