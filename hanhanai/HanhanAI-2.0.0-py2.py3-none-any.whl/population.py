# ======================================================================================================================
# =========================================Population & Select Part=====================================================
# ======================================================================================================================
"""
作者：赵士陆
创建时间：2019.9.4
最后一次修改时间：2019.9.10

"""

from HanhanAI.ga_brain import *
import pickle
import operator

class Population:
    def __init__(self, population_num):             # default init func
        self.size_population = population_num
        self.biont = []
        self.generation = 1

    def initPopulation(self, net_in, net_h1, net_h2, net_out):      # create a new population
        for i in range(self.size_population):
            self.biont.append(Network(net_in, net_h1, net_h2, net_out))

    def selectParents(self):        # select excellent biont in the population

        total_score = 0
        add_rate = 0
        father = Network()
        mother = Network()

        for i in range(self.size_population):
            total_score += self.biont[i].evaluate_score

        for i in range(self.size_population):
            self.biont[i].chosen_rate = self.biont[i].evaluate_score/total_score
            add_rate += self.biont[i].chosen_rate
            self.biont[i].accumulative_rate = add_rate

        sort_key = operator.attrgetter('evaluate_score')        # select two most excellent bionts to be parents
        self.biont.sort(key=sort_key, reverse=True)

        father = self.biont[0]
        mother = self.biont[1]

        print("**************the chosen father's score is ", father.evaluate_score, " **************")
        print("**************the chosen mother's score is ", mother.evaluate_score, " **************")

        return father, mother

    def breed(self, father, mother):            # breed next generation

        for i in range(self.size_population):
            self.biont[i] = mutate(cross(father, mother))

        self.biont[0] = father
        self.biont[1] = mother

        father.generation += 1
        mother.generation += 1

    def saveNet(self, generation):          # save the nets selected
        pickle_file = open('./saved_bionts/'+str(generation), 'wb')
        pickle.dump(self.biont, pickle_file)
        pickle_file.close()

    def loadNet(self, generation):          # load the previous nets
        pickle_file = open('./saved_bionts/'+str(generation), 'rb')
        bionts = pickle.load(pickle_file)
        pickle_file.close()
        return bionts

    def runGame(self, env):                 # run a game with a proper envirionment
        observation = env.reset()

        while True:

            print('-' * 20, 'Generation ', self.biont[0].generation, ' ', '-' * 20)

            # population.loadNet()
            for i in range(self.size_population):
                print('======== Biont ', i, ' Playing... ========')
                reward_vec = []
                for j in range(10):
                    episode_reward = 0
                    while True:
                        env.render()
                        action_vec = self.biont[i].run(observation)
                        action = np.argmax(action_vec)
                        observation, reward, done, info = env.step(action)
                        episode_reward += reward
                        if done:
                            env.reset()
                            reward_vec.append(episode_reward)
                            print('Episode ', j, ' | score = ', episode_reward)
                            break
                self.biont[i].evaluate_score = np.mean(reward_vec)
                print('Biont ', i, ' evaluate score is: ', self.biont[i].evaluate_score)

            father, mother = self.selectParents()
            self.breed(father, mother)

            self.saveNet(self.biont[0].generation)


