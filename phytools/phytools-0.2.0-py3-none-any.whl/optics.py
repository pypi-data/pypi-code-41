from . import constants as const


def wl_to_freq(wl):
    """ Convert wavelength (in vacuum) to frequency

    Parameters
    ----------
    wl : float
        Wavelength

    Returns
    -------
    float
        Frequency
    """
    return const.C0/wl


def freq_to_wl(freq):
    """ Convert frequency to wavelength (in vacuum)

    Parameters
    ----------
    freq : float
        Frequency

    Returns
    -------
    float
        Wavelength

    """
    return const.C0/freq


def spectral_width_freq(width_wl, wl0):
    """ Compute spectral frequency width from spectral wavelength width

    Parameters
    ----------
    width_wl : float
        Spectral wavelength width (in m)
    wl0 : float
        Center wavelength (in m)

    Returns
    -------
    float
        Spectral frequency width (in 1/s)

    """
    return width_wl*const.C0/wl0**2


def spectral_width_wl(width_freq, wl0):
    """ Compute spectral wavelength width from spectral frequency width

    Parameters
    ----------
    width_freq : float
        Spectral frequency width (in 1/s)
    wl0 : float
        Center wavelength (in m)

    Returns
    -------
    float
        Spectral wavelength width (in m)

    """
    return wl0**2/const.C0*width_freq


def free_spectral_range(length):
    """ Compute free-spectral range of an optical cavity with given length.

    Parameters
    ----------
    length : float
        Cavity length (in m)

    Returns
    -------
    float
        Free-specral range (in 1/s)
    """
    return const.C0/(2*length)
