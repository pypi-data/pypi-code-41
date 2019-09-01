import os
import shutil
from pathlib import Path
from types import SimpleNamespace
from collections import UserDict

# provided by setuptools
# see https://setuptools.readthedocs.io/en/latest/pkg_resources.html#id23
import pkg_resources

import docutils.io, docutils.core
import jinja2
from rst2html5_ import HTML5Writer

NODE_PATH_PARTS_NAMES = ('exam_type', 'topic', 'year', 'region', 'exo_nb')

LONG_NAMES = {
    'brevet': 'Brevet des Collèges',
    'bac-s': 'Bac S',
    'math': 'Mathématiques',
    'pondichéry': 'Pondichéry',
    'amérique-nord': 'Amérique du Nord',
    'amérique-sud': 'Amérique du Sud',
    'centres-étrangers': 'Centres Étrangers'
}

# mostly taken from
# https://github.com/getpelican/pelican/
docutils_params = {
    'initial_header_level': '3',
    'syntax_highlight': 'short',
    'input_encoding': 'utf-8',
    'language_code': 'fr',
    'exit_status_level': 2,
    'embed_stylesheet': False,
    'math_output': 'MathJax'
}

def process_restructuredText(source_path, expected_metadata_keys=None):
    # again, mostly taken from
    # https://github.com/getpelican/pelican/
    pub = docutils.core.Publisher(
        writer=HTML5Writer(),
        source_class=docutils.io.FileInput,
        destination_class=docutils.io.StringOutput)
    pub.set_components('standalone', 'restructuredtext', 'html5')
    pub.process_programmatic_settings(None, docutils_params, None)
    pub.set_source(source_path=str(source_path))
    pub.publish()
    
    try:
        metadata = extract_metadata(pub, expected_metadata_keys)
    except Exception as e:
        e.cause_file = source_path
        raise e from None

    body = pub.writer.parts['body']

    return body, metadata

class ExceptionWhileProcessingFile(Exception):
    def __str__(self):
        cause_file = (f'(When processing file "{self.cause_file}") '
                      if hasattr(self, 'cause_file')
                      else '')
        return cause_file + super().__str__()


class InstructionsDoNotStartWithMetadata(ExceptionWhileProcessingFile):
    pass

class MissingMetadataKey(ExceptionWhileProcessingFile):
    pass

def extract_metadata(publisher, expected_keys=None):
    '''extract metadata from restructuredtext publisher'''

    metadata = dict()

    first_node = publisher.document[0]
    if isinstance(first_node, docutils.nodes.docinfo):
        for info_node in first_node.children:
            key = info_node[0].astext()
            value = info_node[1].astext()

            if key == 'points':
                value = float(value)
                if value.is_integer():
                    value = int(value)
                metadata['points'] = value

            elif key == 'catégories':
                metadata['categories'] = [
                    # should handle ending semicolons properly
                    cat.strip() for cat in value.strip('; ').split(';')
                ]
            elif key in ['spécialité']:
                metadata[key] = value
            else:
                raise Exception(f"unknown metadata key '{key}'")
    elif expected_keys:
        raise InstructionsDoNotStartWithMetadata


    if expected_keys:
        for key in expected_keys:
            if key not in metadata:
                raise MissingMetadataKey(f'"{key}" missing')

    return metadata

def empty_dir(path_to_dir):
    for each in path_to_dir.iterdir():
        if each.is_file():
            each.unlink()
        else:
            shutil.rmtree(each)

def write(data, path):
    os.makedirs(path.parent, exist_ok=True)
    with open(path, 'w') as f:
        f.write(data)

class Node:
    '''represent nodes in the source file tree.

    for instance brevet/math/2017/amérique-nord/
    is a valid path for a node
    but brevet/math/2017/amérique-nord/tout is not
    (with 'tout', it is the adress we use for a whole exam,
    that is written at destination
    but does not correspond to a file in particular
    in the source tree).
    '''
    def __init__(self, path, relative_to):
        self.rel_path = Path(path).relative_to(relative_to)
        parts = self.rel_path.parts

        # TODO use attributes
        # this will be so much easier to access
        self.path_metadata = dict(zip(NODE_PATH_PARTS_NAMES, parts))

        if len(parts) == 5:
            if parts[-1] == 'figures':
                self.type = 'figures'
                del self.path_metadata['exo_nb']
            else:
                self.type = 'exo'
        elif len(parts) == 4:
            self.type = 'region'
        elif len(parts) == 3:
            self.type = 'year'
        elif len(parts) == 2:
            self.type = 'topic'
        elif len(parts) == 1:
            self.type = 'exam_type'
        else:
            self.type = None

        for key in ['exam_type', 'topic', 'region']:
            if key in self.path_metadata:
                self.path_metadata[key] = LONG_NAMES[self.path_metadata[key]]

        for key in ['exo_nb', 'year']:
            if key in self.path_metadata:
                self.path_metadata[key] = int(self.path_metadata[key])

