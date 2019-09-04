
# -*- coding: utf-8 -*-
import json
import urllib
import zipfile

from pymouse import PyMouse
from pykeyboard import PyKeyboard
import numpy as np
from matplotlib.path import Path
from selenium import webdriver
from sqlalchemy import create_engine
import pandas as pd
import folium
from folium.plugins import MeasureControl
import webbrowser
from bs4 import BeautifulSoup
from scipy.spatial import KDTree
from multiprocessing.dummy import Pool as ThreadPool
import geopy.distance
import time
import os
from math import atan, cos, pi, radians
import datetime
from datetime import datetime
import threadpool
import random
from math import sin, asin, cos, radians, fabs, sqrt,pi,cos,atan,tan,acos,degrees,atan2
from geographiclib.geodesic import Geodesic
import mplleaflet
import matplotlib.pyplot as plt
from multiprocessing.dummy import Pool
from scipy.spatial import ConvexHull
from sklearn.cluster import DBSCAN
from jieba import lcut
from gensim.similarities import SparseMatrixSimilarity
from gensim.corpora import Dictionary
from gensim.models import TfidfModel
from multiprocessing.dummy import Pool
from scipy.spatial import ConvexHull
# 显示所有列
pd.set_option('display.max_rows', None)
# 显示所有行
pd.set_option('display.max_columns', None)
# 不换行
pd.set_option('display.width', None)

rjtcolor = ['#DC143C', '#0000FF', '#3CB371', '#FFFF00']
enginenetwork = create_engine('postgresql+psycopg2://postgres:qq403239089@127.0.0.1:5432/SourcesNetwork')
enginescence = create_engine('postgresql+psycopg2://postgres:qq403239089@127.0.0.1:5432/SourcesScence')
engineimportantscence = create_engine('postgresql+psycopg2://postgres:qq403239089@127.0.0.1:5432/ImportantSceneMonitor')


# 文本集和搜索词
def Similarfieldname(keywordlist,fiterlist):
    test = fiterlist
    texts = fiterlist
    # 1、将【文本集】生成【分词列表】
    texts = [lcut(text) for text in texts]
    # 2、基于文本集建立【词典】，并获得词典特征数
    dictionary = Dictionary(texts)
    num_features = len(dictionary.token2id)
    # 3.1、基于词典，将【分词列表集】转换成【稀疏向量集】，称作【语料库】
    corpus = [dictionary.doc2bow(text) for text in texts]
    # 4、创建【TF-IDF模型】，传入【语料库】来训练
    tfidf = TfidfModel(corpus)
    # 5、用训练好的【TF-IDF模型】处理【被检索文本】和【搜索词】
    tf_texts = tfidf[corpus]  # 此处将【语料库】用作【被检索文本】
    # 6、相似度计算
    sparse_matrix = SparseMatrixSimilarity(tf_texts, num_features)
    def keyfit(keyword):
        nonlocal test,texts,corpus,num_features
        # 3.2、同理，用【词典】把【搜索词】也转换为【稀疏向量】
        kw_vector = dictionary.doc2bow(lcut(keyword))
        # 5、用训练好的【TF-IDF模型】处理【被检索文本】和【搜索词】
        tf_kw = tfidf[kw_vector]
        # 6、相似度计算
        similarities = sparse_matrix.get_similarities(tf_kw)
        redio=0
        num=0
        for e, s in enumerate(similarities, 1):
            if s>redio:
                redio=s
                num=e-1
        print(test[num],keyword,redio)
        return [keyword,test[num],redio]
    pool=Pool(200)
    results=pool.map(keyfit,keywordlist)
    pool.close()
    pool.join()
    results = pd.DataFrame(results, columns=['原字段名称', '匹配字段名称','适配率'])
    return results

class Point(object):
    def __init__(self, point,filter=True):
        self.point=point

    def CreatPointConBand(self):
        self.ConBand=[]
        self.ConPoint=[]
        for x in self.point.groupby('Name'):
            try:
                hullvertices = ConvexHull(x[1][['Lat', 'Lon']])
                band = x[1].iloc[hullvertices.vertices]
                band = pd.concat([band, band[0:1]])
                self.ConBand.append(band)
            except:
                self.ConPoint.append(x[1])
                print('无法聚合的点群')
        self.ConBand=pd.concat(self.ConBand)
        self.ConPoint=pd.concat(self.ConPoint)
        return {'conband':self.ConBand,
                'conpoint':self.ConPoint
                }


    def GetPointNearcell(self,seachcell,knum,rules):
        cell=seachcell[['Lat','Lon','小区名称','Ci','Ang']]
        # cell.columns=['Lat','Lon','M小区名称','MCi','MAng']
        seachpoint=self.point[['Lat','Lon','Name']]
        seachpoint.columns = ['pointLat', 'pointLon','point名称']
        # nearresults=[]
        site=cell[['Lat','Lon']]
        site.drop_duplicates(inplace=True)
        tree = KDTree(site)
        def searchnearcell(point):
            nonlocal cell,knum,site
            cellout = tree.query(point[0:2], k=knum)
            Ltecellmark = cellout[1].flatten()
            # 生成临近点距离、index列表
            # 转置并去重
            LOONear= site.iloc[Ltecellmark, :]
            near = np.array([point] * len(LOONear))
            # 提取从非边界内小区中提出临近的datafram表
            print(near[0:10])
            LOONear = np.hstack((near, np.array(LOONear)))
            colu =  ['pointLat', 'pointLon','point名称']+['Lat','Lon']
            results = pd.DataFrame(LOONear, columns=colu)
            results[['Lat','Lon']]=results[['Lat','Lon']].astype(float)
            print(results.head())
            cell[['Lat', 'Lon']] = cell[['Lat', 'Lon']].astype(float)
            print(cell.head())
            results = pd.merge(results, cell, on=['Lat','Lon'], how='left')
            results[['Lat','Lon','Ang','pointLat', 'pointLon']] = results[
                ['Lat','Lon','Ang','pointLat', 'pointLon']].astype(float)
            results['distance'] = [get_distance(results.iloc[i][['Lat', 'Lon']].values.tolist() +
                                                results.iloc[i][['pointLat', 'pointLon']].values.tolist()) for i in
                                   range(len(results))]
            results['CtoPdirection'] = [Get_Angle(results.iloc[i][['Lat', 'Lon', 'pointLat', 'pointLon']].values) for i
                                       in
                                       range(len(results))]
            results['directionCPtoA'] = [min([abs(results.iloc[i]['CtoPdirection'] - results.iloc[i]['Ang']),
                                          abs(results.iloc[i]['CtoPdirection'] - results.iloc[i]['Ang'] - 360),
                                          abs(results.iloc[i]['CtoPdirection'] - results.iloc[i]['Ang'] + 360)]) for i
                                     in
                                     range(len(results))]


            try:
                results[['Ci', 'distance', 'CtoPdirection', 'directionCPtoA']] = results[
                    ['Ci', 'distance', 'CtoPdirection', 'directionCPtoA']].astype(int)
            except:
                print('unlongpart')


            for rule in rules:
                results.loc[(rule[1] >= results['distance']) & (results['distance'] >=rule[0]) & (
                        results['directionCPtoA'] <= rule[2]), 'nearselect'] = 'select'


            # results = results[results.nearselect == 'select']

            # nearresults.append(results)
            return results

        pool=Pool(200)
        results=pool.map(searchnearcell,seachpoint.values.tolist())
        pool.close()
        pool.join()
        results = pd.concat(results)




        return results






class Line(object):
    def __init__(self, RTLhean,filter=True):
        if filter==True:
        # 删除无经纬度的点
            print(RTLhean.head())
            RTLhean=RTLhean[['Lat', 'Lon']]

            RTLhean.dropna(subset=['Lat', 'Lon'], inplace=True)
            RTLhean.drop_duplicates(['Lat', 'Lon'],inplace=True)
            RTLhean[['Lat', 'Lon']] = RTLhean[['Lat', 'Lon']].astype(float)

            RTLhean=RTLhean[(RTLhean.Lat>0)&(RTLhean.Lon>0)]

        # 通过NO.排序
        #     RTLhean.sort_values('No.', inplace=True)

            self.RTLhean = pd.DataFrame(RTLhean.reset_index())
            print('int',RTLhean.head())
        else:
            self.RTLhean=RTLhean




