# AirportSolver
by 终结卡尔斯

## 运行环境
Gurobi/CPLEX/CBC/GLPK.  
Python 3.5.1  | Anaconda 4.0.0.  
[PuLP](https://pypi.python.org/pypi/PuLP/) .

## 运行步骤
1. 在/src/main.py中设置可用的线性规划求解库。

2. 运行main.py

3. 结果位于output目录

## 目录结构
├── README.MD				// help  
├── src						// 源代码  
│   ├── main.py				// 程序入口  
│   ├── Airport.py		  
│   ├── ReadData.py		  
│   └── MIPSolver.py		  
├── input  
├── doc						 // 文档  
└── output  

## 运行结果
### 目标函数值:
5.187410586552217(最优解)

## 备注
若使用新版Gurobi 7.0,pulp的取sol文件部分的程序需要修改。  
pulp/solvers.py 中多加一句next(my_file)
``` python
def readsol(self, filename):
    """Read a Gurobi solution file"""
    with open(filename) as my_file:
        try:
            next(my_file)
            next(my_file) # skip the objective value
```
