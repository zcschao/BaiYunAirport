# -*- coding: utf-8 -*-
"""
Created on Sat Oct  1 20:34:00 2016

@author: Chao
"""
class Acitivity:
    def __init__(self,airId,startTime,endTime,typeId):
        self.airId=airId
        self.startTime=startTime
        self.endTime=endTime
        self.typeId=typeId
        
class Airplane:
    def __init__(self,name,pcnt,inTime,outTime):
        self.name=name
        self.pcnt=pcnt
        self.inTime=inTime
        self.outTime=outTime

        
class Parking:
    def __init__(self,name,att,near,taxiwayid):
        self.name=name
        self.near=near
        self.tid=taxiwayid
        self.att=att
    def getScore(self):
        if self.near=="近机位":
            return 1
        else:
            return 0

class Problem:
    def __init__(self,allAirplanes,allActivities,allParkings,air2park,allTaxiways,abandonAirplanes,earliestTime,latestTime):
        self.allAirplanes=allAirplanes#dic{air name:Class air}
        self.allActivities=allActivities#dic{air name:acts}
        self.allParkings=allParkings#dic{park name:Class Parking}
        self.air2park=air2park#dic{air name:park}
        self.allTaxiways=allTaxiways#list([taxi name,...])
        self.abandonAirplanes=abandonAirplanes
        self.earliestTime=earliestTime
        self.latestTime=latestTime
        self.p0=len(self.allAirplanes)+len(self.abandonAirplanes)
