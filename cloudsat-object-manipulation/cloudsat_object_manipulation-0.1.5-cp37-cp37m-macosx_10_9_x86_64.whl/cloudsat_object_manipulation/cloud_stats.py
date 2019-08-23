import LayerObjects
from pandas import Series,DataFrame
from numpy import nan,isnan,nanmin
from numpy import unravel_index,abs,unique,array
from numpy import int32,float32
from sys import exit

class ObjectStatistics(object):
    '''
    '''

    def __init__(self,sparceObjects):
        '''
        '''
        self.sparceObjects = sparceObjects
        self.x_clds_flag = True
        
    def cloud_extent(self):
        '''
        '''
        self.extent  = ((self.sparceObjects.groupby(['indy','objects']).count() - 1) * 1.1) + 1.7
        self.extent  = self.extent.unstack()

        self.extent_stats = array([
                self.extent.min().values.tolist(), 
                self.extent.mean().values.tolist(),
                self.extent.median().values.tolist(),
                self.extent.max().values.tolist(),
                ]).T

    def cloud_layer_base_and_top(self,topData,baseData,fullObjects,height,fill = -99):
        '''
        '''
        self._topHeight   = []
        self._baseHeight  = []
        self._x_only_objs = []
        for i in range(topData.shape[0]):
            if(topData[i][0] == fill): continue
            tmpTop  = topData[i]
            tmpBase = baseData[i]

            tmpTop  = tmpTop[tmpTop != fill]
            tmpBase = tmpBase[tmpBase != fill]

            tmpObj_f = fullObjects[i,]
            tmpHgt   = height[i,]
            
            tmpObj         = tmpObj_f[tmpObj_f != 0]
            tmpObj,_yindc  = unique(tmpObj,return_index = True)
            tmpObj         = tmpObj[_yindc.argsort()]

            if(tmpObj.size == tmpTop.size):
                self._topHeight   += abs(tmpTop).tolist()
                self._baseHeight  += abs(tmpBase).tolist()
                self._x_only_objs += tmpObj.tolist()
            else:
                if(tmpObj.size == 1):
                    self._x_only_objs += tmpObj.tolist()
                    self._baseHeight  += [tmpBase.min()]
                    self._topHeight   += [tmpTop.max()]
                else:
                    for u in tmpObj:
                        hgt_sub = tmpHgt[tmpObj_f == u]
                        topMsk  = abs(hgt_sub.max() - tmpTop)
                        baseMsk = abs(hgt_sub.min() - tmpBase)

                        self._topHeight.append(tmpTop[topMsk.argmin()])
                        self._baseHeight.append(tmpBase[baseMsk.argmin()])
                        self._x_only_objs.append(u)

        self._topHeight  = array(self._topHeight)
        self._baseHeight = array(self._baseHeight)
        self._thickness  = self._topHeight - self._baseHeight
        self._x_only_objs = array(self._x_only_objs)

        assert self._thickness.min() >= 0,"Cloud Thickness must be >= 0"

        df_layers = {
                'objects': Series(self._x_only_objs),
                'top'    : Series(self._topHeight),
                'base'   : Series(self._baseHeight),
                'thick'  : Series(self._thickness),
                }
        df_layers = DataFrame(df_layers)

        min_stats    = df_layers.groupby('objects').min().copy()
        mean_stats   = df_layers.groupby('objects').mean()
        median_stats = df_layers.groupby('objects').median()
        max_stats    = df_layers.groupby('objects').max()

        self.topHeight = array(
                [
                    min_stats.top.values,
                    mean_stats.top.values,
                    median_stats.top.values,
                    max_stats.top.values
                    ]
                ).T
        self.baseHeight = array(
                [
                    min_stats.base.values,
                    mean_stats.base.values,
                    median_stats.base.values,
                    max_stats.base.values
                    ]
                ).T
        self.thickness = array(
                [
                    min_stats.thick.values,
                    mean_stats.thick.values,
                    median_stats.thick.values,
                    max_stats.thick.values
                    ]
                ).T
