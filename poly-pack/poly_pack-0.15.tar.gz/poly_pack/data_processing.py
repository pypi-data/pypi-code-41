import pyFAI
from pyFAI.geometry import Geometry
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator
import pyFAI.calibrant
import numpy as np
from .sample import *
import datetime

#this file has an assortment of helpful functions to do the process all of the SAXS data


#creates a detector based on given values, if using a different detector add in detector_name, wavelength
def createDetector(dist, center0 = 365, center1 = 240, detector_name = 'Pilatus300k', wavelength = 1.5406e-10):
    detectorName = detector_name
    detectorPixel = 172e-6
    detectorDistance = dist

    #if values not already provided, will default to values above
    Center0 = center0
    Center1 = center1
    # energy = 13.5
    # Copper (Cu K-alpha): 8.0478 keV, λ = 1.5406 Å
    wl = wavelength         #x-ray wavelength

    detector = pyFAI.detectors.Detector(detectorPixel, detectorPixel)
    ai_cms = AzimuthalIntegrator(dist=detectorDistance, detector=detectorName)

    ai_cms.wavelength = wl

    p1 = detectorPixel*Center0
    p2 = detectorPixel*Center1
    ai_cms.poni1 = p1
    ai_cms.poni2 = p2

    return ai_cms

#this function will return a list with all the indices with the same name. for example, will return the indices of esaxsnobs esaxs, saxs, maxs and waxs if given name of sample
def findSamples(samplist, name):
    found = []
    for i, samp in enumerate(samplist):
        if(samp.name == name):
            found.append(i)
    return found

#finds the ratio between Iq0 and Iq1 at a certain q value(point)
def findRatio(qq0, Iq0, qq1, Iq1, point ):
    i0 = np.where(qq0 > point)[0][0]
    i1 = np.where(qq1 > point)[0][0]
    return (Iq0[i0]/Iq1[i1])

#uses the findRatio function to find the average ratio between two list at three distinct points, used to align two lists together
def findAverageRatio(qq0,Iq0, qq1, Iq1, point1,point2,point3):
    return (findRatio(qq0, Iq0, qq1, Iq1, point1) + findRatio(qq0, Iq0, qq1, Iq1, point2) + findRatio(qq0, Iq0, qq1, Iq1, point3))/3

#returns a list of indices that are at the given temperature for linkam sampels, this requires the list to be already split up into multiple lists by temp (use splitLinkamSamples)
def findSamplesByTemp(temp,sample_list):
    lsts = []
    for i,j in enumerate(sample_list):
        if(j[0].temp == temp):
            lsts.append(i)
    return lsts

#this returns a list of lists which have been split by temperature, will only create a list if there are more than 1 sample at that temperature
def splitLinkamSamples(sample_list):
    samples_by_temps = []
    cur_sample_list  = []
    #this for loop splits the list by temperature
    for i,sample in enumerate(sample_list):
        if((i>0 and sample.temp != sample_list[i-1].temp) or i == len(sample_list)):
            samples_by_temps.append(cur_sample_list)
            cur_sample_list = []
        cur_sample_list.append(sample)
    k = 0
    #this while loop removes all samples that have only one value, comment out the while loop if you dont want this
    while(k< len(samples_by_temps)):
        if(len(samples_by_temps[k]) == 1):
            samples_by_temps.pop(k)
            k=k-1
        k = k+1
    return samples_by_temps

#returns a list of all temperatures for all the samples
def getLinkamTemps(sample_list):
    temps = [i.temp for i in sample_list]
    return temps

#returns a list of all times for all the samples
def getSampleTimes(sample_list):
    times = [datetime.strptime(i.time , '%c') for i in sample_list]
    return times