#清理删除点距小于50及、超过线路周围5KM的点及、回头点
    def reducePoint(self,longcut=100,outpoint=5000):
        RTLhean=self.RTLhean
        distancelist=[]
        anglist=[]
        indexnum=0

        for i in range(len(RTLhean)-1):
            distance=[get_distance([RTLhean.iloc[indexnum]['Lat'], RTLhean.iloc[indexnum]['Lon'],
                                                   RTLhean.iloc[indexnum + 1]['Lat'],
                                                   RTLhean.iloc[indexnum + 1]['Lon']])]
            ang=[Get_Angle([RTLhean.iloc[indexnum]['Lat'], RTLhean.iloc[indexnum]['Lon'],
                                                   RTLhean.iloc[indexnum + 1]['Lat'],
                                                   RTLhean.iloc[indexnum + 1]['Lon']])]
            # abs(ang[0]) == 90
            if distance[0]<longcut or distance[0]>outpoint:
                RTLhean.drop([i + 1], inplace=True)
            # elif ang[0]==90:
            else:
                distancelist.append(distance)
                anglist.append(ang)
                print(distance,ang)
                indexnum+=1
        distancelist.append([0])
        anglist.append([0])
        print(RTLhean)
        RTLhean['distance']=np.array(distancelist)
        RTLhean['Ang'] = np.array(anglist)
        RTLhean=pd.DataFrame(RTLhean.reset_index())
        RTLhean=RTLhean[['Ang','distance','Lat', 'Lon']]
        RTLheanline = []
        fristpoint = 0
        for i in range(len(RTLhean)):
            if RTLhean.iloc[i]['distance'] > longcut*3:
                joinline = []
                print(RTLhean.iloc[i].values.tolist())
                fristline = RTLhean.iloc[i][RTLhean.columns.difference(['Lat', 'Lon'])].values.tolist()
                print(fristline)
                cutpart = RTLhean.iloc[i]['distance'] // longcut
                ang = Get_Angle(
                    [RTLhean.iloc[i]['Lat'], RTLhean.iloc[i]['Lon'], RTLhean.iloc[i + 1]['Lat'],
                     RTLhean.iloc[i + 1]['Lon']])
                for j in range(1, int(cutpart)):
                    newpoint = Get_distance_point(
                        [RTLhean.iloc[i]['Lat'], RTLhean.iloc[i]['Lon'], 0, ang, j * longcut / 1000])
                    print(newpoint)
                    joinline.append([ang,j * longcut] + newpoint)
                joinline = pd.DataFrame(joinline, columns=['Ang', 'distance', 'Lat', 'Lon'])
                addpart = pd.concat([RTLhean[fristpoint:i], joinline])
                RTLheanline.append(addpart)
                fristpoint = i + 1
                print(RTLhean[fristpoint:])
        RTLheanline.append(RTLhean[fristpoint:])
        RTLheanline = pd.concat(RTLheanline)
        return RTLheanline

    def Get_parallel_line(self,distance):
        linepoint = self.RTLhean
        linepoint.rename(columns={'Lat':'LineLat','Lon':'LineLon'},inplace=True)
        resultlatlon = []
        colbin = linepoint.columns.values.tolist()
        for i in range(1, len(linepoint) - 1):
            try:
                firstdirction = Get_Angle(
                    [linepoint.iloc[i]['LineLat'], linepoint.iloc[i]['LineLon'], linepoint.iloc[i - 1]['LineLat'],
                     linepoint.iloc[i - 1]['LineLon']])

                seconddirction = Get_Angle(
                    [linepoint.iloc[i]['LineLat'], linepoint.iloc[i]['LineLon'], linepoint.iloc[i + 1]['LineLat'],
                     linepoint.iloc[i + 1]['LineLon']])

                directionD = seconddirction - firstdirction

                resultlong = distance / sin(radians(directionD / 2))

                temp = linepoint.iloc[i][['LineLat','LineLon']].values.tolist()+Get_distance_point(
                    [linepoint.iloc[i]['LineLat'], linepoint.iloc[i]['LineLon'], firstdirction, directionD / 2,
                     resultlong]) + [firstdirction, seconddirction, directionD]
                resultlatlon.append(temp)
            except:
                print('point no put')
        parallel_line = pd.DataFrame(resultlatlon,
                                     columns= ['LineLat','LineLon','Lat', 'Lon', 'firstdirction', 'seconddirction',
                                                       'directionD'])
        # parallel_line['Lat'] = parallel_line['Latparallel']
        # parallel_line['Lon'] = parallel_line['Lonparallel']
        return parallel_line

    # 删除回头点
    def dropBackPoint(self,maxIncludedangle=120):
        dropBackRTLhean=self.RTLhean
        beginang = Get_Angle([dropBackRTLhean.iloc[0]['Lat'], dropBackRTLhean.iloc[0]['Lon'], dropBackRTLhean.iloc[1]['Lat'],
                              dropBackRTLhean.iloc[1]['Lon']])
        numbfirst = 0
        for i in range(1, len(dropBackRTLhean) - 1):
            nextang = Get_Angle(
                [dropBackRTLhean.iloc[numbfirst]['Lat'], dropBackRTLhean.iloc[numbfirst]['Lon'], dropBackRTLhean.iloc[numbfirst + 1]['Lat'],
                 dropBackRTLhean.iloc[numbfirst + 1]['Lon']])
            dt = min([abs(beginang - nextang), abs(beginang - nextang - 360), abs(beginang - nextang + 360)])
            print(beginang, ',', nextang, ',', dt, 'dt')
            if abs(dt) > maxIncludedangle:
                dropBackRTLhean.drop([i], inplace=True)
            else:
                beginang = nextang
                numbfirst += 1
        return dropBackRTLhean

    def Creatpoint(**betweeninfo):
        # betweeninfo是一个字典，包含key值参数：['FLat,'FLon','distance','cutlong']
        # 表示含义[起点纬度，起点经度，大于距离开始补点长度，补点的距离间隔]
        # betweeninfo在两个点之间根据起始点经纬度
        # [betweeninfo['FLat'], betweeninfo['FLon']
        # 距离distance、cutlong做点：
        joinline = []
        cutpart = betweeninfo['distance'] // betweeninfo['cutlong']
        ang = Get_Angle([betweeninfo['FLat'], betweeninfo['FLon'], betweeninfo['SLat'], betweeninfo['SLon']])
        for j in range(1, int(cutpart) + 1):
            newpoint = Get_distance_point(
                [betweeninfo['FLat'], betweeninfo['FLon'], 0, ang, j * betweeninfo['cutlong'] / 1000])
            joinline.append([newpoint[0], newpoint[1]])
        return pd.DataFrame(joinline, columns=['Lat', 'Lon'])




    def dropOutPoint(self,outpointdistance=5000):
        RTLheanpoint=self.RTLhean
        dbresult = DBSCAN(eps=500 / 1000 / 111.1, min_samples=6).fit(RTLheanpoint[['Lat', 'Lon']])
        print(dbresult.labels_)
        RTLheanpoint['dblable'] = dbresult.labels_
        RTLheanpointgroup = RTLheanpoint.groupby('dblable')
        grouplable = [x[1].iloc[0]['dblable'] for x in RTLheanpointgroup]
        grouplen = [len(x[1]) for x in RTLheanpointgroup]

        print(grouplen, grouplable)
        maxlenindex = grouplen.index(max(grouplen))

        print(maxlenindex)
        realline = []

        fpart = RTLheanpoint[RTLheanpoint['dblable'] == grouplable[maxlenindex]]
        fpart = pd.DataFrame(fpart.reset_index())
        fpart['dblable'] = grouplable[maxlenindex]
        realline.append(fpart)
        labletobiglist = grouplable[maxlenindex + 1:len(grouplen)]
        for slable in labletobiglist:
            # slable=grouplable[i+1]
            print(slable)

            spart = RTLheanpoint[RTLheanpoint['dblable'] == slable]
            spart = pd.DataFrame(spart.reset_index())
            distance = get_distance([fpart.iloc[-1]['Lat'], fpart.iloc[-1]['Lon'],
                                                   spart.iloc[0]['Lat'], spart.iloc[0]['Lon']])
            print(distance)
            if distance < outpointdistance:
                addpoint = Creatpoint(FLat=fpart.iloc[-1]['Lat'],
                                                    FLon=fpart.iloc[-1]['Lon'],
                                                    SLat=spart.iloc[0]['Lat'],
                                                    SLon=spart.iloc[0]['Lon'],
                                                    distance=distance,
                                                    cutlong=100)
                addpoint['dblable'] = slable
                realline.append(addpoint)
                spart['dblable'] = slable
                realline.append(spart)
                fpart = RTLheanpoint[RTLheanpoint['dblable'] == slable]

        fpart = RTLheanpoint[RTLheanpoint['dblable'] == grouplable[maxlenindex]]
        labletosmalllist = grouplable[0:maxlenindex]
        labletosmalllist.reverse()
        print(grouplable[0:maxlenindex])
        print(labletosmalllist)
        for slable in labletosmalllist:

            spart = RTLheanpoint[RTLheanpoint['dblable'] == slable]
            spart = pd.DataFrame(spart.reset_index())
            distance = get_distance([fpart.iloc[0]['Lat'], fpart.iloc[0]['Lon'],
                                                   spart.iloc[-1]['Lat'], spart.iloc[-1]['Lon']])

            if distance < outpointdistance:
                addpoint = Creatpoint(FLat=fpart.iloc[0]['Lat'],
                                                    FLon=fpart.iloc[0]['Lon'],
                                                    SLat=spart.iloc[-1]['Lat'],
                                                    SLon=spart.iloc[-1]['Lon'],
                                                    distance=distance,
                                                    cutlong=100)
                addpoint['dblable'] = slable
                realline.insert(0, addpoint)
                spart['dblable'] = slable
                realline.insert(0, spart)
                fpart = RTLheanpoint[RTLheanpoint['dblable'] == slable]
        lineall = pd.concat(realline)
        lineall.drop_duplicates(['Lat', 'Lon'], inplace=True)
        lineall = pd.DataFrame(lineall.reset_index())
        return lineall





class Band(object):
    def __init__(self, bandinfo,filter=True):
        if filter==True:
            # bandinfo 包括city Name Lat Lon
            bandinfo[['Lat', 'Lon']] = bandinfo[['Lat', 'Lon']].astype('float')
            self.bandinfo=bandinfo
            self.bandnum = len(set(bandinfo['Name']))
            self.bandnamelist = list(set(bandinfo['Name']))
            self.citylist = list(set(bandinfo['city']))
            self.bandcmap = {self.bandnamelist[i]: randomcolor(['#DC143C','#0000FF','#3CB371','#FFFF00']) for i in
                             range(len(self.bandnamelist))}
            bandgrouplist = bandinfo.groupby('Name')
            self.bandgrouplist = [x[1] for x in bandgrouplist]
            self.avgLat = bandinfo['Lat'].mean()
            self.avgLon = bandinfo['Lon'].mean()
        else:
            self.bandinfo = bandinfo

    def getGcentre(self):
        bandmap=self.bandinfo
        area = 0.0
        # 多边形面积
        Gx = 0.0
        Gy = 0.0
        # 重心的x、y
        bandsize = len(bandmap)
        for i in range(0, bandsize):

            iLatiLng = bandmap[['Lat', 'Lon']].iloc[i % bandsize].to_list()
            nextLatLng = bandmap[['Lat', 'Lon']].iloc[i - 1].to_list()
            temp = (iLatiLng[0] * nextLatLng[1] - iLatiLng[1] * nextLatLng[0]) / 2.0
            area += temp
            Gx += temp * (iLatiLng[0] + nextLatLng[0]) / 3.0
            Gy += temp * (iLatiLng[1] + nextLatLng[1]) / 3.0
        Gx = Gx / area
        Gy = Gy / area
        return pd.DataFrame([[list(set(bandmap['Name']))[0], Gx, Gy]], columns=['bandname', 'centerlat', 'centerlon'])

    def getAppendband(self,expenddistance,cw='clock'):
        RTLheanband=self.bandinfo
        if cw=='clock':
            RTLheanband=RTLheanband.sort_index(ascending=False)
            RTLheanband =pd.DataFrame(RTLheanband.reset_index())
        RTLheanbandhead=RTLheanband.loc[-2:-1,:]
        RTLheanbandtail = RTLheanband.loc[1:2, :]

        RTLheanband=pd.concat([RTLheanbandhead,RTLheanband,RTLheanbandtail])

        RTLheanbandexpend=RTLheanband[RTLheanband.columns.difference(['Lat', 'Lon'])][:-2]
        resultlatlon = []
        for i in range(1, len(RTLheanband) - 1):
            firstdirction = Get_Angle(
                [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], RTLheanband.iloc[i - 1]['Lat'],
                 RTLheanband.iloc[i - 1]['Lon']])
            seconddirction = Get_Angle(
                [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], RTLheanband.iloc[i + 1]['Lat'],
                 RTLheanband.iloc[i + 1]['Lon']])
            directionD = min([abs(seconddirction - firstdirction),
                              abs(seconddirction - firstdirction - 360),
                              abs(seconddirction - firstdirction + 360)])
            try:
                resultlong = expenddistance / sin(radians(directionD / 2))
            except:
                resultlong = expenddistance

            resultlatlon.append(Get_distance_point(
                [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], firstdirction, (180 - directionD / 2),
                 resultlong]))
        Appendband = pd.DataFrame(resultlatlon, columns=['Lat', 'Lon'])
        Appendband=pd.concat([RTLheanbandexpend,Appendband],axis=1)
        return Appendband


    def getInBandPoint(self,point):
        pointcolumns = point.columns.values.tolist()
        print(self.bandinfo)
        codes = [Path.MOVETO]
        for bandlong in range(1, len(self.bandinfo) - 1):
            codes.append(Path.LINETO)
        codes.append(Path.CLOSEPOLY)

        bandlatlon = self.bandinfo[['Lat', 'Lon']]

        pointlonlat = point[['Lat', 'Lon']]
        # [[point.iloc[i]['Lat'], point.iloc[i]['Lon']] for i in range(0, len(point))]

        pth = Path(bandlatlon, codes)
        mask = pth.contains_points(pointlonlat)

        if len(np.array(point)[mask, :]):
            result = pd.DataFrame(np.array(point)[mask, :], columns=pointcolumns)
            result['Name'] = self.bandinfo.iloc[0]['Name']
            return result
        else:
            print('边框内无点')



    def getNearbandcell(self,cell,knum,rules):
        # 返回字段'Nearbandname', 'NearCi', '小区名称', 'Lat', 'Lon','Ang', 'distance', 'directionD', 'type'

        band=self.bandinfo
        print(self.bandinfo)


        colu = cell.columns.values.tolist()
        print(colu)

        # pointsit=cell.drop_duplitates(['Lat','Lon'])

        def nellcell(singleband):
            # Bandcenter = getGcentre(singleband)
            try:
                inbandpoint = Band(singleband,filter='no').getInBandPoint(cell)
                inbandpoint['nearselect']='select'
            except:
                print('noinbabdcell')
            try:
                inBandname = list(set(inbandpoint['小区名称']))
                pointoutdoor = cell[~cell.小区名称.isin(inBandname)]
            except:
                pointoutdoor=cell
            pointoutdoor = pointoutdoor[pointoutdoor.type == 'outdoor']
            nearcell=Point(singleband).GetPointNearcell(cell,knum,rules)
            nearcell=nearcell[nearcell.columns.difference(['pointLat','pointLon'])]
            nearcell.rename(columns={'point名称':'Name'},inplace=True)
            print(inbandpoint)
            print(nearcell)
            try:
                nearcell=pd.concat(nearcell,inbandpoint)
            except:
                print('inbandpoint不存在')
            return nearcell
        pool=Pool(20)
        results=pool.map(nellcell,[x[1] for x in self.bandinfo.groupby(['Name'])])
        pool.close()
        pool.join()
        results = pd.concat(results)

        return  results





