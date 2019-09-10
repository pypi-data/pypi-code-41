import numpy as np
from scipy.stats import norm

from .LoadComponent import LoadComponent

# ignore numpy errors
np.seterr(divide='ignore', invalid='ignore')


class Load(LoadComponent):
    """Load module.

    Parameters
    ----------
    data : dict or ndarray
        Dataset. Pass a dict with 'load' as the key for the hourly load demand
        [kW] for one year. An ndarray can be passed as well.

    Other Parameters
    ----------------
    num_case : int
        Number of scenarios to simultaneously simulate. This is set by the
        Control module.

    """

    def __init__(self, data, **kwargs):
        """Initializes the base class."""

        # initialize component
        super().__init__(
            data, 0.0, 0.0, 0.0, 0.0,
            None, None, 'Load', '#666666',
            20.0, 0.0, False, False, True, False, **kwargs
        )

        # initialize dataset
        self.pow_ld = 0

        # update initialized parameters if essential data is complete
        self._update_init()

    def load_derive(self):
        """Derives energy parameters from dataset.

        Returns
        -------
        approx_powmax : ndarray
            Approximate maximum power [kW] in the load.
        approx_enrtot : ndarray
            Approximate total energy [kWh] in the load.

        Notes
        -----
        This function can be modified by the user.

        """
        # extract dataset
        if isinstance(self.data, dict):  # pass dict

            # custom timesteps
            if isinstance(self.data['load'], tuple):
                ld_data = self.data['load'][0]
                dt = self.data['load'][1]
                enr_tot = np.sum(ld_data)*8760/ld_data.size
                ld_peak = np.max(ld_data)

            # default timesteps
            else:
                enr_tot = np.sum(self.data['load'])
                ld_peak = np.max(self.data['load'])

        elif isinstance(self.data, tuple):  # pass ndarray
            ld_data = self.data[0]
            dt = self.data[1]
            enr_tot = np.sum(ld_data)*8760/ld_data.size
            ld_peak = np.max(ld_data)

        elif isinstance(self.data, np.ndarray):  # pass ndarray
                enr_tot = np.sum(self.data)
                ld_peak = np.max(self.data)

        return (ld_peak, enr_tot)

    def get_pow(self, n):
        """Returns the power output [kW] at the specified time [h].

        Parameters
        ----------
        n : int
            Time in the simulation.

        Returns
        -------
        pow : ndarray
            Power [kW] at the current timestep.

        Notes
        -----
        This function can be modified by the user.

        """
        return self.pow_ld[n]*np.ones(self.num_case)

    def update_init(self):
        """Initalize other parameters for the component."""

        # extract dataset
        self.pow_ld = self._data_proc('load', True)
