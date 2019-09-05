from zipfile import ZipFile
import numpy as np
import nmrglue as ng
import matplotlib.pyplot as plt
import matplotlib.cm
import io
import django.core.files.images as image
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trydjango.settings")
django.setup()
from NMR.models import Spectrum, Peak
from trydjango.settings import MEDIA_ROOT


# open the zip file and return spectrum data
def read_zip(file):
    with ZipFile(file) as zipfile:
        # get the list of files
        list = zipfile.namelist()
        # storage location
        path = os.path.join(MEDIA_ROOT, "spectrum")
        path = os.path.join(path, list[0])
        # read in data with nmrGlue
        dic, data = ng.bruker.read_pdata(path)
    return dic, data, path


# extract baseline value and return
def processing(spectrum):
    baseline = 0
    dic, data, path = read_zip(spectrum.spectrum_file)

    path = os.path.join(path, "clevels")
    with open(path, "r") as f:
        for line in f.readlines():
            if "##$POSBASE=" in line:
                baseline = float(line.split("##$POSBASE=")[1])
    return dic, data, baseline


# fine the maximum
def find_peak(data, contour, quantity):
    # Initialize parameters
    numOfPeak = quantity
    xDim = data.shape[0]
    yDim = data.shape[1]
    locMaxWin = 2
    xWin = 1
    yWin = 1

    # turn negative value to 0
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if data[i, j] < 0:
                data[i, j] = 0

    countPeak = 0
    volume = []
    for i in range(xDim):
        for j in range(yDim):
            if data[i, j] > contour:
                # Define a region to check local maxima
                row1 = max(0, i - locMaxWin)
                row2 = min(i + locMaxWin + 1, xDim)
                column1 = max(0, j - locMaxWin)
                column2 = min(j + locMaxWin + 1, yDim)
                regionMax = data[row1:row2, column1:column2]

                # Define a region to check the volume
                row3 = max(0, i - xWin)
                row4 = min(i + xWin + 1, xDim)
                column3 = max(0, j - yWin)
                column4 = min(j + yWin + 1, yDim)
                regionVol = data[row3:row4, column3:column4]
                # judge if the centre of th region is the largest
                T1 = (regionMax > data[i, j])

                if (not np.any(T1)) and row2 - 1 - row1 == 2 * locMaxWin and column2 - 1 - column1 == 2 * locMaxWin:
                    volume.append([sum(sum(regionVol)), [i, j]])
                    countPeak += 1
    # sort the volume of local maxima
    volume.sort(key=lambda x: x[0], reverse=True)
    # extract user defined number of maxima
    volume = np.array(volume[:numOfPeak])
    # return indexes of maxima
    extremaLocation = volume[:, 1]
    return extremaLocation


