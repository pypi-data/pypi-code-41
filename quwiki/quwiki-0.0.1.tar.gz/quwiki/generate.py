import io
import json
import yaml
import shutil
import os.path
from importlib import import_module
from .filenode import FileNode


FOLDER_DIST = 'dist'


def _get_config(config_file):
    data = None
    with open(config_file, 'r') as stream:
        data = yaml.safe_load(stream)
    return data


def _get_template(template_path):
    html = None
    full_path = os.path.join(template_path, 'index.html')
    with open(full_path, 'r') as f:
        html = f.read()
    return html


def _create_page(file_node, template_html):
    path = file_node.get_path()
    full_path = os.path.join(FOLDER_DIST, path)
    print(full_path)

    if file_node.kind == FileNode.KIND_FILE:
        with open(full_path + '.html', 'w') as f:
            content_html = file_node.get_html()
            template_html = template_html.replace(
                '{page.title}', file_node.name)
            template_html = template_html.replace(
                '{page.content}', content_html)
            template_html = template_html.replace(
                '{page.edit_url}', file_node.get_edit_url())
            f.write(template_html)
    elif file_node.kind == FileNode.KIND_DIRECTORY:
        if not os.path.exists(full_path):
            os.makedirs(full_path)
    else:
        raise Exception('Filetype {} is not supported'.format(file_node.kind))


def _create_navigation_html(file_node):
    children_html = ''
    title = ''

    if file_node.parent is not None and file_node.kind == FileNode.KIND_FILE:
        title = '<a href="{}">{}</a>'.format(
            file_node.get_url(), file_node.name)
    elif file_node.parent is not None and file_node.kind == FileNode.KIND_DIRECTORY:
        title = file_node.name

    if len(file_node.children) > 0:
        children_li = [
            '<li>{}</li>'.format(_create_navigation_html(child)) for child in file_node.children]
        children_html = '<ul>{}</ul>'.format(''.join(children_li))
    return '{}{}'.format(title, children_html)


def generate(args):
    config = _get_config(args.config)
    root = FileNode(
        name='',
        kind=FileNode.KIND_DIRECTORY
    )


    template_html = _get_template(config['template'])
    template_html = template_html.replace('{site.title}', config['title'])

    if os.path.exists(FOLDER_DIST):
        shutil.rmtree(FOLDER_DIST, ignore_errors=False, onerror=None)

    document_id = 1
    for source_name in config['sources']:
        source = config['sources'][source_name]

        if 'title' not in source.keys():
            source['title'] = source_name

        # Generate folder tree
        source_module = import_module(source['type'])
        source_root = source_module.generate_tree(source)
        root.add_child(source_root)

    # Generate files
    content = []
    navigation_html = _create_navigation_html(root)
    template_html = template_html.replace('{site.navigation}', navigation_html)
    queue = [root]
    while len(queue) > 0:
        file_node = queue.pop()
        _create_page(file_node, template_html)
        if file_node.kind == FileNode.KIND_FILE:
            content.append({
                'id': document_id,
                'title': file_node.name,
                'content': file_node.get_text(),
                'url': file_node.get_url(),
            })
            document_id += 1
        for child in file_node.children:
            queue.append(child)

    # Write intro page
    shutil.copyfile(
        os.path.join(FOLDER_DIST, config['intro']),
        os.path.join(FOLDER_DIST, 'index.html')
    )

    # Write content summary
    with open(os.path.join(FOLDER_DIST, 'content.js'), 'w') as f:
        f.write('var CONTENT = ')
        json.dump(content, f)
