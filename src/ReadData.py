# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 20:53:26 2016

@author: Chao
"""

#readData
import datetime
import time
import numpy as np

import pandas as pd
def getTableS1():
    filename="航班信息及规则对应表20160927.xlsx"
    f=open("../input/%s" %filename,"rb")
    tb1=pd.read_excel(f,sheetname="历史航班")
    f.close()
    f=open("../input/%s" %filename,"rb")
    tb2=pd.read_excel(f,sheetname="机位属性表")
    f.close()
    return tb1,tb2


def readTime(t):
    r=time.mktime(datetime.datetime.strptime(t,"%Y-%m-%d %H:%M:%S").timetuple())
    return int(r/60/5)
    
def tb1toList(tb1):
    airplanes=[]
    ealiestTime=np.nan
    latestTime=np.nan
    for index,row in tb1.iterrows():
        airplanes.append([\
        row["进港航班号"],\
        row["航空公司"],\
        row["国际国内属性"],\
        row["飞行任务"],\
        row["机型"],\
        row["进出港总人数"],\
        readTime(row["进机位时间"]),\
        readTime(row["出机位时间"]),\
        ])
        if not ealiestTime<airplanes[-1][6]:
            ealiestTime=airplanes[-1][6]
        if not latestTime>airplanes[-1][7]:
            latestTime=airplanes[-1][7]
    return airplanes,ealiestTime-1,latestTime+2

def tb2toList(tb2):
    parkings=[]
    for index,row in tb2.iterrows():
        parkings.append([\
        row["停机位"],\
        row["航空公司"],\
        row["国际国内属性"],\
        row["飞行任务"],\
        row["机型"],\
        row["远近机位属性"],\
        row["滑行道"],\
        ])
    return parkings

def checkType(item,box):
    for t in range(1,5):
        if t==2 and box[t]=="国际、国内":continue
        ba=box[t].split(",")
        flag=False
        for a in ba:
            if a==item[t]:
                flag=True
                break
        if flag==False:
            return False
    return True

def makeDic(airplanes,parkings):
    dic={}#item id=> box id
    for item in airplanes:
        candlist=[]
        for box in parkings:
            if checkType(item,box):
                candlist.append(box[0])
        if item[6]>item[7]:candlist=[]#时间不符不分配
        dic[item[0]]=candlist
    return dic

from Airport import Airplane
from Airport import Parking
from Airport import Acitivity
from Airport import Problem

def buildAct(name,inTime,outTime):#左闭右开
    inAct=Acitivity(name,inTime-1,inTime,"in")
    stayAct=Acitivity(name,inTime,outTime+2,"stay")
    outAct=Acitivity(name,outTime,outTime+1,"out")
    return inAct,stayAct,outAct

def getData(tb1,tb2):

    airplanes,ealiestTime,latestTime=tb1toList(tb1)
    parkings=tb2toList(tb2)
    air2park=makeDic(airplanes,parkings)
    
    print("Abandon airplane:")
    abandonAir=[]
    allAirplanes={}
    allActivities={}
    for item in airplanes:
        if air2park[item[0]]:
            allAirplanes[item[0]]=Airplane(item[0],item[5],item[6],item[7])
            allActivities[item[0]]=buildAct(item[0],item[6],item[7])
        else:
            abandonAir.append(item[0])
            #print(item[0])
    print("Count:"+str(len(abandonAir)))

    allParkings={}
    for item in parkings:        
        allParkings[item[0]]=Parking(item[0],item[2],item[5],item[6])
    
    allTaxiways=list(tb2["滑行道"].unique())
    
#    ealiestTime=readTime(tb1["进机位时间"][0])-1
#    latestTime=readTime(tb1["出机位时间"].max())+2
    return Problem(allAirplanes,allActivities,allParkings,air2park,allTaxiways,abandonAir,ealiestTime,latestTime)
