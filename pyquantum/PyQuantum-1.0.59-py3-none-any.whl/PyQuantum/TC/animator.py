import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import axes3d
from matplotlib import cm

from mpl_toolkits.mplot3d import Axes3D


def make_plot3D(t, ww, w, state):
    fig = plt.figure(figsize=(14, 8))
    fig.subplots_adjust(left=0.00, bottom=0.00, top=1, right=1)

    ww, t = np.meshgrid(ww, t)

    ax = fig.gca(projection='3d')
    ax.plot_wireframe(ww, t, w,  rstride=20, alpha=0.8, color='#777777')
    # ax.plot_surface(ww, t, w, rstride=10, cmap=cm.bone, alpha=0.8, lw=0.1, antialiased=True)
    ax.set_zlabel(r'$Amplitude$', fontsize=18)
    ax.set_ylabel(r'$t,\ мкс$', fontsize=18)
    ax.set_xticks(np.linspace(0, len(state), len(state)))
    ax.set_xticklabels(state)

    plt.show()


def make_plot(x, xmin, xmax, ymin, ymax, data, color='blue', title='title', X=r'$t,\ мкс$', Y=r'$Amplitude$   ', rotation=90):
    # fig = plt.figure(figsize=(12, 8), facecolor="white")
    # fig.subplots_adjust(left=0.08, bottom=0.1, top=0.9, right=0.92)
    # fig.set_dpi(75)

    # plt.plot(x, data**2, linewidth=0.75, antialiased=True,
    #          solid_joinstyle='round', color=color)

    # plt.axis([xmin, xmax, 0, 1])
    # plt.xlim(xmin, xmax)
    # plt.ylim(ymin, ymax)
    # plt.xlabel(X, fontsize=20)
    # plt.ylabel(Y, fontsize=20, rotation=rotation)
    # # plt.xticks(np.arange(xmin, xmax, round((xmax-xmin)/10, 2)))

    # plt.title(title, fontsize=20)
    # plt.grid(True)
    from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

    init_notebook_mode(connected=True)
    iplot([{"x": x, "y": data}])

    plt.show()


def make_plotw(x, xmin, xmax, ymin, ymax, data1, data2, color='blue', title='title', X=r'$t,\ мкс$', Y=r'$Amplitude$   ', rotation=90):
    fig = plt.figure(figsize=(12, 8), facecolor="white")
    fig.subplots_adjust(left=0.08, bottom=0.1, top=0.8, right=0.92)
    fig.set_dpi(75)

    # plt.plot(x, data1**2, linewidth = 0.75, antialiased = True, solid_joinstyle='round', color=color)
    # plt.plot(x, data2**2, linewidth = 0.75, antialiased = True, solid_joinstyle='round', color=color)

    # plt.axis([xmin, xmax, 0, 1])
    # plt.xlim(xmin, xmax)
    # plt.ylim(ymin, ymax)
    # plt.xlabel(X, fontsize=20)
    # plt.ylabel(Y, fontsize=20, rotation = rotation)
    # plt.xticks(np.arange(xmin, xmax, round((xmax-xmin)/10, 2)))

    # plt.title(title, fontsize = 20)
    # plt.grid(True)

    # plt.show()


def make_plotdiff(x, xmin, xmax, ymin, ymax, data, color='blue', title='title', X=r'$t,\ мкс$', Y=r'$Amplitude$   ', rotation=90):
    fig = plt.figure(figsize=(12, 8), facecolor="white")
    fig.subplots_adjust(left=0.08, bottom=0.1, top=0.9, right=0.92)
    fig.set_dpi(75)

    ymax = np.max(data)
    plt.plot(x, data, linewidth=0.75, antialiased=True,
             solid_joinstyle='round', color=color)

    plt.axis([xmin, xmax, 0, 1])
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.xlabel(X, fontsize=20)
    plt.ylabel(Y, fontsize=20, rotation=rotation)
    plt.xticks(np.arange(xmin, xmax, round((xmax-xmin)/10, 2)))

    # plt.rc('text', usetex=True)
    # plt.rc('font', family='serif')
    plt.title(title, fontsize=20)
    plt.grid(True)

    plt.show()


