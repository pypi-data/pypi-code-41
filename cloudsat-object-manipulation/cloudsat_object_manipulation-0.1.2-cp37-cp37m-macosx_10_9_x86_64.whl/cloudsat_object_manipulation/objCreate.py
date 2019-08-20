from os import path,walk,getcwd,makedirs
import subprocess
from functools import reduce,partial
from operator import add
from math import ceil,log2
from h5py import File
#%%%%%%%%%%%%%%%%%%%%%import package to calculate cloud object properties%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from cloudsat_object_manipulation import cloud_stats
#%%%%%%%%%%%%%%%%%%%%%import c-extension that will use the layer top and base heights to create a binary (0,1) array to label contiguous regions%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import LayerObjects
#%%%%%%%%%%%%%%%%%%%%%import numpy package to reorder array along axis%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from numpy import take_along_axis
#%%%%%%%%%%%%%%%%%%%%%import package to convert list to ndarray%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from numpy import array,zeros
##%%%%%%%%%%%%%%%%%%%%%import package to identify the unique values of a ndarray%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from numpy import unique
#%%%%%%%%%%%%%%%%%%%%%import package to create a mask array based on values in another array%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from numpy import isin
#%%%%%%%%%%%%%%%%%%%%%import packages to convert x-indices and y-indices to and from a 1d array of flattened indices%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from numpy import ravel_multi_index,unravel_index
#%%%%%%%%%%%%%%%%%%%%%impoort package to round ndarray%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from numpy import round,floor
#%%%%%%%%%%%%%%%%%%%%%impoort pandas packages to constrain lat and lon bounds on identified cloud objects%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from pandas import DataFrame,Series
#%%%%%%%%%%%%%%%%%%%%%import package that can be used to label contiguous regions of a 2-d array%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from scipy.ndimage import label
#%%%%%%%%%%%%%%%%%%%%%import scipy package to create sparce 2d array and associated properties%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from scipy.sparse import csr_matrix,coo_matrix
#%%%%%%%%%%%%%%%%%%%%%import xarray dataset to create output netcdf file%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from xarray import Dataset
#%%%%%%%%%%%%%%%%%%%%%import numpy dtypes nessesary%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
from numpy import uint8,int32,float32,finfo