class Cell(object):
    def __init__(self, cellinfo,filter=True):
        if filter==True:
            # bandinfo 包括city Name Lat Lon
            cellinfo.fillna(0, inplace=True)
            cellinfo.replace('', 0, inplace=True)
            cellinfo.replace('Timestamp', '', inplace=True)
            # cellinfo['Ci'] = cellinfo['Ci'].astype(int)
            cellinfo.drop_duplicates(['Lat', 'Lon','Ci','Ang'], inplace=True)
            cellinfo[['Lat', 'Lon']] = cellinfo[['Lat', 'Lon']].astype(float)
            cellinfo = cellinfo[(cellinfo.Lon > 100) & (cellinfo.Lat > 0) & (cellinfo.Lat < 90)]
            try:
                cellinfo['type'] = cellinfo['小区名称'].apply(lambda x: 'indoor' if 'SF' in x or '室分' in x else 'outdoor')
                try:
                    cellinfo['type'] = cellinfo.小区类型.apply(lambda x: 'outdoor' if '室外' in x else 'indoor')
                except:
                    print('no小区类型')
                self.cellcmap = {self.cellinfo.iloc[i]['Ci']: randomcolor(['#DC143C', '#0000FF', '#3CB371', '#FFFF00']) for i in
                                 range(len(self.cellinfo))}
                self.cellavglat = self.cellinfo['Lat'].mean()
                self.cellavglon = self.cellinfo['Lon'].mean()
            except:
                print('单行小区')
            try:
                cellinfo['Ang'] = cellinfo['Ang'].astype(float)
            except:
                print('非特征小区')
            print(cellinfo)
            self.cellinfo = cellinfo[~cellinfo.小区名称.str.contains('NB')]
        else:
            self.cellinfo = cellinfo



    def Createcellband(self):
        colus = self.cellinfo.columns.values.tolist()
        basecellall = self.cellinfo.values.tolist()
        cellall = basecellall * 13
        cellall = sorted(cellall)
        cellall = pd.DataFrame(cellall, columns=colus)

        print(cellall.head(10))
        print(len(cellall))
        numlist = list(range(0, 12))
        numlist.append(0)
        numall = numlist * len(self.cellinfo)
        numall = pd.DataFrame(numall, columns=['adjust'])
        print(numall)
        self.cellinfoband = pd.concat([cellall, numall], axis=1)

        self.cellinfoband['adjust'] = self.cellinfoband.adjust.apply(lambda x: '不调整' if x == 0 else -30 + (x - 1) * 6)

        self.cellinfoband['distance'] = 0.1

        self.cellinfoband.rename(columns={'Lat':'cellLat','Lon':'cellLon'},inplace=True)
        pool = Pool(200)
        resuts = pool.map(Get_distance_point,
                          self.cellinfoband[['cellLat', 'cellLon', 'Ang', 'adjust', 'distance']].values.tolist())
        pool.close()
        pool.join()
        # band经纬度改为标准LatLon
        resuts = pd.DataFrame(resuts, columns=['Lat', 'Lon'])
        self.cellinfoband = pd.concat([self.cellinfoband, resuts], axis=1)
        cellcenter = self.cellinfoband[['Ci','小区名称','Lat', 'Lon']].groupby(['Ci','小区名称']).mean()
        self.cellcenter = pd.DataFrame(cellcenter.reset_index())
        self.cellcenter.columns = ['Ci','小区名称','Lat', 'Lon']
        cellbandgroup = self.cellinfoband.groupby(['Ci','小区名称'])
        self.cellbandgroup = [x[1] for x in cellbandgroup]
        return {'cellband':self.cellinfoband,
                'cellbandgroup': self.cellbandgroup,
                'cellcenter':self.cellcenter
                }


    def GetPointNearcell(self,seachpoint,knum,rules):
        cell=self.cellinfo[['Lat','Lon','小区名称','Ci','Ang']]
        # cell.columns=['Lat','Lon','M小区名称','MCi','MAng']
        seachpoint=seachpoint[['Lat','Lon','Name']]
        seachpoint.columns = ['pointLat', 'pointLon','point名称']
        # nearresults=[]
        site=cell[['Lat','Lon']]
        site.drop_duplicates(inplace=True)
        tree = KDTree(site)
        def searchnearcell(point):
            nonlocal cell,knum,site
            cellout = tree.query(point[0:2], k=knum)
            Ltecellmark = cellout[1].flatten()
            # 生成临近点距离、index列表
            # 转置并去重
            LOONear= site.iloc[Ltecellmark, :]
            near = np.array([point] * len(LOONear))
            # 提取从非边界内小区中提出临近的datafram表
            print(near[0:10])
            LOONear = np.hstack((near, np.array(LOONear)))
            colu =  ['pointLat', 'pointLon','point名称']+['Lat','Lon']
            results = pd.DataFrame(LOONear, columns=colu)
            results[['Lat','Lon']]=results[['Lat','Lon']].astype(float)
            print(results.head())
            cell[['Lat', 'Lon']] = cell[['Lat', 'Lon']].astype(float)
            print(cell.head())
            results = pd.merge(results, cell, on=['Lat','Lon'], how='left')
            results[['Lat','Lon','Ang','pointLat', 'pointLon']] = results[
                ['Lat','Lon','Ang','pointLat', 'pointLon']].astype(float)
            results['distance'] = [get_distance(results.iloc[i][['Lat', 'Lon']].values.tolist() +
                                                results.iloc[i][['pointLat', 'pointLon']].values.tolist()) for i in
                                   range(len(results))]
            results['CtoPdirection'] = [Get_Angle(results.iloc[i][['Lat', 'Lon', 'pointLat', 'pointLon']].values) for i
                                       in
                                       range(len(results))]
            results['directionCPtoA'] = [min([abs(results.iloc[i]['CtoPdirection'] - results.iloc[i]['Ang']),
                                          abs(results.iloc[i]['CtoPdirection'] - results.iloc[i]['Ang'] - 360),
                                          abs(results.iloc[i]['CtoPdirection'] - results.iloc[i]['Ang'] + 360)]) for i
                                     in
                                     range(len(results))]


            try:
                results[['Ci', 'distance', 'CtoPdirection', 'directionCPtoA']] = results[
                    ['Ci', 'distance', 'CtoPdirection', 'directionCPtoA']].astype(int)
            except:
                print('unlongpart')


            for rule in rules:
                results.loc[(rule[1] >= results['distance']) & (results['distance'] >=rule[0]) & (
                        results['directionCPtoA'] <= rule[2]), 'nearselect'] = 'select'


            # results = results[results.nearselect == 'select']

            # nearresults.append(results)
            return results

        pool=Pool(200)
        results=pool.map(searchnearcell,seachpoint.values.tolist())
        pool.close()
        pool.join()
        results = pd.concat(results)




        return results









    def getNeighborcell(self,seachcell,knum,rules):
        cell=self.cellinfo[['Lat','Lon','小区名称','Ci','Ang']]
        cell.columns=['MLat','MLon','M小区名称','MCi','MAng']
        seachcell=seachcell[['小区名称','Ci','Lat','Lon','Ang']]
        seachcell.columns = ['S小区名称', 'SCi', 'SLat', 'SLon', 'SAng']
        # nearresults=[]
        seachsite=seachcell[['SLat', 'SLon']]
        seachsite.drop_duplicates(inplace=True)
        tree = KDTree(seachsite)

        def searchnearcell(point):
            nonlocal cell,seachcell,knum,seachsite

            cellout = tree.query(point[0:2], k=knum)

            Ltecellmark = cellout[1].flatten()
            # 生成临近点距离、index列表


            # 转置并去重
            LOONearsite = seachsite.iloc[Ltecellmark, :]

            LOONear=pd.merge(LOONearsite,seachcell,how='left',on=['SLat', 'SLon'])

            near = np.array([point] * len(LOONear))


            # 提取从非边界内小区中提出临近的datafram表

            print(near[0:10])
            LOONear = np.hstack((near, np.array(LOONear)))

            colu = [ 'MLat', 'MLon','M小区名称', 'MCi', 'MAng'] + ['SLat', 'SLon','S小区名称', 'SCi',  'SAng']

            results = pd.DataFrame(LOONear, columns=colu)
            results[['MLat', 'MLon', 'MAng', 'SLat', 'SLon', 'SAng']] = results[
                ['MLat', 'MLon', 'MAng', 'SLat', 'SLon', 'SAng']].astype(float)
            results['distance'] = [get_distance(results.iloc[i][['MLat', 'MLon']].values.tolist() +
                                                results.iloc[i][['SLat', 'SLon']].values.tolist()) for i in
                                   range(len(results))]
            results['toSdirection'] = [Get_Angle(results.iloc[i][['MLat', 'MLon', 'SLat', 'SLon', ]].values) for i
                                       in
                                       range(len(results))]
            results['directionMS'] = [min([abs(results.iloc[i]['toSdirection'] - results.iloc[i]['MAng']),
                                          abs(results.iloc[i]['toSdirection'] - results.iloc[i]['MAng'] - 360),
                                          abs(results.iloc[i]['toSdirection'] - results.iloc[i]['MAng'] + 360)]) for i
                                     in
                                     range(len(results))]

            results['toMdirection'] = [Get_Angle(results.iloc[i][['SLat', 'SLon', 'MLat', 'MLon' ]].values) for i
                                       in
                                       range(len(results))]
            results['directionSM'] = [min([abs(results.iloc[i]['toMdirection'] - results.iloc[i]['SAng']),
                                          abs(results.iloc[i]['toMdirection'] - results.iloc[i]['SAng'] - 360),
                                          abs(results.iloc[i]['toMdirection'] - results.iloc[i]['SAng'] + 360)]) for i
                                     in
                                     range(len(results))]



            try:
                results[['MCi', 'distance', 'toCdirection', 'directionD']] = results[
                    ['MCi', 'distance', 'toCdirection', 'directionD']].astype(int)
            except:
                print('unlongpart')

            for rule in rules:
                if rule[3]=='single':
                    results.loc[((rule[1] >= results['distance']) & (results['distance'] >=rule[0]) & ((
                            results['directionMS'] <= rule[2])| (
                            results['directionSM'] <= rule[2]))), 'nearselect'] = 'select'
                elif rule[3]=='two':
                    results.loc[((rule[1] >= results['distance']) & (results['distance'] >=rule[0]) & (
                            results['directionMS'] <= rule[2])&(
                            results['directionSM'] <= rule[2])), 'nearselect'] = 'select'

            # results = results[results.nearselect == 'select']

            # nearresults.append(results)
            return results

        pool=Pool(200)
        results=pool.map(searchnearcell,cell.values.tolist())
        pool.close()
        pool.join()
        results = pd.concat(results)




        return results









    def cellNeighborAnalysis(self,neighborpra):
        # neighborpra[[ 'CELLCi',  'NCELLCi']] = neighborpra[
        #     [ 'CELLCi',  'NCELLCi']].astype(int)
        neighborpra= neighborpra[['CELLCi', 'CELLNAME', 'NCELLCi', 'NCELLNAME']]
        neighborpra.columns = ['MCiPRA', 'M小区名称PRA', 'SCiPRA', 'S小区名称PRA']
        neighborpra.drop_duplicates(subset=['MCiPRA', 'SCiPRA'], inplace=True)
        neighborpra[['MCiPRA', 'SCiPRA']] = neighborpra[['MCiPRA', 'SCiPRA']].astype(str)

        nearcell = self.getNeighborcell(self.cellinfo, 15, [[0, 10, 360, 'single'], [10, 100, 180, 'single'],
                                                             [100, 300, 120, 'single'], [300, 500, 150, 'two'],
                                                             [500, 2000, 120, 'two'],[2000, 5000, 90, 'two']])

        nearcell = nearcell[nearcell.nearselect == 'select']


        nearcell.drop_duplicates(subset=['MCi', 'SCi'], keep='first', inplace=True)
        nearcell[['MCi', 'SCi']] = nearcell[['MCi', 'SCi']].astype(str)
        analysisresult = pd.merge(nearcell, neighborpra, how='outer', left_on=['M小区名称', 'S小区名称'],
                                  right_on=['M小区名称PRA', 'S小区名称PRA'])
        print(analysisresult.head())
        cellfit=self.cellinfo[['小区名称','Lon','Lat','Ang']]
        cellfit.rename(columns={'小区名称':'S小区名称PRA','Lon':'SLonPRA','Lat':'SLatPRA','Ang':'SAngPRA'},inplace=True)
        print(cellfit.head())
        analysisresult=pd.merge(analysisresult,cellfit,how='left',left_on=['S小区名称PRA'],right_on=['S小区名称PRA'])
        cellfit = self.cellinfo[['小区名称', 'Lon', 'Lat', 'Ang']]
        cellfit.rename(columns={'小区名称': 'M小区名称PRA', 'Lon': 'MLonPRA', 'Lat': 'MLatPRA', 'Ang': 'MAngPRA'}, inplace=True)
        analysisresult = pd.merge(analysisresult, cellfit, how='left', left_on=['M小区名称PRA'], right_on=['M小区名称PRA'])
        print(analysisresult.head())

        return analysisresult

