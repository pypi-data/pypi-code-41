import matplotlib.pyplot as plt
import numpy as np
import engformat.plot as esfp

from eqsig.exceptions import SignalProcessingError

from bwplot import cbox


def plot_acc_sig_as_response_spectrum(acc_sig, legend_off=False, label="", xaxis="frequency", sub_plot=None,
                                      response_type='acceleration', ccbox="auto", xlog=True,
                                      title=False):
    """
    Plot a response spectrum

    :param acc_sig: eqsig.AccSignal Object
    :param legend_off: bool, no legend
    :param label: str, legend label
    :param xaxis: str, 'frequency' or 'time'
    :param sub_plot: matplotlib.pyplot.subplot object
    :param response_type: str, 'acceleration' or 'velocity' or 'displacement'
    :param ccbox: int, cbox number
    :param title: str, plot title
    :return:
    """
    acc_sig.generate_response_spectrum()
    plot_on = 1

    if label == "":
        label = acc_sig.label

    if response_type == 'acceleration':
        response = acc_sig.s_a
        y_label = 'Spectral acceleration [$m/s^2$]'
    elif response_type == 'velocity':
        response = acc_sig.s_v
        y_label = 'Spectral velocity [$m/s$]'
    elif response_type == 'displacement':
        response = acc_sig.s_d
        y_label = 'Spectral displacement [$m$]'
    else:
        raise NotImplementedError
    if sub_plot is None:
        sub_plot = plt.figure().add_subplot(111)
    else:
        plot_on = 0
    if xaxis == "time":
        x_para = acc_sig.response_times
    else:
        x_para = 1 / acc_sig.response_times

    if ccbox == "auto":
            ccbox = len(sub_plot.lines)
    acc_sig.ccbox = ccbox

    sub_plot.plot(x_para, response, label=label, c=cbox(0 + acc_sig.ccbox), lw=0.7)

    if xlog:
        sub_plot.set_xscale('log')

    if xaxis == "period":
        sub_plot.set_xlabel('Time period [s]')
        sub_plot.set_xlim([0, acc_sig.response_times[-1]])
    else:
        sub_plot.set_xlabel('Frequency [Hz]')
    sub_plot.set_ylabel(y_label)

    if title is not False:
        sub_plot.set_title(title)

    if legend_off is False:
        sub_plot.legend(loc='upper left', prop={'size': 8})
    if plot_on == 1:
        plt.show()
    else:
        return sub_plot


def plot_acc_sig_as_time_series(acc_sig, **kwargs):
    """
    Plots a time series

    :param acc_sig: eqsig.AccSignal Object
    :param kwargs:
    :return:
    """
    plot_on = kwargs.get('plot_on', False)
    legend_off = kwargs.get('legend_off', False)
    info_str = kwargs.get('info_str', '')
    motion_type = kwargs.get('motion_type', 'acceleration')

    y_label = kwargs.get('y_label', motion_type.title())
    x_label = kwargs.get('x_label', 'Time [s]')
    y_limits = kwargs.get('y_limits', False)
    label = kwargs.get('label', acc_sig.label)
    sub_plot = kwargs.get('sub_plot', 0)
    window = kwargs.get('window', [0, -1])
    ccbox = kwargs.get('ccbox', "auto")  # else integer

    cut_index = np.array([0, len(acc_sig.values)])
    if window[0] != 0:
        cut_index[0] = int(window[0] / acc_sig.dt)
    if window[1] != -1:
        cut_index[1] = int(window[1] / acc_sig.dt)

    if sub_plot == 0:
        sub_plot = plt.figure().add_subplot(111)
    else:
        plot_on = 0
    if ccbox == "auto":
        ccbox = len(sub_plot.lines)

    if motion_type == "acceleration":
        motion = acc_sig.values[cut_index[0]:cut_index[1]]
        balance = True
    elif motion_type == "velocity":
        motion = acc_sig.velocity[cut_index[0]:cut_index[1]]
        balance = True
    elif motion_type == "displacement":
        motion = acc_sig.displacement[cut_index[0]:cut_index[1]]
        balance = False
    elif motion_type == "custom":
        motion = acc_sig.values[cut_index[0]:cut_index[1]]
        balance = False
    else:
        raise NotImplementedError

    t0 = acc_sig.dt * (np.linspace(0, (len(motion) + 1), (len(motion))) + cut_index[0])
    sub_plot.plot(t0, motion, label=label, c=cbox(0 + ccbox), lw=0.7)
    esfp.time_series(sub_plot, balance=balance)

    if x_label is not False:
        sub_plot.set_xlabel(x_label)
    sub_plot.set_ylabel(y_label)
    if info_str != '':
        stitle = 'Time series \n' + info_str
        sub_plot.set_title(stitle)
    if y_limits is not False:
        sub_plot.set_ylim(y_limits)

    x_limits = [0, t0[-1]]
    sub_plot.set_xlim(x_limits)
    if not legend_off:
        sub_plot.legend(loc='upper right', prop={'size': 8})
    if plot_on == 1:
        plt.show()
    else:
        return sub_plot


