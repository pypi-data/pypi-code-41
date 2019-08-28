# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Image common types class."""

import matplotlib.pyplot as plt
from ..environ import SparkEnv, PandasEnv, RuntimeEnv

class ImageAnalyzeResult:
    """the ImageSelector analyze result class."""

    def __init__(self, env: RuntimeEnv, resultDic: dict, target: str=None, edaNameList: list=None):
        """
        Initialize.

        :param env: the runtime environment of the class.
        :type env: RuntimeEnv
        :param resultDic: the analyze result dict.
        :type resultDic: dict
        :param target: the target to show.
        :type target: str
        :param edaNameList: the eda name list.
        :type edaNameList: list
        """
        self.env = env
        self.resultDic = resultDic
        self.target = target
        self.edaNameList = edaNameList

    def show(self, saveName: str=None):
        """
        show the result.

        if the target is 'Luminance' or 'Area', use scatter diagram, else barh diagram.
        :param saveName: the save path of the picture.
        :type saveName: str
        :return: figure if RuntimeEnv is SparkEnv
        :rtype: matplotlib.pyplot.figure
        """

        #close the plot shown before
        plt.close('all')
        fig = plt.figure(dpi=100)
        target = self.target
        if target is None:
            plt.title('There is no data or the edaFilterList is empty.')
            if type(self.env) == PandasEnv:
                plt.show()
            else:
                return fig
        elif target =='Luminance':
            xlabel = 'LuminanceMean'
            ylabel = 'LuminanceStd'
            self.__showAsScatter(target, xlabel, ylabel, saveName)
        elif target=='Area':
            xlabel = 'Width'
            ylabel = 'Height'
            self.__showAsScatter(target, xlabel, ylabel, saveName)
        else:
            self.__showAsBarh(target, self.edaNameList, saveName)
        
    def __showAsBarh(self, target: str, edaNameList: list=None, saveName: str=None, subNumber: int=3, limitClass: int=50):
        """
        show the result as barh diagram.

        :param target: the target to show.
        :type target: str
        :param edaNameList: the eda name list.
        :type edaNameList: list
        :param saveName: the save path of the picture.
        :type saveName: str
        :param subNumber: the subplot number: subNumber*subNumber.
        :type subNumber: int
        :param limitClass: only if data size greater than limitClass, then use subplot.
        :type limitClass: int
        :return: figure if RuntimeEnv is SparkEnv
        :rtype: matplotlib.pyplot.figure
        """
        dic = self.resultDic[target]
        label = list(dic.keys())
        length = len(label)
        y = [i for i in range (length)]
        width = list((dic.values()))
        fig = None
    
        if length > limitClass:
            axCount = subNumber*subNumber
            step = length//axCount
            fig = plt.figure(figsize=(25, 70))
            for i in range(axCount):
                ax = fig.add_subplot(subNumber,subNumber,i+1)
                if i==axCount-1:
                    ax.barh(y=range(length-i*step), width=width[:length-i*step], tick_label=label[:length-i*step], alpha=0.6, facecolor='steelblue', edgecolor='blue')
                else:
                    ax.barh(y=range(step), width=width[length-(i*step+step):length-(i*step)], tick_label=label[length-(i*step+step):length-(i*step)], alpha=0.6, facecolor='steelblue', edgecolor='blue')
            fig.suptitle(','.join(edaNameList), y=0.94)
        else:
            fig = plt.figure(figsize=(10, 5))
            ax = fig.add_subplot(111)
            box = ax.get_position()
            ax.set_position([box.x0*2, box.y0, 0.9-box.x0*2, box.height])
            plt.barh(y, width, tick_label=label, alpha=0.6, facecolor='steelblue', edgecolor='blue')
            plt.title(','.join(edaNameList))
        
        
        if saveName is not None:
            plt.savefig(saveName)

        if type(self.env) == PandasEnv:
            plt.show()
        else:
            return fig
        
    def __showAsScatter(self, target: str, xlabel: str, ylabel: str, saveName: str=None): 
        """
        show the result as scatter diagram.

        :param target: the target to show.
        :type target: str
        :param xlabel: the x label.
        :type xlabel: str
        :param ylabel: the y label.
        :type ylabel: str
        :param saveName: the save path of the picture.
        :type saveName: str
        :return: figure if RuntimeEnv is SparkEnv
        :rtype: matplotlib.pyplot.figure
        """
        dic = self.resultDic[target]
        x = list(dic.keys())
        y = list(dic.values())
        
        fig = plt.figure(dpi=100)
        plt.scatter(x, y, color='steelblue', marker='o', edgecolor='black', alpha=0.5)
        plt.title(target)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        if saveName is not None:
            plt.savefig(saveName)
            
        if type(self.env) == PandasEnv:
            plt.show()
        else:
            return fig