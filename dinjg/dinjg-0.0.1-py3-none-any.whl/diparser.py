import itertools
from functools import reduce
from typing import Set

from typed_ast import ast3
from typed_ast._ast3 import ClassDef, FunctionDef


def _unwrap_annotation(ast_obj):
    if isinstance(ast_obj, ast3.Name):
        return [ast_obj.id]

    if isinstance(ast_obj, ast3.Subscript):
        return _unwrap_annotation(ast_obj.value) + _unwrap_annotation(ast_obj.slice)

    if isinstance(ast_obj, ast3.Index):
        return _unwrap_annotation(ast_obj.value)

    if isinstance(ast_obj, ast3.Tuple):
        return reduce(
            list.__add__, [_unwrap_annotation(element) for element in ast_obj.elts], []
        )

    raise ValueError("Unexpected value: {}".format(ast_obj))


def _parse_type_comment(type_comment):
    return ast3.parse(type_comment).body[0].value


def get_di_dependencies(ast_class_def: ClassDef) -> Set[str]:
    for ast_obj in ast_class_def.body:
        if not isinstance(ast_obj, FunctionDef):
            continue

        if ast_obj.name != "__init__":
            continue

        arg_list_list = list(
            arg_list
            for arg_list in [
                ast_obj.args.args,
                ast_obj.args.kwonlyargs,
                ast_obj.args.kw_defaults,
            ]
            if arg_list
        )
        if not arg_list_list:
            return set()

        arg_list = itertools.chain(*arg_list_list)
        return {
            dependency
            for dependency_list in (
                _unwrap_annotation(arg.annotation)
                if arg.annotation is not None
                else _unwrap_annotation(_parse_type_comment(arg.type_comment))
                if arg.type_comment is not None
                else []
                for arg in arg_list
            )
            for dependency in dependency_list
        }
