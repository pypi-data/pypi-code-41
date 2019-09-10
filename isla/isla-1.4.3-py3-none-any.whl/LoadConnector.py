import numpy as np

from .Connector import Connector

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class LoadConnector(Connector):
    """Base class for load component connector. This is used by the
    Control module to manipulate components simultaneously.

    Parameters
    ----------
    comp_list : list
        List of initialized component objects.

    """

    def __init__(self, comp_list):
        """Initializes the base class.

        """
        # initialize base class
        super().__init__(comp_list)

        # derivable load parameters
        self.approx_powmax = 0  # maximum power [kW]
        self.approx_enrtot = 0  # yearly consumption [kWh]
        for cp in self.comp_list:
            self.approx_powmax += cp.approx_powmax
            self.approx_enrtot += cp.approx_enrtot

    def _get_pow(self, n):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        n : int
            Time [h] in the simulation.

        """
        # calculate generated power
        pow = np.zeros(self.num_case)
        self.noise = 0
        for cp in self.comp_list:
            get_pow = cp._get_pow(n)
            pow += get_pow
            self.noise += cp.noise*get_pow

        # noise
        self.noise = self.noise/pow

        # record power generated [kW]
        self.pow = pow  # instantaneous power [kW]
        self.enr_tot += pow*self.dt  # total energy [kWh]

        return pow
