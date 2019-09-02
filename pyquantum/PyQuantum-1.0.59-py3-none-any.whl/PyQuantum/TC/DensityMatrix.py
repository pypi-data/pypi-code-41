# -------------------------------------------------------------------------------------------------
from PyQuantum.TC.WaveFunction import WaveFunction
# from .WaveFunction import WaveFunction
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Matrix import *
# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
import pandas as pd
# -------------------------------------------------------------------------------------------------


# -------------------------------------------------------------------------------------------------
class DensityMatrix(Matrix):

    # ---------------------------------------------------------------------------------------------
    def __init__(self, wf):
        Assert(isinstance(wf, WaveFunction), "wf is not WaveFunction", cf())

        super(DensityMatrix, self).__init__(
            m=wf.m, n=wf.m, dtype=np.complex128)

        wf_data = wf.data

        ro_data = wf_data.dot(wf_data.getH())

        Assert(np.shape(ro_data) == (self.m, self.n), "size mismatch", cf())

        self.data = np.matrix(ro_data, dtype=np.complex128)

        self.states = wf.states
        self.size = np.shape(self.data)[0]
    # ---------------------------------------------------------------------------------------------

    def iprint(self):
        df = pd.DataFrame()

        for i in range(self.size):
            for j in range(self.size):
                df.loc[i, j] = self.data[i, j]

        # df.index = df.columns = self.states_str
        df.index = df.columns = [str(v) for v in self.states.values()]

        self.df = df
# -------------------------------------------------------------------------------------------------
