# -*- coding: utf-8 -*-
"""
Created on Mon Dec  3 16:18:05 2018

@author: Etien & Patr & Benjm
"""

#%% Import modules
import numpy as np
import csv
import math
import scipy.constants as sc
import matplotlib.pyplot as plt
import scipy as sp
from scipy.optimize import curve_fit
import femtoQ.plotting as fqp
fqp.set_default_values_presentation()
#%% Set constants and recurrant functions
C = sc.c                          # Speed of light
pi = sc.pi                        # Pi
sqrt = lambda x: np.sqrt(x)       # Square root
log = lambda x: np.log(x)         # Natural logarithm
exp = lambda x: np.exp(x)         # Exponential

#%% Methods and classes

def ezfft(t, S, normalization = "ortho", neg = False):
    """ Returns the Fourier transform of S and the frequency vector associated with it"""
    y = np.fft.fft(S,norm=normalization)
    y = np.fft.fftshift(y)
    f = np.fft.fftfreq(t.shape[-1], d = t[2]-t[1])
    f = np.fft.fftshift(f)
    if neg == False:
        y = 2*y[f>0]
        f = f[f>0]

    return f,y


def ezifft(f, y, normalization = "ortho"):
    '''Returns the inverse Fourier transform of y and the time vector associatedwith it
    WARNING : the negative frequencies must be included in the y vector'''
    N = len(f)
    tstep = 1/(N*(f[2]-f[1]))
    x = np.linspace(-(N*tstep/2),(N*tstep/2),N)
    y = np.fft.ifftshift(y)
    S = np.fft.ifft(y,norm=normalization)

    return x,S




def ezsmooth(x,window_len=11,window='flat'):
     """smooth the data using a window with requested size.

     This method is based on the convolution of a scaled window with the signal.
     The signal is prepared by introducing reflected copies of the signal
     (with the window size) in both ends so that transient parts are minimized
     in the begining and end part of the output signal.

     input:
         x: the input signal
         window_len: the dimension of the smoothing window; should be an odd integer
         window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
             flat window will produce a moving average smoothing.

     output:
         the smoothed signal

     example:

     t=linspace(-2,2,0.1)
     x=sin(t)+randn(len(t))*0.1
     y=smooth(x)

     see also:

     numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
     scipy.signal.lfilter
     """

     if x.ndim != 1:
         raise ValueError("smooth only accepts 1 dimension arrays.")

     if x.size < window_len:
         raise ValueError("Input vector needs to be bigger than window size.")


     if window_len<3:
         return x


     if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
         raise ValueError("Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


     s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]

     if window == 'flat': #moving average
         w=np.ones(window_len,'d')
     else:
         w=eval('np.'+window+'(window_len)')

     y=np.convolve(w/w.sum(),s,mode='valid')
     return  y[round(window_len/2-1):-round(window_len/2)]


def ezcorr(x, y1, y2, unbiased=False, Norm=False, Mean = False):

    '''Arguments : x, y1, y2, biased, norm
    This function assumes the x arrays are the same, "unbiased" = True for an unbiased calculation and "Norm" = False to not normalize
    One can not have "Norm" = True and "unbiased" = False'''
    if Mean is True:
        y1 = y1-y1.mean()
        y2 = y2-y2.mean()

    delta_t = x[1]-x[0]
    ord_corr = np.correlate(y1,y2,"same")*delta_t
    absc_corr = delta_t*np.linspace(-len(ord_corr)/2,len(ord_corr)/2,len(ord_corr))
    if unbiased == True:
        if Norm == True:
            ord_unbiased = np.empty(len(absc_corr))
            for k in range(len(ord_corr)):
                ord_unbiased[k] = ord_corr[k]/(len(ord_corr)-abs(k-int(len(ord_corr)/2)))
            return(absc_corr,ord_unbiased)
        else:
            ord_unbiased = np.empty(len(absc_corr))
            for k in range(len(ord_corr)):
                ord_unbiased[k] = ord_corr[k]/(len(ord_corr)-abs(k-int(len(ord_corr)/2)))/delta_t
            return(absc_corr,ord_unbiased)
    else:
        return(absc_corr,ord_corr)


