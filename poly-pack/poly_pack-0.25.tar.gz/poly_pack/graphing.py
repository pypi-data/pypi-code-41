import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, SymLogNorm
from .data_processing import *
from .sample import *

def plotSamplesByTemp(temp, samples_by_temps):
    q_list = []
    I_list = []
    for lst in samples_by_temps:
        q0, I0, Eiq0 = reduction(lst[0].tiff, esaxsmask,  0.005, 0.198, lst[0])
        q1, I1, Eiq1 = reduction(lst[1].tiff, esaxsmask,  0.005, 0.198, lst[1])
        q2, I2, Eiq2 = reduction(lst[2].tiff, esaxsmask,  0.005, 0.198, lst[2])
        q3, I3, Eiq3 = reduction(lst[3].tiff, esaxsmask,  0.005, 0.198, lst[3])
        q4, I4, Eiq4 = reduction(lst[-1].tiff, esaxsmask,  0.005, 0.198, lst[-1])
        I0 = I0
        I1 = I1 * find_average_ratio(q0, I0, q1, I1, .065, .07, .075)
        I2 = I2 * find_average_ratio(q0, I0, q1, I1, .065, .07, .075)
        I3 = I3 * find_average_ratio(q0, I0, q1, I1, .065, .07, .075)
        I4 = I4 * find_average_ratio(q0, I0, q1, I1, .065, .07, .075)
        q_list.append([q0,q1,q2,q3,q4])
        I_list.append([I0,I1,I2,I3,I4])
    plt.figure(figsize=(10, 5))
    ax = plt.subplot(121)
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.ylabel("I(q) (a.u.)", fontsize=16)
    plt.xlabel("q (Ang^-1)", fontsize=16)

    plt.ylim(5,10000)
    plt.xlim(0.006, 0.08)

    colors = ["red", "blue", "green", "orange", "yellow"]
    indices = findSamplesByTemp(60)
    multiplier = 1
    for i in indices:
        for k, j in enumerate(q_list[i]):
            plt.loglog(j, I_list[i][k] * multiplier , color = colors[k], lw =1, linestyle = "none", marker = "o")
        plt.text(q_list[i][0][0],I_list[i][0][10] * multiplier,str(samples_by_temps[i][0].temp))
        multiplier = multiplier * 3
    plt.tight_layout()
    plt.show()

def graphAgBeh(sampList):
    name = ""
    for i in sampList:
        for j in i:
            if 'AgBeh' in j.name.upper() and float(j.conf) == 24:
                name = j;
                break;

    AgBehSamples = findSamples(sampList, name)
    plt.figure('AgBeh || Mask ',figsize=(10,3))
    plt.subplot(251)
    plt.imshow(AgBehSamples[0].tiff,vmin=0, vmax=5000)
    plt.subplot(252)
    plt.imshow(AgBehSamples[1].tiff,vmin=0, vmax=50)
    plt.subplot(253)
    plt.imshow(AgBehSamples[2].tiff,vmin=0, vmax=50)
    plt.subplot(254)
    plt.imshow(AgBehSamples[3].tiff,vmin=0, vmax=50)
    plt.subplot(255)
    plt.imshow(AgBehSamples[4].tiff,vmin=0, vmax=50)
    plt.subplot(256)
    plt.imshow(esaxsnobsmask,vmin=0, vmax=1)
    plt.subplot(257)
    plt.imshow(esaxsmask,vmin=0, vmax=1)
    plt.subplot(258)
    plt.imshow(saxsmask,vmin=0, vmax=1)
    plt.subplot(259)
    plt.imshow(maxmask,vmin=0, vmax=1)
    plt.subplot(2,5,10)
    plt.imshow(waxsmask,vmin=0, vmax=1)
    plt.show()

def getIntensity(volumeFraction, sample, neatSample, sampList):
    q, I = stitching(sampList,sample.name)
    _, Ineat = stitching(sample_list,neatSample.name)
    ICorrected = (I/float(sample.thickness)) - (volumeFraction*(Ineat/float(neatSample.thickness)))
    return q, ICorrected

def plotRhsFs(Rhs, Fs, times, name,temps):
    dates_0 = dates.date2num(times)
    plt.figure(figsize=(10, 5))

    ax = plt.subplot(121)
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.title(name + " Rhs", fontsize=22)
    plt.ylabel("Rhs", fontsize=16)
    plt.xlabel("date", fontsize=16)
    plt.plot_date(dates_0, Rhs)

    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:orange'
    ax2.set_ylabel('temps', color=color)  # we already handled the x-label with ax1
    ax2.plot_date(dates_0, temps, color = "orange", ls = "solid")
    ax2.tick_params(axis='y', labelcolor=color)

    ax = plt.subplot(122)
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.title(name + 'Fs', fontsize=22)
    plt.ylabel("Fs", fontsize=16)
    plt.xlabel("date", fontsize=16)
    plt.plot_date(dates_0, Fs)

    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:orange'
    ax2.set_ylabel('temps', color=color)  # we already handled the x-label with ax1
    ax2.plot_date(dates_0, temps, color = "orange", ls = "solid")
    ax2.tick_params(axis='y', labelcolor=color)


    plt.tight_layout()
    plt.show()

def plotRhsFs_ElapsedTime(Rhs, Fs, times, name, temps):
    ts = [t - times[0] for t in times]
    ts = [t.total_seconds()/60 for t in ts]

    plt.figure(figsize=(10, 5))

    ax = plt.subplot(121)
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.title(name + " Rhs", fontsize=22)
    plt.ylabel("I(q) (a.u.)", fontsize=16)
    plt.xlabel("q (Ang^-1)", fontsize=16)
    plt.plot(ts,Rhs , marker = "o", ls = "none")

    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:orange'
    ax2.set_ylabel('temps', color=color)  # we already handled the x-label with ax1
    ax2.plot(ts, temps, color = "orange", ls = "solid", marker = "o")
    ax2.tick_params(axis='y', labelcolor=color)

    ax = plt.subplot(122)
    ax.spines["top"].set_visible(True)
    ax.spines["right"].set_visible(True)
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.title(name + " Fs", fontsize=22)
    plt.ylabel("I(q) (a.u.)", fontsize=16)
    plt.xlabel("q (Ang^-1)", fontsize=16)
    plt.plot(ts, Fs, marker = "o", ls = "none")

    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:orange'
    ax2.set_ylabel('temps', color=color)  # we already handled the x-label with ax1
    ax2.plot(ts, temps, color = "orange", ls = "solid", marker = "o")
    ax2.tick_params(axis='y', labelcolor=color)

    plt.tight_layout()
    plt.show()
