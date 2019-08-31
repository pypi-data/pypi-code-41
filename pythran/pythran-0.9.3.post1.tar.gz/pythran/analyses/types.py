from pythran.passmanager import ModuleAnalysis
from pythran.analyses import UseDefChains, YieldPoints, GlobalDeclarations
from pythran.utils import attr_to_path, path_to_node
from itertools import product
from functools import reduce
from copy import deepcopy

import gast as ast

[BuiltinModuleTrait,
 ListTrait,
 SetTrait,
 TupleTrait,
 SubTupleTrait,
 TupleEndTrait,
 FunTrait,
 IntTrait] = range(8)

def pp(t):
    if isinstance(t, int):
        return {BuiltinModuleTrait: 'module',
                ListTrait: 'list',
                SetTrait: 'set',
                TupleTrait: 'tuple',
                SubTupleTrait: '',
                TupleEndTrait: '',
                FunTrait: 'function',
                IntTrait: 'int'
               }[t]
    if isinstance(t, (TypeOperator, TypeVariable, type(None))):
        return str(t)
    return t.__name__

class TypeOperator(object):
    def __init__(self, *types):
        self.types = types

    def __str__(self):
        return pp(self.types[0]) if len(self.types) == 1 else ", ".join(map(pp,self.types))

    def specialize(self, args):
        return self

class TypeOperatorGenerator(object):

    def __init__(self, generator):
        self.generator = generator

    def specialize(self, args):
        return self.generator(len(args))


class TypeVariable(object):

    def __init__(self, constraints=None, name=None):
        self.constraints = [None] if constraints is None else constraints
        self.name = name

    def isvariable(self):
        return len(self.constraints) == 1 and self.constraints[0] is None

    def isfinal(self):
        if len(self.constraints) > 1:
            return False
        constraint = self.constraints[0]
        return constraint is None or isinstance(constraint, TypeOperator)

    def __str__(self):
        if len(self.constraints) == 1:
            if self.constraints[0] is None:
                return self.name or str(id(self))
            else:
                return str(self.constraints[0])
        else:
            return '({})'.format(' | '.join(str(c) for c in self.constraints))

    def specialize(self, args):
        return self

class Inliner(object):

    def __init__(self, fun, visitor):
        self.fun = fun
        self.visitor = visitor

    def specialize(self, arg_types):
        prev_env = self.visitor.env
        self.visitor.env = {n.id:arg_type for n, arg_type in zip(self.fun.args.args, arg_types)}
        rtype = self.visitor.visit(self.fun)
        self.visitor.env = prev_env
        return rtype


NoneTy = TypeOperator(None)

def IntTy():
    return TypeOperator(int)

def ListTy(elt_type):
    return TypeOperator(ListTrait, elt_type)

def SetTy(elt_type):
    return TypeOperator(SetTrait, elt_type)

def TupleTy(elts_type):
    return TypeOperator(TupleTrait, reduce(lambda x, y: TypeOperator(SubTupleTrait, y, x),
                                       elts_type[::-1],
                                       TypeOperator(TupleEndTrait)))

def GenericTupleTy():
    return TypeOperator(TupleTrait, TypeVariable())

def FunTy(argument_types, result_type):
    return TypeOperator(FunTrait, *(argument_types + [result_type]))

def LenTy():
    return TypeVariable(
            name='len',
            constraints=[
                FunTy([ListTy(TypeVariable())], IntTy()),
                FunTy([SetTy(TypeVariable())], IntTy()),
                FunTy([GenericTupleTy()], IntTy()),
            ]
        )


def PrintTy():
    return TypeOperatorGenerator(lambda n: FunTy([TypeVariable() for _ in range(n)], NoneTy))

def MapTy():
    def generator(n):
        arg_types0 = [TypeVariable() for _ in range(n - 1)]
        arg_types1 = [TypeVariable() for _ in range(n - 1)]
        return_type = TypeVariable()
        fun_type = FunTy([arg_types1], return_type)
        return TypeVariable(name='map',
                            constraints=[
                                FunTy([NoneTy] + [ListTy(arg_ty) for arg_ty in arg_types0], ListTy(arg_types0[0] if n == 2 else TupleTy(arg_types0))),
                                FunTy([fun_type] + [ListTy(arg_ty) for arg_ty in arg_types1], ListTy(return_type))
                            ])
    return TypeOperatorGenerator(generator)

def BuiltinTy():
    return TypeOperator(BuiltinModuleTrait)


class UnificationError(Exception):
    pass

