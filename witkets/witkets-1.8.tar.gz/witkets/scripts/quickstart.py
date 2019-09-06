import argparse
import pkgutil as pkg
import os
from os.path import join


def render_template(template, replacements):
    """Render a given `template` with a `replacements` dictionary.

    The use of this function over other common template engines is
    to avoid adding external dependencies. Only basic variable 
    rendering is supported.

    Args:
        template (str): Template filename relative to witkets/data/templates
        replacements (dict): Replacements dictionary
    
    Returns:
        The template rendered into a string 
    """

    contents = pkg.get_data('witkets', 'data/templates/' + template)
    contents = contents.decode('utf8')
    for key, value in replacements.items():
        contents = contents.replace(key, value)
    return contents


def write_asset(template, replacements, target_filename):
    """Write a template asset to a target folder."""
    with open(target_filename, 'w') as fd:
        fd.write(render_template(template, replacements))


def create_project(name):
    """Scaffold a project with a given name."""
    inline_gui = render_template('gui.xml', {})
    replacements = {
        '@APP_NAME@': name,
        '@INLINE_GUI@': inline_gui
    }
    os.mkdir(name)
    write_asset('app_class.py', replacements, join(name, 'app.py'))
    write_asset('app_basic.py', replacements, join(name, 'app_alt.py'))
    write_asset('app_bundle.py', replacements, join(name, 'app_bundle.py'))
    write_asset('gui.xml', replacements, join(name, 'gui.xml'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scaffold a project.')
    parser.add_argument('project_name', 
                        help='name of the project to be generated')
    args = parser.parse_args()
    create_project(args.project_name)

    
