import numpy as np


__version__ = '1.0.1'


def approximate_natural_frequency_from_stress(m, a, sigma, ro):
    return m * np.pi / a * np.sqrt(sigma / ro)

def approximate_stress_from_natural_frequency(m, a, omega, ro):
    return (omega * a / (m * np.pi))**2 * ro
