from os import path,getcwd,walk,makedirs
import subprocess
from h5py import File
from xarray import open_dataset
from netCDF4 import Dataset
from pandas import Series,DataFrame
from numpy import array,unravel_index
from numpy import uint8
from sys import exit

class LSM(object):
    '''
    Purpose: this class creates the land-sea mask for the cloud object files
    '''

    def __init__(self,pArgs,):
        '''
        Purpose: this funtion initializes this class

        inputs:
            pArgs: command line arguments of type argparse
        '''

        self.input = pArgs.input
        self.ncDir = pArgs.netCDF

    def run(self,fTypeHDF = 'h5'):
        '''
        purpose: run command line tool landSeaMaskCreate
        '''

        self.fType = fTypeHDF

        if(self._path_decision(self.input)):
            self._unpacked()
        else:
            self._packed()

    def _landSeaMask(self,):
        '''
        purpose: determine whether cloud objects occur over land or ocean
        '''
        self.landSeaMask = array(self.dataFields['Navigation_land_sea_flag'][:,].tolist()).flatten()#0=land 1=coast 2=ocean
        self.landSeaMask = self.landSeaMask[self.sparceIndices]
        self.landSeaMask = DataFrame({'objects' : Series(self.sparceObjects),'lsm' : Series(self.landSeaMask)})
        self.landSeaMask = self.landSeaMask.groupby('objects').mean()
        self.landSeaMask = self.landSeaMask.lsm.values
        self.landSeaMask[self.landSeaMask != 2] = 0
        self.landSeaMask[self.landSeaMask == 2] = 1
        
    def _unpacked(self,):
        '''
        Purpose: work with unpacked Data
        '''
        self.geoprofInput = self._ravel_files(self.input,self.fType)
        self.ncFiles      = self._ravel_files(self.ncDir,'nc')

        self._hdf_dateTag()

        for i,self.ncFile in enumerate(self.ncFiles):
            ncDateTag        = path.basename(self.ncFile)
            ncDateTag        = path.splitext(ncDateTag)[0]
            ncDateTag        = ncDateTag.split('_')[0]
            self.geoprofFile = self.geoprofInput[self.hdfDateTags.index(ncDateTag)]
            self.h5Obj   = File(self.geoprofFile,'r') ## read hdf5 file
            try: self.dataset = self.h5Obj['2B-GEOPROF']
            except: raise Exception('Must be 2B-GEOPROF CloudSat Product')
            self._h5_outside_datasets()
            self._extract_sparce_datasets()
            self._landSeaMask()
            self.ncData.close()
            self._append_to_netcdf()


    def _packed(self):
        '''
        Purpose: this function works with tar archives
        '''
        inputDir                 = path.split(self.input)[1]
        inputDir,compressionType = path.splitext(inputDir)
        inputDir                 = path.splitext(inputDir)[0]
        #%%%%%%%%%%%%%%%%%%%%%%%%%%write as utility function that can be used by several different classes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if(compressionType == '.xz'):
            subprocess.call(['tar','xJvf',self.input])
        else:
            raise Exception("add decompression of other variables")
        #%%%%%%%%%%%%%%%%%%%%%%%%%%write as utility function that can be used by several different classes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        self.input = f'{getcwd()}/{inputDir}'

    def _append_to_netcdf(self,):
        '''
        '''
        self.ncOut  = Dataset(self.ncFile,'a')

        self.varLSM = self.ncOut.createVariable(
                'lsm_flag',
                uint8,
                ('allObjects_unq',),
                )
        self.varLSM.description = 'ocean and land cloud object flag'
        self.varLSM.land_clouds  = 0
        self.varLSM.ocean_clouds = 1
        self.varLSM[:,] = self.landSeaMask
        self.ncOut.close()

    def _extract_sparce_datasets(self,):
        self.ncData        = open_dataset(self.ncFile)
        self.orbitShape    = self.ncData.cloudSat_shape.values
        self.sparceObjects = self.ncData.sparce_objects.values
        self.sparceIndices = self.ncData.sparce_1d_indx.values
        self.sparceIndices = unravel_index(self.sparceIndices,self.orbitShape)[0]

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%5
    def _hdf_dateTag(self,):
        self.hdfDateTags = []
        for f in self.geoprofInput:
            tmpF = path.basename(f)
            tmpF = path.splitext(tmpF)[0]
            tmpF = tmpF.split('_')[0]
            self.hdfDateTags.append(tmpF)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%5
    def _ravel_files(self,inDir,fType):
        inFiles = []
        for dp,dn,filenames in walk(inDir):
            for f in filenames:
                if(path.splitext(f)[-1] == f'.{fType}'): inFiles.append(path.join(dp,f))
        sorted(inFiles)

        return inFiles
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%5

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def _path_decision(self,directory):
        return path.isdir(directory)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def _h5_outside_datasets(self):
        '''
        '''
        
        self.geoFields  = self.dataset['Geolocation Fields']
        self.dataFields = self.dataset['Data Fields']
        self.swath      = self.dataset['Swath Attributes']
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%
