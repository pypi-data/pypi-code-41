import os
import glob
import numpy as np
import tifffile
import fabio
import matplotlib.pyplot as plt

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


#saves image of tiff to directory
def save2DSAXS(image_list):
    # Set save path (default to current working directory)
    cwd = os.getcwd()
    save_path = cwd
    # Loop through sample list from importImages
    samp_names = []
    ii = 0
    for i, longname in enumerate(image_list):
        # Trim sample name
        cutdir = longname.rfind('/')
        cutend = longname.rfind('.')
        samp_name = longname[0:cutend]
        samp_name = samp_name.replace('-', '_')
        samp_names.append(samp_name)
        # Make plot for image
        fig, axs = plt.subplots(1, 1, figsize=(5, 5), constrained_layout=True)
        fig.suptitle(samp_names[i] + ' 2Dtiffs\n', fontsize=16)
        if True:
            axs.spines["top"].set_visible(False)
            axs.spines["right"].set_visible(False)
            axs.get_xaxis().tick_bottom()
            axs.get_yaxis().tick_left()
            axs.tick_params(axis='both', which='major', direction='in', top=True, right=True, length=0, width=0)
            axs.tick_params(axis='both', which='minor', direction='in', top=True, right=True, length=0, width=0)
            for tick in axs.xaxis.get_major_ticks():
                tick.label1.set_fontsize(0)
            for tick in axs.yaxis.get_major_ticks():
                tick.label1.set_fontsize(0)
        img = np.array(tifffile.imread(image_list[i]))
        # Pull data (center) from meta data
        sampleinfo = loadSample(image_list[i])
        center0 = np.int(float(sampleinfo.center0))
        center1 = np.int(float(sampleinfo.center1))
        # Change trip size around center
        trim0 = 100
        trim1 = 100
        Vmax = img.max() / 2
        imgZoomed = img[(center0 - trim0):(center0 + trim0),
                    (center1 - trim1):(center1 + trim1)]
        axs.imshow(imgZoomed, cmap='viridis', vmin=0, vmax=Vmax)

        plt.show()

        try:
            save_file = str(sampleinfo.name + '_' + str(ii).zfill(4) + '.png')
            savefig = os.path.join(save_path, save_file)
            fig.savefig(savefig, format='png', dpi=300)
        except:
            save_file = str(sampleinfo.file + '_' + str(ii).zfill(4) + '.png')
            savefig = os.path.join(save_path, save_file)
            fig.savefig(savefig, format='png', dpi=300)
        ii = ii + 1