class Types(ModuleAnalysis):

    def __init__(self):
        self.result = dict()
        super(Types, self).__init__(UseDefChains, GlobalDeclarations)

    def unify(self, type0, type1):
        if not isinstance(type0, (TypeOperator, TypeVariable)):
            if type0 != type1:
                raise UnificationError()
        elif isinstance(type0, TypeOperator) and isinstance(type1, TypeOperator):
            if len(type0.types) != len(type1.types):
                   raise UnificationError()
            for subtype0, subtype1 in zip(type0.types, type1.types):
                self.unify(subtype0, subtype1)
        elif isinstance(type0, TypeOperator) or isinstance(type1, TypeOperator):
            if isinstance(type1, TypeOperator):
                type0, type1 = type1, type0
            # type0 is the TypeOperator and type1 is the TypeVariable
            if type1.isvariable():
                type1.constraints[0] = type0

            valid_constraints = []
            for constraint in type1.constraints:
                try:
                    self.unify(type0, constraint)
                    valid_constraints.append(constraint)
                except UnificationError:
                    pass
            if valid_constraints:
                type1.constraints[:] = valid_constraints
            else:
                raise UnificationError()
        elif type0.isvariable():
            type0.constraints[0] = type1
        elif type1.isvariable():
            type1.constraints[0] = type0
        else:
            valid_constraints = []
            for constraint0, constraint1 in product(type0.constraints, type1.constraints):
                try:
                    c0, c1 = deepcopy(constraint0), deepcopy(constraint1)
                    self.unify(c0, c1)
                    valid_constraints.append(c0)
                except UnificationError:
                    pass
            if valid_constraints:
                type0.constraints = type1.constraints = valid_constraints
            else:
                raise UnificationError()

    def visit_FunctionDef(self, node):
        self.env = {'__builtin__': BuiltinTy(),
                    '@return': TypeVariable()
                   }
        for arg in node.args.args:
            self.env[arg.id] = TypeVariable(name="'{}".format(arg.id))
        for stmt in node.body:
            self.visit(stmt)

        return_type = self.env.setdefault('@return', NoneTy)
        print("=== {} ===".format(node.name))
        for k, v in self.env.items():
            print("{}: {}".format(k, v))
        print("=== +++++ ===")
        return FunTy([self.env[arg.id] for arg in node.args.args], return_type)

    def visit_Return(self, node):
        if node.value is None:
            ret_type = NoneTy
        else:
            ret_type = self.visit(node.value)
        self.unify(ret_type, self.env['@return'])

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id not in self.env:
                # maybe it's a global function? if so let's specialize it
                if node.id not in self.global_declarations:
                    raise ValueError("unbound variable", node.id)
                return Inliner(self.global_declarations[node.id], self)

            return self.env[node.id]
        else:
            return self.env.setdefault(node.id, TypeVariable())

    def visit_Assign(self, node):
        value_type = self.visit(node.value)
        targets_type = [self.visit(target) for target in node.targets]
        for target_type in targets_type:
            self.unify(target_type, value_type)

    def visit_Constant(self, node):
        return TypeOperator(type(node.n))

    def visit_List(self, node):
        elt_types = [self.visit(elt) for elt in node.elts]
        if elt_types:
            for elt_type in elt_types[1:]:
                self.unify(elt_types[0], elt_type)
            return ListTy(elt_types[0])
        else:
            return ListTy(TypeVariable())

    def visit_Set(self, node):
        elt_types = [self.visit(elt) for elt in node.elts]
        if elt_types:
            for elt_type in elt_types[1:]:
                self.unify(elt_types[0], elt_type)
            return SetTy(elt_types[0])
        else:
            return SetTy(TypeVariable())

    def visit_Tuple(self, node):
        elt_types = [self.visit(elt) for elt in node.elts]
        return TupleTy(elt_types)

    def visit_Attribute(self, node):
        _, path = attr_to_path(node)
        if path[-1] == 'len':
            return LenTy()
        if path[-1] == 'map':
            return MapTy()
        if path[-1] == 'print':
            return PrintTy()
        if path[-1] == 'None':
            return NoneTy
        raise NotImplementedError(path)

    def visit_Call(self, node):
        fun_type = self.visit(node.func)
        arg_types = [self.visit(arg) for arg in node.args]
        return_type = TypeVariable()
        import pdb; pdb.set_trace()
        self.unify(FunTy(arg_types, return_type), fun_type.specialize(arg_types))
        return return_type

