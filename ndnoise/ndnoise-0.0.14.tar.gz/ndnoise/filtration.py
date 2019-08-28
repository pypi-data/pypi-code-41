# -*- coding: utf-8 -*-
"""
author: Miroslav Jirik
"""

import logging
logger = logging.getLogger(__name__)
import numpy as np

import scipy
# from scipy.signal import butter, lfilter, freqz
import scipy.signal
import matplotlib.pyplot as plt


def butter_bandpass_1d(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = scipy.signal.butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter_1d(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass_1d(lowcut, highcut, fs, order=order)
    y = scipy.signal.lfilter(b, a, data)
    return y

def butter_bandpass_freq_filter_1d(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass_1d(lowcut, highcut, fs, order=order)
    dataf = np.fft.fft(data)
    # w, h = freqz(b, a, worN=len(dataf), whole=True)
    w, h = scipy.signal.freqz(b, a, worN=len(dataf), whole=True)
    plt.figure(3)
    plt.subplot(211)
    nyq = (fs * 0.5 / np.pi)

    plt.plot(w*nyq, abs(h))
    # filtered_spectrum = dataf * np.real(h)
    # filtered_spectrum = dataf * np.abs(h)
    filtered_spectrum = dataf * h
    filtered = np.fft.ifft(filtered_spectrum)
    # plt.subplot(212)
    # plt.plot(abs(dataf), label='data')
    # plt.plot(abs(h), label='filter')
    # plt.legend()
    # plt.show()
    return np.real(filtered)
    # return np.abs(filtered)


def apply_filter_on_abs(shspectrum, filter):
    radii, angle = R2P(shspectrum)
    radii *= filter
    shspectrum = P2R(radii, angle)
    return shspectrum

def apply_filter(shspectrum, filter):
    ab = np.real(shspectrum)
    im = np.imag(shspectrum)
    shspectrum = ab * filter + 1j * im * filter
    # radii, angle = R2P(shspectrum)
    # radii *= filter
    # shspectrum = P2R(radii, angle)
    return shspectrum

def power_filter(shape, e, dist=None):
    # if dist is None:
    #     dist = construct_filter_dist(shape)
    output = np.power(dist, e)
    return output

def lopass_ideal_fft_mask(shape, radius, freqs=None, **kwargs):
    # if dist is None:
    #     dist = construct_filter_dist(shape)
    output = freqs <= radius
    return output

def hipass_ideal_fft_mask(shape, radius, freqs=None, **kwargs):
    # if dist is None:
    #     dist = construct_filter_dist(shape)
    output = freqs > radius
    return output

def bandpass_butter_fft_mask(shape, flow, fhigh, freqs=None, order=2):
    # TODO implement this function

    # digital
    filter_fs = np.max([fc, np.max(freqs)])
    # filter_fs = fc * 2.0
    nyq = 0.5 * filter_fs
    low_digital = 0.5 * fc / (nyq * np.pi)
    # high_digital = 0.5 * highcut / (nyq * np.pi)
    b_digital, a_digital = scipy.signal.butter(order, Wn=low_digital, btype='lowpass', analog=False)
    w_digital, h_digital = scipy.signal.freqz(b_digital, a_digital, worN=(freqs / filter_fs))

def lopass_butter_fft_mask(shape, fc, freqs=None, order=2):
    # digital
    filter_fs = np.max([fc, np.max(freqs)])
    # filter_fs = fc * 2.0
    nyq = 0.5 * filter_fs
    low_digital = 0.5 * fc / (nyq * np.pi)
    # high_digital = 0.5 * highcut / (nyq * np.pi)
    b_digital, a_digital = scipy.signal.butter(order, Wn=low_digital, btype='lowpass', analog=False)
    w_digital, h_digital = scipy.signal.freqz(b_digital, a_digital, worN=(freqs / filter_fs))

    return h_digital

def hipass_butter_fft_mask(shape, fc, freqs=None, order=2):
    # digital
    filter_fs = np.max([fc, np.max(freqs)])
    # filter_fs = fc * 2.0
    nyq = 0.5 * filter_fs
    high_digital = 0.5 * fc / (nyq * np.pi)
    b_digital, a_digital = scipy.signal.butter(order, Wn=high_digital, btype='highpass', analog=False)
    w_digital, h_digital = scipy.signal.freqz(b_digital, a_digital, worN=(freqs / filter_fs))

    return h_digital

def dist_from_center(shape, axis_size=None):
    if axis_size is None:
        axis_size = np.ones(len(shape))
    axis_size = np.asarray(axis_size, dtype=np.float)

    center = (np.asarray(shape) - 1) / 2.0


    xi = []
    for i in range(len(shape)):
        xi.append(range(shape[i]))
    yi = np.meshgrid(*xi, indexing='ij')

    dist = np.zeros(shape)
    for i in range(len(shape)):
        dist += ((yi[i] - center[i]) * axis_size[i]) ** 2
    dist = dist**0.5
    return dist

def fftfreq(shape, spacing=None):
    """
    N dimensional variant of numpy.fft.fftfreq

    :param shape:
    :param spacing: if None it is set to 1. If it is scalar it is used for every axis
    :return:
    """
    input = np.zeros(shape, dtype=np.bool)

    # set first pixel (for general dimension) to one
    # input[np.zeros([len(input.shape), 1], dtype=int).tolist()] = 1
    # shinput = np.fft.fftshift(input)
    # shdist = scipy.ndimage.morphology.distance_transform_edt(shinput, sampling=spacing)
    # dist = np.fft.ifftshift(shdist)

    if np.isscalar(shape):
        shape = [shape]

    if spacing is None:
        spacing = np.ones(len(shape))

    if np.isscalar(spacing):
        spacing = spacing * np.ones(len(shape))

    spacing = np.asarray(spacing, dtype=np.float)

    center = np.ceil((np.asarray(shape) - 1) / 2.0)

    xi = []
    for i in range(len(shape)):
        xi.append(range(shape[i]))
    yi = np.meshgrid(*xi, indexing='ij')

    shdist = np.zeros(shape)
    for i in range(len(shape)):
        shdist += (((yi[i] - center[i]) / (spacing[i] * shape[i]) ) ** 2) # * spacing[i] / shape[i]
    shdist = (shdist**0.5)

    dist = np.fft.ifftshift(shdist)
    return dist



def spectrum_analysis_3d(spectrum, fs=[1, 1, 1]):
    spectrum = np.abs(spectrum)
    voxelsize = 1.0 / np.asarray(fs)
    freqs = fftfreq(spectrum.shape, spacing=voxelsize)

    # along axis
    fr1 = freqs[:,0]
    sp1 = spectrum[:, 0]
    plt.subplot(121)
    plt.plot(fr1, sp1)
    # plt.show()

    # round
    voxelvol = np.prod(voxelsize)
    surface = 4 * np.pi * freqs

    spf = spectrum.flatten()
    freqsf = freqs.flatten()

    unq_freqs = np.unique(freqsf)
    freqs_spect = dict(zip(unq_freqs, [0.0] * len(unq_freqs)))
    for si, fi in zip(spf, freqsf):
        freqs_spect[fi] += si #* voxelvol / (4 * np.pi * fi)


    sp = freqs_spect.values()
    fr = freqs_spect.keys()
    fr_sp = sorted(zip(fr, sp))
    fr, sp = zip(*fr_sp)

    sp = list(sp)
    # sp is density function

    for i in range(1, len(unq_freqs)):
        sp[i] += sp [i - 1]

    correction = voxelvol / (4 * np.pi * (np.asarray(fr)**2 + np.mean(voxelsize)))
    correction = voxelvol / (2 * np.pi * (np.asarray(fr) + np.mean(voxelsize)))

    # sp is now distribution function

    plt.subplot(121)
    plt.suptitle(str(np.max(freqs)))
    plt.plot(fr, sp * correction)
    #plt.show()





def P2R(radii, angles):
    radii = np.asarray(radii)
    angles = np.asarray(angles)
    return radii * np.exp(1j*angles)

def R2P(x):
    return np.abs(x), np.angle(x)

def spectrum_filtration(spectrum, fs=None, exponent=0, freq0=0, freq1=None, filter_type="butter"):
    """
    Filter spectrum based on frequency
    :param spectrum:
    :param exponent:
    :param freq0:
    :param freq1:
    :return:
    """
    log = "spectrum_filtration() - begin"
    logger.debug(log)
    if freq1 < 0:
        freq1 = None

    if freq0 <= 0:
        freq0 = None

    if fs is None:
        fs = np.ones(len(spectrum.shape))


    voxelsize = 1.0 / np.asarray(fs)

    # dist = dist_from_center(spectrum.shape, axis_size=voxelsize)
    freqs = fftfreq(spectrum.shape, spacing=voxelsize)

    # spectrum = apply_filter(spectrum, pfilter)

    filt = get_freq_filter_mask(spectrum.shape, exponent, freq0, freq1, freqs,
                                filter_type
                                )

    log = "spectrum_filtration() - before apply_filter"
    logger.debug(log)
    spectrum = apply_filter(spectrum, filt)
    # spectrum *= filt
    # spectrum = np.fft.ifftshift(shspectrum)
    signal = get_real_ifft(spectrum)
    log = "spectrum_filtration() - end"
    logger.debug(log)

    return signal, filt, spectrum, freqs

def get_real_ifft(spectrum):
    return np.real(np.fft.ifftn(spectrum))

def get_freq_filter_mask(spectrum_shape, exponent, freq_start, freq_stop, freqs, filter_type):
    filter_type = "ideal"

    if filter_type is "ideal":
        lopass_fcn = lopass_ideal_fft_mask
        hipass_fcn = hipass_ideal_fft_mask
    elif filter_type is "butter":
        lopass_fcn = lopass_butter_fft_mask
        hipass_fcn = hipass_butter_fft_mask
    else:
        logger.error("Unknown filter type")

    # shspectrum = np.fft.fftshift(spectrum)
    filt = power_filter(spectrum_shape, exponent, dist=freqs)
    # not sure if the abs is correct
    if freq_start is not None:
        filt *= np.abs(hipass_fcn(spectrum_shape, freq_start, freqs=freqs))

    if freq_stop is not None:
        filt *= np.abs(lopass_fcn(spectrum_shape, freq_stop, freqs=freqs))

    return filt

def show(real_signal, filter=None, spectrum=None, freqs=None, log_view=False):
    import matplotlib.pyplot as plt

    # plt.gray()
    plt.subplot(331)
    plt.imshow(real_signal, cmap="gray")
    plt.colorbar()

    plt.title("signal")

    # shfilter = np.fft.fftshift(filter)
    plt.subplot(332)
    plt.imshow(np.abs(np.fft.fftshift(filter)))
    plt.colorbar()
    plt.title("filter")

    if freqs is not None:
        ax = plt.subplot(333)
        plt.imshow(np.abs(np.fft.fftshift(freqs)))
        plt.colorbar()
        ax.set_title("freqs")

    shspecturm = np.fft.fftshift(spectrum)
    if log_view:
        shspecturm = np.log(shspecturm)


    plt.subplot(334)
    plt.imshow(np.abs(shspecturm))
    plt.colorbar()
    plt.title("abs")

    plt.subplot(335)
    plt.imshow(np.angle(shspecturm))
    plt.colorbar()
    plt.title("angle")

    ax = plt.subplot(337)
    ax.imshow(np.real(shspecturm))
    plt.colorbar()
    ax.set_title("real")

    ax = plt.subplot(338)
    ax.imshow(np.imag(shspecturm))
    plt.colorbar()
    ax.set_title("imag")


    # plt.show()


