from CampOrganiser import CampOrganiser as c


class Sort(object):
    def sorter(file, numTents, numTrials = 10000, priority = None):
        """Analyse a file (txt) listing brownies and their friends.
        sorts brownies into numTents tents by friendships, doing this
        numTrials times. The happiest sortings are then found
        by a process of filtering according to the priority. Default
        priority maximises global camp happiness, "brownie" makes sure
        there are no severely unhappy brownies in the final sorting
        """
        o = c("brownies193.txt", numTents)
        print(o)
        o.happTrial(numTrials, priority)

if __name__ == "__main__":
    Sort.sorter("brownies193.txt", 4)






