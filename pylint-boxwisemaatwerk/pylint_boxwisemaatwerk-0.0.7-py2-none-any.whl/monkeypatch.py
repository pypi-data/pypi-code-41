import json
import astroid
from pylint.checkers.base import NameChecker
from pylint.checkers.typecheck import TypeChecker,_is_c_extension,_similar_names
from pylint_plugin_utils import NoSuchChecker,get_checker
from checkers.add_reference_checker import AddReferenceChecker

def monkeypatch(linter):
    addref = get_checker(linter,AddReferenceChecker)
    TypeChecker.linter_storage = addref.source
    TypeChecker._get_nomember_msgid_hint = _get_nomember_msgid_hint2










# Monkeypatch to typecheck so that changelist now gets read to provide hints to the user.
# This only catches attributes that are deleted.
# The files to make the changelist can be found in the ironstubs files under make_changelist.py
# Files are then uploaded to the google cloud storage where they hopefully get downloaded by the vscode extension of the user.

    
def _get_nomember_msgid_hint2(self, node, owner):
    suggestions_are_possible = self._suggestion_mode and isinstance(owner, astroid.Module)
    if suggestions_are_possible and _is_c_extension(owner):
        msg = 'c-extension-no-member'
        hint = ""
    else:
        msg = 'no-member'
        if self.config.missing_member_hint:
            hint = _missing_member_hint2(self, owner, node.attrname,
                                        self.config.missing_member_hint_distance,
                                        self.config.missing_member_max_choices)
        else:
            hint = ""
    return msg, hint


def _missing_member_hint2(self,owner, attrname, distance_threshold, max_choices):
    try:
        print "monkeypatch works"
        with open(self.linter_storage['sourcefile'] + "\\changelist.json") as json_file:
            data = json.load(json_file)
        names = _similar_names(owner, attrname, distance_threshold, max_choices)
        if not names:
            # No similar name.
            for version in data.keys():
                if(attrname in data[version]["Attribute"].keys()):
                    return " ("+data[version]["Attribute"][attrname]+ ")"
            return ""

        names = list(map(repr, names))
        if len(names) == 1:
            names = ", ".join(names)
        else:
            names = "one of {} or {}".format(", ".join(names[:-1]), names[-1])

        return "; maybe {}?".format(names)
    except:
        return "no changelist found"
