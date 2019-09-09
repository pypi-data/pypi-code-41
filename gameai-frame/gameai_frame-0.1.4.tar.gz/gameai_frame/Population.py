from . import GameRole as gr
from . import global_vars as g
import random
GA_Train_Parallel = 0
GA_Train_Sequence = 1
class Population(object):
    #indv_type : 传入自定的游戏对象(GameRole的子类)
    def __init__(self, size, pm, pc, indv_type, train_model = GA_Train_Parallel):
        self.bestIndv = indv_type() #best individual
        self.indvs = [indv_type() for i in range(size)]
        self.pm = pm
        self.pc = pc

        self.bestScore = 0 
        self.generation = 0 
        self.bestFitness = 0.0
        self.fitnessSum = 0.0

        self.tmod = train_model

        self.cur_id = 0
        self.one_down = False

        self.__interval = int(g.AG_POP_SIZE / 5) #just used to print msg
        return
    def show(self):
        if self.cur_id == 0:
            self.bestIndv.show()
        else:
            self.indvs[self.cur_id - 1].show()
        return
    def update(self): #train them in sequence order
        if self.tmod == GA_Train_Parallel:
            self._update_parallel()
        else:
            self._update_sequence()
        return
    def _update_parallel(self):
        if self._done(): #all dead generate next
            print('\n-------------<ALL Dead>---------------')
            self._generate_next()
        if not self.bestIndv.dead:
            self.bestIndv.look()
            self.bestIndv.think()
            self.bestIndv.user_update()
        for i in range(len(self.indvs)):
            if not self.indvs[i].dead:
                self.indvs[i].look()
                self.indvs[i].think()
                self.indvs[i].user_update()
        return
    def _update_sequence(self):
        if self.one_down:
            #set cur indv to next
            self.one_down = False
            if self.cur_id != len(self.indvs):
                self.cur_id += 1
            else: #all dead
                self.cur_id = 0
                print('\n-------------<ALL Dead>--------------')
                self._generate_next()
        if self.cur_id != 0:
            self.indvs[self.cur_id - 1].look()
            self.indvs[self.cur_id - 1].think()
            self.indvs[self.cur_id - 1].user_update()
        else:
            self.bestIndv.look()
            self.bestIndv.think()
            self.bestIndv.user_update()
        return
    def _calculate_fitness(self):
        self.bestIndv.calculate_fitness()
        for i in range(len(self.indvs)):
            self.indvs[i].calculate_fitness()
        return
    #all population dead
    def _done(self):
        if not self.bestIndv.dead:
            return False
        for i in range(len(self.indvs)):
            if not self.indvs[i].dead:
                return False
        return True
    #GA------------------------------------------------------------------
    def _set_best(self):
        max_fitness = 0
        max_indx = 0
        best_score = 0
        for i in range(len(self.indvs)):
            if max_fitness < self.indvs[i].fitness:
                max_fitness = self.indvs[i].fitness
                max_indx = i
        if max_fitness > self.bestIndv.fitness:
            if max_fitness > self.bestFitness:
                self.bestFitness = max_fitness
            self.bestIndv = self.indvs[max_indx].clone()
        else:
            if self.bestIndv.fitness > self.bestFitness:
                self.bestFitness = self.bestIndv.fitness
            self.bestIndv = self.bestIndv.clone()
        self.bestIndv.user_init()
        return
    def _select_parent(self):
        rand = random.uniform(0,self.fitnessSum)
        summation = 0
        for i in range(len(self.indvs)):
            summation += self.indvs[i].fitness
            if summation > rand:
                return self.indvs[i]
        return self.bestIndv
    def _mutate(self):
        for i in range(len(self.indvs)):
            self.indvs[i].mutate(self.pm)
        return
    def _generate_next(self):
        self._calculate_fitness()
        #get fitness sum:-----------------------------
        sum_rcd = self.fitnessSum
        self.fitnessSum = self.bestIndv.fitness
        for i in range(len(self.indvs)):
            self.fitnessSum += self.indvs[i].fitness
        if self.fitnessSum < sum_rcd:
            print('-------------<Degenerate>--------------')
        print('Generation<{}> :\n\tBestFitness<{}>\tFitnessSum<{}>'.\
            format(self.generation, self.bestFitness, self.fitnessSum))
        #----------------------------------------------------------------
        self._set_best()#generate new best indv
        next_generation = []
        self.generation += 1
        for i in range(len(self.indvs)):
            if i % self.__interval == 0:
                print('\tNextG<{}> new NO.{} Individual'.format(self.generation, i))
            child = self._select_parent().crossover(self._select_parent())
            child.user_init()
            child.mutate(self.pm)
            next_generation.append(child)
        self.indvs = next_generation
        return
    #--------------------------------------------------------------------
    #called after create Population obj
    def user_init(self):
        self.bestIndv.user_init()
        for i in range(len(self.indvss)):
            self.indvs[i].user_init()
        return