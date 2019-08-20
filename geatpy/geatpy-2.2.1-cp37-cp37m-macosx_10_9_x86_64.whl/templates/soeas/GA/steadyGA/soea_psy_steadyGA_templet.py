# -*- coding: utf-8 -*-
import geatpy as ea # 导入geatpy库
from sys import path as paths
from os import path
paths.append(path.split(path.split(path.realpath(__file__))[0])[0])

class soea_psy_steadyGA_templet(ea.SoeaAlgorithm):
    
    """
soea_psy_steadyGA_templet : class - Polysomy Steady State GA templet(多染色体稳态遗传算法模板)

模板说明:
    该模板是内置算法模板soea_steadyGA_templet的多染色体版本，
    因此里面的种群对象为支持混合编码的多染色体种群类PsyPopulation类的对象。

算法描述:
    本模板实现的是稳态遗传算法，算法流程如下：
    1) 根据编码规则初始化N个个体的种群。
    2) 若满足停止条件则停止，否则继续执行。
    3) 对当前种群进行统计分析，比如记录其最优个体、平均适应度等等。
    4) 独立地从当前种群中选取2个母体。
    5) 独立地对这2个母体进行交叉操作。
    6) 独立地对这2个交叉后的个体进行变异。
    7) 将这2个母体和由交叉变异得到的个体进行一对一生存者竞争选择。
    8) 将第7步得到的个体替换父代中原母体所在位置的个体，形成新一代种群。
    9) 回到第2步。
    
模板使用注意:
    本模板调用的目标函数形如：aimFunc(pop), 
    其中pop为种群类的对象，代表一个种群，
    pop对象的Phen属性（即种群染色体的表现型）等价于种群所有个体的决策变量组成的矩阵，
    该函数根据该Phen计算得到种群所有个体的目标函数值组成的矩阵，并将其赋值给pop对象的ObjV属性。
    若有约束条件，则在计算违反约束程度矩阵CV后赋值给pop对象的CV属性（详见Geatpy数据结构）。
    该函数不返回任何的返回值，求得的目标函数值保存在种群对象的ObjV属性中，
                          违反约束程度矩阵保存在种群对象的CV属性中。
    例如：population为一个种群对象，则调用aimFunc(population)即可完成目标函数值的计算，
         此时可通过population.ObjV得到求得的目标函数值，population.CV得到违反约束程度矩阵。
    若不符合上述规范，则请修改算法模板或自定义新算法模板。
    
"""
    
    def __init__(self, problem, population):
        ea.SoeaAlgorithm.__init__(self, problem, population) # 先调用父类构造方法
        if str(type(population)) != "<class 'PsyPopulation.PsyPopulation'>":
            raise RuntimeError('传入的种群对象必须为PsyPopulation类型')
        self.name = 'psy-steadyGA'
        self.selFunc = 'etour' # 锦标赛选择算子
        # 由于有多个染色体，因此需要用多个重组和变异算子，于是对应有多个重组和变异概率
        self.recFuncs = []
        self.mutFuncs = []
        self.pcs = []
        self.pms = []
        for i in range(population.ChromNum):
            if population.Encodings[i] == 'P':
                self.recFuncs.append('xovpmx') # 部分匹配交叉
                self.mutFuncs.append('mutinv') # 染色体片段逆转变异
            else:
                self.recFuncs.append('xovdp')  # 两点交叉
                if population.Encodings[i] == 'BG':
                    self.mutFuncs.append('mutbin') # 二进制变异
                elif population.Encodings[i] == 'RI':
                    self.mutFuncs.append('mutbga') # breeder GA中的变异算子
                else:
                    raise RuntimeError('编码方式必须为''BG''、''RI''或''P''.')
            self.pcs.append(1) # 重组概率
            self.pms.append(1) # 整条染色体的变异概率
        
    def run(self):
        #==========================初始化配置===========================
        population = self.population
        NIND = population.sizes
        if NIND < 2:
            raise RuntimeError('error: Population'' size is too small. (种群规模不能小于2。)')
        self.initialization() # 初始化算法模板的一些动态参数
        #===========================准备进化============================
        population.initChrom(NIND) # 初始化种群染色体矩阵（内含染色体解码，详见PsyPopulation类的源码）
        self.problem.aimFunc(population) # 计算种群的目标函数值
        population.FitnV = ea.scaling(self.problem.maxormins * population.ObjV, population.CV) # 计算适应度
        self.evalsNum = population.sizes # 记录评价次数
        #===========================开始进化============================
        while self.terminated(population) == False:
            # 选择
            chooseIdx = ea.selecting(self.selFunc, population.FitnV, 2)
            offspring = population[chooseIdx]
            # 进行进化操作，分别对各种编码的染色体进行重组和变异
            for i in range(population.ChromNum):
                offspring.Chroms[i] = ea.recombin(self.recFuncs[i], offspring.Chroms[i], self.pcs[i]) # 重组
                offspring.Chroms[i] = ea.mutate(self.mutFuncs[i], offspring.Encodings[i], offspring.Chroms[i], offspring.Fields[i], self.pms[i]) # 变异
            # 求进化后个体的目标函数值
            offspring.Phen = offspring.decoding() # 染色体解码
            self.problem.aimFunc(offspring) # 计算目标函数值
            self.evalsNum += offspring.sizes # 更新评价次数
            tempPop = population + offspring # 父子合并
            tempPop.FitnV = ea.scaling(self.problem.maxormins * tempPop.ObjV, tempPop.CV) # 计算适应度
            # 得到新一代种群
            tempPop = tempPop[ea.selecting('otos', tempPop.FitnV, 2)] # 采用One-to-One Survivor选择
            population[chooseIdx] = tempPop
            population.FitnV = ea.scaling(self.problem.maxormins * population.ObjV, population.CV) # 计算适应度
            
        return self.finishing(population) # 调用finishing完成后续工作并返回结果
    