import numpy as np
import pyFAI
from .sample import *
from .data_processing import *
import math
import scipy.integrate as integrate
from scipy.optimize import curve_fit

#reduces the provided sample
def reduction(sample, conf = 0):
    qlow = 0
    qhigh = 0
    maskImg = saxsmask
    if conf == 0:
        conf = float(sample.conf)
    #will automatically set the mask and q values dependent on the configuration in the sample
    if conf == 21:
        maskImg = waxsmask
        qlow = 0.049
        qhigh = 1.7
    elif conf == 22:
        maskImg = maxmask
        qlow = 0.015
        qhigh = 0.6
    elif conf == 23:
        maskImg = saxsmask
        qlow = 0.007
        qhigh = 0.275
    elif conf == 24 and (not sample.bstop):
        maskImg = esaxsmask
        qlow = 0.001
        qhigh = 0.198
    else:
        maskImg = esaxsnobsmask
        qlow = 0.001
        qhigh = 0.198

    #creates a detector based off the sample
    ai_cms = createDetector(sample.dist, float(sample.center0), float(sample.center1))

    #reduces the sample
    qq0, Iq0, EIq = ai_cms.integrate1d(sample.tiff, 200, radial_range = (qlow,qhigh), mask=maskImg, unit='q_A^-1', error_model = "poisson")

    Iq0[ Iq0==0 ] = np.nan

    return qq0, Iq0, EIq

# this function stitches all 5 different configurations into one master Qqand master I list, have to provide the name of the blank sample
def stitching(samplist, samp, blank_sample_name):
    #finding all samples with the given name
    indices = findSamples(samplist,samp.name)

    #reducing each individual configuration
    qq0, Iq0, Eiq0 = reduction(samplist[indices[0]])
    qq1, Iq1, Eiq1 = reduction(samplist[indices[1]])
    qq2, Iq2, Eiq2 = reduction(samplist[indices[2]])
    qq3, Iq3, Eiq3 = reduction(samplist[indices[3]])
    qq4, Iq4, Eiq4 = reduction(samplist[indices[4]])

    #reducing the blank sample
    blank_indices = findSamples(samplist,blank_sample_name)
    _, Iqblank, _ = reduction(samplist[blank_indices[0]])

    #normalizing the other configurations to the esaxs
    Iq0 = Iq0* findAverageRatio(qq1, Iq1, qq0, Iq0, 0.008, 0.02, 0.06)
    Iq2 = Iq2 * findAverageRatio(qq1, Iq1, qq2, Iq2, 0.01, 0.035, 0.12)
    Iq3 = Iq3 * findAverageRatio(qq1, Iq1, qq3, Iq3, 0.03, 0.08, 0.06)
    Iq4 = Iq4 * findAverageRatio(qq1, Iq1, qq4, Iq4, 0.06, 0.14, 0.08)

    fs = []
    for i in range(5,20):
        fs.append((Iq0[i]-Iq1[i])/Iqblank[i])

    f = sum(fs)/len(fs)
    Iq0fixed = Iq0-Iqblank*f

    #concatenating all the qs and Is together into one master list
    masterq = np.concatenate((qq0[2:5], qq1[5:10], qq2[2:18],qq3[5:27],qq4[5:] ), axis=None)
    masterI = np.concatenate((Iq0fixed[2:5], Iq1[5:10], Iq2[2:18],Iq3[5:27],Iq4[5:]), axis=None)
    return masterq, masterI

def Ksquared(q, R):
    return ((4/3)*(math.pi)*(R**3)*3*((math.sin(q*R)-(q*R*math.cos(q*R)))/(q*R)**3))**2

def LogNormal(R, mu, sigma, p):
    c = math.sqrt(2*math.pi)*sigma*(mu**(1-p))*math.exp(((1-p)**2)*((sigma**2)/2))
    return (1/c)*(1/(R**p))*math.exp(-((math.log(R/mu))**2)/(2*sigma**2))

def numerator(R,q,mu,sigma,p):
    return Ksquared(q,R)*LogNormal(R, mu, sigma,p)* R**3

def denominator(R,mu,sigma,p):
    return LogNormal(R, mu, sigma, p) * R**3

def hard_sphere(q,R,f):
    d = R*2
    gamma1 = ((1+(2*f))**2)/((1-f)**4)
    gamma2 = -((1+(f/2))**2)/((1-f)**4)
    NC = -24*f*(gamma1*((math.sin(q*d)-(q*d)*math.cos(q*d))/((q*d)**3))- 6 * f * gamma2* ((((q*d)**2)*math.cos(q*d)-2*(q*d)*math.sin(q*d)-2*math.cos(q*d) + 2)/((q*d)**4))-f*(gamma1/2)*((((q*d)**4)*math.cos(q*d)- 4 * ((q*d)**3) * math.sin(q*d) - 12*((q*d)**2)*math.cos(q*d)+24*math.cos(q*d)-24)/((q*d)**6)))
    return 1/ (1- NC)

def integration(qdata, sigma, mu, phi_1,p):
    R = 63

    Iq0 = []
    for q in qdata:
        I = phi_1*(integrate.quad(numerator, 0,1000, args=(q,mu,sigma,p))[0]/integrate.quad(denominator, 0, 1000, args=(mu,sigma,p))[0])
        Iq0.append(I)
    return Iq0

def integration_with_hardshell(qdata, phi_1, Rhs, f ):

    sigma = 2.90000000e-01
    mu = 6.35241167e+01
    p=4.10861101e+00
    Iq = []
    for q in qdata:
        I = phi_1*hard_sphere(q,Rhs,f)*(integrate.quad(numerator, 0,1000, args=(q,mu,sigma,p))[0]/integrate.quad(denominator, 0, 1000, args=(mu,sigma,p))[0])
        Iq.append(I)
    return Iq

def fitData(samplist):
    Rhs = []
    Fs = []
    for i,sample in enumerate(samplist):
        q0, I0, Eiq0 = reduction(sample,21)
        k = 0
        while(k < len(I0)):
            if(math.isnan(I0[k])):
                print(k)
                q0 = np.delete(q0,k)
                I0 = np.delete(I0,k)
            else:
                k = k+1
        I0 = I0[:len(I0)-2]
        q0 = q0[:len(q0)-2]
        q_bounded = q0[1:-1]
        I_bounded = I0[1:-1]
        popt_hardshell, pcov_hardshell = curve_fit(integration_with_hardshell, q_bounded, I_bounded, [2.08670806e-11, 200, .2], bounds=([1e-12,0, 0.001],[1e-8,400,.4]))
        Rhs.append(popt_hardshell[1])
        Fs.append(popt_hardshell[2])
        print("number " + str(i) + "%" + str(i/len(samplist)))
    return Rhs, Fs
