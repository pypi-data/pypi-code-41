# 201904 MiaSUN  changed from TAFormula.py
from pandas import DataFrame as df
import numpy as np
import math
import copy


class TA:
    @staticmethod
    def MA(n_array, params):
        # input: np.array (1D) ，output: np.array (1D) / number
        if type(params) != list:
            raise Exception("params should be a list object.")
        for period in params:
            values = list()
            for idx in range(0, len(n_array)):
                if idx < period-1:
                    values.append(None)
                else:
                    values.append(n_array[idx-(period-1):idx].mean())
        ma_array = np.array(values, dtype=float)
        # series = df(index=df_bars["bartime"])
        # closes = df_bars["close"]
        # for period in params:
        #     values = list()
        #     for idx in range(0, len(closes)):
        #         if idx < period-1:
        #             values.append(None)
        #         else:
        #             values.append(closes[idx-(period-1):idx].mean())
        #
        #     series.insert(0, str(period), values) # input:dataframe, output:dataframe
        return ma_array

    @staticmethod
    def highest(n_array, length):
        # input: np.array (1D) ，output:number
        p_bars = n_array[-length:]
        highest_value = p_bars.max()  # number
        return highest_value

    @staticmethod
    def lowest(n_array, length):
        # input: np.array (1D) ，output:number
        p_bars = n_array[-length:]
        lowest_value = p_bars.min()   # number
        return lowest_value

    @staticmethod
    def CrossAbove(prices1, prices2):
        # input: np.array (1D) ，output:number  True/False
        if len(prices1) < 3:
            raise Exception("Arrays should be longer ~~ .")
        if (prices1[-2] <= prices1[-2]) and (prices1[-1] > prices2[-1]):
            return True
        else:
            return False

    @staticmethod
    def CrossUnder(prices1, prices2):
        # input: np.array (1D) ，output:number  True/False
        if len(prices1) < 3:
            raise Exception("Arrays should be longer ~~ .")
        if (prices1[-2] >= prices1[-2]) and (prices1[-1] < prices2[-1]):
            return True
        else:
            return False

    @staticmethod
    def CrossAboveArray(prices1, prices2):
        # input: np.array (1D) ，output:np.array(1D) True/False
        if len(prices1) != len(prices2):
            raise Exception("Array1 and array2 should have the same length. sig array = array length - 2 ")
        CrossAbove = [False]*len(prices1)
        for idx in range(2, len(prices1)):
            if (prices1[idx-2] <= prices1[idx-2]) and (prices1[idx-1] > prices2[idx-1]):
                CrossAbove[idx] = True
            else:
                CrossAbove[idx] = False
        CrossAbove_array = np.array(CrossAbove)
        return CrossAbove_array

    @staticmethod
    def CrossUnderArray(prices1, prices2):
        # input: np.array (1D) ，output:np.array(1D) True/False
        if len(prices1) != len(prices2):
            raise Exception("Array1 and array2 should have the same length. sig array = array length - 2 ")
        CrossUnder = [False]*len(prices1)
        for idx in range(2, len(prices1)):
            if (prices1[idx-2] >= prices1[idx-2]) and (prices1[idx-1] < prices2[idx-1]):
                CrossUnder[idx] = True
            else:
                CrossUnder[idx] = False
        CrossUnder_array = np.array(CrossUnder)
        return CrossUnder_array

    @staticmethod
    def SMA(n_array, long_len, short_len):
        # input: np.array (1D) ，output: np.array (1D)
        var0 = short_len/long_len
        SMA = list()
        for idx in range(0, len(n_array)):
            if idx == 0:
                SMA.append(n_array[0])
            else:
                sma_value = (1-var0)*SMA[-1]+var0 * n_array[idx]  # SMA[-1]
                SMA.append(sma_value)
        SMA_array = np.array(SMA, dtype=float)
        return SMA_array

    @staticmethod
    def average(n_array, length):
        # input: np.array (1D) ，output:number
        average_value = n_array[-length:].mean()
        return average_value

    @staticmethod
    def RSI(n_array, params):
        # input: np.array (1D) ，output: np.array (1D)
        if type(params) != list:
            raise Exception("params should be a list object.")

        for period in params:
            if len(n_array) < period+1:
                raise Exception("Data number isn't enough for <RSI>.")
            values = list()
            var0 = [0] * len(n_array)
            var1 = [0] * len(n_array)
            var2 = 0
            num = 1/period
            aaa = [0] * len(n_array)
            for idx in range(0, len(n_array)):
                if idx <= period-1:
                    values.append(50)
                elif idx == period:     # period+1,CurrentBar=1
                    data1 = n_array[1:]    # MC:closes
                    data2 = n_array[:-1]   # MC:closes[1], [)
                    var0[idx] = (n_array[idx]-n_array[idx-period])/period
                    var1[idx] = abs(data1[-period:]-data2[-period:]).mean()
                else:
                    var2 = n_array[idx] - n_array[idx-1]
                    var0[idx] = var0[idx-1] + num * (var2 - var0[idx-1])
                    var1[idx] = var1[idx-1] + num * (abs(var2) - var1[idx-1])

                if var1[idx] != 0:
                    aaa[idx] = var0[idx] / var1[idx]
                else:
                    aaa[idx] = 0
                values.append(50*(aaa[idx] + 1))
        RSI_array = np.array(values, dtype=float)
        return RSI_array

    @staticmethod
    def BollingBand(n_array, BB_len, BBup, BBdn):     # 可以简化
        # input: np.array (1D) ，output: np.array (3D)
        BB_high = list()
        BB_low = list()
        MA_line = list()
        for idx in range(0, len(n_array)):
            if idx < BB_len-1:
                BB_high.append(None)
                BB_low.append(None)
                MA_line.append(None)
            else:
                MA_value = np.mean(n_array[idx-(BB_len-1):idx+1])
                MA_line.append(MA_value)
                high_value = MA_value + BBup*np.std(n_array[idx-(BB_len-1):idx+1])
                low_value = MA_value + BBdn*np.std(n_array[idx-(BB_len-1):idx+1])
                BB_high.append(high_value)
                BB_low.append(low_value)
        BB_high_array = np.array(BB_high, dtype=float)
        BB_low_array = np.array(BB_low, dtype=float)
        MA_line_array = np.array(MA_line, dtype=float)
        BB_array = np.vstack((BB_high_array, BB_low_array, MA_line_array))
        return BB_array

    @staticmethod
    def XAverage(n_array, ave_len):
        # input: np.array (1D) ，output: np.array (1D)
        var0 = 2 / (ave_len+1)
        XAverage = list()
        for idx in range(0, len(n_array)):
            if idx == 0:
                XAverage.append(n_array[idx])
            else:
                XAverage.append(XAverage[-1] + var0*(n_array[idx]-XAverage[-1]))
        XAverage_array = np.array(XAverage, dtype=float)
        return XAverage_array

    @staticmethod
    def countif(true_false):
        # input: np.array (1D)，output: number
        true_count = np.sum(true_false)
        return true_count

    @staticmethod
    def summation(n_array, len):
        # input: np.array (1D)，output: number
        var0 = 0
        for kk in range(0, len):
            var0 = var0 + n_array[-1-kk]
        summation = var0
        return summation

    @staticmethod
    def AdaptiveMovAvg(n_array, EffRatio_len, fast_len, slow_len):
        # input: np.array (1D)，output: np.array (1D)
        AdaptiveMovAvg = copy.deepcopy(n_array.tolist())
        dir_value = [0]*len(n_array)
        dir_sum = [0]*len(n_array)
        var3 = [0]*len(n_array)
        var4 = 2/(slow_len+1)
        var5 = 2/(fast_len+1)
        var6 = var5-var4

        dv0 = copy.deepcopy(n_array[1:])
        dv1 = copy.deepcopy(n_array[:-1])
        daily_change = copy.deepcopy(dv0-dv1)   # array - array[1]
        for idx in range(0, len(n_array)):
            # if idx = EffRatio_len:# CurrentBar = 1, bar = Len+1
            if idx > EffRatio_len:      # CurrentBar > 1, bar > Len+1
                dir_value[idx] = abs(n_array[idx]-n_array[idx-EffRatio_len])
                dir_sum[idx] = TAFormula.summation(daily_change[:idx+1], EffRatio_len)  # Good idx!
                if dir_sum[idx] > 0:
                    var2 = dir_value[idx]/dir_sum[idx]
                else:
                    var2 = 0
                var3[idx] = np.square(var4 + var2*var6)
                AdaptiveMovAvg[idx] = AdaptiveMovAvg[idx-1] + var3[idx]*(n_array[idx] - AdaptiveMovAvg[idx-1])

        AdaptiveMovAvg_array = np.array(AdaptiveMovAvg, dtype=float)
        return AdaptiveMovAvg_array

    @staticmethod
    def LRSI(n_array, gamma):
        # { Laguerre RSI } input: np.array (1D)，output: np.array (1D)
        L0 = [0]*len(n_array)
        L1 = [0]*len(n_array)
        L2 = [0]*len(n_array)
        L3 = [0]*len(n_array)
        LRSI = [0]*len(n_array)
        for idx in range(1, len(n_array)):
            L0[idx] = (1-gamma)*n_array[idx] + gamma*L0[idx-1]
            L1[idx] = -gamma*L0[idx] + L0[idx-1] + gamma*L1[idx-1]
            L2[idx] = -gamma*L1[idx] + L1[idx-1] + gamma*L2[idx-1]
            L3[idx] = -gamma*L2[idx] + L2[idx-1] + gamma*L3[idx-1]
            CU = 0
            CD = 0
            if L0[idx] >= L1[idx]:
                CU = L0[idx] - L1[idx]
            else:
                CD = L1[idx] - L0[idx]
            if L1[idx] >= L2[idx]:
                CU = CU + L1[idx] - L2[idx]
            else:
                CD = CD + L2[idx] - L1[idx]
            if L2[idx] >= L3[idx]:
                CU = CU + L2[idx] - L3[idx]
            else:
                CD = CD + L3[idx] - L2[idx]
            if CU+CD != 0:
                LRSI[idx] = CU/(CU+CD)
        LRSI_array = np.array(LRSI, dtype=float)
        return LRSI_array

    @staticmethod
    def LaguerreFilter(n_array, gamma):
        # { Laguerre Filter } input: np.array (1D)，output: np.array (2D)
        L0 = [0]*len(n_array)
        L1 = [0]*len(n_array)
        L2 = [0]*len(n_array)
        L3 = [0]*len(n_array)
        VPTFilt = [0]*len(n_array)
        VPTFIR = [0]*len(n_array)
        for idx in range(3, len(n_array)):
            L0[idx] = (1-gamma)*n_array[idx] + gamma*L0[idx-1]
            L1[idx] = -gamma*L0[idx] + L0[idx-1] + gamma*L1[idx-1]
            L2[idx] = -gamma*L1[idx] + L1[idx-1] + gamma*L2[idx-1]
            L3[idx] = -gamma*L2[idx] + L2[idx-1] + gamma*L3[idx-1]
            VPTFilt[idx] = (L0[idx] + 2*L1[idx] + 2*L2[idx] + L3[idx])/6
            VPTFIR[idx] = (n_array[idx] + 2*n_array[idx-1] + 2*n_array[idx-2] + n_array[idx-3])/6
        VPTFilt_array = np.array(VPTFilt, dtype=float)
        VPTFIR_array = np.array(VPTFIR, dtype=float)
        LFilter_array = np.vstack((VPTFilt_array, VPTFIR_array))
        return

    @staticmethod
    def ITrend(n_array, aph):
        # input: np.array (1D)  output: np.array (1D)
        aph = 0.07
        Itrend = [0]*len(n_array)
        price = n_array.tolist()
        for idx in range(0, len(n_array)):
            if 2 <= idx < 6:
                Itrend[idx] = (price[idx] + 2*price[idx-1] + price[idx-2])/4
            else:
                Itrend[idx] = (aph-aph*aph/4)*price[idx] + 0.5*aph*aph*price[idx-1] - (aph-0.75*aph*aph)*price[idx-2] + 2*(1-aph)*Itrend[idx-1] - (1-aph)*(1-aph)*Itrend[idx-2]
        Itrend_array = np.array(Itrend, dtype=float)
        return Itrend_array

    @staticmethod
    def VPT(n_array, vol_array):
        # input: np.array (1D) * 2  output: np.array (1D)
        varV = (vol_array/100).tolist  # ndarry
        varC = [0]*len(n_array)
        for idx in range(1, len(n_array)):
            varC[idx] = varC[idx-1] + varV[idx] * ((n_array[idx]-n_array[idx-1]) / n_array[idx-1])
        VPT_array = np.array(varC, dtype=float)
        return VPT_array

    @staticmethod
    def Auto_fit_fun(n_array, auto_len, fast_len, slow_len):
        # input: np.array (1D)，output: np.array (1D)
        fast_len = 3
        slow_len = 31
        delta = 2
        var = [0]*len(n_array)
        myc = 2/slow_len
        myd = 2/fast_len - 2/slow_len
        diff_list = [0]*len(n_array)
        path = [0]*len(n_array)
        distance = [0]*len(n_array)
        effectD = [0]*len(n_array)
        auto_fit = [0]*len(n_array)

        dv0 = copy.deepcopy(n_array[1:])
        dv1 = copy.deepcopy(n_array[:-1])
        diff = copy.deepcopy(abs(dv0-dv1))  # array - array[1]
        truePrice = copy.deepcopy(n_array.tolist())
        for idx in range(0, len(n_array)):
            if idx >= auto_len:     # auto_len+1,CurrentBar>=1
                distance[idx] = n_array[idx]-n_array[idx-auto_len]
                path[idx] = TAFormula.summation(diff[:idx+1], auto_len)
                if path[idx] == 0:
                    effectD[idx] = 0
                else:
                    effectD[idx] = distance[idx]/path[idx]
                var[idx] = pow(myc+myd*effectD[idx], delta)
                auto_fit[idx] = var[idx]*truePrice[idx] + (1-var[idx])*auto_fit[idx-1]
        auto_fit_array = np.array(auto_fit, dtype=float)
        return auto_fit_array

    @staticmethod
    def CCI(closes, highs, lows, CCI_len):
        # input: np.array (1D)，output: np.array (1D)
        var0 = [0]*len(closes)
        var1 = [0]*len(closes)
        CCI = [0]*len(closes)
        PriceValue = copy.deepcopy((highs + lows + closes).tolist())
        for idx in range(0, len(closes)):
            if idx >= CCI_len:
                var0[idx] = TAFormula.summation(PriceValue[:idx+1], CCI_len)/CCI_len
                for kk in range(0, CCI_len):
                    var1[idx] = var1[idx] + abs(PriceValue[idx-kk]-var0[idx])
                var1[idx] = copy.deepcopy(var1[idx]/CCI_len)
                if var1[idx] == 0:
                    CCI[idx] = 0
                else:
                    CCI[idx] = (PriceValue[idx]-var0[idx]) / (var1[idx]*.015)
        CCI_array = np.array(CCI, dtype=float)
        return CCI_array

    @staticmethod
    def MyStochastic(n_array, MS_len):
        # input: np.array (1D)，output: np.array (1D)
        HP = [0]*len(n_array)
        Filt = [0]*len(n_array)
        Stoc = [0]*len(n_array)
        MyStochastic = [0]*len(n_array)
        HighestC = [0]*len(n_array)
        LowestC = [0]*len(n_array)
        aph = (math.cos(0.707*360/48) + math.sin(0.707*360/48)-1)/math.cos(0.707*360/48)
        a1 = math.exp(-1.414*3.14159/10)
        b1 = 2*a1*math.cos(1.414*180/10)
        c2 = copy.deepcopy(b1)
        c3 = -pow(a1, 2)
        c1 = 1-c2-c3
        for idx in range(0, len(n_array)):
            if idx >= MS_len:
                # Highpass filter cyclic components
                HP[idx] = pow((1-aph/2), 2)*(n_array[idx]-2*n_array[idx-1]+n_array[idx-2])+2*(1-aph)*HP[idx-1]-pow((1-aph), 2)*HP[idx-2]
                # Smooth with a Super Smoother Filter
                Filt[idx] = c1*(HP[idx] + HP[idx-1])/2 + c2*Filt[idx-1] + c3*Filt[idx-2]
                HighestC[idx] = np.max(Filt[idx+1-MS_len:idx+1])
                LowestC[idx] = np.min(Filt[idx+1-MS_len:idx+1])
                Stoc[idx] = (Filt[idx] - LowestC[idx])/(HighestC[idx] - LowestC[idx])
                MyStochastic[idx] = c1*(Stoc[idx]+Stoc[idx-1])/2 + c2*MyStochastic[idx-1] + c3*MyStochastic[idx-2]
        MyStochastic_array = np.array(MyStochastic, dtype=float)
        return MyStochastic_array

    @staticmethod
    def DirMovement(highs, lows, n_array, DMI_len):   # 下标 check!
        # input: np.array (1D) ，output: array(ND) (DMIplus;DMIminus;DMI;ADX;ADXR;Volty)
        DMIplus = [0]*len(n_array)
        DMIminus = [0]*len(n_array)
        DMI = [0]*len(n_array)
        ADX = [0]*len(n_array)
        ADXR = [0]*len(n_array)
        Volty = [0]*len(n_array)

        varH = [0]*len(n_array)
        varL = [0]*len(n_array)
        varPlus = [0]*len(n_array)
        varMinus = [0]*len(n_array)
        alpha = 1 / DMI_len
        varSum = 0
        for idx in range(0, len(n_array)):
            if idx == DMI_len:  # CurrentBar = 1, bar = Len+1
                numH = [0]*DMI_len
                numL = [0]*DMI_len
                TR = [0]*DMI_len
                for kk in range(0, DMI_len-1):
                    varH[idx] = highs[idx-kk] - highs[idx-kk-1]     # kk=0 不做下标
                    varL[idx] = lows[idx-kk-1] - lows[idx-kk]
                    if varH[idx] > varL[idx] and varH[idx] > 0:     # condition1
                        numH[kk] = copy.deepcopy(varH[idx])         # var0 = 波动大的H
                    elif varL[idx] > varH[idx] and varL[idx] > 0:   # condition2
                        numL[kk] = copy.deepcopy(varL[idx])         # var1 = 波动大的L
                    TR[kk] = copy.deepcopy(max(highs[idx-kk], n_array[idx-kk-1])-min(lows[idx-kk], n_array[idx-kk-1]))
                varPlus[idx] = np.mean(numH[:])     # kk循环内累加,波动大H平均-->向上波动大H的均值,
                varMinus[idx] = np.mean(numL[:])    # kk循环内累加，波动大L平均-->向下波动大L的均值
                Volty[idx] = np.mean(TR[:])         # 日最大波幅的均值--> 'ATR'
            elif idx > DMI_len:
                numHo = 0
                numLo = 0
                varH[idx] = highs[idx]-highs[idx-1]
                varL[idx] = lows[idx-1] - lows[idx]
                if varH[idx] > varL[idx] and varH[idx] > 0:
                    numHo = varH[idx]
                if varL[idx] > varH[idx] and varL[idx] > 0:
                    numLo = varL[idx]
                TRo = copy.deepcopy(max(highs[idx], n_array[idx-1])-min(lows[idx], n_array[idx-1]))
                varPlus[idx] = varPlus[idx-1] + alpha*(numHo - varPlus[idx-1])
                varMinus[idx] = varMinus[idx-1] + alpha*(numLo - varMinus[idx-1])
                Volty[idx] = Volty[idx-1] + alpha*(TRo-Volty[idx-1])

            if Volty[idx] > 0:
                DMIplus[idx] = 100*varPlus[idx]/Volty[idx]
                DMIminus[idx] = 100*varMinus[idx]/Volty[idx]
            else:
                DMIplus[idx] = 0
                DMIminus[idx] = 0

            varSum = DMIplus[idx] + DMIminus[idx]
            if varSum > 0:
                DMI[idx] = 100*abs(DMIplus[idx] - DMIminus[idx])/varSum
            else:
                DMI[idx] = 0

            if 2*DMI_len > idx >= DMI_len:
                cumDMI = np.cumsum(DMI[:idx+1], axis=0)
                ADX[idx] = cumDMI[-1] / (idx-DMI_len+1)
                ADXR[idx] = (ADX[idx] + ADX[DMI_len]) * .5
            else:
                ADX[idx] = ADX[idx-1] + alpha * (DMI[idx]-ADX[idx-1])
                ADXR[idx] = (ADX[idx] + ADX[idx-DMI_len+1]) * .5

        DMIplus_array = np.array(DMIplus, dtype=float)
        DMIminus_array = np.array(DMIminus, dtype=float)
        DMI_array = np.array(DMI, dtype=float)
        ADX_array = np.array(ADX, dtype=float)
        ADXR_array = np.array(ADXR, dtype=float)
        Volty_array = np.array(Volty, dtype=float)
        DirMovement = np.vstack((DMIplus_array, DMIminus_array, DMI_array, ADX_array, ADXR_array, Volty_array))
        return DirMovement

    @staticmethod
    def MACD(n_array, EMA_short, EMA_long, M_MACD):     #
        #       input:array，output: tuple(array1,array2,array3)
        EMA_sh = list()
        EMA_lo = list()
        DIFF = list()
        DEA = list()
        MACD = list()
        for idx in range(0, len(n_array)):
            if idx == 0:
                DIFF.append(0)
                DEA.append(0)
                MACD.append(0)
                EMA_sh.append(n_array[idx])
                EMA_lo.append(n_array[idx])
            else:
                EMA_s = EMA_sh[-1]*(EMA_short-1)/(EMA_short+1)+n_array[idx]*(2/(EMA_short+1))
                EMA_l = EMA_lo[-1]*(EMA_long-1)/(EMA_long+1)+n_array[idx]*(2/(EMA_long+1))
                EMA_sh.append(EMA_s)
                EMA_lo.append(EMA_l)
                gap = EMA_s-EMA_l
                DIFF.append(gap)
                deaverage = DEA[-1]*(M_MACD-1)/(M_MACD+1)+gap*(2/(M_MACD+1))
                DEA.append(deaverage)
                MACD.append(2*(gap-deaverage))
        series_DIFF = np.array(DIFF, dtype=float)
        series_DEA = np.array(DEA, dtype=float)
        series_MACD_temp = np.array(MACD, dtype=float)
        series_MACD = [series_DIFF, series_DEA, series_MACD_temp]
        series_MACD = tuple(series_MACD)
        return series_MACD

    @staticmethod
    def ParabolicSAR(n_array, highs, lows, ):
        # input: np.array (1D) ，output: tuple( ,  ,  ,  ,  )
        # AfStep AfLimit
        ParClose = [0]*len(n_array)
        ParOpen = [0]*len(n_array)
        Position = [0]*len(n_array)
        Transition = [0]*len(n_array)

        var0 = 0
        var1 = 0
        var2 = 0
        for idx in range(0, len(n_array)):
            if idx == 2:  # CurrentBar = 1, bar = Len+1
                ParOpen[idx] = highs[idx]
                Position[idx] = -1
                var0 = copy.deepcopy(highs[idx])
                var1 = copy.deepcopy(lows[idx])
            elif idx > 2:
                Transition[idx] = 0
                if highs[idx] > var0:
                    var0 = highs[idx]
                if lows < var1:
                    var1 = lows[idx]

        return
