from ethics.language import *
from ethics.tools import *
#import z3

"""
def to_z3(f):
    if isinstance(f, And):
        return z3.And(to_z3(f.f1), to_z3(f.f2))
    if isinstance(f, Or):
        return z3.Or(to_z3(f.f1), to_z3(f.f2))
    if isinstance(f, Not):
        return z3.Not(to_z3(f.f1))
    if isinstance(f, Impl):
        return z3.Implies(to_z3(f.f1), to_z3(f.f2))
    if isinstance(f, BiImpl):
        return to_z3(f.f1) == to_z3(f.f2)
    return z3.Bool(str(f))
    
def z3_model_to_cal(f):
    model = []
    for e in f:
        try:
            form = subToAtoms(eval(str(e)))
        except:
            form = subToAtoms(str(e))
        if f[e] == False:
            model.append(Not(form))
        else:
            model.append(form)
    return model
"""
    
def theorySAT(cand_model):
    """ A Solver for Simple Causal Agency Logic
    
    Keyword arguments:
    cand_model --- A list of literals to be checked for consistency
    """
    for m in cand_model:
        if isinstance(m, Good):
            if Bad(m.f1) in cand_model:
                #print("good:bad")
                return False
            if Neutral(m.f1) in cand_model:
                #print("good:neutral")
                return False
        if isinstance(m, Bad):
            if Good(m.f1) in cand_model:
                #print("bad:good")
                return False
            if Neutral(m.f1) in cand_model:
                #print("bad:neutral")
                return False
        if isinstance(m, Neutral):
            if Good(m.f1) in cand_model:
                #print("neutral:good")
                return False
            if Bad(m.f1) in cand_model:
                #print("neutral:bad")
                return False
        if isinstance(m, Causes):
            if Not(m.f1).nnf() in cand_model:
                #print("causes: notf1")
                return False
            if Not(m.f2).nnf() in cand_model:
                #print("causes: notf2")
                return False
            if m.f1 != m.f2 and Causes(m.f2, m.f1) in cand_model:
                #print("causes: symmetry", m)
                return False
            if m == Causes(m.f1, Not(m.f1).nnf()):
                #print("causes: notff")
                return False
            if Causes(m.f1, Not(m.f2).nnf()) in cand_model:
                #print("causes: f1notf2")
                return False
            if Causes(Not(m.f1).nnf(), m.f2) in cand_model:
                #print("causes: notf1nf2")
                return False
        if isinstance(m, Not) and isinstance(m.f1, Causes) and m.f1.f1 == m.f1.f2 and m.f1 in cand_model:
            #print("notcauses", m)
            return False
        if isinstance(m, Not) and isinstance(m.f1, Eq) and m.f1.f1 == m.f1.f2:
            #print("noteq")
            return False
        if isinstance(m, Not) and isinstance(m.f1, Eq) and m.f1.f1 == m.f1.f2:
            return False
        if isinstance(m, Not) and isinstance(m.f1, GEq) and m.f1.f1 == m.f1.f2:
            return False
        if isinstance(m, Eq):
            if Gt(m.f1, m.f2) in cand_model:
                #print("eqgt")
                return False
        if isinstance(m, GEq):
            if Gt(m.f2, m.f1) in cand_model:
                #print("geqgt", m)
                return False
        if isinstance(m, Gt):
            if m.f1 == m.f2:
                return False
            if Gt(m.f2, m.f1) in cand_model:
                return False
            if GEq(m.f2, m.f1) in cand_model:
                return False
            if Eq(m.f1, m.f2) in cand_model:
                return False
            if Eq(m.f2, m.f1) in cand_model:
                return False
        if isinstance(m, Better):
            if m.f1 == m.f2:
                return False
            if Better(m.f2, m.f1) in cand_model:
                return False
            for n in cand_model:
                if isinstance(n, Better):
                    if m.f2 == n.f1:
                        if Not(Better(m.f1, n.f2)) in cand_model:
                            return False
    
    return True
    
def smtAllModels(formula):
    formula = subToAtoms(formula)
    s = TableauxSolver()
    s.append_formula(formula)
    models = []
    for mod in s.enum_models():
        #f = mapBackToFormulae(mod, m)
        #print("mod", mod)
        if theorySAT(mod):
            models.append(mod)
        #print("models", len(models))
    #s.delete()
    return models

def satisfiable(formula, model = False):
    if(isinstance(formula, list)):
        formula = Formula.makeConjunction(formula)

    formula = subToAtoms(formula)
    s = TableauxSolver()
    s.append_formula(formula)
    if model:
        return s.get_model()
    return s.satisfiable()

