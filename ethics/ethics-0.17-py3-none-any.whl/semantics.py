import json
import yaml
import io
import sys

from ethics.language import *
from ethics.tools import *
from ethics.solver import *

class Model(object):
    """ Models """
    def __init__(self):
        self.alternatives = []
        
    def models(self, formula):
        return self.checker.models(self, formula)

    def evaluate(self, principle):
        try:
            p = principle(self)
        except:
            p = principle
        perm = p.permissible()
        return perm

class CausalNetwork(Model):
    """
    Implements a causal network of boolean variables.
    """
    def __init__(self, exo, endo, seq, world = None):
        super().__init__()
        self.endoVars = endo
        self.exoVars = exo
        self.seq = seq
        
        self.interventions = {}
            
        if world == None:
            self.set_world({v:0 for v in self.actions + self.background})
        else:
            self.set_world(world)
    
    def do(self, dic_var):
        for v, k in dic_var.items():
            self.interventions[v] = k
        self.__compute()
        
    def release(self, *var):
        for v in var:
            del self.interventions[v]
        self.__compute()
    
    def set_world(self, dic_var):
        self.world = dic_var
        self.__compute()
        
    def __get_model(self):
        return And(Formula.makeConjunction([f for f in self.causal_network_model if self.causal_network_model[f]]), \
                Formula.makeConjunction([Not(f) for f in self.causal_network_model if not self.causal_network_model[f]]))
    
    def __compute_model(self, *additional):
        s = []
        s.append(self.causal_network)
        for f in additional:
            s.append(f)
        return satisfiable(Formula.makeConjunction(s), model = True)
            
    def __represent_causal_model(self):
        formula = []
        # Exogenous Variables
        for p in self.exoVars:
            if p in self.interventions:
                if self.interventions[p] == True:
                    formula += [Atom(p)]
                else:
                    formula += [Not(Atom(p))]
            else:
                if self.world[p] == True:
                    formula += [Atom(p)]
                else:
                    formula += [Not(Atom(p))]
        # Endogenous Variables
        for p in self.endoVars:
            if p in self.interventions:
                if self.interventions[p] == True:
                    formula += [Atom(p)]
                else:
                    formula += [Not(Atom(p))]
            else:
                formula += [BiImpl(Atom(p), self.seq[p])]
        return Formula.makeConjunction(formula)
        
    def __compute(self):
        self.causal_network = self.__represent_causal_model()
        self.causal_network_model = self.__compute_model()
        
    def models(self, f):
        if isinstance(f, Causes):
            if self.models(f.f1) and self.models(f.f2):
                return self.models(Intervention(f.f1.getNegation(), f.f2.getNegation()))
            return False
        if isinstance(f, Intervention):
            if isinstance(f.f1, Not):
                self.do({f.f1.f1: False})
                r = self.models(f.f2)
                self.release(f.f1.f1)
            else:
                self.do({f.f1: True})
                r = self.models(f.f2)
                self.release(f.f1)
            return r
        if isinstance(f, Not):
            return not self.models(f.f1)
        if isinstance(f, Impl):
            return not self.models(f.f1) or self.models(f.f2)
        if isinstance(f, BiImpl):
            return self.models(Impl(f.f1, f.f2)) and self.models(Impl(f.f2, f.f1))
        if isinstance(f, And):
            return self.models(f.f1) and self.models(f.f2)
        if isinstance(f, Or):
            return self.models(f.f1) or self.models(f.f2)
        if isinstance(f, Atom):
            return f in self.causal_network_model