def plot_acc_sig_as_avd(acc_sig, sub_plots=None, ccbox=0, **kwargs):
    """
    Plot acceleration, velocity and displacement

    :param acc_sig: eqsig.AccSignal Object
    :return:
    """
    label = kwargs.get('label', acc_sig.label)
    legend_off = kwargs.get('legend_off', False)
    if sub_plots is None:
        big_fig = plt.figure()
        sub_plots = [big_fig.add_subplot(311),
                    big_fig.add_subplot(312),
                    big_fig.add_subplot(313)]
    plot_acc_sig_as_time_series(acc_sig, ccbox=ccbox, sub_plot=sub_plots[0], label=label, legend_off=True)
    plot_acc_sig_as_time_series(acc_sig, ccbox=ccbox, sub_plot=sub_plots[1], motion_type="velocity", legend_off=True)
    plot_acc_sig_as_time_series(acc_sig, ccbox=ccbox, sub_plot=sub_plots[2], motion_type="displacement", legend_off=True)

    if not legend_off:
        sub_plots[0].legend()
    return sub_plots


def plot_acc_sig_as_fa_spectrum(acc_sig, **kwargs):
    """
    Plots the Fourier amplitude spectrum

    :param acc_sig: eqsig.AccSignal Object
    :param kwargs:
    :return:
    """
    plot_on = kwargs.get('plot_on', False)
    legend_off = kwargs.get('legend_off', False)
    smooth = kwargs.get('smooth', False)

    info_str = kwargs.get('info_str', '')

    label = kwargs.get('label', acc_sig.label)

    log_off = kwargs.get('log_off', False)
    title = kwargs.get('title', 'Fourier amplitude acceleration spectrums \n' + info_str)

    band = kwargs.get('band', 40)
    sub_plot = kwargs.get('sub_plot', 0)
    ccbox = kwargs.get('ccbox', 'auto')


    if smooth is False:
        spectrum = abs(acc_sig.fa_spectrum)
        frequencies = acc_sig.fa_frequencies

    else:

        acc_sig.generate_smooth_fa_spectrum(band=band)
        spectrum = abs(acc_sig.smooth_fa_spectrum)
        frequencies = acc_sig.smooth_fa_frequencies


    if sub_plot == 0:
        sub_plot = plt.figure().add_subplot(111)
    else:
        plot_on = 0
    if ccbox == "auto":
        ccbox = len(sub_plot.lines)
    acc_sig.ccbox = ccbox

    sub_plot.plot(frequencies, spectrum, label=label, c=cbox(ccbox), lw=0.7)

    sub_plot.set_xscale('log')
    if log_off is not True:
        sub_plot.set_yscale('log')
    sub_plot.set_xlabel('Frequency [Hz]')
    sub_plot.set_ylabel('Fourier Amplitude [m/s2]')

    if title is not False:
        sub_plot.set_title(title)
    if legend_off is False:
        sub_plot.legend(loc='upper left', prop={'size': 8})
    if plot_on == 1:
        plt.show()
    else:
        return sub_plot


def plot_acc_sig_as_transfer_function(base_acc_sig, acc_sigs, **kwargs):
    """
    Plots the transfer function between the base values and a list of other motions

    :param base_acc_sig: eqsig.AccSignal object
    :param acc_sigs: A list of eqsig.AccSignal objects
    :param kwargs:
    :return:
    """
    plot_on = kwargs.get('plot_on', False)
    legend_off = kwargs.get('legend_off', False)
    smooth = kwargs.get('smooth', False)
    info_str = kwargs.get('info_str', '')
    base_label = kwargs.get('label', base_acc_sig.label)
    log_off = kwargs.get('log_off', False)
    title = kwargs.get('title', 'Transfer function \n' + info_str)
    band = kwargs.get('band', 40)
    sub_plot = kwargs.get('sub_plot', 0)
    ccbox = kwargs.get('ccbox', 'auto')

    if smooth is False:
        base_spectrum = abs(base_acc_sig.fa_spectrum)
        base_frequencies = base_acc_sig.fa_frequencies
    else:
        base_acc_sig.generate_smooth_fa_spectrum(band=band)
        base_spectrum = abs(base_acc_sig.smooth_fa_spectrum)
        base_frequencies = base_acc_sig.smooth_fa_frequencies

    if sub_plot == 0:
        sub_plot = plt.figure().add_subplot(111)
    else:
        plot_on = 0
    if ccbox == "auto":
        ccbox = len(sub_plot.lines)

    for rec in acc_sigs:
        if smooth is False:
            if rec.dt != base_acc_sig.dt or len(rec.values) != len(base_acc_sig.values):
                raise SignalProcessingError("Motion lengths and timestep do not match. "
                                            "Cannot build non-smooth spectrum")
            spectrum = abs(rec.fa_spectrum)
        else:
            rec.reset_smooth_spectrum(freq_range=base_acc_sig.freq_range)
            rec.generate_smooth_fa_spectrum(band=band)
            spectrum = abs(rec.smooth_fa_spectrum)

        sub_plot.plot(base_frequencies, spectrum / base_spectrum, label=rec.label, c=cbox(ccbox), lw=0.7)

    sub_plot.set_xscale('log')
    if log_off is not True:
        sub_plot.set_yscale('log')
    sub_plot.set_xlabel('Frequency [Hz]')
    sub_plot.set_ylabel('Transfer function from %s' % base_label)

    if title is not False:
        sub_plot.set_title(title)
    if legend_off is False:
        sub_plot.legend(loc='upper left', prop={'size': 8})
    if plot_on == 1:
        plt.show()
    else:
        return sub_plot