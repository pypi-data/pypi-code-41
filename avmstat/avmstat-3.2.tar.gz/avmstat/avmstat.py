import pandas as pd
import numpy as np
import seaborn as sea
import math

empty = pd.DataFrame

class modelPerformance:

    def __init__(self, df, URN, modelName, predictedPrice, confidence, actualPrice, confidenceTollerence = 0.01):
        self.df = df
        self.urn = df[URN]
        self.val = df[predictedPrice]
        self.name = modelName
        self.fsd = df[confidence]
        self.ref = df[actualPrice]
        self.err = self.__error()
        self.absErr = self.__absError()
        self.perfB_stand = self.__performanceBand()
        self.valueB = self.__valueBand()
        self.fsdB_stand = self.__confidenceBand()
        self.withinConf = self.__withinConfidence(confidenceTollerence)
        
    #Error
    def __error(self):
        return ((self.val - self.ref)/self.ref)

    #Absolute Error
    def __absError(self):
        return abs(((self.val - self.ref)/self.ref))

    #FSD Bands
    def __confidenceBand(self):
        return pd.cut(self.fsd, [-1,0.1,0.15,0.20,0.30,1000], labels = ["0-10", "11-15", "16-20", "21-30", "30+"])

    #Performance Bands
    def __performanceBand(self):
        return pd.cut(self.absErr.values, [-1,0.1,0.15,0.20,0.30,1000], labels = ["0-10", "11-15", "16-20", "21-30", "30+"])

    #value Bands
    def __valueBand(self):
        return pd.cut(self.ref.values, [-1,50000,100000,150000,300000,500000,750000,1000000,100000000], labels = ["->£50,000", "->£100,000", "->£150,000", "->£300,000", "->£500,000", "->£750,000", "->£1,000,000", "£1,000,000++"])

    def __withinConfidence(self, tollerence):
        wC_1 = np.where((self.absErr) <= (self.fsd + tollerence), 1,0)
        wC_s = pd.Series(wC_1)
        return wC_s

    def appendPerformance(self):
        df = pd.DataFrame()
        df['URN'] = self.urn
        df['predictedValue'] = self.val
        df['confidenceScore'] = self.fsd
        df['comparePrice'] = self.ref
        df['error'] = self.err
        df['absoluteError'] = self.absErr
        df['performanceBands'] = self.perfB_stand
        df['confidenceBand'] = self.fsdB_stand
        df['withinConfidence'] = self.withinConf
        return df                    

    def modelStatistics(self, printResults = 'Yes'):
        p = pd.DataFrame()
        f = pd.DataFrame()
        p['Performance#'] = self.absErr.groupby(self.perfB_stand).agg('count')
        p['Performance%'] = ((p['Performance#']/len(self.absErr))*100).map('{:.2f}%'.format)
        f['confidence#'] = self.absErr.groupby(self.fsdB_stand).agg('count')
        f['confidence%'] = ((f['confidence#']/len(self.fsd))*100).map('{:.2f}%'.format)

        perfStatTable = p.join(f, how = 'left')
        withinC = '{:.2f}%'.format((sum(self.withinConf)/len(self.withinConf))*100)

        if printResults == 'Yes':
            print('###########################################################################')
            print('PERFORMANCE & CONFIDENCE METRICS: {} MODEL'.format(self.name))
            print('###########################################################################')
            print('')
            print('Performance & Confidence Bands: {} Price Model'.format(self.name))
            print('')
            print(perfStatTable)
            print('')
            print('---------------------------------------------------------------------------')
            print('%Within Confidence')
            print('')
            print(withinC)
            print('')
            print('---------------------------------------------------------------------------')

        return perfStatTable

    def performancebyConfidence(self, printResults = 'Yes'):

        df_confPerfBands = pd.DataFrame({"Confidence" : self.fsdB_stand, "Performance" : self.perfB_stand})
        conf_by_perf = pd.crosstab(df_confPerfBands['Confidence'], df_confPerfBands['Performance'], margins=True)
        
        rowPerc = pd.crosstab(df_confPerfBands.iloc[:,0], df_confPerfBands.iloc[:,1], normalize='index', margins=True).applymap('{:,.2%}'.format)
        colPerc = pd.crosstab(df_confPerfBands.iloc[:,0], df_confPerfBands.iloc[:,1], normalize='columns', margins=True).applymap('{:,.2%}'.format)
        totPerc = pd.crosstab(df_confPerfBands.iloc[:,0], df_confPerfBands.iloc[:,1], normalize='all', margins=True).applymap('{:,.2%}'.format)
        
        if printResults == 'Yes':
            print('###########################################################################')
            print('CONFIDENCE x PERFORMANCE STATATISTS: {} PRICE MODEL'.format(self.name))
            print('###########################################################################')
            print('---------------------------------------------------------------------------')
            print('Fsd by performance band for {} price model'.format(self.name))
            print('#')
            print('')
            print(conf_by_perf)
            print('')
            print('---------------------------------------------------------------------------')
            print('Row Percentages%')
            print('')
            print(rowPerc)
            print('')
            print('---------------------------------------------------------------------------')
            print('Column Percentages%')
            print('')
            print(colPerc)
            print('')
            print('---------------------------------------------------------------------------')
            print('Total Percentages%')
            print('')
            print(totPerc)
            print('')
            print('---------------------------------------------------------------------------')

        return conf_by_perf, df_confPerfBands

    def performancebySegment(self, segments=[], printResults='Yes'):

        dfmainclass = pd.DataFrame({"URN":self.urn, "Confidence" : self.fsdB_stand, "Performance" : self.perfB_stand, "ValueBand" : self.valueB})

        if len(segments) == 0:
            print('No additional segments are defined within the class initiation')
        else:

            numSegments = [x for x in range(len(self.df[segments].columns) + 1)]
            dfSegments = pd.concat([dfmainclass, self.df[segments]], axis = 1, sort=False)

            #print(pd.crosstab(self.df[segments], dfSegments['Performance'], margins=True))
            
            for i in numSegments:

                segmentName = dfSegments.columns[i+3]

                seg_by_perf = pd.crosstab(dfSegments[segmentName], dfSegments['Performance'], margins=True)
                rowPerc = pd.crosstab(dfSegments[segmentName], dfSegments['Performance'], normalize='index', margins=True).applymap('{:,.2%}'.format)

                if printResults == 'Yes':
                    print('###########################################################################')
                    print('{} x PERFORMANCE STATATISTS: {} PRICE MODEL'.format(segmentName, self.name))
                    print('###########################################################################')
                    print('---------------------------------------------------------------------------')
                    print('{} by performance band for {} price model'.format(segmentName, self.name))
                    print('#')
                    print('')
                    print(seg_by_perf)
                    print('')
                    print('---------------------------------------------------------------------------')
                    print('Row Percentages%')
                    print('')
                    print(rowPerc)
                    print('')
                    print('---------------------------------------------------------------------------')

    def featureMatrix(self, features=[], printResults='Yes'):

        dfmainclass = pd.DataFrame({"URN":self.urn, "Confidence" : self.fsdB_stand, "Performance" : self.perfB_stand, "Error": self.err, "absError": self.absErr})

        if len(features) == 0:
            print('No additional segments are defined within the class initiation')
        else:

            #numFeatures = [x for x in range(len(self.df[features].columns) + 1)]
            dfFeatures = pd.concat([dfmainclass, self.df[features]], axis = 1, sort=False)

            #print(pd.crosstab(self.df[segments], dfSegments['Performance'], margins=True))
            
            newFeatureList = list()
            for feature in features:
                
                dfFeatures[feature+'_YN'] = dfFeatures[feature].apply(lambda x: self.__yesNo(x))
                newFeatureList.append(feature+'_YN')
            
            #print(dfFeatures)

            #group = dfFeatures.groupby(newFeatureList[0])[newFeatureList[1], newFeatureList[2]].value_counts()
            group = dfFeatures.pivot_table(values = ['absError'], index = newFeatureList, columns = dfFeatures['Performance'],  aggfunc=['size'])

            print(group)

                # seg_by_perf = pd.crosstab(dfSegments[segmentName], dfSegments['Performance'], margins=True)
                # rowPerc = pd.crosstab(dfSegments[segmentName], dfSegments['Performance'], normalize='index', margins=True).applymap('{:,.2%}'.format)

                # if printResults == 'Yes':
                #     print('###########################################################################')
                #     print('{} x PERFORMANCE STATATISTS: {} PRICE MODEL'.format(segmentName, self.name))
                #     print('###########################################################################')
                #     print('---------------------------------------------------------------------------')
                #     print('{} by performance band for {} price model'.format(segmentName, self.name))
                #     print('#')
                #     print('')
                #     print(seg_by_perf)
                #     print('')
                #     print('---------------------------------------------------------------------------')
                #     print('Row Percentages%')
                #     print('')
                #     print(rowPerc)
                #     print('')
                #     print('---------------------------------------------------------------------------')
    
    def __yesNo(self, feature):
        if ((pd.isna(feature)) | (feature == 'UK') | (feature == None)):
            output = 'N'
        else:
            output = 'Y'
        return output

