'''
This is a simple sphinx extension to provide nice output from "click"
decorated command-lines. Enables markup like this in the Sphinx rst
files::

.. carml_command:: downloadbundle

Which will document the command "carml downloadbundle"
'''

from docutils import nodes
from docutils.parsers.rst import Directive


class carml_command(nodes.Element):
    pass


class CarmlCommandDirective(Directive):
    has_content = True
    required_arguments = 1

    def run(self):
        env = self.state.document.settings.env

        node = carml_command()
        node.line = self.lineno
        node['command'] = self.arguments[0]
        return [node]

    # targetid = "cb-cmd-%d" % env.new_serialno('cb-cmd')
    # targetnode = nodes.target('', '', ids=[targetid])
    # return [targetnode, node]


# shitcrackers, these aren't Click commands :/
def document_commands(app, doctree):
    return ''
    for node in doctree.traverse(carml_command):
        cmd = find_command(node.get('command', None))
        section = nodes.section()
        # section.append(nodes.subtitle(text='carml {}'.format(cmd.name)))
        section.append(nodes.paragraph(text=cmd.help))
        params = nodes.bullet_list()
        section.append(params)
        for param in cmd.params:
            item = nodes.list_item()
            arg = '--{}'.format(param.name)
            if param.metavar:
                arg = '--{} {}'.format(param.name, param.metavar)
            item.append(nodes.literal('', arg))
            item.append(nodes.Text(': ' + str(param.help)))
            if param.show_default:
                item.append(nodes.Text(' (default: '))
                item.append(nodes.literal('', str(param.default)))
                item.append(nodes.Text(')'))
            params.append(item)

        node.replace_self(section)


def setup(app):
    app.add_directive('carml_command', CarmlCommandDirective)
    app.connect(str('doctree-read'), document_commands)
