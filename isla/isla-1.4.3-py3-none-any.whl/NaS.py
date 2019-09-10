import os

import numpy as np
import pandas as pd
from scipy.interpolate import InterpolatedUnivariateSpline

from .StorageComponent import StorageComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class NaS(StorageComponent):
    """Sodium sulfur (NaS) battery plant module.

    Parameters
    ----------
    dod_max : float
        Maximum depth of discharge (DOD).
    eff_c : float
        Charging efficiency.
    eff_dc : float
        Discharging efficiency.
    c_rate : float
        C-rate [kW/kWh] of the battery.
    capex : float or callable
        Capital expenses [$/kW(h)]. Depends on size. Can be a callable
        function that returns capital cost starting from year zero to end of
        project lifetime.
    opex_fix : float or callable
        Fixed yearly operating expenses [$/kW(h) yr]. Depends on size. Can be
        a callable function that returns the fixed operating cost starting
        from year zero to end of project lifetime.
    opex_var : float or callable
        Variable yearly operating expenses [$/kWh yr]. Depends on energy
        produced. Can be a callable function that returns the variable
        operating cost starting from year zero to end of project lifetime.
    opex_use : float or callable
        Variable yearly operating expenses [$/h yr]. Depends on amount of
        usage. Can be a callable function that returns the variable
        operating cost starting from year zero to end of project lifetime.
    life : float
        Lifetime [y] of the component.
    fail_prob : float
        Probability of failure of the component.
    is_fail : bool
        True if failure probabilities should be simulated.

    Other Parameters
    ----------------
    repex : float or callable
        Replacement costs [USD/kW(h)]. Depends on size. Equal to CapEx by
        default. Can be a callable function that returns replacement costs
        starting from year zero to end of project lifetime.
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module.
    size : int
        Size of the component [kW]. This is set by the Control module.
    size_nom : float
        Size [kWh] per battery.
    c_x : ndarray
        The SOC in a set of internal resistance while charging vs SOC data.
    c_y : ndarray
        The internal resistance [ohm] in a set of internal resistance while
        charging vs SOC data.
    dc_x : ndarray
        The SOC in a set of internal resistance while discharging vs SOC data.
    dc_y : ndarray
        The internal resistance [ohm] in a set of internal resistance while
        discharging vs SOC data.
    ocv_x : ndarray
        The DOD in a set of OCV vs DOD data.
    ocv_y : ndarray
        The OCV [V] in a set of OCV vs DOD data.

    """

    def __init__(
        self, dod_max=0.8, eff_c=0.9, eff_dc=0.9, c_rate=0.125,
        capex=500.0, opex_fix=5.0, opex_var=0.0, opex_use=0.0,
        life=10, fail_prob=0.01, is_fail=False, **kwargs
    ):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            None, dod_max, eff_c, eff_dc, c_rate,
            capex, opex_fix, opex_var, opex_use,
            'NaS', '#0000CC', 'NaS SOC', '#FF0000',
            life, fail_prob, is_fail, True, True, False, **kwargs
        )

        # read datasets
        dir = os.path.dirname(__file__)
        na_rintc = pd.read_csv(
            os.path.join(dir, 'na_rintc.csv'), index_col=None
        ).values
        na_rintd = pd.read_csv(
            os.path.join(dir, 'na_rintd.csv'), index_col=None
        ).values

        # adjustable battery plant parameters
        self.size_nom = kwargs.pop('size_nom', 70.5)  # size per batt [kWh]

        # initialize battery plant parameters
        self.num_batt = np.array([])  # number of batteries

        # adjustable electrical parameters
        self.c_x = kwargs.pop('c_x', na_rintc[:, 0])  # SOC
        self.c_y = kwargs.pop('c_y', na_rintc[:, 1])  # R [ohm] charging
        self.dc_x = kwargs.pop('dc_x', na_rintd[:, 0])  # SOC
        self.dc_y = kwargs.pop('dc_y', na_rintd[:, 1])  # R [ohm] discharging
        self.ocv_x = kwargs.pop('ocv_x', np.array([0, 0.56, 1.1]))  # DOD
        self.ocv_y = kwargs.pop('ocv_y', np.array([116, 116, 97.3]))  # OCV

        # derivable electrical parameters
        self.resc_func = InterpolatedUnivariateSpline(
            self.c_x, self.c_y, k=1  # internal res vs SOC (charging)
        )
        self.resdc_func = InterpolatedUnivariateSpline(
            self.dc_x, self.dc_y, k=1  # internal res vs SOC (discharging)
        )
        self.ocv_func = InterpolatedUnivariateSpline(
            self.ocv_x, self.ocv_y, k=1  # OCV vs DOD
        )

        # update initialized parameters if essential data is complete
        self._update_init()

    def get_iv(self, n, pow_eff):
        """Get current and voltage at EMF source.

        Parameters
        ----------
        n : int
            Time in the simulation.
        pow_eff : ndarray
            Power [kW] into the equivalent circuit corrected for efficiency.

        Returns
        -------
        curr : ndarray
            Current [A] into the EMF source.
        volt : ndarray
            Voltage [V] drop in the EMF source.

        Notes
        -----
        This function can be modified by the user. Positive values indicate
        discharging. The EMF source being referred to is the EMF source in the
        equivalent circuit.

        """
        # solve for power per battery
        pow_batt = pow_eff/self.num_batt

        # solve for current when discharging
        a = -self.resdc_func(1-self.soc)
        b = self.ocv
        c = -pow_batt*1e3
        curr_dc = (-b+np.sqrt(np.abs(b**2-4*a*c)))/(2*a)

        # solve for current when charging
        a = -self.resc_func(1-self.soc)
        curr_c = -(-b+np.sqrt(np.abs(b**2-4*a*c)))/(2*a)

        # update current and voltage
        # nan_to_num removes nan values which appear when no power is used
        curr = -curr_c*(pow_batt < 0)+curr_dc*(pow_batt > 0)  # current [A]
        volt = np.nan_to_num(pow_batt*1e3/curr)  # terminal voltage [V]

        return (curr, volt)

    def get_soc(self, n, curr, volt):
        """Get the SOC of the next time step.

        Parameters
        ----------
        n : int
            Time in the simulation.
        curr : ndarray
            Current [A] at the present time step.
        volt : ndarray
            Voltage [V] at the present time step.

        Returns
        -------
        soc : ndarray
            State of charge at the next time step.

        Notes
        -----
        This function can be modified by the user. Positive values indicate
        discharging. At this point, self.curr and self.volt have already been
        updated according to the values given in self._get_iv

        """
        # get change in soc
        delta_soc = curr*self.ocv*self.dt/(self.size_nom*1e3)

        return self.soc-delta_soc

    def get_ocv(self, n, soc):
        """Get the SOC of the next time step.

        Parameters
        ----------
        n : int
            Time in the simulation.
        soc : ndarray
            State of charge at the next time step.

        Returns
        -------
        ocv : ndarray
            Open circuit voltage of the EMF element at the next time step.

        Notes
        -----
        This function can be modified by the user. At this point, self.curr,
        self.volt, and self.soc have already been updated according to the
        values given in self._get_iv and self._get_soc.

        """
        return self.ocv_func(1-self.soc)

    @staticmethod
    def exp_curve(yr, yr_0=2020, **kwargs):
        """Experience curve for NaS.
        Returns the cost [USD/kWh] at the given year

        Parameters
        ----------
        yr : int
            Index of the year.
        yr_0 : int
            Year where index is set to zero.

        """
        # get regression parameters
        a_sat = kwargs.pop('a_sat', 96)
        a_base = kwargs.pop('a_base', 0.21)
        r = kwargs.pop('r', 0.326)
        a = kwargs.pop('a', 476)
        b = kwargs.pop('b', 0.0948)

        # calculate cost [USD/kWh]
        cap = a_sat/(1+(a_sat-a_base)/a_base*np.exp(-r*(yr+(yr_0-2011))))
        cost = a*cap**(-b)

        return cost

    def update_init(self):
        """Updates other parameters once essential parameters are complete."""

        # update battery plant parameters
        self.num_batt = self.size/self.size_nom  # number of batteries
