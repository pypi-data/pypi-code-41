from os import path,getcwd,walk,makedirs,remove
import subprocess
from h5py import File
from xarray import open_dataset
from netCDF4 import Dataset
from pandas import Series,DataFrame
from scipy.sparse import coo_matrix
from numpy import array,unravel_index,nanmin,nanmax,isnan,nan,unique,zeros,isin
from numpy import uint8,float32
from sys import exit

class PrecipMatch(object):
    ''' Purpose: this class matches cloudsat precipitation flags and rain rates to cloudsat cloud objects
    '''

    def __init__(self,pArgs,):
        '''
        Purpose: this funtion initializes this class

        inputs:
            pArgs: command line arguments of type argparse
        '''

        self.rainRate   = pArgs.rainRate
        self.precipFlag = pArgs.precipFlag
        self.ncDir = pArgs.netCDF

    def run(self,fTypeHDF = 'h5'):
        '''
        purpose: run command line tool landSeaMaskCreate
        '''

        self.fType = fTypeHDF

        if(self._path_decision(self.rainRate) and not self._path_decision(self.precipFlag)):
            raise Exception ("add condition for only precipFlag being a packed tar archive")
            self._unpacked()
        elif(not self._path_decision(self.rainRate) and self._path_decision(self.precipFlag)):#only 2C-RAIN-PROFILE is a tar archive
            self.rainRate = self._packed(self.rainRate)
        elif(not self._path_decision(self.rainRate) and not self._path_decision(self.precipFlag)):#only 2C-RAIN-PROFILE is a tar archive
            self.rainRate   = self._packed(self.rainRate)
            self.precipFlag = self._packed(self.precipFlag)

        self.rainRateFiles   = self._ravel_files(self.rainRate,self.fType)
        self.precipFlagFiles = self._ravel_files(self.precipFlag,self.fType)
        self.ncFiles         = self._ravel_files(self.ncDir,'nc')

        self.rrDateTags = self._hdf_dateTag(self.rainRateFiles)
        self.pfDateTags = self._hdf_dateTag(self.precipFlagFiles)

        for i,self.ncFile in enumerate(self.ncFiles):
            ncDateTag    = path.basename(self.ncFile)
            ncDateTag    = path.splitext(ncDateTag)[0]
            ncDateTag    = ncDateTag.split('_')[0]

            #%%%%%%%%%%%%%%%%%%%%%%%%%if either the 2C-RAIN-PROFILE or 2C-PRECIP-COLUMN file do not exist delete output netcdf%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            try:    self.rrFile  = self.rainRateFiles[self.rrDateTags.index(ncDateTag)]
            except: 
                remove(self.ncFile)
                continue
            try:    self.pfFile  = self.precipFlagFiles[self.pfDateTags.index(ncDateTag)]
            except: 
                remove(self.ncFile)
                continue
            #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

            self.rrh5Obj = File(self.rrFile,'r')#read 2C-RAIN-PROFILE data
            self.pfh5Obj = File(self.pfFile,'r')#read 2C-PRECIP-COLUMN data

            #%%%%%%%%%%%%%%%%%%%%%%%%%%%%read datasets%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            self.rrDataset                                  = self.rrh5Obj['2C-RAIN-PROFILE']
            self.rrDataFields,self.rrGeoFields,self.rrSwath = self._h5_outside_datasets(self.rrDataset)  

            self.pfDataset                                  = self.pfh5Obj['2C-PRECIP-COLUMN']
            self.pfDataFields,self.pfGeoFields,self.pfSwath = self._h5_outside_datasets(self.pfDataset)  

            self.rainRateVariable = array(self.rrDataFields['rain_rate'][:].tolist()).flatten()
            self.rainRateVariable = self._scaleAdjust('rain_rate',self.rainRateVariable,self.rrSwath)
            self.rainRateVariable = self._maskData('rain_rate',self.rainRateVariable,self.rrSwath)

            self.precipFlagVariable = array(self.pfDataFields['Precip_flag'][:].tolist()).flatten()
            self.precipFlagVariable[self.precipFlagVariable > 3] = 0
            self.precipFlagVariable[self.precipFlagVariable < 0] = 0

            self._extract_sparce_datasets()

            if(self._nc_contains('rain_rate') or self._nc_contains('rain_fraction')):
                self.ncData.close()
            else:
                self._sparce_to_full()

                #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%do precipitation analysis%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                self.rain_certain()
                self.rain_certain_and_probable()
                self.rain_certain_and_probable_and_possible()
                self.combine_rain_flags()
                self.rain_rate()
                #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

                self.ncData.close()
                self._append_to_netcdf()

    def rain_rate(self,):
        '''
        Purpose: This function uses the pandas groupby functionality to find the lowest cloudy bin (maximum j index) along the orbit path (x index) to find the min, mean, median, and maximum rain rate for raining cloud objects
        '''
        df_all = DataFrame(
                {
                    'objects' : Series(self.sparceObjects),
                    'xIndc'   : Series(self.xIndc),
                    'yIndc'   : Series(self.yIndc),
                    }
                )

        df_lowestOBJ = df_all.groupby('xIndc').max() # max j index corresponds with the lowest height bin along each x index

        rr = self.rainRateVariable[df_lowestOBJ.index.values]#rain rate
        rr[isnan(rr)] = 0
        rrMsk = rr > 0#rain rate cloud mask

        all_clds = self.full_objs[df_lowestOBJ.index.values,df_lowestOBJ.yIndc.values]
        raining_clds = all_clds[rrMsk]
        cld_rainRate = rr[rrMsk]

        rain_df = DataFrame({'objects' : Series(raining_clds),'rain rate' : Series(cld_rainRate)})

        rain_min    = rain_df.groupby('objects').min()
        rain_mean   = rain_df.groupby('objects').mean()
        rain_median = rain_df.groupby('objects').median()
        rain_max    = rain_df.groupby('objects').max()
        rain_objs   = rain_max.index.values

        out_clds    = unique(df_all.objects.values)
        out_cld_msk = isin(out_clds,rain_objs) 
        out_min    = zeros(out_clds.size,dtype = float)
        out_mean   = zeros(out_clds.size,dtype = float)
        out_median = zeros(out_clds.size,dtype = float)
        out_max    = zeros(out_clds.size,dtype = float)

        out_min[out_cld_msk]    = rain_min['rain rate'].values
        out_mean[out_cld_msk]   = rain_mean['rain rate'].values
        out_median[out_cld_msk] = rain_median['rain rate'].values
        out_max[out_cld_msk]    = rain_max['rain rate'].values

        self.rain_rate_stats = array(
                [
                    out_min,
                    out_mean,
                    out_median,
                    out_max
                    ]
                ).T

        
    def combine_rain_flags(self,):
        '''
        '''
        self.three_flags = array([self.rainCertainFraction,self.rainCertainProbableFraction,self.rainCertainProbablePossibleFraction]).T

    def rain_certain(self,):
        '''
        Purpose: This function uses the pandas groupby functionality to find the lowest cloudy bin (maximum j index) along the orbit path (x index) and identify raining cloud objects using the rain certain flag
        '''
        df_all = DataFrame(##sparce cloud objects and corresponding x and y indices
                {
                    'objects' : Series(self.sparceObjects),
                    'xIndc'   : Series(self.xIndc),
                    'yIndc'   : Series(self.yIndc),
                    }
                )

        df_lowestOBJ = df_all.groupby('xIndc').max()# max i index corresponds with the lowest height bin along each x index

        full_clds = self.full_objs[df_lowestOBJ.index.values,df_lowestOBJ.yIndc.values]
        all_clds,all_cnts = unique(full_clds,return_counts = True)

        pFlag = self.precipFlagVariable[df_lowestOBJ.index.values]
        certMsk = pFlag == 3#precip certain

        certCLDS = full_clds[certMsk]
        certCLDS,certCnt = unique(certCLDS,return_counts = True)

        cldMsk   = isin(all_clds,certCLDS)
        certFrac = certCnt / all_cnts[cldMsk]

        out_clds = unique(df_all['objects'])
        outCld_msk = isin(out_clds,certCLDS)

        out_fraction             = zeros(df_all['objects'].unique().size,dtype = float)
        out_fraction[outCld_msk] = certFrac

        self.rainCertainFraction = out_fraction

    def rain_certain_and_probable(self,):
        '''
        Purpose: This function uses the pandas groupby functionality to find the lowest cloudy bin (maximum j index) along the orbit path (x index) and identify raining cloud objects using the rain certain and probable flag
        '''
        df_all = DataFrame(
                {
                    'objects' : Series(self.sparceObjects),
                    'xIndc'   : Series(self.xIndc),
                    'yIndc'   : Series(self.yIndc),
                    }
                )

        out_fraction = zeros(df_all['objects'].unique().size,dtype = float)

        df_lowestOBJ = df_all.groupby('xIndc').max()# max i index corresponds with the lowest height bin along each x index

        full_clds = self.full_objs[df_lowestOBJ.index.values,df_lowestOBJ.yIndc.values]
        all_clds,all_cnts = unique(full_clds,return_counts = True)

        pFlag = self.precipFlagVariable[df_lowestOBJ.index.values]
        certMsk = pFlag > 1

        certCLDS = full_clds[certMsk]
        certCLDS,certCnt = unique(certCLDS,return_counts = True)

        cldMsk   = isin(all_clds,certCLDS)
        certFrac = certCnt / all_cnts[cldMsk]

        out_clds = unique(df_all['objects'])
        outCld_msk = isin(out_clds,certCLDS)

        out_fraction[outCld_msk] = certFrac

        self.rainCertainProbableFraction = out_fraction

    def rain_certain_and_probable_and_possible(self,):
        '''
        Purpose: This function uses the pandas groupby functionality to find the lowest cloudy bin (maximum j index) along the orbit path (x index) and identify raining cloud objects using the rain certain and probable and possible flag
        '''
        df_all = DataFrame(
                {
                    'objects' : Series(self.sparceObjects),
                    'xIndc'   : Series(self.xIndc),
                    'yIndc'   : Series(self.yIndc),
                    }
                )

        out_fraction = zeros(df_all['objects'].unique().size,dtype = float)

        df_lowestOBJ = df_all.groupby('xIndc').max()# max i index corresponds with the lowest height bin along each x index

        full_clds = self.full_objs[df_lowestOBJ.index.values,df_lowestOBJ.yIndc.values]
        all_clds,all_cnts = unique(full_clds,return_counts = True)

        pFlag = self.precipFlagVariable[df_lowestOBJ.index.values]
        certMsk = pFlag > 0

        certCLDS = full_clds[certMsk]
        certCLDS,certCnt = unique(certCLDS,return_counts = True)

        cldMsk   = isin(all_clds,certCLDS)
        certFrac = certCnt / all_cnts[cldMsk]

        out_clds = unique(df_all['objects'])
        outCld_msk = isin(out_clds,certCLDS)

        out_fraction[outCld_msk] = certFrac

        self.rainCertainProbablePossibleFraction = out_fraction

    def _sparce_to_full(self,):
        self.full_objs = array(coo_matrix((self.sparceObjects,(self.xIndc,self.yIndc)),shape = self.orbitShape).todense())

    def _unpacked(self,):
        '''
        Purpose: work with unpacked Data
        '''
        #    #self._extract_sparce_datasets()
        #    #self._landSeaMask()
        #    #self.ncData.close()
        #    #self._append_to_netcdf()


    def _packed(self,dirIn):
        '''
        Purpose: this function works with tar archives
        '''
        inputDir                 = path.split(dirIn)[1]
        inputDir,compressionType = path.splitext(inputDir)
        inputDir                 = path.splitext(inputDir)[0]
        ##%%%%%%%%%%%%%%%%%%%%%%%%%%write as utility function that can be used by several different classes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if(compressionType == '.xz'):
            subprocess.call(['tar','xJvf',dirIn])
        elif(compressionType == '.gz'):
            subprocess.call(['tar','xzvf',dirIn])
        else:
            raise Exception("add decompression of other variables")
        #%%%%%%%%%%%%%%%%%%%%%%%%%%write as utility function that can be used by several different classes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
        return f'{getcwd()}/{inputDir}'
        #self._unpacked()

    def _append_to_netcdf(self,):
        '''
        '''
        self.ncOut  = Dataset(self.ncFile,'a')

        self.rainFlag_dim = self.ncOut.createDimension('rain_flag_combination',self.three_flags.shape[-1])

        self.varRR = self.ncOut.createVariable(
                'rain_rate',
                float32,
                ('allObjects_unq','stats'),
                )
        self.varRR.description = 'Rain rate statistics for individual cloud objects'

        self.varRR[:,] = self.rain_rate_stats

        self.varPF = self.ncOut.createVariable(
                'rain_fraction',
                float32,
                ('allObjects_unq','rain_flag_combination'),
                )
        self.varPF.description = 'Fraction of rain each individual cloud object produces based on flags from 2B-PRECIP-COLUMN product'
        self.varPF.row_1       = 'only rain certain flag included'
        self.varPF.row_2       = 'rain certain and probable included'
        self.varPF.row_3       = 'rain certain,probable and possible included'

        self.varPF[:,] = self.three_flags
        self.ncOut.close()

    def _extract_sparce_datasets(self,):
        self.ncData           = open_dataset(self.ncFile)
        self.orbitShape       = self.ncData.cloudSat_shape.values
        self.sparceObjects    = self.ncData.sparce_objects.values
        self.sparceIndices    = self.ncData.sparce_1d_indx.values
        self.xIndc,self.yIndc = unravel_index(self.sparceIndices,self.orbitShape)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%5
    def _hdf_dateTag(self,files):
        self.hdfDateTags = []
        for f in files:
            tmpF = path.basename(f)
            tmpF = path.splitext(tmpF)[0]
            tmpF = tmpF.split('_')[0]
            self.hdfDateTags.append(tmpF)

        return self.hdfDateTags

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
    def _h5_outside_datasets(self,dset):
        '''
        '''
        
        geoFields  = dset['Geolocation Fields']
        dataFields = dset['Data Fields']
        swath      = dset['Swath Attributes']

        return dataFields,geoFields,swath

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%write as a utility function%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    def _scaleAdjust(self,variable,var,swath):
        '''
        purpose: remove scale and offset from h5-data variable

        inputs:
            variable (string):     variable name in h5 file
            var      (ndarray):    data associated with variable
            swath    (h5 dataset): variable attributes

        outputs:
            scaled and offset version of var (see return statement)
        '''
    
        varSwath = [s for s in swath.keys() if variable in s and '_t' not in s]
        factor   = swath[[s for s in varSwath if 'factor' in s][0]][0][0]
        offset   = swath[[s for s in varSwath if 'offset' in s][0]][0][0]

        return (var * factor) + offset

    def _maskData(self,variable,var,swath):
        '''
        '''
        varSwath = [s for s in swath.keys() if variable in s and '_t' not in s]
        fill       = swath[[s for s in varSwath if 'missing' in s][0]][0][0]
        validRange = swath[[s for s in varSwath if 'range' in s][0]][0][0]

        var[isnan(var)] = fill
        var[~((var <= max(validRange)) & (var >= min(validRange)))] = fill
        var[var == fill] = nan

        return var

    def _nc_contains(self,var):
        '''
        '''
        return self.ncData.__contains__(var)
