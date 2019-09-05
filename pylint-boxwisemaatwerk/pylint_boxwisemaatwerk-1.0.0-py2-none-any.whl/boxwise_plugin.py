from checkers.add_reference_checker import AddReferenceChecker
from checkers.function_type_checker import FunctionTypeChecker
from monkeypatch import monkeypatch


def register(linter):
    print "adding checker for trancon"
    linter.register_checker(AddReferenceChecker(linter))
    linter.register_checker(FunctionTypeChecker(linter))
    monkeypatch(linter)

