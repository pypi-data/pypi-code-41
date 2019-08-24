"""This package includes modules for standard Hamiltonian MCMC sampling
and for some analyses of the posterior distribution
defined by an array of (possibly Hamiltonian-generated) samples.

*** Version history:

New in v 1.1.0, 2019-08-23??:
2019-08-24, HamiltonianSampler objects have separate random-number generator,
    Require Generator class from numpy.random v 1.17

2019-07-xx, ******* safer safe_sample, allow increasing epsilon ??? ****

Version 1.0.5, 2018-09-13, minor cleanup, fixes

Version 1.0.3, 2018-08-15, first published version
"""
__name__ = 'samppy'
__version__ = '1.1.0'
__all__ = ['hamiltonian_sampler', 'credibility', 'sample_entropy']

