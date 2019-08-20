import astroid
import os
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
import json


class AddReferenceChecker(BaseChecker):
    __implements__ = IAstroidChecker
    assembly_list =[]
    source = {}
    setup = False
    name = 'AddReference-notvalid'
    priority = -1
    msgs = {
        'E8101': (
            'AddReference is not valid.',
            'AddReference-cant-be-found',
            'AddReference string should be a valid module.'
        ),
    }
    options = (
        (
            "linterstorage-path",
            {
                "default": ("C:\\dev\\ironpython-stubs\\ironstubs"),
                "type": "string",
                "metavar": "<names>",
                "help": "Locations of the json files containing a list of assemblies ",
            },
        ),
        (
            "module-name-contains",
            {
                "default": ("TranCon","Wms"),
                "type": "csv",
                "metavar": "<names>",
                "help": "Add which modules need to be checked",
            }
        )

    )

    def __init__(self, linter=None):
        super(AddReferenceChecker, self).__init__(linter)


    def setup_after_pylintrc_read(self):
        try:
            self.source["sourcefile"] = self.config.linterstorage_path
            

            with open(self.config.linterstorage_path + "/assemblylist.json") as json_file:
                data = json.load(json_file)
                self.assembly_list += (data['assemblylist'])
                self.setup = True
                print "setup works"
        except:
            print "setup broke"


    def visit_call(self, node):
        if not self.setup:
            self.setup_after_pylintrc_read() 
        try:
            if node.func.expr.name == 'clr' and node.func.attrname == 'AddReference':
                path = node.args[0].value
                if path not in self.assembly_list and any([path.startswith(x) for x in self.config.module_name_contains]):
                    self.add_message('AddReference-cant-be-found', node=node)
        except: #catch if the function doesn't reference an external source.
            return

