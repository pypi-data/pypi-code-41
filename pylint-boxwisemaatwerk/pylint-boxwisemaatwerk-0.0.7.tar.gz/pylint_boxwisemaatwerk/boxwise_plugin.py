from checkers.add_reference_checker import AddReferenceChecker
from monkeypatch import monkeypatch


def register(linter):
    print "adding checker for trancon"
    linter.register_checker(AddReferenceChecker(linter))
    monkeypatch(linter)

