import time
import logging

from prophesy.regions.region_solutionfunctionchecker import SolutionFunctionRegionChecker
from prophesy.regions.region_etrchecker import EtrRegionChecker
from prophesy.regions.region_checker import RegionCheckResult
from prophesy.smt.smt import Answer
from prophesy.smt.IcpCli_solver import IcpCliSolver
from prophesy.data.samples import ParameterInstantiation, InstantiationResult
from prophesy.adapter.pycarl import Rational
import prophesy.adapter.pycarl as pc

from prophesy.data.hyperrectangle import HyperRectangle
from prophesy.data.interval import string_to_interval
from prophesy.modelcheckers.stormpy import StormpyModelChecker

logger = logging.getLogger(__name__)



class ICPRegionChecker(EtrRegionChecker):


    def __init__(self, smt2interface, mc, pla_processing=True):
        if not isinstance(smt2interface, IcpCliSolver):
            logger.warning("Running ICP without an ICP solver.")
        super().__init__(smt2interface, mc)
        self._exact = True
        self._pla_processing = True
        self._additional_constraints = False
        # maybe initialize some additional stuff
        from prophesy.config import configuration
        self._result_file = configuration.get_icp_result_file()
        self._parameters = None # Only necessary for PLA.

    def initialize(self, problem_description, fixed_threshold):
        # For now, just do what the smt checker does. Change if necessary.
        super().initialize(problem_description, fixed_threshold, fixed_direction="border")
        self._parameters = problem_description.parameters

    def supports_only_closed_regions(self):
        return True


    def analyse_region(self, region, safe, check_for_eq):
        logger.debug("Call analyse with region %s (safe={}, check_for_eq={})".format(safe, check_for_eq), str(region))
        terminate_after_pla = False

        smt_successful = False
        smt_model = None

        upper_state_bounds = None
        lower_state_bounds = None
        ran_pla = False
        if self._pla_processing and region.is_closed():
            ran_pla = True
            upper_state_bounds, _ = self.model_explorer.bound_value_in_hyperrectangle(self._parameters, region,
                                                                           True, all_states=True)
            lower_state_bounds, _ = self.model_explorer.bound_value_in_hyperrectangle(self._parameters, region,
                                                                           False, all_states=True)
            print(upper_state_bounds.at(self.model_explorer.get_model().initial_states[0]))
            print(lower_state_bounds.at(self.model_explorer.get_model().initial_states[0]))

            if check_for_eq:
                if float(self._threshold) < lower_state_bounds.at(self.model_explorer.get_model().initial_states[0]):
                    logger.debug("PLA obtained a result.")
                    return RegionCheckResult.Homogenous, None
                if float(self._threshold) > upper_state_bounds.at(self.model_explorer.get_model().initial_states[0]):
                    logger.debug("PLA obtained a result.")
                    return RegionCheckResult.Homogenous, None
            if terminate_after_pla:
                return RegionCheckResult.Unknown, None
            logger.debug("PLA Preprocessing inconclusive.")

        constraint = region.to_formula(self.parameters)

        while not smt_successful:
            # check constraint with smt
            with self._smt2interface as smt_context:
                smt_context.assert_constraint(constraint)

                if not self._fixed_direction:
                    if check_for_eq:
                        smt_context.set_guard("?_equals", True)
                        smt_context.set_guard("?_safe", False)
                        smt_context.set_guard("?_bad", False)
                    else:
                        # Invert the safe flag to try and find a counter example
                        smt_context.set_guard("?_equals", False)
                        smt_context.set_guard("?_safe", not safe)
                        smt_context.set_guard("?_bad", safe)

                if not self._exact:
                    smt_context.set_guard("?_exact", False)

                for state in self.model_explorer.get_model().states:
                    state_var = self._state_var_mapping.get(state.id)
                    if state_var is None:
                        continue
                    if upper_state_bounds:
                        self._smt2interface.assert_constraint(
                            pc.Constraint(state_var, pc.Relation.LESS, pc.Rational(upper_state_bounds.at(state.id))))

                    if lower_state_bounds:
                        self._smt2interface.assert_constraint(
                            pc.Constraint(state_var, pc.Relation.GREATER, pc.Rational(lower_state_bounds.at(state.id))))


                start = time.time()
                logger.debug("Execute smt interface")
                checkresult = smt_context.check()
                duration = time.time() - start

                self.benchmark_output.append((checkresult, duration, region.size()))

                # self.print_benchmark_output(self.benchmark_output)
                if not checkresult in [Answer.sat, Answer.unsat]:
                    break
                else:
                    if checkresult == Answer.unsat or not self.over_approximates():
                        logger.info("ICP obtained a result{}.".format(" after PLA" if ran_pla else ""))

                    if checkresult == Answer.sat:
                        smt_model = smt_context.get_model()
                    break
        if check_for_eq:
            if checkresult == Answer.unsat:
                return RegionCheckResult.Homogenous, None
            elif checkresult == Answer.sat:
                if not isinstance(self._smt2interface, IcpCliSolver):
                    return RegionCheckResult.Unknown, None
                logger.debug("sat")
                # read the output of icp and get the contracted intervals.
                intervals = []
                with open(self._result_file, "r") as refinement_file:
                    for line in refinement_file:
                        line.rstrip()
                        if line == '\n':
                            break
                        tokens = line.split("=")
                        # only update our parameters!
                        for par in self.parameters:
                            if par.name == tokens[0]:
                                interval = string_to_interval(tokens[1], Rational)
                                intervals.append(interval)
                hrect = HyperRectangle(*intervals)
                if hrect == region:
                    logger.info("Refinement yields no new information!")
                    return RegionCheckResult.Unknown, hrect
                elif hrect.close() == region.close():
                    logger.info("Refinement yields no new information!")
                    return RegionCheckResult.Unknown, hrect
                logger.info("Refinement successfull: {} to {} (new is {}\% of old )".format(region, hrect, hrect.size() / region.size()))
                return RegionCheckResult.Refined, hrect
                #return RegionCheckResult.Inhomogenous, None
                # TODO: Add benchmark output.
        if checkresult == Answer.unsat:
            logger.debug("unsat")
            return RegionCheckResult.Satisfied, None
        elif checkresult == Answer.sat:

            if not isinstance(self._smt2interface, IcpCliSolver):
                return RegionCheckResult.Unknown, None
            logger.debug("sat")
            # add new point as counter example to existing regions
            sample = ParameterInstantiation()
            for par in self.parameters:
                value = smt_model[par.name]
                rational = Rational(value)
                sample[par] = rational
            eval_dict = dict([(k.variable, v) for k, v in sample.items()])
            value = self._ratfunc.evaluate(eval_dict)
            return RegionCheckResult.CounterExample, None
        elif checkresult == Answer.unknown:

            if not isinstance(self._smt2interface, IcpCliSolver):
                return RegionCheckResult.Unknown, None
            logger.debug("unknown")
            # read the output of icp and get the contracted intervals.
            intervals = []
            with open(self._result_file, "r") as refinement_file:
                for line in refinement_file:
                    line.rstrip()
                    if line == '\n':
                        break
                    tokens = line.split("=")
                    # only update our parameters!
                    for par in self.parameters:
                        if par.name == tokens[0]:
                            interval = string_to_interval(tokens[1], Rational)
                            intervals.append(interval)
            hrect = HyperRectangle(*intervals)
            if hrect.size() > region.size():
                logger.info("Refinement only increased the size :(")
                return RegionCheckResult.Unknown, region
            if hrect == region:
                logger.info("Refinement yields no new information!")
                return RegionCheckResult.Unknown, hrect
            elif hrect.close() == region.close():
                logger.info("Refinement yields no new information!")
                return RegionCheckResult.Unknown, hrect
            logger.info("Refinement successfull: {} to {} (size {} to size {} , new is {}% of old )".format(region, hrect, region.size(), hrect.size(),
                                                                                            format(float(hrect.size() / region.size() * 100), '.4f')))


            return RegionCheckResult.Refined, hrect
        else:
            return RegionCheckResult.Unknown, None