# create two images for a peak and store in the database
def plot(spectrum, x, y, count, contour, data, ucf0, ucf1, xPad, yPad):
    # if ppm value passed
    if isinstance(ucf0, float) and isinstance(ucf1, float):
        ppm_y = ucf0
        ppm_x = ucf1
        # shift the peak location
        y += 55
    else:
        # convert index to ppm
        ppm_y = ucf0.ppm(y)
        ppm_x = ucf1.ppm(x)
    pad = 2
    cmap = matplotlib.cm.Blues_r  # contour map (colors to use for contours)
    xDim = data.shape[1]
    yDim = data.shape[0]
    plt.rcParams.update({'figure.max_open_warning': 0})

    # judge if the fixed box out of range of matrix
    if x - xPad <= 0 or x + xPad >= xDim-1:
        xPad = min(x, abs(xDim - x - 1))
    if y - yPad <= 0 or y + yPad >= yDim-1:
        yPad = min(y, abs(yDim - y - 1))
    # fixed box
    x0, x1, y0, y1 = x - xPad, x + xPad, y - yPad, y + yPad
    # larger box
    X0, X1, Y0, Y1 = large_box(data, y, x, contour)
    if X0 > x0: X0 = x0
    if X1 < x1: X1 = x1
    if Y0 > y0: Y0 = y0
    if Y1 < y1: Y1 = y1

    # slice the data around the peak
    slice_s = data[y0:y1 + 1, x0:x1 + 1]
    slice_l = data[Y0:Y1 + 1, X0:X1 + 1]

    # Plotting contour levels are normalized with local maximum
    cl_s = np.linspace(contour, data[y, x], 10)
    if np.max(slice_s) > data[y, x]:
        cl_s = np.concatenate([np.linspace(contour, data[y, x], 6),
                               np.linspace(data[y, x], np.max(slice_s), 7)[1:]])
    cl_l = np.linspace(contour, np.max(slice_l), 10)

    # create the figures and store to corresponding field
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    etup1 = (x0, x1, y0, y1)
    ax1.contour(slice_s, cl_s, cmap=cmap, extent=etup1)
    ax1.plot(x, y, 'b+')
    figure1 = io.BytesIO()
    fig1.savefig(figure1, format="png")
    content_small = image.ImageFile(figure1)
    s_id = str(spectrum.id) + str(0) + str(count - 1)
    small_name = s_id + ".png"
    plot_instance1 = Peak(spectrum=spectrum, pid=count / 2, id=s_id, x=x, y=y,
                          x0=x0, x1=x1, y0=y0, y1=y1, x_ppm=ppm_x, y_ppm=ppm_y)
    plot_instance1.plot.save(small_name, content_small)
    plot_instance1.save()

    l_id = str(spectrum.id) + str(0) + str(count)
    plot_instance2 = Peak(spectrum=spectrum, pid=count / 2, id=l_id, x=x, y=y,
                          x0=X0, x1=X1, y0=Y0, y1=Y1)

    # if the larger box is smaller than the fixed area
    if X0 > x0 and X1 < x1 and Y0 > y0 and Y1 < y1:
        plot_instance2.plot = plot_instance1.plot
        plot_instance2.save()
    else:
        fig2 = plt.figure()
        ax2 = fig2.add_subplot(111)
        etup2 = (X0 - pad, X1 + pad, Y0 - pad, Y1 + pad)
        ax2.contour(slice_l, cl_l, cmap=cmap, extent=etup2)
        # draw a box around the peak
        ax2.plot([x0, x1, x1, x0, x0], [y0, y0, y1, y1, y0], 'k--')
        figure2 = io.BytesIO()
        fig2.savefig(figure2, format="png")
        content_large = image.ImageFile(figure2)
        large_name = l_id + ".png"
        plot_instance2.plot.save(large_name, content_large)
        plot_instance2.save()
        del fig2
    del fig1
    return plot_instance1


# Not used automated peaks confining program. use fixed area instead
def small_box(data, row, column, contour):
    up, down, left, right = 0, 0, 0, 0
    n = 2
    up_avg, down_avg, left_avg, right_avg = 1, 1, 1, 1
    pre_up_avg = 0
    pre_down_avg = 0
    pre_left_avg = 0
    pre_right_avg = 0
    while row-up-n > 1 and pre_up_avg < up_avg and data[row-up, column] >= contour:
        up +=1
        pre_up_avg = up_avg
        up_avg = np.mean(data[row-up-n:row-up+1, column])
    while row+down+n < data.shape[0] and pre_down_avg < down_avg and data[row+down, column] >= contour:
        down += 1
        pre_down_avg = down_avg
        down_avg = np.mean(data[row+down:row+down+n, column])
    while column-left-n > 1 and pre_left_avg < left_avg and data[row, column-left] >= contour:
        left += 1
        pre_left_avg = left_avg
        left_avg = np.mean(data[row, column-left-n:column-left+1])
    while column+right+n < data.shape[1] and pre_right_avg < right_avg and data[row, column+right] >= contour:
        right += 1
        pre_right_avg = right_avg
        right_avg = np.mean(data[row, column + right:column + right + n])
    return column-left-n, right+column+n, row-up-n, row+down+n


# confine the peak with respect to baseline value
def large_box(data, row, column, contour):
    down, up = row, row
    left, right = column, column
    while up > 0 and data[up, column] > contour:
        up -= 1
    while down < data.shape[0] and data[down, column] > contour:
        down += 1
    while left > 0 and data[row, left] > contour:
        left -= 1
    while right < data.shape[1] and data[row, right] > contour:
        right += 1
    return left, right, up, down