def ezcsvload(filename, nbrcolumns = 2, delimiter = '\t', decimalcomma = False, outformat = 'array', skiprows = 0, profile = None):
    """
    Function for easy loading of csv-type files. Loading parameters can be set manually,
    or instruments-specific "profiles" can be called.

    """

    # Load profile, if any is specified
    if profile is not None:
        if profile is 'HR2000':
            nbrcolumns = 2
            delimiter = '\t'
            decimalcomma = False
            skiprows = 0

        if profile is 'testfile':
            nbrcolumns = 3
            delimiter = ';'
            decimalcomma = False
            skiprows = 1
        if profile is 'OSA':
            nbrcolumns = 2
            delimiter = '\t'
            decimalcomma = True
            skiprows = 0

        # Add your own profiles here

    # Preallocate output list
    outlist = [ [] for var in range(nbrcolumns) ]

    # Load file
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=delimiter, quotechar='|')
        for index, row in enumerate(spamreader):

            if index >= skiprows: # Skip first "skiprows" rows of file

                for outlist_index in range(nbrcolumns):

                    if decimalcomma is True: # Convert comma to marks
                        tmp = str(row[outlist_index])
                        tmp = tmp.replace(',','.')
                        try:
                            outlist[outlist_index].append(float( tmp ))
                        except:
                            print("1 data point failed")

                    else:
                        try:
                            outlist[outlist_index].append(float(row[outlist_index]))
                        except:
                            print("1 data point failed")

    if outformat is 'array': # Convert lists of values to numpy arrays
        for outlist_index in range(nbrcolumns):
            outlist[outlist_index] = np.array(outlist[outlist_index])

    return outlist


def ezfindwidth(x, y, halfwidth = False, height = 0.5, interp_points = 1e6):
    # Ensure x is stricktly ascending
    IIsort = np.argsort(x)
    x = x[IIsort]
    y = y[IIsort]
    # Max. / min. values of y array
    ymin = np.nanmin(y)
    ymax = np.nanmax(y - ymin)

    # Normalize
    ytmp = (y - ymin) / ymax

    # Interpolate data for better accuracy, if necessary
    if interp_points > len(x):
        # Interpolate data inside search domain for better accuracy
        xinterp = np.linspace(x[0] , x[-1] ,int(interp_points))
        yinterp = np.interp(xinterp,x,ytmp)
    else:
        xinterp = x
        yinterp = y

    # Cut interpolation domain at desired height
    tmp1 = (yinterp >= height )

    # Ensure there's a uniquely defined width
    tmp2 = np.linspace(0,len(tmp1)-1,len(tmp1),dtype = int)
    tmp2 = tmp2[tmp1]
    tmp3 = tmp2[1:] - tmp2[:-1]

    # Output width, if defined
    if any(tmp3 > 1) | (len(tmp2)==0):
        width = np.nan
    else:
        width = xinterp[tmp2[-1]] - xinterp[tmp2[0]]

    # Divide by two, if desired
    if halfwidth is True:
        width /= 2

    return width



