from abc import abstractmethod

import numpy as np

from .NullComp import NullComp
from .Component import Component
from .LoadComponent import LoadComponent
from .IntermittentComponent import IntermittentComponent
from .StorageComponent import StorageComponent
from .DispatchableComponent import DispatchableComponent
from .SinkComponent import SinkComponent
from .GridComponent import GridComponent
from .SupplementaryComponent import SupplementaryComponent
from .Connector import Connector
from .LoadConnector import LoadConnector
from .IntermittentConnector import IntermittentConnector
from .StorageConnector import StorageConnector
from .DispatchableConnector import DispatchableConnector
from .SinkConnector import SinkConnector
from .GridConnector import GridConnector
from .SupplementaryConnector import SupplementaryConnector
from .StorageComponent import StorageComponent


class Dispatch(object):
    """Base class for dispatch strategies.

    Parameters
    ----------
    comp_list : list of Component
        List of initialized components.
    size : dict
        Sizes [kW] or [kWh] of the components. Use component objects as
        keys and sizes as values.
    spin_res : float
        Spinning reserve.
    tol : float
        Tolerance.

    """

    def __init__(self, comp_list, dt, t_span, size, spin_res, tol=1e-2):
        """Initializes the base class."""

        # store parameters
        self.comp_list = comp_list  # list of components
        self.dt = dt  # length of timestep [h]
        self.t_span = t_span  # length of simulation [h]
        self.size = size  # size
        self.spin_res = spin_res  # spinning reserve
        self.tol = tol  # tolerance

        # make placeholders if component is not present
        # in order: ld, im, st, dp, tk, sk, gd, su
        self.null_list = [NullComp() for i in range(7)]

        # initialize per-class list of components
        cp_list = [[] for i in range(8)]

        # sort components in comp_list into per-class lists
        class_list = [
            LoadComponent, IntermittentComponent, StorageComponent,
            DispatchableComponent, SinkComponent, GridComponent,
            SupplementaryComponent
        ]
        for cp in comp_list:
            for cl, cpl in zip(class_list, cp_list):
                if isinstance(cp, cl):
                    cpl.append(cp)  # append to per-class list
                    break  # proceed to next cp

        # check if at least one required load was given
        if not cp_list[0]:
            raise ValueError('No required load was given.')

        # create connectors
        self.ld = LoadConnector(cp_list[0])
        self.im = IntermittentConnector(cp_list[1])
        self.st = StorageConnector(cp_list[2])
        self.dp = DispatchableConnector(cp_list[3])
        self.sk = SinkConnector(cp_list[4])
        self.gd = GridConnector(cp_list[5])
        self.su = SupplementaryConnector(cp_list[6])
        conn_list = [  # list of connectors
            self.ld, self.im, self.st, self.dp,
            self.sk, self.gd, self.su
        ]

        # determine number of cases to simulate
        num_case = -1  # initialize number of cases to simulate
        for sz in size.values():
            if sz is not None:
                num_new = np.atleast_1d(sz).size  # number of cases to simulate
                if num_new != num_case and num_case != -1:
                    raise ValueError('Size array dimensions do not agree.')
                else:
                    num_case = num_new

        # append NullComp if component is absent
        for cpl, nu in zip(cp_list, self.null_list):
            if not cpl:
                cpl.append(nu)  # append NullComp
                size.update({nu: np.zeros(num_case)})  # size of None

        # initialize connectors
        for cn, cpl in zip(conn_list, cp_list):
            cn._set_num(num_case)  # number of cases to simulate
            cn._set_time(self.dt, self.t_span)  # simulation time
            if cn is not self.ld:
                cp_dict = {cp: size[cp] for cp in cpl if cp in size}
                cn._set_size(cp_dict)  # sizes of components

        # initialize
        self.pow_def = np.zeros(num_case)  # power deficit
        self.num_def = np.zeros(num_case)  # number of deficits
        self.feas = np.ones(num_case, dtype=bool)  # load feasibility
        self.nt = self.t_span/self.dt  # number of simulation points
        self.n = 0  # time increment

    def _step(self):
        """Increments the timestep."""

        # calculate load that needs to be served
        ld_pow = self.ld._get_pow(self.n)
        pow_maxdc_old = self.st.pow_maxdc  # previous max dc of storage

        # simulate for electrical load
        pow_data = self.step(ld_pow)
        im_pow, st_c, st_dc, dp_pow, sk_pow, gd_c, gd_dc = pow_data

        # record energy exchanges
        self.st._rec_pow(st_dc-st_c, self.n)
        self.dp._rec_pow(dp_pow, self.n)
        self.sk._rec_pow(sk_pow, self.n)
        self.gd._rec_pow(gd_dc-gd_c, self.n)

        # calculate power deficit
        pow_miss = (
            ld_pow+st_c*self.st.noise_c+self.gd.pow_ret*self.gd.noise_c
        )-(
            im_pow*self.im.noise+st_dc*self.st.noise +
            dp_pow*self.dp.noise+self.gd.pow*self.gd.noise
        )*(1+self.tol)
        self.pow_def += pow_miss*(pow_miss > 0)  # power deficit
        self.num_def += pow_miss > 0  # number of deficits

        # check if setup is still feasible
        # to check: SOC, sufficed load, NaN values
        val_ld = ld_pow <= (1+self.tol) * (
            im_pow+st_dc+dp_pow+self.gd.pow
        )
        val_sr = ld_pow*(1+self.spin_res) <= (1+self.tol) * (
            im_pow+pow_maxdc_old+self.dp.pow_max+self.gd.pow_max
        )
        val_soc = self.st.soc >= 1-self.st.dod_max
        val_ot = np.logical_not(np.isnan(
            ld_pow+im_pow+st_c+st_dc +
            dp_pow+sk_pow+gd_c+self.gd.pow
        ))
        self.feas = np.logical_and.reduce([
            val_soc, val_ld, val_ot, val_sr, self.feas
        ])

        # increment
        self.n += 1

    @abstractmethod  # implementation required
    def step(self, pow_ld):
        """Dispatch algorithm.

        Parameters
        ----------
        pow_ld : ndarray
            The load that needs to be served.

        Returns
        -------
        ld_pow : ndarray
            Total load demand
        im_pow : ndarray
            Power given by intermittent sources.
        st_c : ndarray
            Charging into energy storage.
        st_dc : ndarray
            Discharging from energy storage.
        dp_pow : ndarray
            Power given by dispatchable sources.
        sk_pow : ndarray
            Power given to load sink.
        gd_c : ndarray
            Power given back to the grid.
        gd_dc : ndarray
            Power drawn from the grid.

        """
        pass