class CausalModel(CausalNetwork):
    """
    Causal Agency Model
    """
    def __init__(self, file, world = None):
        self.file = file
        with io.open(file) as data_file:
            if self.file.split(".")[-1] == "json":
                self.model = json.load(data_file)
            else:
                self.model = yaml.load(data_file, Loader=yaml.FullLoader)
            # Actions are mandatory
            self.actions = [Atom(a) for a in self.model["actions"]]
            # Only for compatibility reasons
            self.action = self.actions[0]
            
            # Optional entries
            try:
                self.utilities = {str(k): v for k, v in self.model["utilities"].items()}
            except:
                self.utilities = dict()
            try:
                self.patients = [str(a) for a in self.model["patients"]] 
            except: 
                self.patients = []
            try:
                self.description = str(self.model["description"])
            except:
                self.description = "No Description"
            try:
                self.consequences = [Atom(c) for c in self.model["consequences"]]
            except:
                self.consequences = []
            try:
                self.background = [Atom(b) for b in self.model["background"]]
            except:
                self.background = []
            try:
                mechanisms = {str(k): myEval(v) for k, v in self.model["mechanisms"].items()}
            except:
                mechanisms = dict()
            try:
                self.intentions = {str(k): list(map(myEval, v)) for k, v in self.model["intentions"].items()}
            except:
                self.intentions = dict()
            try:
                self.goals = {str(k): list(map(myEval, v)) for k, v in self.model["goals"].items()}
            except:
                self.goals = dict()
            try:
                self.affects = {str(k): v for k, v in self.model["affects"].items()}
            except: 
                self.affects = dict()
                
            super().__init__(self.actions + self.background, self.consequences, mechanisms, world)

    def __evaluate_term(self, term):
        if isinstance(term, int):
            return term
        if isinstance(term, Minus):
            return -1*self.__evaluate_term(term.f1)
        if isinstance(term, Add):
            return self.__evaluate_term(term.t1) + self.__evaluate_term(term.t2)
        if isinstance(term, Sub):
            return self.__evaluate_term(term.t1) - self.__evaluate_term(term.t2)
        if isinstance(term, U):
            return self.__sum_up(term.t1)
            
    def __sum_up(self, formula):
        if formula is None:
            return 0
        if isinstance(formula, bool):
            return 0
        if isinstance(formula, Atom):
            if formula in self.utilities:
                return self.utilities[str(formula)]
            else:
                return 0
        if isinstance(formula, Not):
            if isinstance(formula.f1, Atom):
                if str(formula) in self.utilities:
                    return self.utilities[str(formula)]
                else:
                    return 0
            if isinstance(formula.f1, Not):
                return self.__sum_up(formula.f1.f1)
        if isinstance(formula, And):
            return self.__sum_up(formula.f1) + self.__sum_up(formula.f2)
            
    def __affects(self, affects, formula, posneg):
        if isinstance(formula, And):
            return self._affects(affects, formula.f1, posneg) and self._affects(affects, formula.f2, posneg)
        return formula in [i[0] for i in affects if i[1] == posneg]
        
    def get_actual_goals(self):
        goals = []
        for a in self.get_performed_actions():
            goals += self.goals[a]
        return goals
        
    def get_actual_intentions(self):
        intentions = []
        for a in self.get_performed_actions():
            intentions += self.intentions[a]
        return intentions
        
    def get_actual_consequences(self):
        return [e for e in self.consequences if self.models(e)] + [Not(e) for e in self.consequences if not self.models(e)]
        
    def get_all_consequences(self):
        return [e for e in self.consequences] + [Not(e) for e in self.consequences]
    
    def get_direct_consequences(self):
        cons_all = self.get_all_consequences()
        cons_direct = []
        for a in self.get_performed_actions():
            cons_direct += [c for c in cons_all if self.models(Causes(a, c))]
        return cons_direct
        
    def get_all_actions(self):
        return [e for e in self.actions]  
              
    def get_performed_actions(self):
        return [e for e in self.actions if self.models(e)]
        
    def explain(self, principle):
        try:
            p = principle(self)
        except:
            p = principle
        return p.explain()
        
    def models(self, f):
        if isinstance(f, Eq):
            return self.__evaluate_term(f.f1) == self.__evaluate_term(f.f2)
        if isinstance(f, Gt):
            return self.__evaluate_term(f.f1) > self.__evaluate_term(f.f2)
        if isinstance(f, GEq):
            return self.__evaluate_term(f.f1) >= self.__evaluate_term(f.f2)
        if isinstance(f, Good):
            return self.__evaluate_term(U(f.f1)) > 0
        if isinstance(f, Bad):
            return self.__evaluate_term(U(f.f1)) < 0
        if isinstance(f, Neutral):
            return self.__evaluate_term(U(f.f1)) == 0
        if isinstance(f, I):
            return f.f1 in self.get_actual_intentions()
        if isinstance(f, Goal):
            return f.f1 in self.get_actual_goals()
        if isinstance(f, Affects):
            if str(f.f1) not in self.affects:
                return False
            return self.__affects(self.affects[str(f.f1)], f.f2, "+") or self.__affects(self.affects[str(f.f1)], f.f2, "-")
        if isinstance(f, AffectsPos):
            if str(f.f1) not in self.affects:
                return False
            return self.__affects(self.affects[str(f.f1)], f.f2, "+")
        if isinstance(f, AffectsNeg):
            if str(f.f1) not in self.affects:
                return False
            return self.__affects(self.affects[str(f.f1)], f.f2, "-")  
        if isinstance(f, End):
            foundPos = False
            for i in self.get_actual_goals():
                if self.models(AffectsNeg(i, f.f1)):
                    return False
                if not foundPos and self.models(AffectsPos(i, f.f1)):
                    foundPos = True
            return foundPos
        if isinstance(f, Means):
            for i in self.get_all_actions()+self.get_direct_consequences():
                if f.f1 == "Reading-1":
                    for g in self.get_actual_goals():
                        if self.models(And(Causes(i, g), Affects(i, f.f2))):
                            return True
                if f.f1 == "Reading-2":
                    if self.models(Affects(i, f.f2)):
                        return True
            return False
        #Everything else
        return super().models(f)