"""
class Z3Solver():
    def __init__(self):
        self.s = z3.Solver()
        self.models = []
    
    def append_formula(self, f):
        self.s.add(to_z3(f))
        
    def enum_models(self):
        while self.s.check() == z3.sat:
            m = self.s.model()
            n = self.__buildNegModel(m)
            self.s.add(n)
            self.models.append(z3_model_to_cal(m))
        return self.models
        
    def __buildNegModel(self, model):
        f = None
        for v in model:
            if model[v]:
                g = z3.Not(z3.Bool(str(v)))
            else:
                g = z3.Bool(str(v))
            if f is None:
                f = g
            else:
                f = z3.Or(g, f)
        return f
        
    def satisfiable(self):
        return self.s.check() == z3.sat
        
    def get_model(self):
        self.s.check()
        return z3_model_to_cal(self.s.model())
"""

class TableauxSolver():
    def __init__(self):
        self.formulae = []
        self.tree = []
        self.lits = None

    def append_formula(self, f):
        f = subToAtoms(f)
        nnf = f.nnf()
        if len(self.formulae) == 0:
            self.lits = list(set(nnf.getAllCALLiterals()))
        self.formulae.append(nnf)

    def enum_models(self):
        models = []
        while True:
            m = self.get_model()
            if m == False:
                #print("all models found")
                return models
            if theorySAT(m):
                models.append(m)
                #print("append", m)
            #print("# Models:", len(models))
            #print("Add:", Not(Formula.makeConjunction(m)).nnf())
            self.formulae.append(Not(Formula.makeConjunction(m)).nnf())

    def satisfiable(self):
        return self.get_model() is not False

    def get_model(self):
        self.tree = []
        self.tree.append(Branch(self, list(self.formulae)))
        for branch in self.tree:
            branch.saturate()
            model = branch.extractModel()
            if branch.consistent():
                return model
        return False


class Branch:
    def __init__(self, solver, formulae):
        self.formulae = formulae
        self.solver = solver
        self.expanded = []
        self.inconsistent = False
        
        if not self.consistent():
            self.inconsistent = True
        

    def extractModel(self):
        return [e for e in self.solver.lits if e in self.formulae] + [e.getNegation() for e in self.solver.lits if e.getNegation() in self.formulae]

    def consistent(self):
        for f in self.formulae:
            if (f in self.solver.lits or f.getNegation() in self.solver.lits) and f.getNegation() in self.formulae:
                return False
        return True

    def appendNew(self, formula):
        if (formula in self.solver.lits or formula.getNegation() in self.solver.lits) and formula.getNegation() in self.formulae:
            self.inconsistent = True
        if formula not in self.formulae:
            self.formulae.append(formula)

    def equalBranchExists(self, branch):
        for b in self.solver.tree:
            if b == branch:
                return True
        return False

    def appendNewBranch(self, formula):
        newBranch = Branch(self.solver, list(self.formulae))
        newBranch.appendNew(formula)
        newBranch.expanded = list(self.expanded)
        self.solver.tree.append(newBranch)

    def expandAnd(self):
        found = False
        for f in [g for g in self.formulae if isinstance(g, And) and g not in self.expanded]:
            if self.inconsistent:
                break
            self.expanded.append(f)
            self.appendNew(f.f1)
            self.appendNew(f.f2)
            found = True
        
        for f in [g for g in self.formulae if isinstance(g, Or) and g not in self.expanded]:
            if self.inconsistent:
                break
            if Not(f.f1).nnf() in self.formulae:
                self.expanded.append(f)
                self.appendNew(f.f2)
                found = True
                continue
            if Not(f.f2).nnf() in self.formulae:
                self.expanded.append(f)
                self.appendNew(f.f1)
                found = True
                continue
        return found
            
            
    def expandOr(self):
        found = False
        for f in [g for g in self.formulae if isinstance(g, Or) and g not in self.expanded]:
            if self.inconsistent:
                break
            self.expanded.append(f)
            found = True
            if f.f1 not in self.formulae and f.f2 not in self.formulae:
                self.appendNewBranch(f.f2)
                self.appendNew(Not(f.f2).nnf())
                self.appendNew(f.f1)
        return found
            

    def saturate(self):
        while True and not self.inconsistent:
            
            while True and not self.inconsistent:
                if not self.expandAnd():
                    break             
                    
            if not self.expandOr():
                if not self.expandAnd():
                    break
        
