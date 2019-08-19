# import curses
import multiprocess as mp
import nibabel as nib
import numpy as np
import os
import shutil
import sys

from colorama import Cursor, init, Style, Fore
from nibabel import Nifti1Image
from numba import jit
from pathlib import Path
from progressbar import Bar, AdaptiveETA, Percentage, ProgressBar, RotatingMarker, Timer
from sys import stderr

RESET = Style.RESET_ALL


def res(path: Path):
    return str(path.absolute().resolve())


def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)


def log(label, var):
    eprint(f"{label}: {var}")


# https://stackoverflow.com/a/42913743
def is_symmetric(a, rtol=1e-05, atol=1e-08) -> bool:
    return np.allclose(a, a.T, rtol=rtol, atol=atol)


def array_map(array: np.array, f, x):
    it = np.nditer(array, flags=["f_index"], op_flags=["readwrite"])
    while not it.finished:
        i = it.index
        it[0] = f(x[i])
        it.iternext()
    it.close()


def make_cheaty_nii(orig: Nifti1Image, array: np.array) -> Nifti1Image:
    """clone the header and extraneous info from `orig` and data in `array`
    into a new Nifti1Image object, for plotting
    """
    affine = orig.affine
    header = orig.header
    return nib.Nifti1Image(dataobj=array, affine=affine, header=header)


def make_directory(path: Path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            return path
        except Exception as e:
            print(
                f"Error making directory {path}. Another program likely modified it while this script was running.",
                file=sys.stderr,
            )
            print("Original error:", file=sys.stderr)
            raise e
    else:
        return path


def make_parent_directories(path: Path):
    path = path.absolute()
    paths = []
    for folder in path.parents:
        if folder != Path.home():
            paths.append(folder)
        else:
            break
    paths.reverse()

    for path in paths:
        make_directory(path)


def parallel_map(func, data: list, cpus: int or None = None):
    """func: function that takes one parameter
    data: the array of values that func will take
    """
    result = None
    if cpus is None:
        with mp.Pool(
            mp.cpu_count()
        ) as pool:  # ensure automatic closing, use available cpus
            result = pool.map(func, data)
    else:
        with mp.Pool(cpus) as pool:  # ensure automatic closing, use available cpus
            result = pool.map(func, data)

    return result


@jit(nopython=True, cache=True, fastmath=True)
def nd_find(arr: np.array, value) -> int:
    for i, val in np.ndenumerate(arr):
        if val == value:
            return i
    return None


# clear all
def tty_clear(COLS, ROWS):
    sys.stdout.write(Cursor.POS(1, 1))
    for row in range(ROWS):
        sys.stdout.write(Cursor.POS(1, row + 1))
        sys.stdout.write(f"{' ' * COLS}")
    sys.stdout.write(Cursor.POS(1, 1))


def write_in_place(message: str, value: str, value_color):
    init()
    COLS, ROWS = shutil.get_terminal_size((80, 40))
    tty_clear(COLS, ROWS)
    full = f"{message}: {value_color}{value}{Style.RESET_ALL}{Cursor.POS(1, 1)}"
    sys.stdout.write(full)
    sys.stdout.flush()


def write_block(messages: [str], border=None):
    init()
    COLS, ROWS = shutil.get_terminal_size((80, 40))
    tty_clear(COLS, ROWS)
    if border is not None and len(str(border[0])) == 1:
        sys.stdout.write(str(border[0]) * COLS)
    for i, message in enumerate(messages):
        if border is not None and len(str(border[0])) == 1:
            full = "{:160}{}".format(message, Cursor.POS(1, i + 3))
        else:
            full = "{:160}{}".format(message, Cursor.POS(1, i + 2))
        sys.stdout.write(full)

    if border is not None and len(str(border[0])) == 1:
        sys.stdout.write("=" * COLS)
        sys.stdout.write(f"{Cursor.POS(0, len(messages)+2)}")
    else:
        sys.stdout.write(f"{Cursor.POS(0, len(messages)+1)}")
    sys.stdout.write(f"{Fore.RESET}")
    sys.stdout.flush()


# def end_curses(screen):
#     curses.nocbreak()
#     screen.keypad(False)
#     curses.echo()
#     curses.endwin()


def setup_progressbar(desc: str, max_count: int, marker=False) -> ProgressBar:
    bar = Bar(marker=RotatingMarker()) if marker else ""
    bar_space = " " if marker else ""
    pbar_widgets = [
        f"{Fore.GREEN}{desc}: {Style.RESET_ALL}",
        f"{Fore.BLUE}",
        Percentage(),
        f" {Style.RESET_ALL}",
        bar,
        bar_space,
        f"|{Fore.WHITE}",
        Timer(),
        f"{Style.RESET_ALL} |",
        f"{Fore.YELLOW}",
        AdaptiveETA(),
        f"{Style.RESET_ALL}|",
    ]
    pbar = ProgressBar(
        widgets=pbar_widgets, maxval=max_count, redirect_stderr=True
    ).start()
    return pbar


@jit(nopython=True, fastmath=True, cache=True)
def slope(x: np.array, y: np.array) -> np.float64:
    x_mean = np.mean(x)
    y_mean = np.mean(y)
    x_dev = x - x_mean
    y_dev = y - y_mean
    cov = np.sum(x_dev * y_dev)
    var = np.sum(x_dev * x_dev)
    if var == 0:
        return 0
    return cov / var


@jit(nopython=True, fastmath=True)
def variance(arr: np.array) -> float:
    """i.e. s^2"""
    n = len(arr)
    scale = 1.0 / (n - 1.0)
    mean = np.mean(arr)
    diffs = arr - mean
    squares = diffs ** 2
    summed = np.sum(squares)
    return scale * summed


@jit(nopython=True, fastmath=True, cache=True)
def intercept(x: np.array, y: np.array, slope: np.float64) -> np.float64:
    return np.mean(y) - slope * np.mean(x)


@jit(nopython=True, fastmath=True, cache=True)
def fast_r(x: np.array, y: np.array) -> np.float64:
    n = len(x)
    num = x * y - n * np.mean(x) * np.mean(y)
    denom = (n - 1) * np.sqrt(variance(x)) * np.sqrt(variance(y))
    if denom == 0:
        return 0
    return num / denom


# termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
