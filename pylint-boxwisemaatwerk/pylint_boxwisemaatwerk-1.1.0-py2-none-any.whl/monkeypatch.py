import json
import astroid
from pylint.checkers.base import NameChecker
from pylint.checkers.typecheck import (
    TypeChecker,
    _is_c_extension,_similar_names,
    _no_context_variadic_positional,
    _no_context_variadic_keywords,
    STR_FORMAT,
    safe_infer,has_known_bases,
    _determine_callable)
from pylint_plugin_utils import NoSuchChecker,get_checker
from checkers.add_reference_checker import AddReferenceChecker
from checkers.function_type_checker import FunctionTypeChecker
def monkeypatch(linter):
    addref = get_checker(linter,AddReferenceChecker)
    TypeChecker.linter_storage = addref.source
    FunctionTypeChecker.linter_storage = addref.source
    TypeChecker._get_nomember_msgid_hint = _get_nomember_msgid_hint2
    #TypeChecker.visit_call = visit_call2









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
        with open(self.linter_storage['sourcefile'] + "\\changelist.json") as json_file:
            data = json.load(json_file)

        full_name = owner.name + '.' + attrname
        names = _similar_names(owner, attrname, distance_threshold, max_choices)
        if not names:
            # No similar name.
            for version in data["Deleted"]:
                if(full_name in data["Deleted"][version].keys()):
                    return " (Deleted in version " + version + ": " + data["Deleted"][version][full_name]+ ")"
            return ""

        names = list(map(repr, names))
        if len(names) == 1:
            names = ", ".join(names)
        else:
            names = "one of {} or {}".format(", ".join(names[:-1]), names[-1])

        return "; maybe {}?".format(names)
    except:
        return "(Possible error in finding changelist?)"




#since we dont use types to check if functions can be compiled, we now use the count
def visit_call2(self, node):
    print "wyd"


    """check that called functions/methods are inferred to callable objects,
    and that the arguments passed to the function match the parameters in
    the inferred function's definition
    """
    # Build the set of keyword arguments, checking for duplicate keywords,
    # and count the positional arguments.
    call_site = astroid.arguments.CallSite.from_call(node)
    num_positional_args = len(call_site.positional_arguments)
    keyword_args = list(call_site.keyword_arguments.keys())

    # Determine if we don't have a context for our call and we use variadics.
    if isinstance(node.scope(), astroid.FunctionDef):
        has_no_context_positional_variadic = _no_context_variadic_positional(node)
        has_no_context_keywords_variadic = _no_context_variadic_keywords(node)
    else:
        has_no_context_positional_variadic = has_no_context_keywords_variadic = False

    called = safe_infer(node.func)
    # only function, generator and object defining __call__ are allowed
    if called and not called.callable():
        if isinstance(called, astroid.Instance) and not has_known_bases(called):
            # Don't emit if we can't make sure this object is callable.
            pass
        else:
            self.add_message('not-callable', node=node,
                                args=node.func.as_string())

    self._check_uninferable_call(node)

    try:
        called, implicit_args, callable_name = _determine_callable(called)
    except ValueError:
        # Any error occurred during determining the function type, most of
        # those errors are handled by different warnings.
        return

    num_positional_args += implicit_args
    if called.args.args is None:
        # Built-in functions have no argument information.
        return

    if len(called.argnames()) != len(set(called.argnames())):
        # Duplicate parameter name (see duplicate-argument).  We can't really
        # make sense of the function call in this case, so just return.
        return

    # Warn about duplicated keyword arguments, such as `f=24, **{'f': 24}`
    for keyword in call_site.duplicated_keywords:
        self.add_message('repeated-keyword',
                            node=node, args=(keyword, ))

    if call_site.has_invalid_arguments() or call_site.has_invalid_keywords():
        # Can't make sense of this.
        return

    # Analyze the list of formal parameters.
    num_mandatory_parameters = len(called.args.args) - len(called.args.defaults)
    parameters = []
    parameter_name_to_index = {}
    for i, arg in enumerate(called.args.args):
        if isinstance(arg, astroid.Tuple):
            name = None
            # Don't store any parameter names within the tuple, since those
            # are not assignable from keyword arguments.
        else:
            assert isinstance(arg, astroid.AssignName)
            # This occurs with:
            #    def f( (a), (b) ): pass
            name = arg.name
            parameter_name_to_index[name] = i
        if i >= num_mandatory_parameters:
            defval = called.args.defaults[i - num_mandatory_parameters]
        else:
            defval = None
        parameters.append([(name, defval), False])

    kwparams = {}
    for i, arg in enumerate(called.args.kwonlyargs):
        if isinstance(arg, astroid.Keyword):
            name = arg.arg
        else:
            assert isinstance(arg, astroid.AssignName)
            name = arg.name
        kwparams[name] = [called.args.kw_defaults[i], False]

    # Match the supplied arguments against the function parameters.

    # 1. Match the positional arguments.
    for i in range(num_positional_args):
        print called.args.vararg
        if i < len(parameters):
            parameters[i][1] = True
        elif called.args.vararg is not None:
            # The remaining positional arguments get assigned to the *args
            # parameter.
            break
        else:
            # Too many positional arguments.
            self.add_message('too-many-function-args',
                                node=node, args=(callable_name,))
            break

    # 2. Match the keyword arguments.
    for keyword in keyword_args:
        if keyword in parameter_name_to_index:
            i = parameter_name_to_index[keyword]
            if parameters[i][1]:
                # Duplicate definition of function parameter.

                # Might be too hardcoded, but this can actually
                # happen when using str.format and `self` is passed
                # by keyword argument, as in `.format(self=self)`.
                # It's perfectly valid to so, so we're just skipping
                # it if that's the case.
                if not (keyword == 'self' and called.qname() in STR_FORMAT):
                    self.add_message('redundant-keyword-arg',
                                        node=node, args=(keyword, callable_name))
            else:
                parameters[i][1] = True
        elif keyword in kwparams:
            if kwparams[keyword][1]:  # XXX is that even possible?
                # Duplicate definition of function parameter.
                self.add_message('redundant-keyword-arg', node=node,
                                    args=(keyword, callable_name))
            else:
                kwparams[keyword][1] = True
        elif called.args.kwarg is not None:
            # The keyword argument gets assigned to the **kwargs parameter.
            pass
        else:
            # Unexpected keyword argument.
            self.add_message('unexpected-keyword-arg', node=node,
                                args=(keyword, callable_name))

    # 3. Match the **kwargs, if any.
    if node.kwargs:
        for i, [(name, defval), assigned] in enumerate(parameters):
            # Assume that *kwargs provides values for all remaining
            # unassigned named parameters.
            if name is not None:
                parameters[i][1] = True
            else:
                # **kwargs can't assign to tuples.
                pass

    # Check that any parameters without a default have been assigned
    # values.
    for [(name, defval), assigned] in parameters:
        if (defval is None) and not assigned:
            if name is None:
                display_name = '<tuple>'
            else:
                display_name = repr(name)
            # TODO(cpopa): this should be removed after PyCQA/astroid/issues/177
            if not has_no_context_positional_variadic:
                self.add_message('no-value-for-parameter', node=node,
                                    args=(display_name, callable_name))

    for name in kwparams:
        defval, assigned = kwparams[name]
        if defval is None and not assigned and not has_no_context_keywords_variadic:
            self.add_message('missing-kwoa', node=node,
                                args=(name, callable_name))