class Mr(object):
    def __init__(self, net,con):
        self.net=net
        self.con=con

    def getCityMr(self,city):
        sql4g = 'SELECT "Lon","Lat","Ci","CellMRCount","AvgeRSRQ"   FROM "%sMR安徽"   where "city"=%s and "CellMRCount">0' % (
            self.net, "'"+city+"'",)
        citymr= pd.read_sql(sql4g, con=self.con)
        return citymr


    def mrInBand(self,bandinfo,citylist='selecet'):
        if citylist=='selecet':
            sql4g = 'SELECT "Lon","Lat","Ci","CellMRCount","AvgeRSRQ"   FROM "%sMR安徽"   where "city"=%s and "CellMRCount">0  and  ("Lon" between %s and %s) and ("Lat"  between %s and %s)' % (
                self.net, "'" + bandinfo.iloc[0]['city'] + "'", bandinfo['Lon'].min(), bandinfo['Lon'].max(),bandinfo['Lat'].min(), bandinfo['Lat'].max())
        elif citylist=='all':
            sql4g = 'SELECT "Lon","Lat","Ci","CellMRCount","AvgeRSRQ"   FROM "%sMR安徽"   where "CellMRCount">0  and  ("Lon" between %s and %s) and ("Lat"  between %s and %s)' % (
                self.net, bandinfo['Lon'].min(), bandinfo['Lon'].max(),bandinfo['Lat'].min(), bandinfo['Lat'].max())
        Ltemrtemp = pd.read_sql(sql4g, con=self.con)
        print(Ltemrtemp.head())
        print(bandinfo.head())
        LInbandmr = Pointinband([Ltemrtemp, bandinfo])
        print(LInbandmr,'LInbandmr')
        LInbandmr['Ci'] = LInbandmr['Ci'].astype(int)
        LInbandmr[['AvgeRSRQ', 'CellMRCount']] = LInbandmr[['AvgeRSRQ', 'CellMRCount']].astype('float')

        LInbandmr = LInbandmr[['bandname', 'Ci', 'CellMRCount', 'AvgeRSRQ', 'Lat', 'Lon']]
        LInbandmr.columns = ['Mrbandname', 'MrCi', 'CellMRCount', 'AvgeRSRQ', 'Lat', 'Lon']

        LInbandmr['MrCi'] = LInbandmr['MrCi'].astype(str)

        LInbandmr.drop_duplicates(inplace=True)

        LICountbandmr = LInbandmr[['Mrbandname', 'MrCi', 'CellMRCount']].groupby(['Mrbandname', 'MrCi']).sum()
        LIPowerbandmr = LInbandmr[['Mrbandname', 'MrCi', 'AvgeRSRQ']].groupby(['Mrbandname', 'MrCi']).mean()

        LICountbandmr = pd.DataFrame(LICountbandmr.reset_index())
        LIPowerbandmr = pd.DataFrame(LIPowerbandmr.reset_index())

        LICountbandmr = pd.merge(LICountbandmr, LIPowerbandmr, how='outer', left_on=['Mrbandname', 'MrCi'],
                                 right_on=['Mrbandname', 'MrCi'])

        LICountbandmr = LICountbandmr.sort_values(by=['Mrbandname', 'CellMRCount'], ascending=[True, False])
        LICountbandmr['percent'] = round(LICountbandmr['CellMRCount'] / LICountbandmr.Mrbandname.apply(
            lambda x: LICountbandmr.loc[LICountbandmr.Mrbandname == x]['CellMRCount'].sum()), 4) * 100

        Ciname = list(set(LInbandmr['MrCi']))
        Mrcmap = {Ciname[i]: randomcolor(['#DC143C', '#0000FF', '#3CB371', '#FFFF00']) for i in range(len(Ciname))}

        return {'Mrinband':LInbandmr,
                'Mrinbandcount':LICountbandmr,
                'cmap':Mrcmap}

    # def mrRelatcell(self,cell):
    #     for i in range(len(cell)):
    #         sql4g = 'SELECT "Lon","Lat","Ci","CellMRCount","AvgeRSRQ"   FROM "%sMR安徽"   where "city"=%s and "CellMRCount">0  and  ("Lon" between %s and %s) and ("Lat"  between %s and %s)' % (
    #             self.net, "'" + bandinfo.iloc[0]['city'] + "'", bandinfo['Lon'].min(), bandinfo['Lon'].max(),
    #             bandinfo['Lat'].min(), bandinfo['Lat'].max())
    #         Ltemrtemp = pd.read_sql(sql4g, con=self.con)


class Towercell(object):
    def __init__(self,towercell):
        towercell.dropna(subset=['经度', '纬度'],inplace=True)
        towercell.drop(towercell[(towercell.经度==0)|(towercell.纬度==0)].index, inplace=True)
        self.towercellinfo = towercell
        self.towercellinfo =self.towercellinfo[['站址编码','铁塔站址名称', '运营商', '经度', '纬度', '详细地址', '铁塔种类', '铁塔高度(米)', '机房类型']]
        self.towercellinfo .columns = ['towerno','小区名称', 'username', 'Lon', 'Lat', 'address', 'towertype', 'towerhigh', 'housetype']
        self.towercellinfo ['shareinfo'] = self.towercellinfo .towerno.apply(lambda x: ','.join(sorted(list(set(self.towercellinfo .loc[self.towercellinfo .towerno == x]['username'])))))
        self.towercellinfo ['sharenum'] = self.towercellinfo .towerno.apply(lambda x: len(self.towercellinfo .loc[self.towercellinfo .towerno == x]))
        self.towercellinfo=self.towercellinfo[['towerno','小区名称', 'Lon', 'Lat', 'address', 'towertype', 'towerhigh', 'housetype','shareinfo','sharenum']]
        self.towercellinfo.drop_duplicates(inplace=True)


