# -*- coding: utf-8 -*-
import numpy as np
import geatpy as ea # 导入geatpy库
from sys import path as paths
from os import path
paths.append(path.split(path.split(path.realpath(__file__))[0])[0])

class moea_psy_NSGA2_templet(ea.MoeaAlgorithm):
    
    """
moea_psy_NSGA2_templet : class - 多染色体的多目标进化NSGA-II算法模板
    
描述:
    采用NSGA-II进行多目标优化，算法详见参考文献[1]。
    该模板是内置算法模板moea_NSGA2_templet的多染色体版本。
    因此里面的种群对象为支持混合编码的多染色体种群类PsyPopulation类的对象。

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

参考文献:
    [1] Deb K , Pratap A , Agarwal S , et al. A fast and elitist multiobjective 
    genetic algorithm: NSGA-II[J]. IEEE Transactions on Evolutionary 
    Computation, 2002, 6(2):0-197.

    """
    
    def __init__(self, problem, population):
        ea.MoeaAlgorithm.__init__(self, problem, population) # 先调用父类构造方法
        if str(type(population)) != "<class 'PsyPopulation.PsyPopulation'>":
            raise RuntimeError('传入的种群对象必须为PsyPopulation类型')
        self.name = 'psy-NSGA2'
        self.ndSort = ea.ndsortESS # 设置非支配排序算子
        self.selFunc = 'tour' # 选择方式，采用锦标赛选择
        # 由于有多个染色体，因此需要用多个重组和变异算子，于是对应有多个重组和变异概率
        self.recFuncs = []
        self.mutFuncs = []
        self.pcs = []
        self.pms = []
        for i in range(population.ChromNum):
            if population.Encodings[i] == 'P':
                self.recFuncs.append('xovpmx') # 部分匹配交叉
                self.mutFuncs.append('mutinv') # 染色体片段逆转变异
            elif population.Encodings[i] == 'BG':
                self.recFuncs.append('xovud') # 均匀交叉
                self.mutFuncs.append('mutbin') # 二进制变异
            elif population.Encodings[i] == 'RI':
                self.recFuncs.append('recsbx') # 模拟二进制交叉
                self.mutFuncs.append('mutpolyn') # 多项式变异
            else:
                raise RuntimeError('编码方式必须为''BG''、''RI''或''P''.')
            self.pcs.append(1) # 重组概率
            self.pms.append(1) # 整条染色体的变异概率
    
    def reinsertion(self, population, offspring, NUM):
        
        """
        描述:
            重插入个体产生新一代种群（采用父子合并选择的策略）。
            NUM为所需要保留到下一代的个体数目。
            注：这里对原版NSGA-II进行等价的修改：先按帕累托分级和拥挤距离来计算出种群个体的适应度，
            然后调用dup选择算子(详见help(ea.dup))来根据适应度从大到小的顺序选择出个体保留到下一代。
            这跟原版NSGA-II的选择方法所得的结果是完全一样的。
        """
        
        # 父子两代合并
        population = population + offspring
        # 选择个体保留到下一代
        [levels, criLevel] = self.ndSort(self.problem.maxormins * population.ObjV, NUM, None, population.CV) # 对NUM个个体进行非支配分层
        dis = ea.crowdis(population.ObjV, levels) # 计算拥挤距离
        population.FitnV[:, 0] = np.argsort(np.lexsort(np.array([dis, -levels])), kind = 'mergesort') # 计算适应度
        chooseFlag = ea.selecting('dup', population.FitnV, NUM) # 调用低级选择算子dup进行基于适应度排序的选择，保留NUM个个体
        return population[chooseFlag]
    
    def run(self):
        #==========================初始化配置===========================
        population = self.population
        NIND = population.sizes
        self.initialization() # 初始化算法模板的一些动态参数
        #===========================准备进化============================
        population.initChrom() # 初始化种群染色体矩阵（内含解码，详见PsyPopulation类的源码）
        self.problem.aimFunc(population) # 计算种群的目标函数值
        self.evalsNum = population.sizes # 记录评价次数
        [levels, criLevel] = self.ndSort(self.problem.maxormins * population.ObjV, NIND, None, population.CV) # 对NIND个个体进行非支配分层
        population.FitnV[:, 0] = 1 / levels # 直接根据levels来计算初代个体的适应度
        #===========================开始进化============================
        while self.terminated(population) == False:
            # 选择个体参与进化
            offspring = population[ea.selecting(self.selFunc, population.FitnV, NIND)]
            # 进行进化操作，分别对各个种群染色体矩阵进行重组和变异
            for i in range(population.ChromNum):
                offspring.Chroms[i] = ea.recombin(self.recFuncs[i], offspring.Chroms[i], self.pcs[i]) #重组
                offspring.Chroms[i] = ea.mutate(self.mutFuncs[i], offspring.Encodings[i], offspring.Chroms[i], offspring.Fields[i], self.pms[i]) # 变异
            offspring.Phen = offspring.decoding() # 解码
            self.problem.aimFunc(offspring) # 求进化后个体的目标函数值
            self.evalsNum += offspring.sizes # 更新评价次数
            # 重插入生成新一代种群
            population = self.reinsertion(population, offspring, NIND)
        
        return self.finishing(population) # 调用finishing完成后续工作并返回结果