def ezdiff(x, y, n = 1, order = 2):
    """ Numerical differentiation based on centered finite-difference formulas.
    Outputs d^n/dx^n(y) and a appropriately truncated x vector. "order" parameter
    determines the order of the finite difference formula; it must be an even
    number greater than 0. High values of order can help precision or lead to
    significant numerical errors, depending on the situation. x needs to increase
    monotonically in constant increments dx.
    """

    # X increments
    dx = x[1] - x[0]

    # Number of finite difference coefficients to calculate
    nbr_coeff = 2 * math.floor( (n+1)/2 ) - 1 + order

    # p number (see wikipedia for more info)
    p = int((nbr_coeff - 1)/2)

    # Matrix of linear system Ax = b to solve
    Amatrix = np.zeros((nbr_coeff,nbr_coeff))
    for jj in range(nbr_coeff):
        tmp = -p + jj
        for kk in range(nbr_coeff):
            Amatrix[kk,jj] = tmp**kk

    # b vector
    bvector = np.zeros(nbr_coeff)
    bvector[n] = math.factorial(n)

    # Solve to find "x" vector, not related to "x" input
    # (sorry if this confusing)
    xvector = np.linalg.solve(Amatrix,bvector)

    # Preallocation
    deriv = np.zeros_like(x[p:-p])
    c = np.zeros_like(x[p:-p])

    # Evaluating finite difference, using Neumaier's improved Kahan summation
    # algorithm. Using it should reduce numerical errors during summation,
    # although it slows down calculations
    for ll in range(-p,p+1):

        new_term = (xvector[ll+p] * y[p+ll : len(y)-p+ll])/(dx**n)

        tmp1 = deriv + new_term


        cond = np.abs(deriv) >= np.abs(new_term)
        not_cond = np.logical_not(cond)

        c[cond] = c[cond] + (deriv[cond] - tmp1[cond]) + new_term[cond]

        c[(not_cond)] = c[(not_cond)] + (new_term[(not_cond)] - tmp1[(not_cond)]) + deriv[(not_cond)]


        deriv = tmp1

    # Requested derivative, corrected
    deriv += c

    # Appropriately truncated x vector for math and plotting
    xtrunc = x[p:-p]


    return xtrunc, deriv

def knife_edge_experiment(z = None, P = None, P0 = 0, P_max = None):
    """
    z in mm
    """
    if z is None or P is None:
        print('Position or power array is missing')
        return
    
    if type(z) != np.ndarray or type(P) != np.ndarray:
        print('z and P must be numpy arrays')
        return
    
    if len(P) != len(z):
        print('z and P must be the same length')
        return
    
    # Defining error function
    if P_max:
        def func(z, z0, w):
            return P0 + 0.5*P_max*(1-sp.special.erf(np.sqrt(2) * (z -z0)/w))
        # Fit an error function on the data
        params, param_covar = curve_fit(func, z, P)
        z_fit = np.linspace(3, 11, 100)
        P_fit = func(z_fit, params[0], params[1])
    else:
        def func(z, z0, w, P_max):
            return P0 + 0.5*P_max*(1-sp.special.erf(np.sqrt(2) * (z -z0)/w))
        # Fit an error function on the data
        params, param_covar = curve_fit(func, z, P, bounds=(0, [np.max(z), np.max(z), np.max(P)]))
        z_fit = np.linspace(3, 11, 100)
        P_fit = func(z_fit, params[0], params[1], params[2])
        print('The fitted max power is: ' + str(params[2]))
    
    print('The beam diameter (1/e^2) is: ' + str(2*params[1]) + ' mm')
    
    # Plotting
    plt.figure
    plt.plot(z,P, 'o', label = 'Measured')
    plt.plot( z_fit, P_fit, label = 'Fitted')
    plt.xlabel('Razor edge position (mm)')
    plt.ylabel('Average power (mW)')
    if P_max:
        plt.ylim([0,1.05*P_max])
    else:
        plt.ylim([0,1.05*params[2]])
    plt.legend()

    plt.show()

