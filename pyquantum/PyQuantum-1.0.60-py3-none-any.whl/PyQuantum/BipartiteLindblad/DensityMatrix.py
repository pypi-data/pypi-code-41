# -------------------------------------------------------------------------------------------------
from PyQuantum.BipartiteLindblad.WaveFunction import WaveFunction
# -------------------------------------------------------------------------------------------------
# Common
from PyQuantum.Common.Matrix import *
# -------------------------------------------------------------------------------------------------
# scientific
import numpy as np
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
    # ---------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------