class Railwayuser():
    def __init__(self,user,phonetype):
        self.enginerailway = create_engine('postgresql+psycopg2://postgres:qq403239089@127.0.0.1:5432/RailwayOpt')
        user = user.iloc[:, 1:]
        user.drop_duplicates(inplace=True)
        user.replace(np.nan, 0, inplace=True)
        user = user[user.用户号码 > 0]
        user[['TAC码', '用户号码']] = user[['TAC码', '用户号码']].astype(np.int64)
        user['用户号码'] = user['用户号码'].astype(str)
        user['truephone'] = user.用户号码.apply(
            lambda x: 'yes' if x.startswith(('13', '14', '15', '16', '17', '18', '19')) else 'no')
        user = user[user.truephone == 'yes']


        phonetype.loc[phonetype['UNICOM_2G'] == 1, 'phonenetwork'] = '2G'
        phonetype.loc[phonetype['UNICOM_3G'] == 1, 'phonenetwork'] = '3G'
        phonetype.loc[phonetype['UNICOM_4G'] == 1, 'phonenetwork'] = '4G'

        self.railwayuser=pd.merge(user[['Layer2名称','站点名','TAC码','用户号码','date','日期','小时','分钟']],phonetype[['TAC','COMPANY_NAME','phonenetwork']],how='left',left_on='TAC码',right_on='TAC')
        self.railwayuser.sort_values(['用户号码','date'], inplace=True)

        # railwayphonemove=railwayuser.sort_values(['用户号码','date','日期','小时','分钟'])
    def peruserrouteinfo(self,pyhonno):
        railwaypeoplemove = []
        movepeople=self.railwayuser[self.railwayuser.用户号码==pyhonno]
        if len(movepeople) > 1:
            # movepeople.sort_values('date', inplace=True)
            # print(movepeople)
            for i in range(len(movepeople) - 1):
                firstcolumns = ['站点名', '用户号码', 'date', '日期', '小时', '分钟', 'COMPANY_NAME', 'phonenetwork']
                secondcolumns = ['站点名', 'date', '日期', '小时', '分钟']
                betweensite = [movepeople.iloc[i]['站点名'], movepeople.iloc[i + 1]['站点名']]
                # print(movepeople.iloc[i],movepeople.iloc[i+1])
                betweensite.sort()
                betweensite = 'and'.join(betweensite)
                # print(betweensite, 'betweensite')
                railwaypeoplemove.append(np.hstack(
                    [movepeople[firstcolumns].iloc[i].values, movepeople[secondcolumns].iloc[i + 1].values,
                     np.array(betweensite)]))
                # print(datetime.now(),'railwaypeoplemove')
            railwaypeoplemove = np.vstack(railwaypeoplemove)
            railwaypeoplemove = pd.DataFrame(railwaypeoplemove,
                                             columns=['出发站点名', '用户号码', '出发date', '出发日期', '出发小时', '出发分钟', '终端品牌', '终端网络',
                                                      '到达站点名', '到达date', '到达日期', '到达小时', '到达分钟', '在途区间'])
            railwaypeoplemove[['出发小时', '出发分钟', '到达小时', '到达分钟']] = railwaypeoplemove[
                ['出发小时', '出发分钟', '到达小时', '到达分钟']].astype('int')
            minutebins = [0, 30, 60]
            railwaypeoplemove['分钟区间'] = pd.cut(railwaypeoplemove['出发分钟'].values, minutebins)
            railwaypeoplemove['分钟区间'] = railwaypeoplemove['分钟区间'].astype(str)

            betweentime = [(datetime.strptime(railwaypeoplemove.iloc[i]['到达date'], "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                railwaypeoplemove.iloc[i]['出发date'], "%Y-%m-%d %H:%M:%S")).seconds for i in range(len(railwaypeoplemove))]
            railwaypeoplemove['时间差'] = betweentime



            railwaypeoplemove.to_sql('railwaypeoplemove', con=self.enginerailway, index=False, if_exists='append',
                                     chunksize=50)
            print(datetime.now())

        # return railwaypeoplemove

    def alluserrout(self):
        pool = Pool(20000)
        userphoninfoall=list(set(self.railwayuser['用户号码']))
        pool.map(self.peruserrouteinfo,userphoninfoall)
        pool.close()
        pool.join()
        # band经纬度改为标准LatLon
        # resuts = pd.concat(resuts)
        # # resuts.to_sql('railwaypeoplemove', con=self.enginerailway, index=False, if_exists='append',
        # #                          chunksize=50)
        # print('write', resuts.head())
        # return resuts









def timestamp_to_format(timestamp=None,format = '%Y-%m-%d %H:%M:%S'):
    # try:
    if timestamp:
        time_tuple = time.localtime(timestamp)
        print('time_tuple:',time_tuple)
        #print('type(time_tuple):',type(time_tuple))
        res = time.strftime(format,time_tuple)
    else:
        res = time.strftime(format)
    return res

def randomcolor(rejectcolor):
    for rjtcolor in range(200000000):
        colorArr = ['1','2','3','4','5','6','7','8','9','A','B','C','D','E','F']
        color = ""
        for i in range(6):
            color += colorArr[random.randint(0,14)]
        if "#"+color not in rejectcolor:
            return "#"+color
            break

def clickmouse(x,y,duble=1,right=1):
    # //分别定义一个实例
    m = PyMouse()
    k = PyKeyboard()
    m.click(x,y, duble, right)
    # –鼠标点击
    # x,y –是坐标位置
    # buttong  1表示左键，2表示点击右键


def Creatcolorcmp(data):
    # data可以是一组数据，用来做颜色字典的key
    rjtcolor = ['#DC143C', '#0000FF', '#3CB371', '#FFFF00']
    colorlistkey=list(set(data))
    colorcmap = {colorlistkey[i]: randomcolor(rjtcolor) for i in range(len(colorlistkey))}
    return colorcmap

def Creatpoint(**betweeninfo):
    # betweeninfo是一个字典，包含key值参数：['FLat,'FLon','distance','cutlong']
    #表示含义[起点纬度，起点经度，大于距离开始补点长度，补点的距离间隔]
    # betweeninfo在两个点之间根据起始点经纬度
    # [betweeninfo['FLat'], betweeninfo['FLon']
    # 距离distance、cutlong做点：

    joinline=[]
    cutpart = betweeninfo['distance'] // betweeninfo['cutlong']
    ang = Get_Angle([betweeninfo['FLat'], betweeninfo['FLon'],betweeninfo['SLat'], betweeninfo['SLon']])
    for j in range(1, int(cutpart) + 1):
        newpoint = Get_distance_point(
            [betweeninfo['FLat'], betweeninfo['FLon'], 0, ang, j * betweeninfo['cutlong'] / 1000])
        joinline.append([newpoint[0], newpoint[1]])
    return pd.DataFrame(joinline,columns=['Lat','Lon'])


def Clearline(RTLheanpoint,longcut):

    indexnum = 0
    Nline = []

    for i in range(len(RTLheanpoint) - 1):
        distance = get_distance([RTLheanpoint.iloc[indexnum]['Lat'], RTLheanpoint.iloc[indexnum]['Lon'],
                                               RTLheanpoint.iloc[indexnum + 1]['Lat'],
                                               RTLheanpoint.iloc[indexnum + 1]['Lon']])
        Nline.append(RTLheanpoint.iloc[indexnum][['Lat','Lon']].tolist())
        if distance < longcut:
            RTLheanpoint.drop([i + 1], inplace=True)
        else:
            if distance > longcut+50:
                cutpart = distance // longcut
                ang = Get_Angle([RTLheanpoint.iloc[indexnum]['Lat'], RTLheanpoint.iloc[indexnum]['Lon'],
                                               RTLheanpoint.iloc[indexnum + 1]['Lat'],
                                               RTLheanpoint.iloc[indexnum + 1]['Lon']])
                for j in range(1, int(cutpart)):
                    newpoint = Get_distance_point(
                        [RTLheanpoint.iloc[indexnum]['Lat'], RTLheanpoint.iloc[indexnum]['Lon'], 0, ang,
                         j * longcut / 1000])
                    Nline.append([newpoint[0], newpoint[1]])
            indexnum += 1
    Nline=pd.DataFrame(Nline,columns=['Lat','Lon'])
    return Nline

def Cleargobackpoint(RTLhean,maxIncludedangle=120):
    beginang = Get_Angle([RTLhean.iloc[0]['Lat'], RTLhean.iloc[0]['Lon'], RTLhean.iloc[1]['Lat'],
                                        RTLhean.iloc[1]['Lon']])
    numbfirst = 0
    for i in range(1, len(RTLhean)-1):
        nextang = Get_Angle(
            [RTLhean.iloc[numbfirst]['Lat'], RTLhean.iloc[numbfirst]['Lon'], RTLhean.iloc[numbfirst + 1]['Lat'],
             RTLhean.iloc[numbfirst + 1]['Lon']])
        dt = min([abs(beginang - nextang), abs(beginang - nextang - 360), abs(beginang - nextang + 360)])
        print(beginang, ',', nextang, ',', dt, 'dt')
        if abs(dt) > maxIncludedangle:
            RTLhean.drop([i], inplace=True)
        else:
            beginang = nextang
            numbfirst += 1
    return RTLhean


def get_distance(latloninterval):
    # point格式为[起点lat，起点lon，终点lat，终点lon]
    lat_a = latloninterval[0]
    lon_a = latloninterval[1]
    lat_b = latloninterval[2]
    lon_b = latloninterval[3]

    radlat1 = radians(lat_a)
    radlat2 = radians(lat_b)
    a = radlat1 - radlat2
    b = radians(lon_a) - radians(lon_b)
    s = 2 * asin(sqrt(pow(sin(a/2),2) + cos(radlat1) * cos(radlat2)*pow(sin(b/2),2)))
    earth_radius = 6378137
    s = s * earth_radius
    return s

def get_DBSCANdistance(array_1, array_2):
    lon_a = array_1[0]
    lat_a = array_1[1]
    lon_b = array_2[0]
    lat_b = array_2[1]
    radlat1 = radians(lat_a)
    radlat2 = radians(lat_b)
    a = radlat1 - radlat2
    b = radians(lon_a) - radians(lon_b)
    s = 2 * asin(sqrt(pow(sin(a/2),2) + cos(radlat1) * cos(radlat2)*pow(sin(b/2),2)))
    earth_radius = 6378137
    s = s * earth_radius
    return s




def changwebpage(webfilename, sou, tag):
    file = webfilename
    content = open(file, 'r', encoding="utf-8")
    html_cont = content.read()
    find_content = BeautifulSoup(html_cont, 'lxml')

    for change_script in find_content.find_all('script', src=True):
        print(change_script, change_script['src'])
        change_script.get_text(strip=True)
        if change_script['src'] == sou:
            change_script['src'] = tag
    change_content = str(find_content).encode(encoding='utf-8')  # 尤其注意，soup生成了字典，进行修改后要转为str，并将其固定utf-8编码，才能存回去
    change_html = open(file, "w+b")
    change_html.write(change_content)
    change_html.close()
    print(file + ' ' + 'changed!')

def InputMRtoSql(path,sqlfilename,changciname,cityname,sqlengine):
    # 各地市MR数据导入sql
    # 除256取商就是enodeBid，CI - enodeBid * 256 = cellid
    filelist = os.listdir(path)
    cityen = ['ANQING', 'BENGBU', 'BOZHOU', 'CHIZHOU', 'CHUZHOU', 'FUYANG', 'HEFEI', 'HUAIBEI', 'HUAINAN', 'HUANGSHAN',
              'LIUAN', 'MAANSHAN', 'SUZHOU', 'TONGLING', 'WUHU', 'XUANCHENG']
    print(cityen[5])
    citych = ['安庆', '蚌埠', '亳州', '池州', '滁州', '阜阳', '合肥', '淮北', '淮南', '黄山', '六安', '马鞍山', '宿州', '铜陵', '芜湖', '宣城']
    citydic = {cityen[i]: citych[i] for i in range(len(cityen))}
    print(path)
    print(filelist)
    for file in filelist:
        print(path + file)
        MRtemp = pd.read_csv(path + file, sep=',', low_memory=False, encoding='gb18030')
        MRtemp[changciname] = MRtemp.栅格主覆盖CI.apply(lambda x: str(x // 256) + str(x - x // 256 * 256))
        MRtemp[cityname] = MRtemp.城市.apply(lambda x: citydic[x])
        MRtemp.columns = ['Ci', 'city','Lon', 'Lat',  'CellMRCount', 'AvgeRSRQ']
        print(MRtemp.head())
        MRtemp.to_sql(sqlfilename, con=sqlengine, if_exists='append', index=False, chunksize=10)


def Get_Angle(latloninterval):
    # point格式为[起点lat，起点lon，终点lat，终点lon]
    angle = 0.0
    dx = (latloninterval[3] - latloninterval[1]) * cos(radians(latloninterval[2]))
    dy = latloninterval[2] - latloninterval[0]
    if latloninterval[3] == latloninterval[1]:
        angle = pi / 2.0
        if latloninterval[2] == latloninterval[0]:
            angle = 0.0
        elif latloninterval[2] < latloninterval[0]:
            angle = 3.0 * pi / 2.0
    elif latloninterval[3] > latloninterval[1] and latloninterval[2] > latloninterval[0]:
        angle = atan(dx / dy)
    elif latloninterval[3] > latloninterval[1] and latloninterval[2] < latloninterval[0]:
        angle = pi / 2 + atan(-dy / dx)
    elif latloninterval[3] < latloninterval[1] and latloninterval[2] < latloninterval[0]:
        angle = pi + atan(dx / dy)
    elif latloninterval[3] < latloninterval[1] and latloninterval[2] > latloninterval[0]:
        angle = 3.0 * pi / 2.0 + atan(dy / -dx)
    return (angle * 180 / pi)


def drawbandmap(bandg,idname,popname,color,fillOpacity,mapname):
    latlonband = np.array(bandg[['Lon', 'Lat']]).tolist()
    bandgeo = {"type": "FeatureCollection",
               "features": [
                   {
                       "properties": {"name": 'band'},
                       "id": idname,
                       "type": "Feature",
                       "geometry": {
                           "type": "Polygon",
                           "coordinates": [latlonband]
                       }
                   }]}


    style_function = lambda feature: {'fillOpacity': fillOpacity,
                                      'weight': 2,
                                      'fillColor': color,
                                      'color': color
                                      }

    gj = folium.GeoJson(bandgeo,style_function=style_function)
    gj.add_child(folium.Popup(popname))
    gj.add_to(mapname)

def Get_Appendband(twoinfo):
    # twoinfo:[twoinfo[0], appenddistance]
    # 输入一组pandas格式的，包含字段'Lat', 'Lon'格式的点，输出凸包及凸包扩展点
    print(twoinfo[0][['Lat', 'Lon']])
    twoinfo[0] = np.array(twoinfo[0][['Lat', 'Lon']])
    hull = ConvexHull(twoinfo[0])
    mask = hull.vertices
    mask = np.append(mask, mask[0])
    RTLheanband = twoinfo[0][mask, :]

    # folium.PolyLine(locations=RTLheanband, color='green').add_to(m)
    RTLheanband=np.vstack([RTLheanband,RTLheanband[1]])
    RTLheanband = pd.DataFrame(RTLheanband, columns=['Lat', 'Lon'])

    resultlatlon = []

    for i in range(1, len(RTLheanband)-1):
        firstdirction = Get_Angle(
            [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], RTLheanband.iloc[i - 1]['Lat'],
             RTLheanband.iloc[i - 1]['Lon']])
        seconddirction = Get_Angle(
            [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], RTLheanband.iloc[i + 1]['Lat'],
             RTLheanband.iloc[i + 1]['Lon']])
        directionD = min([abs(seconddirction - firstdirction),
                          abs(seconddirction - firstdirction - 360),
                          abs(seconddirction - firstdirction + 360)])

        # resultdirecton = firstdirction - (180 - directionD / 2)
        resultlong = twoinfo[1] / sin(radians(directionD / 2))

        # movelatlon = Get_distance_point(
        #     [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], firstdirction, (180 - directionD / 2),
             # resultlong])
        # folium.Circle(location=movelatlon, radius=10, color='red').add_to(m)

        resultlatlon.append(Get_distance_point(
            [RTLheanband.iloc[i]['Lat'], RTLheanband.iloc[i]['Lon'], firstdirction, (180 - directionD / 2),
             resultlong]))
        #
        # print(resultlatlon)
    resultlatlon.append(resultlatlon[0])
    Appendband = pd.DataFrame(resultlatlon, columns=['Lat', 'Lon'])
    return RTLheanband[:-1],Appendband


def Get_parallel_line(linepoint,distance):
    resultlatlon = []
    colbin=linepoint.columns.values.tolist()
    for i in range(1, len(linepoint)-1):
        try:
            firstdirction = Get_Angle(
                [linepoint.iloc[i]['Lat'], linepoint.iloc[i]['Lon'], linepoint.iloc[i - 1]['Lat'],
                 linepoint.iloc[i - 1]['Lon']])
        except:
            firstdirction=180
        try:
            seconddirction = Get_Angle(
                [linepoint.iloc[i]['Lat'], linepoint.iloc[i]['Lon'], linepoint.iloc[i + 1]['Lat'],
                 linepoint.iloc[i + 1]['Lon']])
        except:
            seconddirction=180

        directionD = min([abs(seconddirction - firstdirction),
                          abs(seconddirction - firstdirction - 360),
                          abs(seconddirction - firstdirction + 360)])

        print(directionD / 2)
        print(radians(directionD / 2))
        print(sin(radians(directionD / 2)))
        if directionD != 0 and directionD >= 90:
            resultlong = distance/ sin(radians(directionD / 2))
            temp=linepoint[i:i+1].values.tolist()
            temp=temp[0]+Get_distance_point([linepoint.iloc[i]['Lat'],linepoint.iloc[i]['Lon'], firstdirction, -(180 - directionD / 2),
                 resultlong])+[firstdirction,seconddirction,directionD ]
            resultlatlon.append(temp)
    parallel_line = pd.DataFrame(resultlatlon, columns=colbin+['Latparallel', 'Lonparallel','firstdirction','seconddirction','directionD'])
    parallel_line['Lat']=parallel_line['Latparallel']
    parallel_line['Lon'] = parallel_line['Lonparallel']
    return parallel_line

    
    
def Pointinband(tooinfo):
    # tooinfo为列表结构，包含两个元素point, band,都为pandas数据结构
    # 输出为pandas结构

    pointcolumns=tooinfo[0].columns.values.tolist()

    codes=[Path.MOVETO]
    for bandlong in range(1,len(tooinfo[1])-1):
        codes.append(Path.LINETO)
    codes.append(Path.CLOSEPOLY)

    bandlatlon=tooinfo[1][['Lat','Lon']]

    pointlonlat=tooinfo[0][['Lat','Lon']]
    # [[tooinfo[0].iloc[i]['Lat'], tooinfo[0].iloc[i]['Lon']] for i in range(0, len(tooinfo[0]))]

    pth = Path(bandlatlon, codes)
    mask = pth.contains_points(pointlonlat)


    if len(np.array(tooinfo[0])[mask,:]):
        result=pd.DataFrame(np.array(tooinfo[0])[mask,:],columns=pointcolumns)
        result['bandname']=tooinfo[1].iloc[0]['Name']
        return result
    else:
        print('边框内无点')





def Nearbandcell(point,band):
    # 返回字段'Nearbandname', 'NearCi', '小区名称', 'Lat', 'Lon','Ang', 'distance', 'directionD', 'type'
    colu=point.columns.values.tolist()
    print(colu)
    gruopbandnametemp = list(set(band['Name']))[0]
    Bandcenter=getGcentre(band)


    inbandpoint=Pointinband([point,band])


    try:
        inBandname = list(set(inbandpoint['小区名称']))
        point =point[~point.小区名称.isin(inBandname)]


    except:
        print('非必选包含关系点')

    point = point[point.type == 'outdoor']



    bandresults=[]
    for bandid in range(len(band)):
        colu = point.columns.values.tolist()
        bandpointlatlon = band[bandid:bandid+1][['Lat', 'Lon']].values.tolist()[0]
        print(bandpointlatlon)
        tree = KDTree(point[['Lat', 'Lon']])
        cellout = tree.query(bandpointlatlon, k=15)

        Ltecellmark = cellout[1].flatten()
        # 生成临近点距离、index列表
        print(np.array([bandpointlatlon] * len(Ltecellmark)))
        near = np.vstack(
            (np.array([gruopbandnametemp] * len(Ltecellmark)), np.array([bandpointlatlon] * len(Ltecellmark)).T)).T
        # 转置并去重
        LOONear = point.iloc[Ltecellmark, :]

        # 提取从非边界内小区中提出临近的datafram表

        print(near[0:10])
        LOONear = np.hstack((np.array(LOONear), near))
        print(colu)
        colu=colu+['bandname','bandpointlat','bandpointlon']
        print(colu)
        results=pd.DataFrame(LOONear,columns=colu)
        bandresults.append(results)

    results=pd.concat(bandresults,ignore_index=True)
    results[['Lat', 'Lon', 'bandpointlat', 'bandpointlon']] = results[['Lat', 'Lon', 'bandpointlat', 'bandpointlon']].astype(float)
    results['distance']=[get_distance(results[i:i+1][['Lon', 'Lat']].values.tolist()[0]+results[i:i+1][['bandpointlon', 'bandpointlat']].values.tolist()[0]) for i in
                               range(len(results))]

    results.sort_values(by=["bandname", '小区名称', 'distance'], ascending=[False, False, True], inplace=True)
    results.drop_duplicates(subset=['Ci', '小区名称', 'Lon', 'Lat', 'bandname'], keep='first', inplace=True)
    results = pd.merge(results, Bandcenter, on='bandname', how='left')

    results['toCdirection'] = [Get_Angle(results.iloc[i][['Lat', 'Lon','centerlat', 'centerlon']].values) for i in
                               range(len(results))]
    results['directionD'] = [min([abs(results.iloc[i]['toCdirection'] - results.iloc[i]['Ang']),
                      abs(results.iloc[i]['toCdirection']  - results.iloc[i]['Ang'] - 360),
                      abs(results.iloc[i]['toCdirection']  - results.iloc[i]['Ang'] + 360)]) for i in
                               range(len(results))]

    print(results,'notfilt')
    results.loc[((150 >= results['distance']) & (results['directionD'] < 120)) | \
                    ((300 >= results['distance']) & (results['distance'] > 150) & (
                            results['directionD'] < 90)) | \
                    ((400 >= results['distance']) & (results['distance'] > 300) & (
                            results['directionD'] < 60)) | \
                    ((500 >= results['distance']) & (results['distance'] > 400) & (
                            results['directionD'] < 45)) | \
                    ((600 >= results['distance']) & (results['distance'] > 500) & (
                            results['directionD'] < 30)) | \
                    ((800 >= results['distance']) & (results['distance'] > 600) & (
                            results['directionD'] < 15)),'nearselect']='select'

    results.loc[results.nearselect==np.nan,'nearselect']='noselect'
    print(results, 'filt')

    try:
        inbandpoint['distance'] = 0
        inbandpoint['centerlat'] = 0
        inbandpoint['centerlon'] = 0
        inbandpoint['toCdirection'] = 0
        inbandpoint['directionD'] = 0
        inbandpoint['nearselect'] = 'select'
        results = pd.concat([results, inbandpoint], axis=0)
    except:
        print('边框内无小区')

    results[['Lat', 'Lon', 'Ang','distance', 'directionD']] = results[
        ['Lat', 'Lon','Ang','distance', 'directionD']].astype(float)
    results = results[(results.nearselect == 'select') | (results.distance < 200)]
    print(results, 'scfilt')
    results = results[
        ['bandname', 'Ci', '小区名称', 'Lat', 'Lon', 'Ang','distance', 'directionD', 'type']]
    results.columns = ['Nearbandname', 'NearCi', '小区名称', 'Lat', 'Lon','Ang', 'distance', 'directionD', 'type']
    results.drop_duplicates(inplace=True)
    results = pd.DataFrame(results.reset_index())
    results['NearCi'] = results['NearCi'].astype(str)
    results[['Lat', 'Lon', 'Ang','distance', 'directionD']] = results[
        ['Lat', 'Lon','Ang', 'distance', 'directionD']].astype(float)
    print(results, 'drop')






    return  results




def Nearpointcell(threeinfo):
    # gruopbandnametemp = list(set(band['Name']))[0]
    # for bandid in range(len(band)):
    #POINT 格式 Lat Lon
    # cell, point, getnum
    # bandpointlatlon = list(band.iloc[bandid][['lat', 'lon']].values)

    tree = KDTree(threeinfo[0][['Lat', 'Lon']])
    cellout = tree.query(threeinfo[1], k=threeinfo[2])
    print(cellout)
    print(threeinfo[1])

    # distance = cellout[0].flatten() * 111.11 * 1000
    # print(distance)
    cellmark= cellout[1].flatten()
    # 生成临近点距离、index列表
    print(cellmark)
    pointinfo = np.array([threeinfo[1]] * len(cellmark))
    # 转置并去重
    # print(threeinfo[0])
    LOONear = threeinfo[0].iloc[cellmark,:]
    # 提取从非边界内小区中提出临近的datafram表

    Coluin = threeinfo[0].columns.values.tolist()



    LOONear = np.hstack((np.array(LOONear), pointinfo))
    Coluin.append('pointLat')
    Coluin.append('pointLon')

    return pd.DataFrame(LOONear,columns=Coluin)


def SearchNearpoint(nearpoint,sourcepoint,searchnum):
    # sourcepoint 结构必须['Lat', 'Lon'...........]
    tree = KDTree(nearpoint[['Lat', 'Lon']])
    Coluinnearpoint = nearpoint.columns.values.tolist()
    sourcepoint.rename(columns={'Lat':'pointLat','Lon':'pointLon'},inplace=True)
    Coluinsearchpoint = sourcepoint.columns.values.tolist()

    def pointfit(point):
        nonlocal tree,searchnum,nearpoint,Coluinnearpoint,Coluinsearchpoint
        cellout = tree.query(point[0:2], k=searchnum)
        cellmark= cellout[1].flatten()
        # 生成临近点距离、index列表
        print(cellmark)
        pointinfo = np.array([point] * len(cellmark))
        # 转置并去重
        # print(threeinfo[0])
        LOONear = nearpoint.iloc[cellmark,:]
        # 提取从非边界内小区中提出临近的datafram表
        LOONear = np.hstack((np.array(LOONear), pointinfo))
        Coluin=Coluinnearpoint+Coluinsearchpoint
        return pd.DataFrame(LOONear,columns=Coluin)
    pool=Pool(200)
    results=pool.map(pointfit,sourcepoint.values.tolist())
    pool.close()
    pool.join()
    results = pd.concat(results)
    return results

def getGcentre(bandmap):
    area = 0.0
    # 多边形面积
    Gx = 0.0
    Gy = 0.0
    # 重心的x、y
    bandsize = len(bandmap)
    for i in range(0, bandsize):
        print(i % bandsize)
        iLatiLng = bandmap[['Lat', 'Lon']].iloc[i % bandsize].to_list()
        nextLatLng = bandmap[['Lat', 'Lon']].iloc[i - 1].to_list()
        temp = (iLatiLng[0] * nextLatLng[1] - iLatiLng[1] * nextLatLng[0]) / 2.0
        area += temp
        Gx += temp * (iLatiLng[0] + nextLatLng[0]) / 3.0
        Gy += temp * (iLatiLng[1] + nextLatLng[1]) / 3.0
    Gx = Gx / area
    Gy = Gy / area
    return pd.DataFrame([[list(set(bandmap['Name']))[0], Gx, Gy]], columns=['bandname', 'centerlat', 'centerlon'])


def Cellfilter(Ltecell):
    rjtcolor = ['#DC143C', '#0000FF', '#3CB371', '#FFFF00']
    Ltecell.fillna(0, inplace=True)
    Ltecell.replace('', 0, inplace=True)
    Ltecell.replace('Timestamp', '', inplace=True)
    Ltecell = Ltecell[(Ltecell.Lon > 0) & (Ltecell.Lat > 0)]
    # Ltecell['小区名称']=Ltecell['小区名称'].str.replace('-','')
    # '经度','纬度','实际方位角'作为计算用的表做类型转换
    Ltecell[['Lat', 'Lon', 'Ang']] = Ltecell[['Lat', 'Lon', 'Ang']].astype(float)
    Ltecell['Ci'] = Ltecell['Ci'].apply(int)
    # '经度','纬度','实际方位角'作为计算用的表做类型转换
    # 增加区分室分的type列
    Ltecell['type'] = Ltecell.小区名称.apply(lambda x: 'indoor' if 'SF' in x or '室分' in x else 'outdoor')
    Ltecell = Ltecell[~Ltecell.小区名称.str.contains('NB')]

    Ltecellcmap = {Ltecell.iloc[i]['小区名称']: randomcolor(rjtcolor) for i in range(len(Ltecell))}
    return Ltecell,Ltecellcmap


def Get_distance_point(LatLonDD):
    """
    根据经纬度，距离，方向获得一个地点 lat,lon,Ang,调整偏移（不变：‘不调整’）, distance
    :param distance: 距离（千米）
    :source:纬度,经度,direction: 方向（北：0，东：90，南：180，西：360）
    :return:目标经纬度：[纬度,经度]
    """
    if LatLonDD[3]=='不调整':
        return [LatLonDD[0], LatLonDD[1]]
    else:
        start = geopy.Point(LatLonDD[0], LatLonDD[1])
        d = geopy.distance.VincentyDistance(kilometers=LatLonDD[4])
        return list(d.destination(point=start, bearing=LatLonDD[2]+LatLonDD[3]))[0:2]



def Createcellband(Ltecell):
    """

    :param pandascell:
    :return:
    """
    Ltecell.fillna(0, inplace=True)
    Ltecell.replace('', 0, inplace=True)
    Ltecell.replace('Timestamp', '', inplace=True)
    Ltecell = Ltecell[(Ltecell.Lon > 0) & (Ltecell.Lat > 0)]
    # Ltecell['小区名称']=Ltecell['小区名称'].str.replace('-','')
    # '经度','纬度','实际方位角'作为计算用的表做类型转换
    Ltecell[['Lat', 'Lon', 'Ang']] = Ltecell[['Lat', 'Lon', 'Ang']].astype(float)
    Ltecell['Ci'] = Ltecell['Ci'].apply(int)
    # '经度','纬度','实际方位角'作为计算用的表做类型转换
    # 增加区分室分的type列
    Ltecell['type'] = Ltecell.小区名称.apply(lambda x: 'indoor' if 'SF' in x or '室分' in x else 'outdoor')

    colus=Ltecell.columns.values.tolist()
    basecellall=Ltecell.values.tolist()
    cellall=basecellall*13
    cellall=sorted(cellall)
    cellall=pd.DataFrame(cellall,columns=colus)

    print(cellall.head(10))
    print(len(cellall))
    numlist=list(range(0,12))
    numlist.append(0)
    numall=numlist*len(Ltecell)
    numall=pd.DataFrame(numall,columns=['adjust'])
    print(numall)
    Ltecellband=pd.concat([cellall,numall],axis=1)
    Ltecellband['adjust']=Ltecellband.adjust.apply(lambda x:'不调整' if x==0 else -30+(x-1)*6)
    Ltecellband['distance']=0.1
    pool=Pool(200)
    resuts=pool.map(Get_distance_point,Ltecellband[['Lat','Lon','Ang','adjust','distance']].values.tolist())
    pool.close()
    pool.join()
    print(resuts)

    resuts=pd.DataFrame(resuts,columns=['bandLat','bandLon'])

    Ltecellband=pd.concat([Ltecellband,resuts],axis=1)
    return Ltecellband

def  LinepointDreduce(linepoint,subnum):
    # 线上的点降维
    # 构造分段的gj数据点
    angles = [90]
    for i in range(len(linepoint) - 1):
        info = Geodesic.WGS84.Inverse(
            linepoint.iloc[i]['Lat'], linepoint.iloc[i]['Lon'],
            linepoint.iloc[i + 1]['Lat'], linepoint.iloc[i + 1]['Lon']
        )
        angles.append(info['azi2'])
    print(angles)

    # Change from CW-from-North to CCW-from-East.
    angles = np.deg2rad(450 - np.array(angles))

    # Normalize the speed to use as the length of the arrows.
    r = 1
    linepoint['u'] = r * np.cos(angles)
    linepoint['v'] = r * np.sin(angles)

    fig, ax = plt.subplots()
    linepoint = linepoint.dropna()

    # This style was lost below.
    ax.plot(
        linepoint['Lon'],
        linepoint['Lat'],
        color='darkorange',
        linewidth=5,
        alpha=0.5
    )

    # This is preserved in the SVG icon.
    sub = subnum
    kw = {'color': 'deepskyblue', 'alpha': 0.8, 'scale': 10}
    ax.quiver(linepoint['Lon'][::sub],
              linepoint['Lat'][::sub],
              linepoint['u'][::sub],
              linepoint['v'][::sub], **kw)

    gj = mplleaflet.fig_to_geojson(fig=fig)
    # 构造分段的gj数据点
    Dpoint=[]
    for feature in gj['features']:
        if feature['geometry']['type'] == 'LineString':
            continue
        elif feature['geometry']['type'] == 'Point':
            lon, lat = feature['geometry']['coordinates']
            Dpoint.append([lat,lon])

    return pd.DataFrame(Dpoint,columns=['Lat','Lon'])

            # 线上的点降维

def sendmarkdown(webhook,massage):
    my_data = {
        "msgtype": "markdown",
        "markdown": {"title": " ",
                     "text": " "
                     },
        "at": {
            "isAtAll": True
        }
    }
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    url=webhook
    my_data["markdown"]["title"]='lTE零话务报表'
    my_data["markdown"]["text"]=massage

    sendData = json.dumps(my_data)  # 将字典类型数据转化为json格式
    sendDatas = sendData.encode("utf-8")  # python3的Request要求data为byte类型
    # 发送请求
    request = urllib.request.Request(url=url, data=sendDatas, headers=header)
    # 将请求发回的数据构建成为文件格式
    opener = urllib.request.urlopen(request)
    print(opener.read())

def ReadExcelFileSameSheet(filename):
    y=pd.ExcelFile(filename).sheet_names
    report=[]
    for sheet in y:
        x = pd.read_excel(filename,sheet_name=sheet)
        colum=x.columns.values.tolist()
        columc=[]
        for co in colum:
            columc.append(co.split('(')[0])
        x.columns=columc
        report.append(x)
    report=pd.concat(report)
    return report







def GetPreReport(reporturl,reporttitle,engineinfo,downlosdpath='C:\\Users\\Banch\\Downloads\\',alarmwebhook= 'https://oapi.dingtalk.com/robot/send?access_token=4953d3d105349724726f815ff64e8d56aee658f4e55ae028984d9955988115b6'):
    driver=webdriver.Chrome()
    driver.maximize_window()
    driver.get('https://134.98.158.72:8443/common/assets/htmls/main/main.html')
    for i in range(0,700):
        try:
            driver.find_element_by_id('username').clear()  # 用户名
            driver.find_element_by_id('username').send_keys('tonglinglte')
            driver.find_element_by_id('value').clear()
            driver.find_element_by_id('value').send_keys('TLlte@123456')
            driver.find_element_by_id('submitData').click()
            print('打开主页面')
            break
        except (Exception,BaseException) as e:
            sendmarkdown(alarmwebhook,repr(e))
            time.sleep(1)
            print(i,'秒已过，等待登陆prs系统')

    for i in range(0,1000):
    # 当天数据查询----------------------------------------
        try:
            js = 'window.open("url")'
            driver.execute_script(js)
            handles = driver.window_handles
            print(handles, '待打开当天页面')
            driver.switch_to.window(handles[1])
            driver.get(reporturl)
            break
        except (Exception,BaseException) as e:
            sendmarkdown(alarmwebhook,repr(e))
            time.sleep(1)
            print(i, '秒已过，等待打开需要获取报表页面')

    time.sleep(10)
    for i in range(0,100000):
        try:
            driver.find_element_by_class_name('exportRpt').click()
            break
        except (Exception,BaseException) as e:
            sendmarkdown(alarmwebhook,repr(e))
            time.sleep(1)
            print(i, '秒已过，等待打开获取报表页面')

    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="1"]').click()

    for i in range(0,10000):
        driver.find_element_by_class_name('prs_btn_green').click()
        break
    else:
        time.sleep(1)
        print(i, '秒已过，等待打开获取报表下载点击页面')
    time.sleep(10)
    readyname=driver.find_element_by_class_name('prs_task_name').text
    print(readyname)
    taskname=driver.find_elements_by_class_name('prs_task_name')
    taskpro=driver.find_elements_by_class_name('prs_task_progress')
    taskdown=driver.find_elements_by_class_name('prs_task_downlink')



    for i in range(2000):
        filelist = os.listdir(downlosdpath)
        if len(filelist):
            for file in filelist:
                os.remove(downlosdpath + file)
                print(downlosdpath + file, '文件已删除')
        else:
            break



    for i in range(len(taskname)):
        print(taskname[i].text)
        if taskname[i].text==readyname:
            print(taskpro[i].text)
            for over in range(0, 2000000):
                try:
                    progresstext = taskpro[i].text
                    if progresstext == '100%':
                        time.sleep(3)
                        print(taskpro[i].text)
                        taskdown[i].click()
                        print(taskpro[i].text,'已点击下载')
                        break
                    else:
                        time.sleep(3)

                except (Exception,BaseException) as e:
                    testwebhook = 'https://oapi.dingtalk.com/robot/send?access_token=4953d3d105349724726f815ff64e8d56aee658f4e55ae028984d9955988115b6'
                    sendmarkdown(alarmwebhook,repr(e))
                    time.sleep(3)
                    print(over, '秒已过，等待保存报表')
            break


    time.sleep(10)
    for filnum in range(1,70000):
        filelist = os.listdir(downlosdpath)

        i=0
        for file in filelist:
            if reporttitle in file:
                i+=1
                print(i,reporttitle)
        if i==1:
            break
        else:
            print('正在等待',i,len(filelist))
            time.sleep(1)
    driver.close()
    print(handles[0],'关闭原始表')
    driver.switch_to.window(handles[0])
    driver.close()

    time.sleep(3)


    filelist = os.listdir(downlosdpath)
    for zipfileinfo in filelist:
        if reporttitle in  zipfileinfo:
            if 'zip' in zipfileinfo:
                print(downlosdpath + zipfileinfo)
                f = zipfile.ZipFile(downlosdpath + zipfileinfo, 'r')
                for file in f.namelist():
                    print(file)
                    f.extract(file, downlosdpath)
                    if file[-4:]=='xlsx':
                        os.rename(downlosdpath+file,downlosdpath+reporttitle+'.xlsx')
                        print(downlosdpath+file,downlosdpath+reporttitle+'.xlsx')
                    # metrics = np.array(pd.read_csv(file))
                        Monitorallall=pd.read_excel(downlosdpath+reporttitle+'.xlsx')
                    elif file[-3:]=='csv':
                        os.rename(downlosdpath + file, downlosdpath + reporttitle + '.csv')
                        print(downlosdpath + file, downlosdpath + reporttitle + '.csv')
                        # metrics = np.array(pd.read_csv(file))
                        Monitorallall = pd.read_csv(downlosdpath + reporttitle + '.csc',sep=',',low_memory=False,header=3)
                    f.close()
                # shutil.move(path + zipfileinfo, 'D:\\PycharmProjects\\Dingdingopration-PRS\\getfromprs\\' + zipfileinfo)

    print(Monitorallall.head())
    Monitorcul=Monitorallall.columns.tolist()
    # cul={}
    for x in Monitorcul:
        Monitorallall.rename(columns={x:x.split('(')[0]},inplace=True)
        # cul.append(x:x.split('(')[0])
    # print(cul)
    # Monitorallall=pd.DataFrame(Monitorallall,columns=cul)
    print(Monitorallall.head())

    try:
        basetable=pd.read_sql_table(reporttitle,con=engineinfo)
        Monitorallall=pd.merge(Monitorallall,basetable[['日期','时间','小区名称','基站名称']],on=['日期','时间','小区名称'],how='left')
        print(Monitorallall.head(),'meger')
        Monitorallall=Monitorallall[Monitorallall.基站名称_y.isnull()==True]
        print(Monitorallall.head(),'null')
        Monitorallall=Monitorallall[Monitorallall.columns.difference(['基站名称_y'])]
        Monitorallall.rename(columns={'基站名称_x':'基站名称'},inplace=True)
        print(Monitorallall.head(), 'rename')
        Monitorallall.to_sql(reporttitle,con=engineinfo,if_exists='append',index=False)
    except:
        Monitorallall.to_sql(reporttitle, con=engineinfo, if_exists='replace', index=False)


def GetPreReportMouse(reporturl,reporttitle,pagemouse,reportmouse,engineinfo,path='C:\\Users\\Administrator\\Downloads\\',testwebhook= 'https://oapi.dingtalk.com/robot/send?access_token=4953d3d105349724726f815ff64e8d56aee658f4e55ae028984d9955988115b6'):
    m=PyMouse()
    k = PyKeyboard()
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get('https://134.98.158.72:8443/common/assets/htmls/main/main.html')
    m.click(pagemouse[0],pagemouse[1])
    k.tap_key(k.enter_key)

    for i in range(0, 700):
        try:
            driver.find_element_by_id('username').clear()  # 用户名
            driver.find_element_by_id('username').send_keys('tonglinglte')
            driver.find_element_by_id('value').clear()
            driver.find_element_by_id('value').send_keys('TLlte@123456')
            driver.find_element_by_id('submitData').click()
            print('打开主页面')
            break
        except (Exception, BaseException) as e:
            testwebhook = 'https://oapi.dingtalk.com/robot/send?access_token=4953d3d105349724726f815ff64e8d56aee658f4e55ae028984d9955988115b6'
            sendmarkdown(testwebhook, repr(e))
            time.sleep(1)
            print(i, '秒已过，等待登陆prs系统')

    time.sleep(10)
    m.click(105, 450)
    # driver.find_element_by_id('prs.reportmanagement.reportList').click()
    time.sleep(10)

    m.click(reportmouse[0], reportmouse[1])
    time.sleep(10)
    handles = driver.window_handles
    print(handles, '待打开当天页面')


    driver.switch_to.window(handles[-1])

    time.sleep(10)
    for i in range(0, 100000):
        try:
            driver.find_element_by_class_name('exportRpt').click()
            break
        except (Exception, BaseException) as e:
            testwebhook = 'https://oapi.dingtalk.com/robot/send?access_token=4953d3d105349724726f815ff64e8d56aee658f4e55ae028984d9955988115b6'
            sendmarkdown(testwebhook, repr(e))
            time.sleep(1)
            print(i, '秒已过，等待打开获取报表页面')

    #
    time.sleep(2)
    driver.find_element_by_xpath('//*[@id="1"]').click()

    for i in range(0, 10000):
        driver.find_element_by_class_name('prs_btn_green').click()
        break
    else:
        time.sleep(1)
        print(i, '秒已过，等待打开获取报表下载点击页面')
    time.sleep(10)
    readyname = driver.find_element_by_class_name('prs_task_name').text
    print(readyname)
    taskname = driver.find_elements_by_class_name('prs_task_name')
    taskpro = driver.find_elements_by_class_name('prs_task_progress')
    taskdown = driver.find_elements_by_class_name('prs_task_downlink')
    print(driver.find_elements_by_class_name('prs_task_progress'))
    print(driver.find_elements_by_class_name('prs_task_name'))

    for i in range(2000):
        filelist = os.listdir(path)
        if len(filelist):
            for file in filelist:
                os.remove(path + file)
                print(path + file, '文件已删除')
        else:
            break

    for i in range(len(taskname)):
        print(taskname[i].text)
        if taskname[i].text == readyname:
            print(taskpro[i].text)
            for over in range(0, 2000000):
                try:
                    progresstext = taskpro[i].text
                    if progresstext == '100%':
                        time.sleep(3)
                        print(taskpro[i].text)
                        taskdown[i].click()
                        print(taskpro[i].text, '已点击下载')
                        break
                    else:
                        time.sleep(3)
                        print(taskpro[i].text)

                        print(taskname[i].text)
                        print(over, '秒已过，等待保存报表')
                except (Exception, BaseException) as e:
                    testwebhook = 'https://oapi.dingtalk.com/robot/send?access_token=4953d3d105349724726f815ff64e8d56aee658f4e55ae028984d9955988115b6'
                    sendmarkdown(testwebhook, repr(e))
                    time.sleep(3)
                    print(over, '秒已过，等待保存报表')
            break



    time.sleep(10)
    for filnum in range(1, 70000):
        filelist = os.listdir(path)
        print(filelist)
        print(len(filelist))
        i = 0
        for file in filelist:
            if (reporttitle in file) and file[-4:]!='load':
                i += 1
                print(i, 'xz文件')
        if i == 1:
            filnum=80000
            break
        else:
            print('正在等待', len(filelist))
            time.sleep(1)
            print(i)
    time.sleep(20)
    driver.close()
    print(handles[0], '关闭原始表')
    driver.switch_to.window(handles[0])
    driver.close()
    driver.quit()
    time.sleep(3)


    filelist = os.listdir(path)
    for zipfileinfo in filelist:
        if reporttitle in  zipfileinfo:
            if 'zip' in zipfileinfo:
                print(path + zipfileinfo)
                f = zipfile.ZipFile(path + zipfileinfo, 'r')
                for file in f.namelist():
                    print(file)
                    f.extract(file, path)
                    if file[-4:]=='xlsx':
                        os.rename(path+file,path+reporttitle+'.xlsx')
                        print(path+file,path+reporttitle+'.xlsx')
                    # metrics = np.array(pd.read_csv(file))
                        Monitorallall=pd.read_excel(path+reporttitle+'.xlsx')
                    elif file[-3:]=='csv':
                        os.rename(path + file, path + reporttitle + '.csv')
                        print(path + file, path + reporttitle + '.csv')
                        # metrics = np.array(pd.read_csv(file))
                        Monitorallall = pd.read_csv(path + reporttitle + '.csc',sep=',',low_memory=False,header=3)
                    f.close()
                # shutil.move(path + zipfileinfo, 'D:\\PycharmProjects\\Dingdingopration-PRS\\getfromprs\\' + zipfileinfo)

    print(Monitorallall.head())
    Monitorcul=Monitorallall.columns.tolist()
    # cul={}
    for x in Monitorcul:
        Monitorallall.rename(columns={x:x.split('(')[0]},inplace=True)
        # cul.append(x:x.split('(')[0])
    # print(cul)
    # Monitorallall=pd.DataFrame(Monitorallall,columns=cul)
    print(Monitorallall.head())

    try:
        basetable=pd.read_sql_table(reporttitle,con=engineinfo)
        Monitorallall=pd.merge(Monitorallall,basetable[['日期','时间','小区名称','基站名称']],on=['日期','时间','小区名称'],how='left')
        print(Monitorallall.head(),'meger')
        Monitorallall=Monitorallall[Monitorallall.基站名称_y.isnull()==True]
        print(Monitorallall.head(),'null')
        Monitorallall=Monitorallall[Monitorallall.columns.difference(['基站名称_y'])]
        Monitorallall.rename(columns={'基站名称_x':'基站名称'},inplace=True)
        print(Monitorallall.head(), 'rename')
        Monitorallall.to_sql(reporttitle,con=engineinfo,if_exists='append',index=False)
    except:
        Monitorallall.to_sql(reporttitle, con=engineinfo, if_exists='replace', index=False)

def GetYiyangReport(namelist,cell,path,enginecon,mousepoint):
# 字典参数：reportadmin,alarm,cut,for2019,droporzero,citydown,citytl,cityadd,timeadd,dubtime,addtime,timeup,firsttime,excelpoint,download
    for name in namelist:
        k = PyKeyboard()
        m = PyMouse()
        driver = webdriver.Ie()
        driver.maximize_window()
        driver.get("http://134.98.154.11/WNMSWeb/Login.aspx?ReturnUrl=%2fWNMSWeb%2fdefault.aspx")
        data = driver.title
        print(data)
        print(driver.find_element_by_id('txtUserName').tag_name)
        driver.find_element_by_id('txtUserName').send_keys('t')
        # 向下及点击进入主页面
        time.sleep(1)
        k.tap_key(k.down_key)
        time.sleep(1)

        k.tap_key(k.enter_key)
        time.sleep(3)

        k.tap_key(k.enter_key)



        # 打开报表页面
        time.sleep(20)
        m.click(mousepoint['reportadmin'][0], mousepoint['reportadmin'][1])



        # 打开断站页面
        time.sleep(5)
        m.click(mousepoint['alarm'][0], mousepoint['alarm'][1])

        # 打开断站页面
        time.sleep(10)
        m.click(mousepoint['cut'][0], mousepoint['cut'][1])

        # 打开退服专题
        time.sleep(10)
        m.click(mousepoint['for2019'][0], mousepoint['for2019'][1])

        time.sleep(5)
        for i in range(0, 3):
            k.tap_key(k.down_key)

        if name == '超24小时小区零话务':
            # 打开零话务明细
            time.sleep(5)
            m.click(mousepoint['zero'][0], mousepoint['zero'][1])
        elif name == '小区退服告警':
            # 打开断站明细
            time.sleep(5)
            m.click(mousepoint['drop'][0], mousepoint['drop'][1])

        # 选择城市
        time.sleep(5)
        for i in range(0, 10):
            m.click(mousepoint['citydown'][0], mousepoint['citydown'][1])

        time.sleep(5)
        m.click(mousepoint['citytl'][0], mousepoint['citytl'][1])

        time.sleep(5)
        m.click(mousepoint['cityadd'][0], mousepoint['cityadd'][1])

    # 向上选择时间滚轮
        time.sleep(5)
        m.click(mousepoint['dubtime'][0], mousepoint['dubtime'][1])

    # 点击增加时间的空格
        time.sleep(3)
        m.click(mousepoint['addtime'][0], mousepoint['addtime'][1])

        # 增加时间31
        time.sleep(3)
        k.tap_key('1')

        # 向上滚动到1日
        for i in range(0, 20):
            m.click(mousepoint['timeup'][0], mousepoint['timeup'][1])

        # 选择1日
        time.sleep(5)
        m.click(mousepoint['firsttime'][0], mousepoint['firsttime'][1])

        # 点击增加
        time.sleep(5)
        m.click(mousepoint['timeadd'][0], mousepoint['timeadd'][1])
        #

        #     # 点击生成excel表
        time.sleep(5)
        m.click(mousepoint['excelpoint'][0], mousepoint['excelpoint'][1])
        print(mousepoint['excelpoint'][0], mousepoint['excelpoint'][1])

        time.sleep(5)
        k.press_key(k.alt_l_key)
        time.sleep(1)
        k.press_key(k.space_key)
        time.sleep(1)
        k.press_key('x')
        time.sleep(1)
        k.release_key(k.alt_l_key)
        time.sleep(1)
        k.release_key(k.space_key)
        time.sleep(1)
        k.release_key('x')
        time.sleep(1)

        #
        #
        filelist = os.listdir(path)
        for file in filelist:
            if name in file:
                os.remove(path + file)
                print(path + file, '文件已删除')
        # 等待取话务报表

        for i in range(20000):
            filelist = os.listdir(path)
            for file in filelist:
                if name in file:
                    fileget = 'yes'
                    i = 20005
                    break
                else:
                    fileget = 'no'
                    # 等待取话务报表
            if fileget == 'no':
                m.click(mousepoint['download'][0], mousepoint['download'][1])
                time.sleep(3)
                k.tap_key(k.down_key)
                time.sleep(3)
                k.tap_key(k.enter_key)
                time.sleep(5)
            else:
                print(name + '已取出')

        time.sleep(3)
        data = driver.title
        print(data)

        k.press_key(k.control_l_key)
        k.press_key('w')
        k.release_key(k.control_l_key)
        k.release_key('w')
        driver.close()
        driver.quit()

        cell.drop_duplicates(inplace=True)
        cell['归属负责人'] = cell.小区名称.apply(
            lambda x: '凌菁菁' if ('室分' in x or 'sf' in x or 'SF' in x or 'ws' in x) else '王军政' if '枞阳' in x else '曾昊')
        cellnamelist = list(set(cell['小区名称']))

        filelist = os.listdir(path)
        for file in filelist:
            print(file)
            if name in file:
                print(datetime.now())
                zerotable=pd.read_excel(path + file,header=2)
                zerotable.rename(columns={'业务量开始时间': '开始时间', '业务量结束时间': '结束时间'}, inplace=True)
                zerotable = zerotable[zerotable.columns.difference(['查询时间'])]
                zerotable.rename(columns={'告警发生时间': '开始时间', '告警结束时间': '结束时间'}, inplace=True)
                try:
                    zerotable = zerotable[zerotable.小区类型 != '2G']
                except:
                    print('tableunfit')

                try:
                    zerotable['lostlong']=[(zerotable.iloc[i]['开始时间']-zerotable.iloc[i]['结束时间']).days*24*60+(zerotable.iloc[i]['开始时间']-zerotable.iloc[i]['结束时间']).seconds/60  for i in range(len(zerotable))]
                except:
                    print('断站报表')



                zerotable = pd.merge(zerotable, cell, how='left', on=['小区名称'])
                unfitname = zerotable['小区名称'][zerotable.归属负责人.isnull() == True].values.tolist()
                unfitname = Similarfieldname(unfitname, cellnamelist)
                unfitname = pd.merge(unfitname, cell, how='left', left_on=['匹配字段名称'], right_on=['小区名称'])
                unfitname = unfitname[['原字段名称', '归属负责人']]
                unfitname.columns = ['小区名称', '二次匹配归属负责人']
                zerotable = pd.merge(zerotable, unfitname, how='left', on=['小区名称'])
                zerotable.loc[zerotable.归属负责人.isnull() == True, '归属负责人'] = zerotable['二次匹配归属负责人'][zerotable.归属负责人.isnull() == True]
                print(zerotable)

                basetable=pd.read_sql_table(name+'详情明细',con=enginecon)
                zerotableappend=pd.merge(zerotable,basetable[['开始时间','小区名称','结束时间']],how='left',on=['开始时间','小区名称',])
                print(zerotableappend)
                zerotableappend=zerotableappend[zerotableappend.结束时间_y.isnull()==True]
                print(zerotableappend)
                if len(zerotableappend)>0:
                    zerotableappend = zerotableappend[zerotableappend.columns.difference(['结束时间_y'])]
                    zerotableappend.rename(columns={'结束时间_x':'结束时间'},inplace=True)
                    print(zerotableappend)
                    zerotable.to_sql(name+'详情明细', if_exists='append', index=False, con=enginecon)
                else:
                    print('超24小时小区零话务存取记录无变化')
                Notelog=[[name,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),zerotable['结束时间'].max().strftime("%Y-%m-%d %H:%M:%S"),len(zerotable)]]
                Notelog=pd.DataFrame(Notelog,columns=['type','存取时间','最近故障时间','记录总数'])
                print(Notelog)
                Notelog.to_sql(name+'存取记录', if_exists='append', index=False, con=enginecon)



    #
    # filelist = os.listdir(path)
    # for file in filelist:
    #     print(file)
    #     if  '小区退服告警' in file:
    #         print(datetime.now())
    #         droptable = pd.read_excel(path + file, header=2)
    #
    #         droptable =droptable[droptable.小区类型!='2G']
    #         droptable = droptable[droptable.columns.difference(['查询时间'])]
    #         droptable.rename(columns={'告警发生时间': '开始时间', '告警结束时间': '结束时间'}, inplace=True)
    #
    #
    #         droptable = pd.merge(droptable, cell, how='left', on=['小区名称'])
    #         unfitname=droptable['小区名称'][droptable.归属负责人.isnull()==True].values.tolist()
    #         unfitname=Similarfieldname(unfitname,cellnamelist)
    #         unfitname = pd.merge(unfitname, cell, how='left', left_on=['匹配字段名称'],right_on=['小区名称'])
    #         unfitname=unfitname[['原字段名称','归属负责人']]
    #         unfitname.columns =['小区名称','二次匹配归属负责人']
    #         droptable = pd.merge(droptable, unfitname, how='left', on=['小区名称'])
    #         droptable.loc[droptable.归属负责人.isnull() == True,'归属负责人']=droptable['二次匹配归属负责人'][droptable.归属负责人.isnull() == True]
    #
    #         basetable=pd.read_sql_table('小区退服告警详情明细',con=enginecon)
    #         droptableappend=pd.merge(droptable,basetable[['时间','小区名称','告警流水号']],how='left',on=['告警发生时间','小区名称'])
    #         droptableappend=droptableappend[droptableappend.告警流水号_y.isnull()==True]
    #         if len(droptableappend)>0:
    #             droptableappend = droptableappend[droptableappend.columns.difference(['告警流水号_y'])]
    #             droptableappend.rename(columns={'告警流水号_x':'告警流水号'},inplace=True)
    #             print(droptableappend)
    #             droptable.to_sql('小区退服告警详情明细', if_exists='append', index=False, con=enginecon)
    #         else:
    #             print('小区退服告警详情存取记录无变化')
    #         Notelog=[['断站',datetime.now().strftime("%Y-%m-%d %H:%M:%S"),droptable['告警结束时间'].max().strftime("%Y-%m-%d %H:%M:%S"),len(droptable)]]
    #         Notelog=pd.DataFrame(Notelog,columns=['type','存取时间','最近故障恢复时间','记录总数'])
    #         print(Notelog)
    #         Notelog.to_sql('小区退服告警存取记录', if_exists='append', index=False, con=enginecon)


    sql = 'select "小区名称","基站等级" as "小区等级","基站类型" as "小区类型","开始时间" as "starttime","结束时间" as "stoptime","lostlong" as "中断时长","归属负责人" from "超24小时小区零话务详情明细"'
    zerocell = pd.read_sql(sql, con=enginecon)
    zerocell.drop_duplicates(inplace=True)
    zerocell['故障属性'] = '零话务'
    zerocell['日期'] = zerocell.starttime.apply(lambda x: x.strftime("%Y-%m-%d"))
    zerocell['月份'] = zerocell.starttime.apply(lambda x: x.strftime("%Y-%m"))
    # print(zerocell.head())

    sql = 'select "小区名称","小区等级","小区类型","开始时间" as "starttime","结束时间" as "stoptime","故障历时（分钟）" as "中断时长","归属负责人" from "小区退服告警详情明细"'
    badell = pd.read_sql(sql, con=enginecon)
    badell.drop_duplicates(inplace=True)
    badell['日期'] = badell.starttime.apply(lambda x: x.strftime("%Y-%m-%d"))
    badell['月份'] = badell.starttime.apply(lambda x: x.strftime("%Y-%m"))
    badell['开始时间'] = badell.starttime.apply(lambda x: x.strftime("%Y-%m-%d %H:00:00"))
    badell['结束时间'] = badell.stoptime.apply(lambda x: x.strftime("%Y-%m-%d %H:00:00"))
    nowtime = datetime.now()
    nowm = nowtime.strftime("%Y-%m")
    print(nowm)
    badell['故障属性'] = '断站'
    print(badell.head())

    zeroandbad = pd.concat([zerocell, badell])
    print(zeroandbad)
    nowmon = zeroandbad[zeroandbad.月份 == nowm]
    nowmon.to_sql('当月断站及零话务明细', if_exists='replace', index=False, con=enginecon)
