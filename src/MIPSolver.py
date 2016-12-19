# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 17:01:20 2016

@author: Chao
"""
import pandas as pd
from ReadData import getData
from ReadData import getTableS1
import time
import pulp
#import csv

def addAct(schedule,act):
    for i in range(act.startTime,act.endTime):
        schedule[i].append(act)
        
def makeContentionGroup(parkingSchedule,problem):
    groupSetListParkDic={}
    for parkname in parkingSchedule.keys():
        groupSetListParkDic[parkname]=[]
        schedule=parkingSchedule[parkname]
        for i in range(problem.earliestTime,problem.latestTime+1):
            if len(schedule[i])<=1:
                continue
            groupSet=set()
            for act in schedule[i]:
                groupSet.add(act.airId)
            if len(groupSet)<=1:
                continue
            if groupSet not in groupSetListParkDic[parkname]:
                IsSubSet=False
                for groupSetAdded in groupSetListParkDic[parkname]:
                    if not (groupSet-groupSetAdded):
                        IsSubSet=True
                        break
                    if not (groupSetAdded-groupSet):
                        groupSetListParkDic[parkname].remove(groupSetAdded)
                        break
                if not IsSubSet:
                    groupSetListParkDic[parkname].append(groupSet)
    return groupSetListParkDic
    
#def DicToResult(dic,tb1,filename):
#    lines=[]
#    with open("%s" %filename, "w") as f:
#        writer = csv.writer(f)
#        for index,row in tb1.iterrows():
#            airId=row["进港航班号"]
#            if airId in dic and dic[airId]:
#                line=[str(row["进港航班号"]),row["进机位时间"],row["出机位时间"],dic[airId]]
#                lines.append(line)                        
#        writer.writerows(lines)  
    
def DicToResult(dic,tb1,filename):
    lines=[]
    #with open("%s" %filename, "w") as f:
        #writer = csv.writer(f)
    for index,row in tb1.iterrows():
        airId=row["进港航班号"]
        if airId in dic and dic[airId]:
            line=[str(row["进港航班号"]),row["进机位时间"],row["出机位时间"],dic[airId]]
            lines.append(line)                        
    #writer.writerows(lines)
    re=pd.DataFrame(lines)
    re.to_csv(filename,index=False,header=False)



def AirportSolver(Solver,tb1,tb2,filename="../output/result.csv"):
    start = time.clock()
    print("Read data...")
    problem=getData(tb1,tb2)
    print("Preprocess...")
    maxClashNum=50
    parkingSchedule={}
    for name in problem.allParkings.keys():
        parkingSchedule[name]={}
        for i in range(problem.earliestTime,problem.latestTime+1):
            parkingSchedule[name][i]=[]
    
    taxiwaySchedule={}
    for name in problem.allTaxiways:
        taxiwaySchedule[name]={}
        for i in range(problem.earliestTime,problem.latestTime+1):
            taxiwaySchedule[name][i]=[]
                
                
    for air in list(problem.allAirplanes.values()):
        for parkname in problem.air2park[air.name]:
            park=problem.allParkings[parkname]
            inAct,stayAct,outAct=problem.allActivities[air.name]
            addAct(parkingSchedule[parkname],stayAct)
            if park.tid!="无限制":
                addAct(taxiwaySchedule[park.tid],outAct)
                addAct(taxiwaySchedule[park.tid],inAct)
        
    #记录有意义的时间
    #竞争组合
    groupSetListParkDic=makeContentionGroup(parkingSchedule,problem)
    groupSetListTaxiDic=makeContentionGroup(taxiwaySchedule,problem)


    airplanes=list(problem.allAirplanes.keys())
    parkings=list(tb2["停机位"].unique())
    taxiways=list(tb2["滑行道"].unique())
    taxiways.remove("无限制")
    air2park=problem.air2park
    air_park=[]
    c_air_park={}
    
    air_taxi=set()
    air_taxi2park={}
    for air in airplanes:
        for park in air2park[air]:
            air_park.append((air,park))
            c_air_park[(air,park)]=problem.allParkings[park].getScore()*2+3
            tid=problem.allParkings[park].tid
            if tid=="无限制":
                continue
            air_taxi.add((air,tid))
            if (air,tid) not in air_taxi2park:
                air_taxi2park[(air,tid)]=[park]
            else:
                air_taxi2park[(air,tid)].append(park)
    air_taxi=list(air_taxi)
    #每个taxiGroup对应一个clash
    tid_gidx=[]
    for tid in groupSetListTaxiDic.keys():
        for i in range(len(groupSetListTaxiDic[tid])):
            tid_gidx.append((tid,i))    
    
    
    end = time.clock()
    print("Done")
    print ("[Time: %.3f s]" % (end - start))
    print("Write LP")
    
    prob = pulp.LpProblem('Airport', pulp.LpMaximize) 
    
    v_air_park= pulp.LpVariable.dicts("air_park",air_park,0,1,pulp.LpInteger)
    v_air_taxi= pulp.LpVariable.dicts("air_taxi",air_taxi,0,1,pulp.LpInteger)
    v_air_taxi_c= pulp.LpVariable.dicts("air_taxi_c",air_taxi,0,1,pulp.LpInteger)  
    v_clash_taxi_gidx= pulp.LpVariable.dicts("Clash",tid_gidx,0,1,pulp.LpInteger)
    
    #OBJ
    print("->Obj")
    prob+=pulp.lpSum([c_air_park[ap]*v_air_park[ap] for ap in air_park])\
    -pulp.lpSum([v_air_taxi_c[at] for at in air_taxi])    
    
#    prob+=v_air_park[air_park[0]] 
    #s.t
    #一架飞机只能停在一个机位
    print("->Constraint 1")
    for air in airplanes:
        prob+=pulp.lpSum([v_air_park[(air,park)] for park in air2park[air]])<=1,""
    
#    一架飞机是否用了滑行道取与是否用了对应的机位之一
    print("->Constraint 2")
    for at in air_taxi:
        prob+=pulp.lpSum([v_air_park[(at[0],park)] for park in air_taxi2park[at]])\
        -v_air_taxi[at]-v_air_taxi_c[at]==0,""
        
    #冲突组中只能有一架飞机
    print("->Constraint 3")
    for park in parkings:
        for groupSet in groupSetListParkDic[park]:
            if groupSet:
                prob+=pulp.lpSum([v_air_park[(air,park)] for air in groupSet])<=1,""
    
    #若不冲突，冲突组只能有一架飞机
    #若冲突，在冲突机位停放
    print("->Constraint 4")
    for taxi in taxiways:
        if taxi=="无限制":
            continue
        for gidx in range(len(groupSetListTaxiDic[taxi])):
            groupSet=groupSetListTaxiDic[taxi][gidx]
            if groupSet:
                prob+=pulp.lpSum([v_air_taxi[(air,taxi)] for air in groupSet])\
                +v_clash_taxi_gidx[(taxi,gidx)]<=1,""
            
                prob+=pulp.lpSum([v_air_taxi_c[(air,taxi)] for air in groupSet])\
                -maxClashNum*v_clash_taxi_gidx[(taxi,gidx)]<=0,""
    
    end = time.clock()
    print ("[Time: %.3f s]" % (end - start))

    print("Solving...")
    Solver(prob)

    print("Solved.")
    print("Write Result")
    dic={}
    for ap in air_park:
        if v_air_park[ap].value()==1:
            dic[ap[0]]=ap[1]
    
    
    DicToResult(dic,tb1,filename)
            
    score=pulp.value(prob.objective)/problem.p0+1
    print("Score:",score)



if __name__=="__main__":
    start = time.clock()
    tb1,tb2=getTableS1()
    
    #Solver=pulp.GUROBI_CMD().solve
    Solver=pulp.CPLEX_CMD().solve 
    #Solver=pulp.COIN_CMD(path="F:/Program Files (x86)/COIN-OR/1.7.4/win32-msvc10/bin/cbc.exe").solve
    #Solver=pulp.GLPK_CMD(path="F:/ToolBox/glpk-4.60/w64/glpsol.exe").solve
    
    AirportSolver(Solver,tb1,tb2)
    
    
    end = time.clock()
    print("Done")
    print ("[Time: %.3f s]" % (end - start))