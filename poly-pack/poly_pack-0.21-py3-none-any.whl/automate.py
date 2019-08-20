from .data_processing import *
from .fitting import *

#function: given a directory and the number of spots(default to 1) will automatically load them, create samples from them and reduce them
def autoLoad(curDir, numSpots = 1):
    #import images
    imgs = importImages(curDir, numSpots)

    #take the lists of images(one list per spot) and turn them into samples to get metadata
    sampleList = []
    for i,lst in enumerate(imgs):
        cur_list = []
        for j in imgs[i]:
            cur_list.append(loadSample(j))
        sampleList.append(cur_list)

    #automatically finds the blank sample name
    blankSample = ""
    for i in sampleList:
        for j in i:
            if 'BLANK' in j.name.upper() and float(j.conf) == 24:
                blankSample = j.name
                break

    #reduces all the samples into the reductions list
    reductions = []
    #to access q and I for a specific sample reductions[index of sample][0 for q, 1 for I]
    for i in sampleList:
        for sample in i:
            #only want to reduce each sample once as the stitching function reduces all of the configurations at once, so only looking for esaxsnobs sample
            if not sample.bstop and float(sample.conf) == 24:
                q,I = stitching(i, sample, blankSample)
                #add a list with the qs and Is to the master reduction list
                reductions.append([q,I])

    return reductions
