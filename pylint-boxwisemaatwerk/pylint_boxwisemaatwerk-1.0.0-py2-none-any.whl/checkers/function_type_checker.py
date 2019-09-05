import astroid
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker
from pylint.checkers.utils import safe_infer
from pylint.checkers.typecheck import _determine_callable
import json




class FunctionTypeChecker(BaseChecker):
    __implements__ = IAstroidChecker
    refactordict = {}

    # gets filled at runtime from the addreference checker in monkeypatch
    linter_storage = None


    setup = False
    name = 'possible-refactoring-needed'
    priority = -1
    msgs = {
        'E8102': (
            '%s %s needs possible refactor on %s member%s',
            'possible-refactor',
            'Signature cant be found in stubs'
        ),
    }
    options = (
        (
            'possible-refactor-version',
            {
                "default": ("None"),
                'type': "string",
                "metavar": "<refactor_version>",
                "help": "Version used for checking possible refactors "
            }
        ),

    )



    def __init__(self, linter=None):
        super(FunctionTypeChecker, self).__init__(linter)


    def setup_after_pylintrc_read(self):
        try:
            with open(self.linter_storage['sourcefile'] + "/changelist.json") as json_file:
                data = json.load(json_file)
                self.refactordict = (data["Refactors"])
                self.setup = True
                print "setup refactors works"
        except:
            print "setup refactors broke"


    def visit_call(self, node):
        try:
            if not self.setup:
                self.setup_after_pylintrc_read()
            version = self.config.possible_refactor_version
            if version not in self.refactordict.keys():
                return
            func = node.func.attrname
            inferred = list(node.func.expr.infer())

            # get all inferred classes
            non_opaque_inference_results = [
                owner for owner in inferred
                if owner is not astroid.Uninferable
                and not isinstance(owner, astroid.nodes.Unknown)
            ]
            for owner in non_opaque_inference_results:
                name = getattr(owner, 'name', None)
                full = name + "." + func



                print self.refactordict.keys()
                if full in self.refactordict[version]:
                    hint = " (" + self.refactordict[version][full] + ")"
                    print hint
                    self.add_message('possible-refactor', node=node,
                                    args=(owner.display_type(), name,
                                        func, hint))
        except: #catch if the function doesn't reference an external source.
            return