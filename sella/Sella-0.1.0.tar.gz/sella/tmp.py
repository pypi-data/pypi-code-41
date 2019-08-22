from sella.aseopt import Sella

calc = Gaussian(...)
myatoms.calc = calc

# everything after 'dxL' is optional
dyn = Sella(atoms, trajectory='test.traj', dxL=1e-4, r_trust=5e-4,
            inc_factr=1.1, dec_factr=0.9, dec_ratio=5.0, inc_ratio=1.01,
            order=1, eig=True)

for converged in dyn.irun(fmax=0., steps=3000):
    x = atoms.get_positions()
    f = atoms.get_forces()

    # the Hessian matrix
    H = dyn.mm.H

    # its eigenvalues excluding translation/rotation
    lams = dyn.mm.lams

    # the corresponding eigenvectors
    vecs = dyn.mm.vecs
