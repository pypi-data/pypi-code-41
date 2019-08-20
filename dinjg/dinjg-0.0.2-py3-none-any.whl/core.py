import importlib.util
import importlib
import inspect
import os
import pkgutil
from importlib.machinery import FileFinder, SourceFileLoader
from pprint import pformat
from typing import Iterable, List, Dict, Tuple

import click
from typed_ast import ast3
import graphviz

from dinjg.diparser import get_di_dependencies


def get_mro_dependencies(class_def: ast3.ClassDef, module):
    class_name = class_def.name
    target_cls = getattr(module, class_name)
    return [
        cls.__name__
        for cls in target_cls.__mro__
        if cls is not target_cls and cls is not object
    ]


def _main(package_name: str):
    edges = []
    for ast_class_def, module in iter_class_def(package_name):
        name, dependencies = ast_class_def.name, get_di_dependencies(ast_class_def)
        if not dependencies:
            continue

        edges.extend([name, d, False] for d in dependencies)

    for ast_class_def, module in iter_class_def(package_name):
        name, dependencies = (
            ast_class_def.name,
            get_mro_dependencies(ast_class_def, module),
        )
        if not dependencies:
            continue

        edges.extend([name, d, True] for d in dependencies)

    nodes = {}
    for ast_class_def, module in iter_class_def(package_name):
        class_name = ast_class_def.name
        cls_obj = getattr(module, class_name)
        nodes[class_name] = inspect.isabstract(cls_obj)
    return build_graph(nodes, edges)


def build_graph(nodes: Dict[str, bool], edges: List[Tuple[str, str, bool]]):
    click.echo(pformat(nodes), err=True)
    graph = graphviz.Digraph()
    graph.graph_attr["overlap"] = "false"

    for name, cls_type in nodes.items():
        graph.node(name, shape={True: "box", False: "oval"}.get(cls_type, "oval"))

    for edge in edges:
        graph.edge(
            edge[0],
            edge[1],
            **(
                dict(arrowhead="dot", dir="both", arrowtail="oinv")
                if edge[2]
                else dict()
            )
        )

    click.echo(graph.source)


def iter_class_def(package_name: str):
    module = importlib.import_module(package_name)
    path = module.__path__
    for module in walk_packages(path, prefix=module.__name__ + "."):
        ast_module = _parse(module)
        for ast_class_def in _iter_class_def(ast_module):
            yield ast_class_def, module


def _get_source(module):
    sourcefile = inspect.getsourcefile(module)
    if os.path.isdir(sourcefile):
        targetfile = os.path.join(sourcefile, "__init__.py")
    else:
        targetfile = sourcefile
    with open(targetfile, "rb") as f:
        return f.read(), targetfile


def _parse(module):
    source, path = _get_source(module)
    return ast3.parse(source, filename=os.path.basename(path))


def _iter_class_def(module: ast3.Module) -> Iterable[ast3.ClassDef]:
    for ast_obj in module.body:
        if isinstance(ast_obj, ast3.ClassDef):
            yield ast_obj


def walk_packages(path: List[str], prefix: str) -> Iterable:
    spec = importlib.util.spec_from_file_location(
        prefix.strip("."), location=path[0], loader=FileFinder(path[0])
    )
    module = importlib.util.module_from_spec(spec)
    yield module
    for info in pkgutil.iter_modules(path, prefix=prefix):
        module_finder = info.module_finder  # type: FileFinder
        loader = module_finder.find_loader(info.name)[0]  # type: SourceFileLoader
        submodule = loader.load_module(info.name)
        if not hasattr(submodule, "__path__"):
            yield submodule
            continue
        yield from walk_packages(submodule.__path__, prefix=info.name + ".")