class cloudSatObjects(object):
    '''
    '''

    def __init__(self,pArgs,):
        '''
        '''
        self.input       = pArgs.input
        self.output      = pArgs.output
        self.scale       = pArgs.scale
        self.mask        = pArgs.mask
        self.idVars      = reduce(add,pArgs.idVariables)
        self.verbose     = pArgs.verbose
        self.overwrite   = pArgs.overwrite
        self.dataset_arg = pArgs.dataset
        
        self.layerFlag = 'LayerBase' in self.idVars and 'LayerTop' in self.idVars

        '''Check that only two input variables have been given through the command line'''
        assert len(self.idVars) == 2,'Only accepts two input variables'

    def run(self,fType = 'h5'):
        '''
        '''

        self.fType = fType

        if(self._path_decision(self.input)):
            self._unpacked()
        else:
            self._packed()

    def varDict(self,variable,dSet,swath,scale = True,fill = True,):
        '''
        '''
        self.var = dSet[variable][:,]
    
        varSwath = [s for s in swath.keys() if variable in s and '_t' not in s]
    
        if(scale):
            self.scaleFactor = swath[[s for s in varSwath if 'factor' in s][0]][0][0]
            self.offset      = swath[[s for s in varSwath if 'offset' in s][0]][0][0],
            var = self._scaleAdjust()
        if(fill):  
            self.missing    = swath[[s for s in varSwath if 'missing' in s][0]][0][0]
            self.missing_op = swath[[s for s in varSwath if 'missop' in s][0]][0][0],
            self.validRange = swath[[s for s in varSwath if 'range' in s][0]][0][0],

        return (variable,self.var)

    def _unpacked(self):
        '''
        '''

        self._ravel_files()

        if(not self._path_decision(self.output)): self._create_output_dir()
        
        for i,self.file in enumerate(self.inFiles):
            self._format_output_file_name()
            if(self._overwrite_output_file()): continue
            self.h5Obj   = File(self.file,'r')                  ## read hdf5 file
            self.dataset = self.h5Obj[self.dataset_arg] ## obtain datafields
            self._h5_outside_datasets()                 ## separate datafields
            self.height = self.geoFields['Height'][:,]  ## pull height fields
            if(len(self.idVars) == 2):
                self._var_dict()
                self._create_binary()
            else: raise Exception("add condition for only one variable")
            self._createObjects()
            self._create_sparce()
            self._remove_single_bin_clouds()
            self.sparce_flat_indx = ravel_multi_index((self.csr_indx,self.csr_indy),self.cloudObjects.shape)

            #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            #ADD cloud object statistics
            #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            self._cStats()
            self._min_max_lat_lon()
            self._single_layer_clouds()
            self._verbose_file_name()
            self._write_netcdf()

            #if(i == 100): break
    
    def _packed(self):
        path.split(self.input)[1].split('.')[0]
        #%%%%%%%%%%%%%%%%%%%%%%%%%%write as utility function that can be used by several different classes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if(path.splitext(self.input)[-1] == '.xz'):
            subprocess.call(['tar','xJvf',self.input])
        else:
            raise Exception("add decompression of other variables")
        #%%%%%%%%%%%%%%%%%%%%%%%%%%write as utility function that can be used by several different classes%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        self.input = f'{getcwd()}/{path.split(self.input)[1].split(".")[0]}'
        self._ravel_files()

        if(not self._path_decision(self.output)): self._create_output_dir()
        
        for i,self.file in enumerate(self.inFiles):
            self._format_output_file_name()
            if(self._overwrite_output_file()): continue
            self.h5Obj   = File(self.file,'r')                  ## read hdf5 file
            self.dataset = self.h5Obj[self.dataset_arg] ## obtain datafields
            self._h5_outside_datasets()                 ## separate datafields
            self.height = self.geoFields['Height'][:,]  ## pull height fields
            if(len(self.idVars) == 2):
                self._var_dict()
                self._create_binary()
            else: raise Exception("add condition for only one variable")
            self._createObjects()
            self._create_sparce()
            self._remove_single_bin_clouds()
            self.sparce_flat_indx = ravel_multi_index((self.csr_indx,self.csr_indy),self.cloudObjects.shape)

            #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            #ADD cloud object statistics
            #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
            self._cStats()
            self._min_max_lat_lon()
            self._single_layer_clouds()
            self._verbose_file_name()
            self._write_netcdf()

            #if(i == 100): break

    def _verbose_file_name(self,):
        '''
        '''
        if(self.verbose): print(self._output_file)

    def _overwrite_output_file(self,):
        '''
        '''
        if(self.overwrite and path.exists(self._output_file)):
            return True
        else:
            return False

    def _path_decision(self,directory):
        return path.isdir(directory)

    def _create_output_dir(self,):
        '''
        '''
        makedirs(self.output)

    def _format_output_file_name(self,):
        '''
        '''
        self._output_file = f'{self.output}/{path.basename(self.file).split("_")[0]}_all_cloud_objects_2B-GEOPROF-LIDAR-Layer-identification.nc'

    def _ravel_files(self):
        self.inFiles = []
        for dp,dn,filenames in walk(self.input):
            for f in filenames:
                if(path.splitext(f)[-1] == f'.{self.fType}'): self.inFiles.append(path.join(dp,f))
        sorted(self.inFiles)

    def _h5_outside_datasets(self):
        '''
        '''
        
        self.geoFields  = self.dataset['Geolocation Fields']
        self.dataFields = self.dataset['Data Fields']
        self.swath      = self.dataset['Swath Attributes']

    def _var_dict(self):
        '''
        '''
        self.inDict = dict(
                map(
                    partial(self.varDict,
                        dSet  = self.dataFields,
                        swath = self.swath,
                        scale = self.scale,
                        fill  = self.mask,
                        ),
                    self.idVars
                    )
                )
        varMsk  = self.inDict[self.idVars[0]] - self.inDict[self.idVars[-1]]
        topMsk  = self.inDict[self.idVars[0]] < 0
        baseMsk = self.inDict[self.idVars[-1]] < 0

        self.inDict[self.idVars[0]][topMsk]  = -99
        self.inDict[self.idVars[0]][baseMsk] = -99
        self.inDict[self.idVars[0]][varMsk < 0] = -99

        self.inDict[self.idVars[-1]][topMsk]  = -99
        self.inDict[self.idVars[-1]][baseMsk] = -99
        self.inDict[self.idVars[-1]][varMsk < 0] = -99

        reorder_arr = (-1 * self.inDict[self.idVars[-1]]).argsort(axis = 1)
        self.inDict[self.idVars[0]]  = take_along_axis(self.inDict[self.idVars[0]],reorder_arr,axis = 1)
        self.inDict[self.idVars[-1]] = take_along_axis(self.inDict[self.idVars[-1]],reorder_arr,axis = 1)
        #exit()

    def _create_binary(self,):
        '''
        '''
        test = self.inDict[self.idVars[0]] - self.inDict[self.idVars[-1]]
        self.binaryData = LayerObjects.createBinary(
                self.inDict[self.idVars[0]].astype(int32),
                self.inDict[self.idVars[-1]].astype(int32),
                self.height.astype(int32),
                -99, ##fill value
                )

    def _createObjects(self,):
        '''
        '''
        self.cloudObjects,self.numObjects = label(self.binaryData)

    def _create_sparce(self,):
        '''
        '''
        self.csr_cOBJS        = csr_matrix(self.cloudObjects[:,:]).tocoo()
        self.csr_indx         = array(self.csr_cOBJS.row)
        self.csr_indy         = array(self.csr_cOBJS.col)
        self.csr_data         = array(self.csr_cOBJS.data)

    def _remove_single_bin_clouds(self,):
        '''
        '''
        unqCLDS,unqCnts   = unique(self.csr_data,return_counts = True)
        noSinglePixelClds = unqCLDS[unqCnts > 1]
        self.noSingleMsk  = isin(self.csr_data,noSinglePixelClds)
        self.csr_indx     = self.csr_indx[self.noSingleMsk]
        self.csr_indy     = self.csr_indy[self.noSingleMsk]
        self.csr_data     = self.csr_data[self.noSingleMsk]
        self.unq_clds     = noSinglePixelClds
        self.unq_full     = unique(self.cloudObjects[self.cloudObjects != 0])
        self.unq_msk      = isin(self.unq_full,self.unq_clds)

    def _cStats(self,):
        '''
        '''
        self._sparce_df  = DataFrame(
                {
                    'objects' : Series(self.csr_data), 
                    'indx'    : self.csr_indx, 
                    'indy'    : self.csr_indy,
                    }
                )
        self.objStatistics = cloud_stats.ObjectStatistics(self._sparce_df)
        self.objStatistics.cloud_extent()

        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%This function is SLOW NEEDS TO BE RE-WRITTEN%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        if(self.layerFlag): 
            self.objStatistics.cloud_layer_base_and_top(
                    self.inDict['LayerTop'],
                    self.inDict['LayerBase'],
                    self.cloudObjects,
                    self.height
                    )
        #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        
    def _write_netcdf(self,):
        '''
        '''

        data_dict = {
                'sparce_objects'    : (('sparce_1d_indx',),self.csr_data),
                'single_layer_flag' : (('allObjects_unq',),self.single_layer_clouds),
                'extent'            : (('allObjects_unq','stats'),self.objStatistics.extent_stats,),
                'top'               : (('allObjects_unq','stats'),self.objStatistics.topHeight[self.unq_msk].astype(float32) / 1000.,),
                'base'              : (('allObjects_unq','stats'),self.objStatistics.baseHeight[self.unq_msk].astype(float32) / 1000.,),
                'thickness'         : (('allObjects_unq','stats'),self.objStatistics.thickness[self.unq_msk].astype(float32) / 1000.,),
                'lat_bounds'        : (('allObjects_unq','geo_bounds'),self.lat_bounds),
                'lon_bounds'        : (('allObjects_unq','geo_bounds'),self.lon_bounds),
                }

        coords_dict = {
                'sparce_1d_indx' : self.sparce_flat_indx.astype(int32),
                'allObjects_unq' : self.unq_clds,
                'cloudSat_shape' : array(self.cloudObjects.shape),
                'stats'          : [1,2,3,4],
                }

        _outData = Dataset(data_vars = data_dict,coords = coords_dict)

        #_extent_offset,_extent_scale = self._add_scale_and_offset(_outData.extent.values)
        #_top_offset,_top_scale       = self._add_scale_and_offset(_outData.top.values)
        #_base_offset,_base_scale     = self._add_scale_and_offset(_outData.base.values)
        #_thick_offset,_thick_scale   = self._add_scale_and_offset(_outData.thickness.values)

        _outData.cloudSat_shape.attrs = self.set_var_attributes(
                _outData.cloudSat_shape,
                description = 'Shape of cloudsat orbit',
                )
        _outData.sparce_1d_indx.attrs = self.set_var_attributes(
                _outData.sparce_1d_indx,
                description = 'flattend indices of sparce_objects variable',
                )
        _outData.sparce_objects.attrs = self.set_var_attributes(
                _outData.sparce_objects,
                description = 'cloud objects corresponding to 1d coordinates from 2d cloudsat field',
                )
        _outData.allObjects_unq.attrs = self.set_var_attributes(
                _outData.allObjects_unq,
                description = 'unique list of cloud objects',
                )
        _outData.stats.attrs = self.set_var_attributes(
                _outData.stats,
                col_1 = 'min',
                col_2 = 'mean',
                col_3 = 'median',
                col_4 = 'max',
                )
        _outData.extent.attrs = self.set_var_attributes(
                _outData.extent,
                description = 'cloud object along-track extent',
                )
        _outData.top.attrs = self.set_var_attributes(
                _outData.top,
                description = 'cloud object top height',
                )
        _outData.base.attrs = self.set_var_attributes(
                _outData.base,
                description = 'cloud object base height',
                )
        _outData.thickness.attrs = self.set_var_attributes(
                _outData.thickness,
                description = 'cloud object thickness',
                )
        _outData.lat_bounds.attrs = self.set_var_attributes(
                _outData.lat_bounds,
                long_name = 'cloud object latitude bounds',
                units     = 'degrees north',
                )
        _outData.lon_bounds.attrs = self.set_var_attributes(
                _outData.lon_bounds,
                long_name = 'cloud object longitude bounds',
                units     = 'degrees east',
                )

        _outData.to_netcdf(
                self._output_file,
                format = 'NETCDF4',
                encoding = {
                    'sparce_objects'    : {'dtype' : 'int32'},
                    'single_layer_flag' : {'dtype' : 'uint8'},
                    'stats'             : {'dtype' : 'uint8'},
                    'cloudSat_shape'    : {'dtype' : 'uint16'},
                    'extent'            : {
                        'dtype'        : 'float32',
                        '_FillValue'   : -999.,
                        #'scale_factor' : _extent_scale,
                        #'add_offset'   : _extent_offset,
                        },
                    'top'              : {
                        'dtype'        : 'float32',
                        '_FillValue'   : -999.,
                        #'scale_factor' : _top_scale,
                        #'add_offset'   : _top_offset,
                        },
                    'base'             : {
                        'dtype'        : 'float32',
                        '_FillValue'   : -999.,
                        #'scale_factor' : _base_scale,
                        #'add_offset'   : _base_offset,
                        },
                    'thickness'        : {
                        'dtype'        : 'float32',
                        '_FillValue'   : -999.,
                        #'scale_factor' : _thick_scale,
                        #'add_offset'   : _thick_offset,
                        },
                    'lon_bounds'       : {
                        'dtype'        : 'float32',
                        '_FillValue'   : -999.,
                        #'scale_factor' : _thick_scale,
                        #'add_offset'   : _thick_offset,
                        },
                    'lat_bounds'       : {
                        'dtype'        : 'float32',
                        '_FillValue'   : -999.,
                        #'scale_factor' : _thick_scale,
                        #'add_offset'   : _thick_offset,
                        },
                    }
                )
        
    def _single_layer_clouds(self,):
        '''
        '''

        self.single_layer_clouds = zeros(self.unq_clds.shape,dtype = uint8)
        single_msk = DataFrame({'objects' : Series(self.csr_data),'indc' : Series(self.csr_indx)}).groupby('objects')['indc'].nunique().values
        self.single_layer_clouds[single_msk == 1] = 1

    def _min_max_lat_lon(self,):
        '''
        '''

        self.latitude  = array(self.dataset['Geolocation Fields']['Latitude'][:,].tolist()).flatten()
        self.longitude = array(self.dataset['Geolocation Fields']['Longitude'][:,].tolist()).flatten()

        df_geo = {
                'objects'   : Series(self.csr_data),
                'latitude'  : Series(self.latitude[self.csr_indx]),
                'longitude' : Series(self.longitude[self.csr_indx]),
                }
        df_geo     = DataFrame(df_geo)
        df_geo_min = df_geo.groupby('objects').min().copy()
        df_geo_max = df_geo.groupby('objects').max().copy()

        self.lat_bounds = array([df_geo_min['latitude'].values,df_geo_max['latitude'].values]).T.astype(float32)
        self.lon_bounds = array([df_geo_min['longitude'].values,df_geo_max['longitude'].values]).T.astype(float32)

    def set_var_attributes(self,variable,**kwargs,):
        for k,v in kwargs.items():
            variable.attrs[k] = v

        return variable.attrs

    def _add_scale_and_offset(self,data):
        '''
        '''
        precision = finfo(float32).precision 
        nvalues = 1 + ceil( (data.max() - data.min()) / (2 * precision))
        n = ceil(log2(nvalues))
        offset = data.min()
        scale = (data.max() - data.min()) / (2**n - 1)

        P = round((data - offset) / scale)
        
        return offset,scale

    def _scaleAdjust(self,):
        '''
        '''
    
        self.var = (self.var * self.scaleFactor) + self.offset

    def _maskData(self,):
        '''
        '''
    
        if(self.missing_op.decode() == '=='): self.var[self.var == self.missing] = self.missing
        else: raise Exception('need condition for other operators')

        self.var[~((self.var <= max(self.validRange)) & (data >= min(self.validRange)))] = self.missing