class YearIndex:
    def __init__(self, node):
        self.exercices = dict()
        self.whole_exams = dict()
        self.rel_path = node.rel_path
        self.path_metadata = node.path_metadata

    def template_data(self):
        template_data = {
            'exercices': self.exercices,
            'whole_exams': self.whole_exams
        }
        template_data.update(self.path_metadata)
        return template_data

    def add_exo(self, node, has_solution, categories):
        assert node.type == 'exo'

        region = node.path_metadata['region']
        exo_nb = node.path_metadata['exo_nb']

        self.exercices[region].append({
            'url': node.rel_path.relative_to(self.rel_path),
            'description': f'Exercice {exo_nb}',
            'has_solution': has_solution,
            'categories': categories
        })

    def add_region(self, node):
        assert node.type == 'region'
        
        region = node.path_metadata['region']
        self.exercices[region] = list()
        self.whole_exams[region] = node.rel_path.relative_to(self.rel_path) / 'tout'

class WholeExam:
    def __init__(self, node):
        assert node.type == 'region'

        self.exercises = list()
        self.rel_path = node.rel_path / 'tout'
        self.path_metadata = node.path_metadata

    def add_exo(self, body, has_solution, rel_path=None, **metadata):
        if has_solution:
            solution = Path('..') / rel_path.relative_to(self.rel_path.parent) / 'corrigé.html'
        else:
            solution = None
        exo = {'body': body, 'solution': solution}
        exo.update(metadata)

        self.exercises.append(exo)

    def template_data(self):
        template_data = {
            'exercices':self.exercises
        }
        template_data.update(self.path_metadata)

        return template_data

class CategoriesIndex:
    def __init__(self, node):
        assert node.type == 'topic'

        self.rel_path = node.rel_path / "catégories"
        self.path_metadata = node.path_metadata

        self.index = dict()

    def add_exo(self, node, categories):
        # href for instance
        # from brevet/math/catégories/géométrie.html
        # to brevet/math/2017/amérique-nord/06/
        href = Path('..') / node.rel_path.relative_to(node.rel_path.parents[2])

        # XXX there must be a nicer way to unpack
        (exam_type, year, region, exo_nb) = [
            node.path_metadata[key]
            for key in ('exam_type', 'year', 'region', 'exo_nb')
        ]
        description = f'{exam_type} {year} {region} Exercice {exo_nb}'

        item = {
            'href': href,
            'description': description
        }

        for category in categories:
            if category not in self.index:
                self.index[category] = [item]
            else:
                self.index[category].append(item)

    def template_data(self, category):
        template_data = {
            'index': self.index[category],
            'category': category
        }
        template_data.update(self.path_metadata)
        return template_data

class TopLevelIndex:
    def __init__(self):
        self.index = dict()

    def add_exam_type(self, node):
        assert node.type == 'exam_type'

        exam_type = node.path_metadata['exam_type']

        self.index[exam_type] = dict()

    def add_topic(self, node):
        assert node.type == 'topic'

        exam_type = node.path_metadata['exam_type']
        topic = node.path_metadata['topic']

        self.index[exam_type][topic] = {
            'years': list(),
            'categories': list(),
        }

    def add_year(self, node):
        assert node.type == 'year'

        exam_type = node.path_metadata['exam_type']
        topic = node.path_metadata['topic']
        year = node.path_metadata['year']

        self.index[exam_type][topic]['years'].append({
            'href': node.rel_path,
            'text': str(year)
        })

    def add_categories(self, category_index):
        exam_type = category_index.path_metadata['exam_type']
        topic = category_index.path_metadata['topic']

        categories = category_index.index.keys()

        self.index[exam_type][topic]['categories'] += [
            {
                'href': category_index.rel_path / (category+'.html'),
                'text': category
            }
            for category in categories
        ]
        
    def template_data(self):
        return {'index': self.index}
        