class Pulse:
    """
    Input:
            - Center wavelength & time bandwidth
            OR
            - Center frequency and frequency bandwidth
            OR
            - Electric field in time
            &
            - Amplitude (Optional)
            - T: length of the time vector
            - dt: precision in the time vector
    Pulse is caracterized by its electric field in the time domain.
    """
    def __init__(self, lambda0 = None, tau_FWHM = None, v0 = None, v_bandwidth = None, A = 1, t = None, E = None, T = 10000e-15, dt = 0.1e-15):
        #%% Simulation parameters
        self.T = T
        self.dt = dt
        if ((t is not None) & (E is not None)):
            self.t = t
            self. E = E

        elif ((lambda0 is not None) & (tau_FWHM is not None)):

            # Other pulse parameters
            tau = tau_FWHM / sqrt(2*log(2)) # Gaussian pulse half width @ e^-2
            v0 = C/lambda0                  # Pulse's carrier frequency
            w0 = 2*pi*v0                    # Pulse's carrier angular frequency

            # Electric field in time domain
            self.t = np.linspace(-T/2,T/2, round(T/self.dt) )
            self.E = A*np.exp(1j * w0 * self.t) * np.exp(-  (self.t)**2 / (tau)**2)

        elif ((v0 is not None) & (v_bandwidth is not None)):
            tauFWHM = 0.44/v_bandwidth         # Initial pulse duration, full width at half maximum
            tau = tauFWHM / sqrt(2*log(2)) # Gaussian pulse half width @ e^-2
            w0 = 2*pi*v0                    # Pulse's carrier angular frequency
            self.t = np.linspace(-T/2,T/2, round(T/self.dt) )
            self.E = A* exp(1j * w0 * (t)) * np.exp( - (t)**2 / (tau)**2)    # Electric field of the pulse in the time domain

    def disperse(self, medium = None, L = None, dispVec = None, v0 = "Auto"):
        """
        This method takes the the pulse and retrieves the temporal shape of the electric field
        after propagation in a given medium, using Sellmeier's equations of this medium. If an
        optionnal manual_GGD is entered, the code will not use "medium" and "L".

        Input:
            material : The optical medium through which the pulse propagates
            L: The thickness of through which the pulse propagates
            dispVec(optional): Custom amount of dispersion. Vector containing orders of dispersion from 2 to needed.
        """
        # v is freqnecy vector, s is frequency-domain electric field vector
        v,s = ezfft(self.t,self.E, neg = True)
        # Calculate mean frequency
        if dispVec is not None:
            if v0 == "Auto":
                v0 = np.trapz(np.abs(s)**2 * v)/np.trapz(np.abs(s)**2)
            # conversion in angular frequency
            w0 = 2*pi*v0
            w = 2*pi*v
            # Calculate all phase orders
            phase = np.zeros_like(v)
            for i, disp in enumerate(dispVec):
                phase += 1/math.factorial(i+2)*disp*(w-w0)**(i+2)*(1e-15)**(i+2)
            s = s*exp(1j*phase)
        else:
            if medium == "BK7" or "bk7":
                lambda_1 = 0.3e-6   # Cutoff wavelengths of the equation's validity
                lambda_2 = 2.5e-6
                n_sellmeier = lambda x: (1+1.03961212/(1-0.00600069867/x**2)+0.231792344/(1-0.0200179144/x**2)+1.01046945/(1-103.560653/x**2))**.5  #https://refractiveindex.info/?shelf=glass&book=BK7&page=SCHOTT
            elif medium == "FS" or "Fused silica" or "fused silica":
                lambda_1 = 0.21e-6
                lambda_2 = 6.7e-6
                n_sellmeier = lambda x: (1+0.6961663/(1-(0.0684043/x)**2)+0.4079426/(1-(0.1162414/x)**2)+0.8974794/(1-(9.896161/x)**2))**.5       #https://refractiveindex.info/?shelf=glass&book=fused_silica&page=Malitson
            elif medium == "YAG" or "yag":
                lambda_1 = 0.4e-6
                lambda_2 = 5e-6
                n_sellmeier = lambda x: (1+2.28200/(1-0.01185/x**2)+3.27644/(1-282.734/x**2))**.5   #https://refractiveindex.info/?shelf=main&book=Y3Al5O12&page=Zelmon
            elif medium == "SF11" or "sf11":
                lambda_1 = 0.37e-6
                lambda_2 = 2.5e-6
                n_sellmeier = lambda x: (1+1.73759695/(1-0.013188707/x**2)+0.313747346/(1-0.0623068142/x**2)+1.89878101/(1-155.23629/x**2))**.5      #https://refractiveindex.info/tmp/data/glass/schott/N-SF11.html
            else:
                print("The entered medium does not exist or its Sellmeier's equations are not contained in this method")
                return self

            #%% Dispersive propagation
            # Convert Sellmeier's equations cutoff wavelengths to frequencies
            v1 = C / lambda_2
            v2 = C / lambda_1

            # Convert frequencies within the equation's validity domain to wavelengths in um
            vtmp = v[( (v>v1) & (v<v2) )]
            lambdatmp = C / vtmp

            # Calculate refractive index for relevant frequencies
            ntmp = n_sellmeier(lambdatmp*1e6)

            # Generate refractive index vector n(v). Values outside of validity range are
            # set to zero.
            n = np.ones_like(v)
            n[( (v>v1) & (v<v2) )] = ntmp

            # Apply material's spectral phase to frequency domain electric field
            s[v!=0] = s[v!=0] * np.exp(1j * 2 * pi * n[v!=0] * (v[v!=0] / C) * L)

        #%% Inverse fast fourier transform
        # E2 is final time domain electric field vector, t2 is its corresponding time
        # vector. If all works as intended, t2 is equivalent to t at this point
        t2, E2 = ezifft(v,s)

        #%% Final pulse realignment
        # Find final pulse's peak in time
        tpeak = np.mean( t2[np.abs(E2)**2 == np.nanmax(np.abs(E2)**2)] )

        tExtended = np.concatenate((t2-np.abs(np.min(t2)) - np.max(t2) - self.dt, t2, t2+np.abs(np.min(t2)) + np.max(t2) + self.dt), axis = 0 )

        EExtended = np.pad(E2, E2.shape, mode = 'wrap')

        # Shift time vector
        E2 = np.interp(t2, tExtended-tpeak, EExtended)

        # New object
        new_Pulse = Pulse(t = t2,E = E2)
        return new_Pulse

    def getFWHM(self, domain = "wavelength"):
        """
        Returns the FWHM of the pulse.
        Can return the FWHM in either of these 3 domains, as selected by the user:
            - wavelength (default)
            - frequency
            - time
        """
        v, s = ezfft(self.t, self.E)
        if domain is "time":
            return ezfindwidth(self.t, np.abs(self.E)**2)
        elif domain is "frequency":
            return ezfindwidth(v, np.abs(s)**2)
        elif domain is "wavelength":
            l = C/v
            return ezfindwidth(l, np.abs(s)**2)
        else:
            print("Invalid domain")
            return None


    def getInstFreq(self):
        """
        No input
        Returns instantanious frequency
        """
        # Temporal phase
        phi_t = np.unwrap(np.angle(self.E))
        # Instantaneous angular frequency
        w_inst = (phi_t[2:] - phi_t[:-2]) / (self.t[2] - self.t[0])
        # Add zeros the the extremities to keep the same vector length
        w_inst = np.insert(w_inst, 0, 0)
        w_inst = np.append(w_inst, 0)
        # Return instentanious frequency
        return w_inst

    def SFG(self, Pulse2, SFGonly = True):
        """
        Returns the spectral amplitude of the SFG from Pulse1 and Pulse2, along with a new Pulse object
        defined by the total field resulting of the interaction. If SFGonly is False, the two SHGs will also
        be returned along with the SFG in both the field and the spectral amplitude.
        """
        # Verification that the time vectors are the same
        if self.t.all() == Pulse2.t.all():
            # Consider SFG without SHGs
            if SFGonly is True:
                Atmp = self.E * Pulse2.E
            # Consider both SHGs and the SFG
            elif SFGonly is False:
                E_tot =  self.E + Pulse2.E
                Atmp = E_tot * E_tot

            f_nl, A_nl = ezfft(self.t, Atmp)
            return Pulse(t = self.t, E = Atmp), f_nl, A_nl
        else:
            print("time vector must be identical")
            return None


    def delay(self, timeDelay):
        """
        Delay the pulse in time domain by a value equal to timeDelay. Does not wrap it back once it reaches the
        end of time vector t. A positive delay means the pulse's peak will shift towards negative time values.
        """
        
        newEfield = np.interp(self.t, self.t - timeDelay, self.E)
        
        newPulse = Pulse(t = self.t, E = newEfield)
        
        return newPulse