class modelCompare:

    def __init__(self, comparisonModels):
    #''' All inputs are objects of type pricePerformance class. comparionPrice can be an array of pricePerformance classes. comarisonPrices = ['pricePerformance1', 'pricePerformance2'] '''

        self.comparison = comparisonModels

    def comparePerformance(self):

        modelStatList = list()
        for model in self.comparison:
            output = model.modelStatistics(printResults='No') 
            modelStatList.append(output)
            print(output)

        modelMatrixList = list()
        for model in self.comparison:
            output = tuple(model.performancebyConfidence(printResults='No')) 
            modelMatrixList.append(output)
        
        numModels = [x for x in range(len(self.comparison))]
        for i in numModels:
            for j in numModels:

                if (i == j):
                    continue

                else:
                    #PerfConfBand = modelStatList[i] - modelStatList[j]
                    ConfbyPerf = modelMatrixList[i][0] - modelMatrixList[j][0] 

                    print('###########################################################################')
                    print('PERFORMANCE COMPARISON OF {} AGAINST {} PRICE MODEL'.format(self.comparison[i].name, self.comparison[j].name))
                    print('###########################################################################')
                    print('')
                    print('Difference in performance: Model {} compared to {}'.format(self.comparison[i].name, self.comparison[j].name))
                    # print('---------------------------------------------------------------------------')
                    # print('Performance & confidence band comparison')
                    # print('')
                    # print(PerfConfBand)
                    # print('')
                    print('---------------------------------------------------------------------------')
                    print('Confidence by performance band comparison')
                    print('')
                    print(ConfbyPerf)
                    print('')

                    df = modelMatrixList[i][1].join(modelMatrixList[j][1], how = 'left', lsuffix = self.comparison[i].name, rsuffix=self.comparison[j].name)
                    df['p1Num'] = df['Performance' + self.comparison[i].name].apply(lambda x: self.__numericCat(x))
                    df['p2Num'] = df['Performance' + self.comparison[j].name].apply(lambda x: self.__numericCat(x))

                    perfnum = pd.crosstab(df['Performance' + self.comparison[i].name], df['Performance' + self.comparison[j].name], margins=True)
                    perfperc = pd.crosstab(df['Performance' + self.comparison[i].name], df['Performance' + self.comparison[j].name], normalize='all', margins=True).applymap('{:,.2%}'.format)

                    sumSame = df[df['Performance'+ self.comparison[i].name] == df['Performance' + self.comparison[j].name]]
                    sumHigh = df[df.p1Num < df.p2Num]
                    sumLow = df[df.p1Num > df.p2Num]

                    print('---------------------------------------------------------------------------')
                    print('{} by {} price performance matrix'.format(self.comparison[i].name, self.comparison[j].name))
                    print('---------------------------------------------------------------------------')
                    print('#')
                    print('')
                    print(perfnum)
                    print('')
                    print('---------------------------------------------------------------------------')
                    print('%')
                    print('')
                    print(perfperc)
                    print('')
                    print('---------------------------------------------------------------------------')
                    print('Performance is the same for {} of {} records. {:.2%} of total'.format(len(sumSame),len(df),(len(sumSame)/len(df))))
                    print('Performance is better for {} on {} of {} records. {:.2%} of total'.format(self.comparison[i].name,len(sumHigh),len(df),(len(sumHigh)/len(df))))
                    print('Performance is worse for {} on {} of {} records. {:.2%} of total'.format(self.comparison[i].name,len(sumLow),len(df),(len(sumLow)/len(df))))
                    print('---------------------------------------------------------------------------')
    
    def __numericCat(self, perf):

        if (perf == '0-10'):
            output = 1
        elif (perf == '11-15'):
            output = 2
        elif (perf == '16-20'):
            output = 3
        elif (perf == '21-30'):
            output = 4
        elif (perf == '30+'):
            output = 5
        elif (perf == None):
            output = 6
        return output