def make_plot2(x, xmin, xmax, ymin, ymax, data1, data2, title='title', X='X', Y='Y'):
    fig = plt.figure(figsize=(12, 8), facecolor="white")
    fig.set_dpi(75)

    plt.plot(x, data1 ** 2, linewidth=0.75, antialiased=True,
             solid_joinstyle='round', color="blue", label="RWA")
    plt.plot(x, data2 ** 2, linewidth=0.75, antialiased=True,
             solid_joinstyle='round', color="red", label="Exact")

    plt.axis([xmin, xmax, 0, 1])
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.xlabel(X, fontsize=20)
    plt.ylabel(Y, fontsize=20)
    plt.xticks(np.arange(xmin, xmax, round((xmax-xmin)/10, 2)))

    plt.title(title, fontsize=20)
    plt.grid(True)
    plt.legend()
    plt.show()


def make_plot2w(x, xmin, xmax, ymin, ymax, data1, data2, init_state, st1, st2, title='title', X='X', Y='Y'):
    fig = plt.figure(figsize=(12, 8), facecolor="white")
    fig.set_dpi(75)

    fig.subplots_adjust(left=0.08, bottom=0.1, top=0.85, right=0.92)

    plt.plot(x, data1 ** 2, linewidth=0.75, antialiased=True,
             solid_joinstyle='round', color="blue", label=st1)
    plt.plot(x, data2 ** 2, linewidth=0.75, antialiased=True,
             solid_joinstyle='round', color="red", label=st2)

    plt.axis([xmin, xmax, 0, 1])
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    plt.xlabel(X, fontsize=20)
    plt.ylabel(Y, fontsize=20)
    plt.xticks(np.arange(xmin, xmax, round((xmax-xmin)/10, 2)))

    plt.title(title, fontsize=20)
    plt.grid(True)
    ll = plt.legend(title=r'$Initial\ state:\ ' + str(init_state) + '$')
    ll.get_title().set_fontsize('20')

    plt.show()
# def make_plot3D(x, xmin, xmax, data, ymin, ymax, state, not_empty, max_limit = 1e-3):
#   #------------------------------------------------------------------------------------------------------------------
#   fig = plt.figure(figsize = (14, 8))
#   fig.subplots_adjust(left=0.00, bottom=0.00, top=1, right=1)

#   ax = fig.gca(projection='3d')
#   #------------------------------------------------------------------------------------------------------------------
#   count = np.shape(data)[1]

#   pos_count = 0
#   pos_state = []
#   #------------------------------------------------------------------------------------------------------------------
#   for i in range(0, count):
#       elem = data[:,i]

#       min = np.min(elem)
#       max = np.max(elem)

#       if ((not not_empty) or (not_empty and max > max_limit)) and (min>=ymin) and (max<=ymax):
#           ax.plot(x, elem, zs=pos_count, zdir='x', label=r'$%s$' %state[i], linewidth = 1, antialiased = True)
#           pos_state.append(state[i])

#           pos_count += 1
#   #------------------------------------------------------------------------------------------------------------------
#   ax.set_xlim3d(0, pos_count)
#   ax.set_ylim3d(xmin, xmax)
#   ax.set_zlim3d(ymin, ymax)

#   ax.set_xticks(np.arange(0, pos_count))
#   ax.set_xticklabels(pos_state)

#   ax.set_ylabel(r'$time$', fontsize=18)
#   ax.set_zlabel(r'$|\lambda|$', fontsize=18)
#   plt.setp(plt.xticks()[1], rotation=90)
#   ax.zaxis.set_rotate_label(False)
#   #------------------------------------------------------------------------------------------------------------------
#   plt.legend(loc='upper left', shadow=True, title="States", fontsize=18)
#   ax.get_legend().get_title().set_fontsize(18)
#   #------------------------------------------------------------------------------------------------------------------
#   plt.show()
