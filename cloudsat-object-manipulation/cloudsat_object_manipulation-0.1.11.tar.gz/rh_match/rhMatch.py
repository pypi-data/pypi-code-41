from os import path,walk,remove
from datetime import datetime
from xarray import open_dataset
from netCDF4 import Dataset
from h5py import File
from numpy import unravel_index,array,unique,digitize
from numpy import nan,isnan,nanmean
from numpy import float32
from sys import exit

class MatchRH(object):
    '''
    '''

    def __init__(self,glPath,rhPath,geopotentialPath,outDir):
        '''
        '''


        self.glPath           = glPath
        self.rhPath           = rhPath
        self.geopotentialPath = geopotentialPath
        self.ncDir            = outDir

    def run(self,):
        '''
        '''

        if(not self._path_decision(self.glPath)):
            self.glPath = self._packed(self.glPath)

        self.glFiles = self._ravel_files(self.glPath,'h5')
        self.ncFiles = self._ravel_files(self.ncDir,'nc')

        self.glDateTags = self._hdf_dateTag(self.glFiles)

        self.rhData           = open_dataset(self.rhPath)
        self.geopotentialData = open_dataset(self.geopotentialPath)

        for i,self.ncFile in enumerate(self.ncFiles):
            ncDateTag    = path.basename(self.ncFile)
            ncDateTag    = path.splitext(ncDateTag)[0]
            ncDateTag    = ncDateTag.split('_')[0]

            try: self.glFile = self.glFiles[self.glDateTags.index(ncDateTag)]
            except: 
                remove(self.ncFile)
                continue

            self.glh5Obj                                    = File(self.glFile,'r')#read 2B-GEOPROF-LIDAR data
            self.glDataset                                  = self.glh5Obj['2B-GEOPROF-LIDAR']
            self.glDataFields,self.glGeoFields,self.glSwath = self._h5_outside_datasets(self.glDataset)  
            self.objLat = array(self.glGeoFields['Latitude'][:,].tolist()).flatten()
            self.objLon = array(self.glGeoFields['Longitude'][:,].tolist()).flatten()

            self._extract_sparce_datasets()

            self.unq_clds = self.ncData.allObjects_unq.values

            self.rh = self.match_rh(self.objLat,self.objLon,self.rhData,self.geopotentialData,ncDateTag,)

            self.ncData.close()
            self._append_to_netcdf()

    def match_rh(self,cldLat,cldLon,rhData,geoData,date,res = 0.75,fill_value = -1e20):
        '''
        '''

        gravity = 9.87
        mTokm   = (1 / 1000.)
        date   = datetime.strptime(date,'%Y%j%H%M%S')

        rhData  = rhData.sel(time = date.strftime('%Y-%m-%d-%H'),method = 'nearest')
        geoData = geoData.sel(time = date.strftime('%Y-%m-%d-%H'),method = 'nearest')

        lat_bins = rhData.latitude.values + (res / 2.)
        lon_bins = rhData.longitude.values + (res / 2.)

        lat_bins = lat_bins[:-1]
        lon_bins = lon_bins[:-1]

        tmp_rh   = rhData.r.values
        tmp_geoZ = (geoData.z.values / gravity) * mTokm

        bnd_layer_msk = tmp_geoZ <= 3.
        tmp_rh[~bnd_layer_msk] = nan

        out_rh = array([fill_value] * self.unq_clds.size)

        for i,u in enumerate(self.unq_clds):
            tmp_sparceMsk  = self.sparceObjects == u
            tmpX           = unique(self.xIndc[tmp_sparceMsk])
            tmpLat         = cldLat[tmpX]
            tmpLon         = cldLon[tmpX]
            tmp_lat_bounds = digitize(tmpLat,bins = lat_bins)
            tmp_lon_bounds = digitize(tmpLon,bins = lon_bins)

            out_val = nanmean(tmp_rh[:,tmp_lat_bounds,tmp_lon_bounds])

            if(~isnan(out_val)): out_rh[i] = out_val

        return out_rh

    def _extract_sparce_datasets(self,):
        self.ncData           = open_dataset(self.ncFile)
        self.orbitShape       = self.ncData.cloudSat_shape.values
        self.sparceObjects    = self.ncData.sparce_objects.values
        self.sparceIndices    = self.ncData.sparce_1d_indx.values
        self.xIndc,self.yIndc = unravel_index(self.sparceIndices,self.orbitShape)

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

    def _packed(self,dirIn):
        '''
        Purpose: this function works with tar archives
        '''
        inputDir                 = path.split(dirIn)[1]
        inputDir,compressionType = path.splitext(inputDir)
        inputDir                 = path.splitext(inputDir)[0]

    def _hdf_dateTag(self,files):
        self.hdfDateTags = []
        for f in files:
            tmpF = path.basename(f)
            tmpF = path.splitext(tmpF)[0]
            tmpF = tmpF.split('_')[0]
            self.hdfDateTags.append(tmpF)

        return self.hdfDateTags

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def _h5_outside_datasets(self,dset):
        '''
        '''
        
        geoFields  = dset['Geolocation Fields']
        dataFields = dset['Data Fields']
        swath      = dset['Swath Attributes']

        return dataFields,geoFields,swath

    def _unit_conversions(self,):
        self.kmTom = 1000.

    def _append_to_netcdf(self,):
        '''
        '''
        self.ncOut  = Dataset(self.ncFile,'a')

        self.rh_var = self.ncOut.createVariable(
                'boundary_layer_relative_humidity',
                float32,
                ('allObjects_unq',),
                fill_value = -1e20,
                )
        self.rh_var.description = 'Relative Humidity within 3 km of the surface using 0.75 x 0.75 6-hourly ERA-Interim relative humidity and geopotential associated with each individual cloud object'
        self.rh_var.long_name = 'Relative Humidity'
        self.rh_var.units = '%'
        self.rh_var[:,] = self.rh

        self.ncOut.close()