class Generator:
    def __init__(self, src_root, dest, site_root):
        self.src_root = Path(src_root)
        self.destination = Path(dest)
        self.site_root = site_root

        self.template_env = jinja2.Environment(
            loader=jinja2.PackageLoader('calusern'),
            # will raise if we try to use an undefined variable
            undefined=jinja2.StrictUndefined,
            # TODO escaping
            # autoescape=jinja2.select_autoescape(['html', 'xml'])
        )

    def render_template(self, path_to_template, **template_data):
        template = self.template_env.get_template(path_to_template)

        return template.render(
                site_root=self.site_root,
                **template_data
        )

    def render_and_write(self, template, path, **template_data):
        html = self.render_template(template, **template_data)
        write(html, path)

    def render_and_write_pendings(self, up_to=None):
        names = NODE_PATH_PARTS_NAMES

        if (up_to == None or names.index(up_to) <= names.index('topic')) \
           and self.pending.category_index != None:
            for category in self.pending.category_index.index:
                self.render_and_write(
                    'category.html',
                    self.destination / self.pending.category_index.rel_path / (category+'.html'),
                    **self.pending.category_index.template_data(category)
                )

            self.pending.toplevel_index.add_categories(self.pending.category_index)

        if (up_to == None or names.index(up_to) <= names.index('year')) \
           and self.pending.year_index != None:
            self.render_and_write(
                'year_index.html',
                self.destination / self.pending.year_index.rel_path / 'index.html',
                **self.pending.year_index.template_data()
            )

        if (up_to == None or names.index(up_to) <= names.index('region')) \
            and self.pending.whole_exam != None:
            self.render_and_write(
                'entire_exam.html',
                self.destination / self.pending.whole_exam.rel_path / 'index.html',
                **self.pending.whole_exam.template_data()
            )

        if up_to == None:
            self.render_and_write(
                'index.html',
                self.destination / 'index.html',
                **self.pending.toplevel_index.template_data()
            )


    def render_and_write_about_page(self):
        '''takes HTML body from path './static/a-propos.html' and renders it with base template'''
        body = pkg_resources.resource_string(__name__, "static/a-propos.html")

        self.render_and_write('base.html',
                              self.destination / 'a-propos.html',
                              title='À propos', heading='À propos',
                              body=body)

    def run(self):
        os.makedirs(self.destination, exist_ok=True)
        empty_dir(self.destination)
        
        self.pending = SimpleNamespace()
        self.pending.year_index = None
        self.pending.whole_exam = None
        self.pending.category_index = None
        self.pending.toplevel_index = TopLevelIndex()

        for dirpath, dirnames, filenames in os.walk(self.src_root):
            current_node = Node(dirpath, self.src_root)

            if current_node.type == 'exo':
                instructions = self.src_root / current_node.rel_path / 'instructions.rst'

                instructions_body, metadata = process_restructuredText(instructions,
                                                                       expected_metadata_keys=['points'])

                solution = self.src_root / current_node.rel_path / 'corrigé.rst'
                has_solution = solution.exists()

                if has_solution:
                    # '_' is for metadata that we discard
                    # (no metadata in solution)
                    # XXX error-prone
                    solution_body, _ = process_restructuredText(solution)

                    self.render_and_write(
                        'solution.html',
                        self.destination / current_node.rel_path / 'corrigé.html',
                        instructions_body=instructions_body,
                        solution_body=solution_body,
                        **metadata,
                        **current_node.path_metadata
                    )

                self.render_and_write(
                    'exercice.html',
                    self.destination / current_node.rel_path / 'index.html',
                    body=instructions_body,
                    has_solution=has_solution,
                    **metadata,
                    **current_node.path_metadata
                )

                self.pending.year_index.add_exo(current_node, has_solution,
                                                metadata.get('categories'))
                self.pending.whole_exam.add_exo(instructions_body,
                                                has_solution,
                                                rel_path=current_node.rel_path,
                                                **metadata,
                                                **current_node.path_metadata)
                if 'categories' in metadata:
                    self.pending.category_index.add_exo(current_node,
                                                        metadata['categories'])

            elif current_node.type == 'figures':
                dest_dir = self.destination / current_node.rel_path

                os.makedirs(dest_dir)
                for f in (self.src_root / current_node.rel_path).iterdir():
                    shutil.copy(f, dest_dir)

            elif current_node.type == 'region':
                self.render_and_write_pendings(up_to='region')
                self.pending.whole_exam = WholeExam(current_node)
                self.pending.year_index.add_region(current_node)

            elif current_node.type == 'year':
                self.render_and_write_pendings(up_to='year')
                self.pending.year_index = YearIndex(current_node)
                self.pending.toplevel_index.add_year(current_node)

            elif current_node.type == 'topic':
                self.render_and_write_pendings(up_to='topic')
                self.pending.category_index = CategoriesIndex(current_node)
                self.pending.toplevel_index.add_topic(current_node)

            elif current_node.type == 'exam_type':
                self.pending.toplevel_index.add_exam_type(current_node)

        # processing remaining pendings
        self.render_and_write_pendings()
        
        self.render_and_write_about_page()

        # copying CSS
        css_dir = pkg_resources.resource_filename(__name__, 'static/css')
        shutil.copytree(css_dir, self.destination / 'css') 
