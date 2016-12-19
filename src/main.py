# -*- coding: utf-8 -*-
"""
Created on Wed Oct 19 20:16:22 2016

@author: Chao
"""
import time
import pulp
from ReadData import getTableS1
from MIPSolver import AirportSolver

if __name__=="__main__":
    start = time.clock()
    tb1,tb2=getTableS1()
    
    Solver=pulp.GUROBI_CMD().solve
#    Solver=pulp.CPLEX_CMD().solve 
#    Solver=pulp.COIN_CMD(path="F:/Program Files (x86)/COIN-OR/1.7.4/win32-msvc10/bin/cbc.exe").solve
#    Solver=pulp.GLPK_CMD(path="F:/ToolBox/glpk-4.60/w64/glpsol.exe").solve
    
    AirportSolver(Solver,tb1,tb2,filename="../output/result.csv")
    
    
    end = time.clock()
    print ("[Time: %.3f s]" % (end - start))
    
    