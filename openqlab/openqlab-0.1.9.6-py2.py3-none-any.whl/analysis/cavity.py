"""Automatically calculate cavity parameters with data taken from an oscilloscope."""

from typing import Optional, Tuple, List
import logging as log
from pandas import Series
from scipy.signal import find_peaks, peak_widths
import numpy as np
import matplotlib.pyplot as plt


def modematching(data: Series,  # pylint: disable=invalid-name, too-many-arguments
                 plot: bool = False,
                 U_max: Optional[float] = None,
                 offset: Optional[float] = None,
                 rel_prominence: float = .02,
                 without_main_peaks: bool = False,
                 ) -> float:
    """Calculate the mode matching.

    It assumes a cavity scan bounded by two peaks of the main mode.
    The method looks for the smaller peaks where the detection threshold
    can be adjusted with :obj:`rel_prominence`.

    Offset
        The default method to find out the offset is by calculating the mean value.
        If you have measured it more precisely, use the parameter :obj:`offset`.

    Improve precision
        To get a better resolution for small peaks there is an option to take data
        with a clipped main mode. Use the parameter :obj:`U_max` to manually set
        the measured maximum value.

    Parameters
    ----------

    data : Series
        Measured data (just one column).
    plot : bool
        Make a plot to see, if the correct peaks where detected.
    U_max : Optional[float]
        U_max is the parameter to set the peak voltage of the clipped main peak.
    rel_prominence : float
        rel_prominence is the parameter to adjust the threshold for the detection
        of small peaks.
    without_main_peaks : bool
        Takes all peaks as minor peaks, if the main peaks are clipped.
        This requires the parameter :obj:`U_max` to be set.

    Returns
    -------

    float
        Calculated mode matching value.
    """
    if len(data.shape) != 1:
        raise ValueError('The DataFrame should only contain one single column.')
    if without_main_peaks and not U_max:
        raise ValueError('without_main_peaks can not be used without U_max.')

    data = data.dropna()

    # Adjust offset
    if offset is None:
        offset = np.median(data)
    data -= offset

    # Make peaks positive if necessary
    _adjust_peak_sign(data)

    # Find highest value
    if U_max is None:
        U_max = np.max(data)
    else:
        U_max = abs(U_max - offset)

    peaks, main_mode = _find_peaks(data, rel_prominence, U_max)

    if not without_main_peaks:
        if len(main_mode) != 2:
            raise ValueError('The main mode must occur exactly two times for the algorithm to work,'
                             f' but it found {len(main_mode)} main modes.')

    # Main peak voltage
    log.info(f'U_max: {U_max}')
    # Sum of all different modes (excluding 2nd main mode)
    if without_main_peaks:
        U_sum = sum(data.iloc[peaks], U_max)  # pylint: disable=invalid-name
    else:
        U_sum = sum(data.iloc[peaks[main_mode[0]+1:main_mode[1]]], U_max)  # pylint: disable=invalid-name
    # This version with U_max makes it possible to manually
    # include a clipped value for the main peak
    log.info(f'U_sum: {U_sum}')

    # Mode matching
    mode_matching = U_max / U_sum

    # Plotting
    if plot:
        _main_plot(data, peaks=peaks, main_peaks=peaks[main_mode])

        if not without_main_peaks:
            index_first, index_last = peaks[main_mode]
            plt.axvline(x=data.index[index_first], color='gray')
            plt.axvline(x=data.index[index_last], color='gray')
            plt.axvspan(data.index[0], data.index[index_first], color='gray', alpha=0.5)
            plt.axvspan(data.index[index_last], data.index[-1], color='gray', alpha=0.5)

    print(f'Mode matching: {round(mode_matching*100, 2)}%')

    return mode_matching


def _main_plot(data: Series,
               peaks: Optional[np.ndarray] = None,
               main_peaks: Optional[np.ndarray] = None):
    axes = data.plot()
    axes.set_xlim(data.index[0], data.index[-1])
    if peaks is not None:
        data.iloc[peaks].plot(style='.')
    if main_peaks is not None:
        data.iloc[main_peaks].plot(style='o')


def _find_peaks(data: Series,
                rel_prominence: float,
                max_value: Optional[float] = None
                ) -> Tuple[np.ndarray, np.ndarray]:
    if max_value is None:
        max_value = np.max(data)

    # Find peaks
    peaks, peak_dict = find_peaks(data, prominence=max_value*rel_prominence)
    # Find occurences of the main mode.
    main_mode = np.where(peak_dict['prominences'] >= np.max(data)*.9)[0]

    return peaks, main_mode


def finesse(data: Series, plot: bool = False) -> List[float]:
    """Finesse calculation using a cavity scan.

    Parameters
    ----------

    data : Series
        data is the amplitude column with two main modes.
    plot : bool
        plot is giving out a plot to make shure the algorithm has found the correct points.

    Returns
    -------

    list(float)
        Calculated finesse for both peaks.
    """
    if len(data.shape) != 1:
        raise ValueError('The DataFrame should only contain one single column.')
    data = data.dropna()
    _adjust_peak_sign(data)

    peaks, main_mode = _find_peaks(data, .9)
    result = _calculate_finesse(data, peaks, main_mode, plot)
    print(f'Finesse first peak: {round(result[0], 2)}, second peak: {round(result[1], 2)}')
    return result


def _calculate_finesse(data: Series,
                       peaks: np.ndarray,
                       main_mode: np.ndarray,
                       plot: bool = False
                       ) -> List[float]:
    peak_data = peak_widths(data, peaks)
    peak_fwhm = peak_data[0]
    peaks_left = peak_data[2]
    peaks_right = peak_data[3]
    main_width = peak_fwhm[main_mode]
    fsr = peaks[main_mode[1]] - peaks[main_mode[0]]

    if plot:
        _main_plot(data, main_peaks=peaks[main_mode])
        for x in np.concatenate([peaks_left[main_mode], peaks_right[main_mode]]):
            plt.axvline(x=data.index[int(x)], ls=':', color='green')

    return [fsr / main_width[0], fsr / main_width[1]]


def _adjust_peak_sign(data: Series):
    minimum = np.min(data)
    maximum = np.max(data)

    if abs(minimum) > abs(maximum):
        data *= -1
