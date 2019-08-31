from __future__ import print_function

import numpy as np
from scipy.constants import mu_0, h, e, pi
from numpy.fft import fft2, ifft2, fftfreq
from collections import namedtuple
import matplotlib.pylab as plt
plt.ion()

from .tem_tools import e_lambda


def landau(shape=(128,)*2, pad_width=0, origin='top', plot=False):
    '''
    Generates an anticlockwise landau pattern.
    
    Parameters
    ----------
    shape : length 2 tuple
        y, x size in pixels.
    pad_width : {None, sequence, array_like, int} 
        If not None, the magnetisation arrays are padded using to np.pad.    
    origin : string in ['top', 'bottom']
        Indicates the direction positive pixel values represent. If 'top', the
        positive, values correspond to increases in y-axis position when plotted
        with (0,0) at the top. If 'bottom', positive pixels represent the movement
        along negative y-axis, when plotted with (0,0) at the top. Note that the
        results are always plotted with origin='top'.
    plot : bool
        If True, the returned data are also plotted.
    
    Returns
    -------
    my, mx : 3-D array
        y- and x- magnetisation in [-1, 1]. 
    
    '''
    
    bottom = origin.lower() == 'bottom'
    
    y, x = np.indices(shape)
    regions = (x>y)[::-1]*1 + (x>y)*1
    
    my = np.zeros(shape, dtype=float)
    my[regions==0] = +1
    my[regions==2] = -1
    mx = (my == 0)*1.0
    mx[:mx.shape[0]//2] *= -1
    
    if pad_width is not None:
        my = np.pad(my, pad_width, mode='constant', constant_values=0)
        mx = np.pad(mx, pad_width, mode='constant', constant_values=0)
    
    if bottom:
        my *= -1
    
    if plot:
        plt.matshow(my)
        plt.title('My')
        plt.matshow(mx)
        plt.title('Mx')
    
    return np.array([my, mx])


def stripes(nstripes=4, h2h=False, shape=(128,)*2, pad_width=0, origin='top', plot=False):
    '''
    Generates a stripe pattern.
    
    Parameters
    ----------
    nstripes : int
        Number of stripes.
    h2h : bool
        If True, stripes are head to head.    
    shape : length 2 tuple
        y, x size in pixels.
    pad_width : {None, sequence, array_like, int} 
        If not None, the magnetisation arrays are padded using to np.pad.    
    origin : string in ['top', 'bottom']
        Indicates the direction positive pixel values represent. If 'top', the
        positive, values correspond to increases in y-axis position when plotted
        with (0,0) at the top. If 'bottom', positive pixels represent the movement
        along negative y-axis, when plotted with (0,0) at the top. Note that the
        results are always plotted with origin='top'.
    plot : bool
        If True, the returned data are also plotted.
    
    Returns
    -------
    my, mx : 3-D array
        y- and x- magnetisation in [-1, 1]. 
    
    Examples
    --------
    Infinitely long antiparallel stripes.
    >>> my, mx = stripes(nstripes=2, shape=(256,128), pad_width=[(0,)*2, (50,)*2], plot=True)
    
    Infinitely long head-to-head stripes (note that only my and mx have swapped below):
    >>> mx, my = stripes(nstripes=2, shape=(256,128), pad_width=[(0,)*2, (50,)*2])
    
    '''
    
    bottom = origin.lower() == 'bottom'
    
    y, x = np.indices(shape)
    regions = x[0] // (shape[1] // nstripes)
    labels = np.unique(regions)

    for i, lab in enumerate(labels):
        inds = np.where(regions == lab)
        odd = i % 2
        if odd:
            factor = +1
        else:
            factor = -1
        y[:, inds] = factor

    mx = y*0.0
    my = y

    if h2h:
        my[:shape[0]//2] *= -1
    
    if pad_width is not None:
        my = np.pad(my, pad_width, mode='constant', constant_values=0)
        mx = np.pad(mx, pad_width, mode='constant', constant_values=0)
    
    if bottom:
        my *= -1
    
    if plot:
        plt.matshow(my)
        plt.title('My')
        plt.matshow(mx)
        plt.title('Mx')
    
    return np.array([my, mx])


def uniform(shape=(128,)*2, pad_width=0, origin='top', plot=False):
    '''
    Generates a uniform pattern.
    
    Parameters
    ----------
    shape : length 2 tuple
        y, x size in pixels.
    pad_width : {None, sequence, array_like, int} 
        If not None, the magnetisation arrays are padded using to np.pad.    
    origin : string in ['top', 'bottom']
        Indicates the direction positive pixel values represent. If 'top', the
        positive, values correspond to increases in y-axis position when plotted
        with (0,0) at the top. If 'bottom', positive pixels represent the movement
        along negative y-axis, when plotted with (0,0) at the top. Note that the
        results are always plotted with origin='top'.
    plot : bool
        If True, the returned data are also plotted.
    
    Returns
    -------
    my, mx : 3-D array
        y- and x- magnetisation in [-1, 1]. 
    
    '''
    
    bottom = origin.lower() == 'bottom'
    
    y, x = np.indices(shape)
    my = x*0.0
    mx = my + 1.0
    
    if pad_width is not None:
        my = np.pad(my, pad_width, mode='constant', constant_values=0)
        mx = np.pad(mx, pad_width, mode='constant', constant_values=0)
    
    if bottom:
        my *= -1
    
    if plot:
        plt.matshow(my)
        plt.title('My')
        plt.matshow(mx)
        plt.title('Mx')
    
    return np.array([my, mx])


def grad(shape=(128,)*2, pad_width=0, origin='top', plot=False):
    '''
    Generates a gradient pattern.
    
    Parameters
    ----------
    shape : length 2 tuple
        y, x size in pixels.
    pad_width : {None, sequence, array_like, int} 
        If not None, the magnetisation arrays are padded using to np.pad.    
    origin : string in ['top', 'bottom']
        Indicates the direction positive pixel values represent. If 'top', the
        positive, values correspond to increases in y-axis position when plotted
        with (0,0) at the top. If 'bottom', positive pixels represent the movement
        along negative y-axis, when plotted with (0,0) at the top. Note that the
        results are always plotted with origin='top'.
    plot : bool
        If True, the returned data are also plotted.
    
    Returns
    -------
    my, mx : 3-D array
        y- and x- magnetisation in [-1, 1]. 
    
    '''
    
    bottom = origin.lower() == 'bottom'
    
    y, x = np.indices(shape)
    my = y/float(y.max())
    mx = x * 0.0
    
    if pad_width is not None:
        my = np.pad(my, pad_width, mode='constant', constant_values=0)
        mx = np.pad(mx, pad_width, mode='constant', constant_values=0)
    
    if bottom:
        my *= -1
    
    if plot:
        plt.matshow(my)
        plt.title('My')
        plt.matshow(mx)
        plt.title('Mx')
    
    return np.array([my, mx])


def divergent(shape=(128,)*2, pad_width=0, origin='top', plot=False):
    '''
    Generates a divergent pattern.
    
    Parameters
    ----------
    shape : length 2 tuple
        y, x size in pixels.
    pad_width : {None, sequence, array_like, int} 
        If not None, the magnetisation arrays are padded using to np.pad.    
    origin : string in ['top', 'bottom']
        Indicates the direction positive pixel values represent. If 'top', the
        positive, values correspond to increases in y-axis position when plotted
        with (0,0) at the top. If 'bottom', positive pixels represent the movement
        along negative y-axis, when plotted with (0,0) at the top. Note that the
        results are always plotted with origin='top'.
    plot : bool
        If True, the returned data are also plotted.
    
    Returns
    -------
    my, mx : 3-D array
        y- and x- magnetisation in [-1, 1]. 

    '''
    
    bottom = origin.lower() == 'bottom'
    
    y, x = np.indices(shape)
    y = y - y.mean()
    x = x - x.mean()
    
    my = y / y.max()
    mx = x / x.max()
    
    if pad_width is not None:
        my = np.pad(my, pad_width, mode='constant', constant_values=0)
        mx = np.pad(mx, pad_width, mode='constant', constant_values=0)
    
    if bottom:
        my *= -1
    
    if plot:
        plt.matshow(my)
        plt.title('My')
        plt.matshow(mx)
        plt.title('Mx')
        
        plt.figure()
        n=8
        plt.quiver(mx[::n,::n], -my[::n, ::n], scale=16)
        plt.gca().set_aspect(1)
        plt.gca().invert_yaxis()
    
    return np.array([my, mx])


def neel(width=8.0, shape=(128,)*2, pad_width=0, origin='top', plot=False):
    '''
    Generates a Neel domain wall pattern.
    
    Parameters
    ----------
    width : scalar
        Full width of the tanh profile.
    shape : length 2 tuple
        y, x size in pixels.
    pad_width : {None, sequence, array_like, int} 
        If not None, the magnetisation arrays are padded using to np.pad.    
    origin : string in ['top', 'bottom']
        Indicates the direction positive pixel values represent. If 'top', the
        positive, values correspond to increases in y-axis position when plotted
        with (0,0) at the top. If 'bottom', positive pixels represent the movement
        along negative y-axis, when plotted with (0,0) at the top. Note that the
        results are always plotted with origin='top'.
    plot : bool
        If True, the returned data are also plotted.
    
    Returns
    -------
    my, mx : 3-D array
        y- and x- magnetisation in [-1, 1]. 

    '''
    
    bottom = origin.lower() == 'bottom'
    
    y, x = np.indices(shape)    
    
    xc1, xc2 = np.percentile(x[0], [100/3.0, 100/3.0*2])
    
    my = np.tanh((x-xc1)/(width*2.0)*np.pi) - np.tanh(-(x-xc2)/(width*2.0)*np.pi)
    my /= 2.0
    mx = (1-my**2)**0.5
    
    if pad_width is not None:
        my = np.pad(my, pad_width, mode='constant', constant_values=0)
        mx = np.pad(mx, pad_width, mode='constant', constant_values=0)
    
    if bottom:
        my *= -1
    
    if plot:
        plt.matshow(my)
        plt.title('My')
        plt.matshow(mx)
        plt.title('Mx')
        
        plt.figure()
        n=8
        plt.quiver(mx[::n,::n], -my[::n, ::n], scale=16)
        plt.gca().set_aspect(1)
        plt.gca().invert_yaxis()
        
        plt.figure()
        plt.plot(my[0], label='My')
        plt.plot(mx[0], label='Mx')
        plt.legend()
    
    return np.array([my, mx])



def bt2phasegrad(bt):
    '''
    Phase gradient from integrated induction.
    
    Parameters
    ----------
    bt : ndarray or scalar
        Integrated induction in Tesla*m.
    
    Returns
    -------
    phase_grad : ndarray or scalar
        Phase gradient in radians / m.
    
    '''
    
    phase_grad = 2*pi*e/h * bt
    return phase_grad


def phasegrad2bt(phase_grad):
    '''
    Local integrated induction from phase gradient.
    
    Parameters
    ----------
    phase_grad : ndarray or scalar
        Phase gradient in radians / m.
    
    Returns
    -------
    bt : ndarray or scalar
        Integrated induction in Tesla*m.
    
    '''
    
    bt = phase_grad * h/(2*pi*e)
    return bt


def bt2beta(bt, kV=200.0):
    '''
    Beta from local integrated induction.
    
    Parameters
    ----------
    bt : ndarray or scalar
        Integrated induction in Tesla*m.
    kV : scalar
        Bean energy in kV. The wavelength calculation is relativistic.
    
    Returns
    -------
    beta : ndarray or scalar
        Deflection (semi-) angle in radians.
    
    '''
    
    lamb = e_lambda(kV)
    beta = lamb*e/h*bt
    return beta


def beta2bt(beta, kV=200.0):
    '''
    Local integrated induction from beta.
    
    Parameters
    ----------
    beta : ndarray or scalar
        Deflection (semi-) angle in radians.
    kV : scalar
        Bean energy in kV. The wavelength calculation is relativistic.
    
    Returns
    -------
    bt : ndarray or scalar
        Integrated induction in Tesla*m.
    
    '''
    
    lamb = e_lambda(kV)
    bt = beta / (lamb*e/h)
    return bt


def beta2phasegrad(beta, kV=200.0):
    '''
    Phase gradient from beta.
    
    Parameters
    ----------
    beta : ndarray  or scalar
        Deflection (semi-) angle in radians.
    kV : scalar
        Bean energy in kV. The wavelength calculation is relativistic.
    
    Returns
    -------
    phase_grad : ndarray  or scalar
        Phase gradient in radians / m.
    
    '''
    
    lamb = e_lambda(kV)
    phase_grad = 2*pi/lamb * beta
    return phase_grad


def phasegrad2period(phase_grad):
    '''
    Equivalent periodicity from phase gradient.
    
    Parameters
    ----------
    phase_grad : ndarray or scalar
        Phase gradient in radians / m.
    
    Returns
    -------
    period : ndarray or scalar
        Equivalent periodicity in m.
    
    '''
    
    period = 2*pi/phase_grad
    return period


def mag_phase(my, mx, ypix=1e-9, xpix=1e-9, thickness=10e-9, pad_width=None,
               phase_amp=10, origin='top', plot=False):
    '''
    Electromagnetic phase calculations from magnetisation, following
    Beleggia et al., APL 83 (2003), DOI: 10.1063/1.1603355.
    
    Parameters
    ----------
    my : 2-D array
        Magnetisation in y-axis in [0, 1], where 1 is taken as Bs of 1 Tesla.
    mx : 2-D array
        Magnetisation in x-axis in [0, 1], where 1 is taken as Bs of 1 Tesla.
    ypix : scalar
        y-axis pixel spacing in metres.
    xpix : scalar
        x-axis pixel spacing in metres.
    thickness : scalar
        Material thicknes metres.
    pad_width : {None, sequence, array_like, int} 
        If not None, the magnetisation arrays are padded using to np.pad.
    phase_amp : scalar
        Factor by which the phase is scalled for cosine plot.
    origin : string in ['top', 'bottom']
        Indicates the direction positive pixel values represent. If 'top', the
        positive, values correspond to increases in y-axis position when plotted
        with (0,0) at the top. If 'bottom', positive pixels represent the movement
        along negative y-axis, when plotted with (0,0) at the top. Note that the
        results are always plotted with origin='top'.
    plot : bool
        If True, the returned data are also plotted.
    
    Returns
    -------
    p : named_tuple
        Contains the following parameters:
    phase : 2-D array
        Phase change in radians.
    phase_grady, phase_gradx : 2-D array
        Phase gradient in radians / metre.
    phase_laplacian : 2-D array
        Phase gradient in radians / metre**2.
    my, mx : 2-D array
        Optionally padded 'magnetisation' in Tesla.
    localBy, localBx : 2-D array
        Local induction. Note this number only relates to saturation induction,
        Bs, under centain conditions.
    
    Examples
    --------
    Generate a Landau pattern, calculate phase properties, and plot DPC signals.
    
    >>> import fpd
    >>> import matplotlib.pylab as plt
    >>> plt.ion()
    
    >>> my, mx = fpd.mag_tools.landau()
    >>> p = fpd.mag_tools.mag_phase(my, mx, plot=True)
    >>> byx = [p.localBy, p.localBx]
    >>> b = fpd.DPC_Explorer(byx, vectrot=270, cmap=2, cyx=(0,0), pct=0, r_max_pct=100)
    
    
    '''
    # TODO
    # add tilt angles
    # add defocus Fresnel
    # add mean inner potential?
    
    
    # implementation is top, meaning +ve y points down (plotted with 0,0 at top,
    # the pixel value indicates the delta on the x-axis.
    bottom = origin.lower() == 'bottom'
    if bottom:
        my = my*-1.0
    
    if pad_width is not None:
        my = np.pad(my, pad_width, mode='constant', constant_values=0)
        mx = np.pad(mx, pad_width, mode='constant', constant_values=0)
    
    phi0 = h/(2*e)
    constant = 1j * pi * mu_0 / phi0

    # convert T to A/m^2
    mx_ft = fft2(mx/mu_0)
    my_ft = fft2(my/mu_0)

    # reciprocal vectors
    ky = fftfreq(mx.shape[0], ypix) / 2*np.pi
    kx = fftfreq(mx.shape[1], xpix) / 2*np.pi
    kyy, kxx = np.meshgrid(ky, kx, indexing='ij')

    # eq 3 in Beleggia et al., APL 83 (2003), DOI: 10.1063/1.1603355.
    denom = (kxx**2 + kyy**2)
    # avoide runtime warning
    denom[0, 0] = 1.0
    c = (mx_ft * kyy - my_ft * kxx) / denom
    
    phase_ft = constant * thickness * c
    phase_ft[0, 0] = 0j
    phase = ifft2(phase_ft).real 

    # fft derivative
    phase_gradx = ifft2(phase_ft * kxx * 1j).real
    phase_grady = ifft2(phase_ft * kyy * 1j).real

    # 2nd derivative and laplacian
    phase_gradx2 = ifft2(phase_ft * (kxx * 1j)**2).real
    phase_grady2 = ifft2(phase_ft * (kyy * 1j)**2).real
    phase_laplacian = -(phase_gradx2 + phase_grady2)
    
    # local induction
    localBy = phasegrad2bt(phase_grady) / thickness
    localBx = phasegrad2bt(phase_gradx) / thickness
    
    if plot:
        #s = (slice(pw, -pw),  slice(pw, -pw))
        s = (slice(None, None),  slice(None, None))
        
        plt.matshow(my[s])
        plt.title('My')
        plt.matshow(mx[s])
        plt.title('Mx')
        
        plt.matshow(phase[s])
        plt.title('phase')
        plt.matshow(np.cos(phase[s]*phase_amp))
        plt.title('phase cosine')
        
        plt.matshow(phase_laplacian[s])
        plt.title('phase_laplacian')
        
        plt.matshow(phase_grady[s])
        plt.title('phase_grady')
        plt.matshow(phase_gradx[s])
        plt.title('phase_gradx')
        
        plt.matshow(localBy[s])
        plt.title('Local By')
        plt.matshow(localBx[s])
        plt.title('Local Bx')
        
    PhaseResults = namedtuple('PhaseResults',
                              ['phase', 'phase_grady', 'phase_gradx', 'phase_laplacian', 'my', 'mx', 'localBy', 'localBx'])
    p = PhaseResults(phase, phase_grady, phase_gradx, phase_laplacian, my, mx, localBy, localBx)
    return p

 
def tesla2mag(tesla):
    '''
    Magnetisation (A/m) from induction (T).
    
    Parameters
    ----------
    tesla : ndarray or scalar
        Induction in Tesla.
    
    Returns
    -------
    m : ndarray or scalar
        Magnetisation in A/m.
    
    '''
    
    m = tesla * 1e7/(4*np.pi)
    return m


def mag2tesla(m):
    '''
    Induction (T) from magnetisation (A/m).
    
    Parameters
    ----------
    m : ndarray or scalar
        Magnetisation in A/m.
    
    Returns
    -------
    tesla : ndarray or scalar
        Induction in Tesla.
    
    '''
    
    tesla = m / (1e7/(4*np.pi))
    return tesla


def tesla2Oe(tesla):
    '''
    Field (Oe) from induction (T).
    
    Parameters
    ----------
    tesla : ndarray or scalar
        Induction in Tesla.
    
    Returns
    -------
    o : ndarray or scalar
        field in Oe.
    
    '''
    
    o = tesla * 10000
    return o


def tesla2G(tesla):
    '''
    Field (G) from induction (T).
    
    Parameters
    ----------
    tesla : ndarray or scalar
        Induction in Tesla.
    
    Returns
    -------
    g : ndarray or scalar
        field in Oe.
    
    '''
    
    g = tesla * 10000
    return g

