"""A wrapper for the GibbeEnergyPredictor in component-contribution."""
# The MIT License (MIT)
#
# Copyright (c) 2013 Weizmann Institute of Science
# Copyright (c) 2018 Institute for Molecular Systems Biology,
# ETH Zurich
# Copyright (c) 2018 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from typing import Dict, List, Tuple

import numpy as np
from component_contribution import GibbsEnergyPredictor

from . import (
    FARADAY,
    Q_,
    R,
    ccache,
    default_I,
    default_pH,
    default_pMg,
    default_T,
    ureg,
)
from .phased_reaction import PhasedReaction


class ComponentContribution(object):
    """A wrapper class for GibbsEnergyPredictor.

    Also holds default conditions for compounds in the different phases.
    """

    predictor = GibbsEnergyPredictor(ccache)

    @ureg.check(None, None, None, "[concentration]", "[temperature]")
    def __init__(
        self,
        p_h: Q_ = default_pH,
        p_mg: Q_ = default_pMg,
        ionic_strength: Q_ = default_I,
        temperature: Q_ = default_T,
    ) -> object:
        """Create a ComponentContribution object.

        :param p_h:
        :param p_mg:
        :param ionic_strength:
        :param temperature:
        """
        self.p_h = p_h
        self.ionic_strength = ionic_strength
        self.p_mg = p_mg
        self.temperature = temperature

    @property
    def RT(self) -> Q_:
        """Get the value of RT."""
        return R * self.temperature

    @staticmethod
    def standard_dg(reaction: PhasedReaction) -> ureg.Measurement:
        """Calculate the chemical reaction energies of a reaction.

        :param reaction: the input Reaction object
        :return: a tuple of the dG0 in kJ/mol and standard error. to
        calculate the confidence interval, use the range -1.96 to 1.96 times
        this value
        """
        residual_reaction, stored_dg = reaction.separate_stored_dg()

        standard_dg = ComponentContribution.predictor.standard_dg(
            residual_reaction
        )

        return standard_dg + stored_dg

    @staticmethod
    def standard_dg_multi(
        reactions: List[PhasedReaction]
    ) -> Tuple[np.array, np.array]:
        """Calculate the chemical reaction energies of a list of reactions.

        Using the major microspecies of each of the reactants.

        :return: a tuple with the CC estimation of the major microspecies'
        standard formation energy, and the uncertainty matrix.
        """
        rxn_dg_pairs = map(lambda r: r.separate_stored_dg(), reactions)
        residual_reactions, stored_dg = zip(*rxn_dg_pairs)
        stored_dg = np.array(stored_dg)

        standard_dg, dg_sigma = ComponentContribution.predictor.standard_dg_multi(  # noqa
            residual_reactions
        )
        return standard_dg + stored_dg, dg_sigma

    def standard_dg_prime(self, reaction: PhasedReaction) -> ureg.Measurement:
        """Calculate the transformed reaction energies of a reaction.

        :param reaction: the input Reaction object
        :return: a tuple of the dG0_prime in kJ/mol and standard error. to
        calculate the confidence interval, use the range -1.96 to 1.96 times
        this value
        """
        residual_reaction, stored_dg_prime = reaction.separate_stored_dg_prime(
            p_h=self.p_h,
            ionic_strength=self.ionic_strength,
            temperature=self.temperature,
        )

        standard_dg_prime = ComponentContribution.predictor.standard_dg_prime(  # noqa
            residual_reaction,
            p_h=self.p_h,
            ionic_strength=self.ionic_strength,
            temperature=self.temperature,
        )

        return standard_dg_prime + stored_dg_prime

    def dg_prime(self, reaction: PhasedReaction) -> ureg.Measurement:
        """Calculate the dG'0 of a single reaction.

        :param reaction: an object of type Reaction
        :return: a tuple of (dG_r_prime, dG_uncertainty) where dG_r_prime is
        the estimated Gibbs free energy of reaction and dG_uncertainty is the
        standard deviation of estimation. Multiply it by 1.96 to get a 95%
        confidence interval (which is the value shown on eQuilibrator).
        """
        return (
            self.standard_dg_prime(reaction)
            + self.RT * reaction.dg_correction()
        )

    def standard_dg_prime_multi(
        self, reactions: List[PhasedReaction]
    ) -> Tuple[np.array, np.array]:
        """Calculate the transformed reaction energies of a list of reactions.

        :return: a tuple of two arrays. the first is a 1D NumPy array
        containing the CC estimates for the reactions' transformed dG0
        the second is a 2D numpy array containing the covariance matrix
        of the standard errors of the estimates. one can use the eigenvectors
        of the matrix to define a confidence high-dimensional space, or use
        U as the covariance of a Gaussian used for sampling
        (where dG0_cc is the mean of that Gaussian).
        """
        rxn_dg_pairs = map(
            lambda r: r.separate_stored_dg_prime(
                p_h=self.p_h,
                ionic_strength=self.ionic_strength,
                temperature=self.temperature,
            ),
            reactions,
        )
        residual_reactions, stored_dg_primes = zip(*rxn_dg_pairs)
        stored_dg_primes = np.array(stored_dg_primes)

        standard_dg_prime, dg_sigma = ComponentContribution.predictor.standard_dg_prime_multi(  # noqa
            residual_reactions,
            p_h=self.p_h,
            ionic_strength=self.ionic_strength,
            temperature=self.temperature,
        )
        return standard_dg_prime + stored_dg_primes, dg_sigma

    def physiological_dg_prime(
        self, reaction: PhasedReaction
    ) -> ureg.Measurement:
        """Calculate the dG'm of a single reaction.

        Assume all aqueous reactants are at 1 mM, gas reactants at 1 mbar and
        the rest at their standard concentration.

        :param reaction: an object of type PhasedReaction
        :return: a tuple (dG_r_prime, dG_uncertainty) where dG_r_prime is
        the estimated Gibbs free energy of reaction and dG_uncertainty is the
        standard deviation of estimation. Multiply it by 1.96 to get a 95%
        confidence interval (which is the value shown on eQuilibrator).
        """
        return (
            self.standard_dg_prime(reaction)
            + self.RT * reaction.physiological_dg_correction()
        )

    def ln_reversibility_index(
        self, reaction: PhasedReaction
    ) -> ureg.Measurement:
        """Calculate the reversibility index (ln Gamma) of a single reaction.

        :return: ln_RI - The reversibility index (in natural log scale).
        """
        physiological_dg_prime = self.physiological_dg_prime(reaction)

        abs_sum_coeff = reaction._sum_absolute_coefficients()
        if abs_sum_coeff == 0:
            return np.inf
        ln_RI = (2.0 / abs_sum_coeff) * physiological_dg_prime / self.RT
        return ln_RI

    def standard_e_prime(self, reaction: PhasedReaction) -> ureg.Measurement:
        """Calculate the E'0 of a single half-reaction.

        :param reaction: a PhasedReaction object
        :return: a tuple (E0_prime, E0_uncertainty) where E0_prime is
        the estimated standard electrostatic potential of reaction and
        E0_uncertainty is the standard deviation of estimation. Multiply it
        by 1.96 to get a 95% confidence interval (which is the value shown on
        eQuilibrator).
        """
        n_e = reaction.check_half_reaction_balancing()
        if n_e is None:
            raise ValueError("reaction is not chemically balanced")
        if n_e == 0:
            raise ValueError(
                "this is not a half-reaction, " "electrons are balanced"
            )
        return -self.standard_dg_prime(reaction) / (n_e * FARADAY)

    def physiological_e_prime(
        self, reaction: PhasedReaction
    ) -> ureg.Measurement:
        """Calculate the E'0 of a single half-reaction.

        :param reaction: a PhasedReaction object
        :return: a tuple (E0_prime, E0_uncertainty) where E0_prime is
        the estimated standard electrostatic potential of reaction and
        E0_uncertainty is the standard deviation of estimation. Multiply it
        by 1.96 to get a 95% confidence interval (which is the value shown on
        eQuilibrator).
        """
        n_e = reaction.check_half_reaction_balancing()
        if n_e is None:
            raise ValueError("reaction is not chemically balanced")
        if n_e == 0:
            raise ValueError(
                "this is not a half-reaction, " "electrons are balanced"
            )
        return -self.physiological_dg_prime(reaction) / (n_e * FARADAY)

    def e_prime(self, reaction: PhasedReaction) -> ureg.Measurement:
        """Calculate the E'0 of a single half-reaction.

        :param reaction: a PhasedReaction object
        :return: a tuple (E0_prime, E0_uncertainty) where E0_prime is
        the estimated standard electrostatic potential of reaction and
        E0_uncertainty is the standard deviation of estimation. Multiply it
        by 1.96 to get a 95% confidence interval (which is the value shown on
        eQuilibrator).
        """
        n_e = reaction.check_half_reaction_balancing()
        if n_e is None:
            raise ValueError("reaction is not chemically balanced")
        if n_e == 0:
            raise ValueError(
                "this is not a half-reaction, " "electrons are balanced"
            )
        return -self.dg_prime(reaction) / (n_e * FARADAY)

    def dg_analysis(self, reaction: PhasedReaction) -> List[Dict[str, object]]:
        """Get the analysis of the component contribution estimation process.

        :param reaction: a PhasedReaction object.
        :return: the analysis results as a list of dictionaries
        """
        return ComponentContribution.predictor.get_dg_analysis(reaction)

    def is_using_group_contribution(self, reaction: PhasedReaction) -> bool:
        """Check whether group contribution is needed to get this reactions' dG.

        :param reaction: a PhasedReaction object.
        :return: true iff group contribution is needed
        """
        return ComponentContribution.predictor.is_using_group_contribution(
            reaction
        )

    @ureg.check(None, None, None, None, "[length]**2 * [mass] / [time]**2")
    def multicompartmental_standard_dg_prime(
        self,
        reaction: PhasedReaction,
        nH: int,
        charge: int,
        delta_p_h: ureg.Measurement,
        delta_phi: ureg.Measurement,
    ) -> ureg.Measurement:
        """Calculate the transformed reaction energies of a
        multi-compartmental reaction.

        Based on the equations from
        Harandsdottir et al. 2012 (https://doi.org/10.1016/j.bpj.2012.02.032)

        :param reaction:
        :param nH: the number of hydrogens being transported
        :param charge: the net charge being transported
        :param delta_p_h: the difference in pH between the two sides
        :param delta_phi: the difference in electro-static potential between
        the two sides
        :return: the transport reaction Gibbs free energy change
        """

        dg = self.standard_dg_prime(reaction)
        dg -= nH * self.RT * np.log(10.0) * delta_p_h
        dg -= FARADAY * charge * delta_phi
        return dg
