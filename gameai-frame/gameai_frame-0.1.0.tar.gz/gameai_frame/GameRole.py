from . import NeuroNetwork as NN
from . import global_vars as g
from abc import ABCMeta, abstractmethod
#abstract
#represent the role in specific game
#base class of user defined game role 
class GameRole(object):
    #assert to be default constructable
    #living_time_limit : if an individual cotinuously perform foolly for such long time, it dead
    def __init__(self, living_time_limit = 200):
        self.brain = NN.NeuralNet(g.NN_INPUT_SIZE, g.NN_HIDDEN_SIZE, g.NN_OUTPUT_SIZE,\
            g.NN_HIDDENLAYER_NUM)
        self.vision = [0.0 for i in range(g.NN_INPUT_SIZE)]
        self.descision = [0.0 for i in range(g.NN_OUTPUT_SIZE)]
        #string used to illustrate----
        self.illus_movement = ''
        self.illus_dead_reason = ''
        #-----------------------------
        self.fitness = 0.0
        self.lifetime = 0
        self.timeleft = living_time_limit
        self.timelimit = living_time_limit
        self.dead = False
        return
    @abstractmethod
    def calculate_fitness(self):
        pass
    @abstractmethod
    #look around to get self.vision(NN input)
    def look(self):
        pass
    @abstractmethod
    #draw the game role
    def show(self):
        pass
    #called after look
    #need to be overrided---------------------------------------
    def think(self):
        self.descision = self.brain.output(self.vision)
        #deal the descision, generate move-----
        #and update self.illus_movement if need

        #--------------------------------------
        return
    #-----------------------------------------------------------
    #override it to do user define game role initialize
    #take no args, use global data in overrided funtion if need
    #it can be blank
    def user_init(self):
        return
    #update user special data
    #called in Population::update()
    def user_update(self):
        return
    #just change the name'GameRole' and copy it to user subclass
    #-----------------------------------------------------------
    def clone(self):
        retval = GameRole()
        retval.brain = self.brain.clone()
        return retval
    def crossover(self, partner):
        retval = GameRole()
        retval.brain = self.brain.crossover(partner)
        return retval
    #-----------------------------------------------------------
    def mutate(self, pm):
        self.brain.mutate(pm)
        return