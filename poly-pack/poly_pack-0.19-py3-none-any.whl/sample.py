import os
import glob
import numpy as np
import tifffile
import fabio

#importing all the masks that are default in the package
saxsmask = (fabio.open(os.path.join(os.path.dirname(__file__), 'saxsmask.edf'))).data
esaxsnobsmask = (fabio.open(os.path.join(os.path.dirname(__file__), 'esaxsnobsmax.edf'))).data
waxsmask = (fabio.open(os.path.join(os.path.dirname(__file__), 'waxsmask.edf'))).data
maxmask = (fabio.open(os.path.join(os.path.dirname(__file__), 'maxmask.edf'))).data
esaxsmask = (fabio.open(os.path.join(os.path.dirname(__file__), 'esaxsmask.edf'))).data

#imports all of the tiffs into a master list, split up by spot
def importImages(curDir, numSpots = 1):

    #setting the current directory
    os.chdir(curDir)

    #importing all the images
    images = glob.glob("*.tiff", recursive=True)
    images.sort(key=lambda str: str[:])
    image_list = []

    #splitting all the images into the different spots
    for i in range(numSpots):
        k = i
        cur_list = []
        cur_list.append(images[k])
        for image in images:
            if(k == numSpots):
                cur_list.append(image)
                k = 0
            k = k +1
        image_list.append(cur_list)
    return image_list

# sample object, to create one: loadSample(file), if a linkam sample, set temperature to true
class loadSample:
    def __init__(self, file, temperature = False):
        self.file = file
        self.tiff = np.array(tifffile.imread(self.file))
        with tifffile.TiffFile(file) as tif:
            self.tif_tags = {}
            for tag in tif.pages[0].tags.values():
                name, value = tag.name, tag.value
                self.tif_tags[name] = value
        self.name = self.findInfo("Description", 'Artist', ' ', 2)
        self.thickness = self.findInfo("sample_thickness", "Artist", "<",2)
        self.conf = self.findConf("in Conf ", 'Artist', ",",0)
        self.bstop = True if(float(self.findInfo("bstop", 'Artist', '<', 2)) > 0) else False
        self.dist = float(self.findInfo("detector_dist", "Artist", '<', 2))/1000
        self.center0 = self.findInfo("beamcenter_nominal", 'Artist', ' ', 2)
        self.center1 = self.findInfo(self.center0, 'Artist', '<', 4)
        self.time = self.findInfo("start_timestamp", 'Artist', '<', 2)
        if temperature :
            self.temp = float(self.findInfo("sample_temp", 'Artist', '<', 2))

    #these functions find information in the metadata, the marker is what you are looking for to find the variable, the key is whether you are looking in the Artist value or other metadata values, the endmarker is where you want the variable to cut off, and the shift is how much space to leave between the marker and the variable
    def findInfo(self, marker, key,endmarker, shift):
        startindex = self.tif_tags[key].find(marker) + len(marker) + shift
        endindex = self.tif_tags[key].find(endmarker, startindex)
        return self.tif_tags[key][startindex:endindex]
    def findConf(self, marker, key,endmarker, shift):
        startindex = self.tif_tags[key].find(marker) + len(marker) + shift
        endindex = startindex + 2
        return self.tif_tags[key][startindex:endindex]
