"""
Author: Alex Peden
email:  apeden23@gmail.com
July 2019

A programme for sorting brownies* into groups (tents)
of equal size according to friendships. Brownies and
friendship choices are imported from a text file.
An algorithm is run to find the optimal (or near best)
groupings of brownies. The best camp can be printed to screen
as a list of tents, their occupants, and the associated
happiness scores. 

*in the UK, a brownie is a junior girl-guide (or junior
girl-scout)
"""

import random
import math

class Brownie(object):
    """A participant in a camp who has to share a tent
    (or be in a group) with other brownies. The happiness
    of this participant depends on whether the other participants
    she is grouped with are friends, mutual friends, or (non-
    reciprocated) admirers.
    """
    def __init__(self, name):
        self.name = name
        self.friends = []
        self.happiness = 0
    def addFriend(self, friend):
        """Add friend to friend list of this brownie."""
        self.friends.append(friend)
    def setHappiness(self, deltaHapp):
        """Increase happiness of this brownie by 'deltaHapp'."""
        self.happiness += deltaHapp
    def getHappiness(self):
        """Return happiness score of this brownie"""
        return self.happiness
    def getFriends(self):
        """Return names of brownies this brownie says she likes"""
        return self.friends
    def bonding(self, other):
        """Determine bond of this brownie with another.
        If brownie likes other brownie, bond is 1.
        If other brownie also likes this brownie, bond is 2.
        If only other brownie likes this brownie, bond is 1.
        """
        bond = 0
        if self.name in other.friends:
           bond += 1
        if other.name in self.friends:
           bond += 1
        return bond
    def getName(self):
        """Return name of brownie."""
        return self.name
    def __str__(self):
        """Print brownie name and friends."""
        return self.name + " has friends "+ str(self.friends)

class Tent(object):
    """A kind of grouping (which may actually be a tent)
    which will contain brownies. It will have a happiness,
    set according to the friendship statuses of the occupant
    brownies.
    """
    def __init__(self, num):
        self.num = num
        self.brownies = []
        self.brownie_profiles = ()# brownie names and happinesses
        self.happiness = 0
    def getNum(self):
        """Returning the identifying  number of this tent"""
        return self.num
    def getCapacity(self):
        """Return the capacity of this tent."""
        return self.capacity 
    def addBrownie(self, brownie):
        """Add a brownie to this tent.
        """
        self.brownies.append(brownie)
    def favIndex(self, otherBrownies):
        """Return the index of the brownie in a list
        of brownies that is most favoured by the
        occupants of this tent.
        """
        favIndex, topBond = 0,0
        for i in range(len(otherBrownies)):
            tentBond = 0
            for brownie in self.brownies:
                tentBond += brownie.bonding(otherBrownies[i])
            if tentBond > topBond:
                topBond = tentBond
                favIndex = i
        return favIndex
    def setHappiness(self):
        """Determine happiness of this tent
        on the basis of declared friendships
        amungst the brownies.
        For example, if a brownie in the
        tent likes another brownie in the tent,
        this increases tent happiness by 1. If
        the other brownie likes them back, happiness is
        increased by not 1, but 2 etc. 
        """
        self.happiness = 0
        for b1 in self.brownies:
            for b2 in self.brownies:
                if b1 == b2:
                    continue
                if b1.getName() in b2.getFriends():
                    b1.setHappiness(1)
                    self.happiness += 1
                for friend in b1.getFriends():
                    if friend == b2.getName():
                        b1.setHappiness(1)
                        self.happiness += 1
    def getHappiness(self):
        "Return happiness of the tent."""
        return self.happiness
    def getBrownies(self):
        """Return all brownies in the tent."""
        return self.brownies
    def __str__(self):
        """Print tent occupants and their happinesses"""
        for brownie in self.brownies:
            self.brownie_profiles += (brownie.getName().ljust(12, " ")\
                                      +": "+str(brownie.happiness),)

        summary = "Tent " + str(self.num + 1)+": "
        summary += " Happiness: "+ str(self.getHappiness()) +"\n"
        for profile in self.brownie_profiles:
            summary += profile + "\n"
        return summary

class Camp(object):
    """A camp of brownies that will comprise tents (
    groupings of brownies) each with 'happiness' scores
    that will depend on who they are sharing a tent with.
    """
    def __init__(self, camp_name,  num_tents =4):
        self.name = camp_name
        self.num_tents = num_tents
        self.tents = []
        self.allBrownies = []
        self.availBrownies = []
        self.happiness = 0
        self.minHapp = 0
    def getName(self):
        """Return name of camp."""
        return self.name
    def setTents(self, tent):
        """Add a tent to the camp if the total will
        be less then or equal to that allowed.
        """
        if len(self.tents) < self.num_tents:
            self.tents.append(tent)
    def getTents(self):
        """Return the tents in this camp."""
        return self.tents
    def addBrownie(self,brownie):
        """Add this brownie to the camp"""
        self.allBrownies.append(brownie)
        self.availBrownies = self.allBrownies[:]
    def randSeedTents(self):       
        """Place one brownie at random in each of the
        empty tents. Then call voteFill() to fully
        populate the tents with brownies.
        """
        for i in range(self.num_tents):
            t = Tent(i)
            numBrownies = len(self.availBrownies)
            randIndex = random.choice(range(numBrownies))
            randBrownie = self.availBrownies.pop(randIndex) 
            t.addBrownie(randBrownie)
            self.setTents(t)
        self.voteFill()
    def voteFill(self):
        i = 0
        """Sequentially (tent by tent) get brownie(s) in each
        tent to vote on which of the remaining brownies they
        would (collectively) most like to join them. The chosen
        brownie is added to the tent.
        """
        while len(self.availBrownies)> 0:
            tentNum = (i%self.num_tents)
            tent =self.tents[tentNum]
            favIndex = tent.favIndex(self.availBrownies)
            tent.addBrownie(self.availBrownies.pop(favIndex))
            i += 1
    def setHappiness(self):
        """Determine happiness of the camp on basis of collective
        happinesses of the tents (in turn dependent on the
        happinesses of the brownies therein).
        """
        self.happiness = 0
        for tent in self.tents:
            tent.setHappiness()
            self.happiness += tent.getHappiness()
    def getHappiness(self):
        """Return camp happiness."""
        return self.happiness
    def getRangeHapp(self):
        """Determine difference between most happy
        and least happy tent in the camp.
        """
        max = self.tents[0].getHappiness()
        min = self.tents[0].getHappiness()
        for tent in self.tents:
            if tent.getHappiness() > max:
                max = tent.getHappiness()
            elif tent.getHappiness() < min:
                min = tent.getHappiness()
        return max-min
    def setMinHapp(self):
        "Determine happiness of least happy brownie in the camp."""
        minHapp = self.tents[0].brownies[0].getHappiness()
        for tent in self.tents:
            for brownie in tent.getBrownies():
                if brownie.getHappiness() < minHapp:
                    minHapp = brownie.getHappiness()
        self.minHapp = minHapp
    def getMinHapp(self):
        "Return happiness of least happy brownie in the camp."""
        return self.minHapp
    def getTents(self):
        """Return tents"""
        return self.tents
    def __str__(self):
        """Print camp name and number of groups."""
        return "Hypothetical camp " \
               + self.name \
               + " has " + str(self.num_tents) + " tents."
    
class CampOrganiser(object):
    """Class for finding for a camp a very good arrangement
    of brownies into equally-sized groups on the basis of
    friendships.

    Arrangments are made on the basis of the organiser
    declaring the number of tents (groups) OR their individual
    capacities (i.e. the size of the groups):
    The former will override the latter.
    """
    def __init__(self, file = None, numTents = None,
                 capacityTents = None):
        if not file == None:
            self.file = file
        self.brownies = []
        self.friendlist = []
        self.readFile()
        self.brownieObjs = []
        self.camps = []
        if numTents == None:
            try:
                self.numTents = math.ceil(len(self.friendlist)/capacityTents)
            except:
                print ("Please declare the number of tents, ",\
                    "or the capacity of the tents as ints")
        else:
            self.numTents = numTents
    def readFile(self):
        """Read in brownies and friends from a text file."""
        try:
            f = open(self.file)
        except:
            print("Error opening brownie file")
        inFile = open(self.file)
        for l in inFile:
            try:              
                brownieAndFriends = l.rstrip('\n').split(',')
                self.friendlist.append(brownieAndFriends)
            except:
                print("Error reading line")
    def are_brownies(self, friend_list):
        """Check all friends quoted by brownies are
        actually in the list of brownies coming to the
        camp.
        """
        for friend in friend_list:
            if not friend in self.brownies:
                print (friend + " is not a named brownie")
                return False
        return True
    def addBrownies(self):
        """Generate list of brownie names with their chosen friends
        and a list of brownies (objects).
        """
        self.brownies, self.brownieObjs = [],[]
        for brownieAndFriends in self.friendlist:
            self.brownies.append(brownieAndFriends[0])
        for brownieAndFriends in self.friendlist:
            b = Brownie(brownieAndFriends[0])
            if self.are_brownies(brownieAndFriends[1:]):
                for friend in brownieAndFriends[1:]:
                    b.addFriend(friend)
            else:
                print ("A friend of "+ brownieAndFriends[0] \
                       + " is not listed as brownie: " \
                       + str(brownieAndFriends[1:]))
                raise
            self.brownieObjs.append(b)
    def setCamps(self, numTrials):
        """Generate numTrials alternative camps"""
        self.camps = []
        for x in range(numTrials):
            self.addBrownies()
            camp  = Camp (str(x), self.numTents)
            for brownie in self.brownieObjs:
                camp.addBrownie(brownie)
            #seed tents with random brownies
            #tents filled by voting of tent occupants
            camp.randSeedTents()
            #calc brownie, tent and camp happiness
            camp.setHappiness()
            #calc min happiness of brownie in camp
            camp.setMinHapp()
            self.camps.append(camp)
    def happFilt(self):
        happCamps = []
        """Filter alternative camps
        to maximise camp happiness
        """
        maxHappCamp = max(self.camps,
                              key =lambda x:x.getHappiness())
        maxHapp =  maxHappCamp.getHappiness()
        for camp in self.camps:
            if camp.getHappiness() == maxHapp:
                happCamps.append(camp)
        self.camps = happCamps
        print("Max Happiness: "+str(maxHapp))
        print("Num alternative camps after filtering"
              + " to maximise camp happiness: "
              + str(len(self.camps)))
    def maxMinBrownieHappFilt(self):
        """Filter alternative camps
        to minimize individual brownie unhappiness.
        """
        maxMinHappCamps = []
        maxMinBrownHappCamp = max(self.camps,
                              key = lambda x:x.getMinHapp())      
        maxMinBrownHapp = maxMinBrownHappCamp.getMinHapp()
        for camp in self.camps:
            if camp.getMinHapp() == maxMinBrownHapp:
                maxMinHappCamps.append(camp)
        self.camps = maxMinHappCamps
        print("Max min brownie happiness: "
              + str(maxMinBrownHapp)
              + "\nNum alternative camps after filtering"
              + " for brownie happiness: "
              + str(len(self.camps)))
    def rangeFilt(self):
        """Filter alternative camps
        to minimize variation in tent happiness.
        """
        minRangeCamps = []
        minRangeHappCamp = min(self.camps,
                              key = lambda x:x.getRangeHapp())
        minRangeHapp = minRangeHappCamp.getRangeHapp()
        for camp in self.camps:
            if camp.getRangeHapp() == minRangeHapp:
                minRangeCamps.append(camp)
        self.camps = minRangeCamps
        print("Min range of tent happinesses: ",str(minRangeHapp))
        print("Num alternative camps after filtering"
              + " to minimise range of tent happinesses: "
              + str(len(self.camps)))
    def happTrial(self, numTrials, priority = None):
        """Find a good arrangement of brownies in tents
        by generating numTrials numbers of possible camps
        and then select an example of the best ones on
        the basis of a 'priority'.

        Keyword argument: priority (default = 'camp')

        If priority is 'camp' the selection process favours
        the camps with the overall highest happiness scores.

        A priority of 'brownie' aims the maximise the 'happiness'
        of the least happy brownie in the camp.

        A priority of 'evenTents' tries to minimise the differences
        in 'happiness scores' between the tents.
        """
        
        print("NumTrials =", str(numTrials), "....") 
        self.setCamps(numTrials)
        filters = {1:self.happFilt,
                   2:self.maxMinBrownieHappFilt,
                   3:self.rangeFilt}    
        if priority == None:
            print("Prioritising camp happiness")
            filter_order = [1,2,3]
        elif priority == "brownie":
            print("Prioritising no unhappy brownies")
            filter_order = [2,1,3]
        elif priority == "evenTents":
            print("Prioritising evenly happy tents")
            filter_order = [3,1,2]
        for x in filter_order:
            filters[x]()
        print("Chosen camp has the following arrangement....\n")
        for tent in self.camps[0].getTents():
            print(tent)
    def __str__(self):
        """print brownies alongside the other brownies they like.
        e.g. Anna likes Susan Jane Julia...
        (because Anna has declared liking the three other brownies
        named above)
        """
        summary = "Summary of Relationships\n"
        for line in self.friendlist:
            summary += line[0].ljust(12, " ") \
                       + " likes  "
            for friend in line[1:]:
                summary += friend.ljust(12, " ") + "  "
            summary += "\n" 
        return summary

def sorter(file, numTents = None, capacityTents = None, numTrials = 10000, priority = None):
    global o
    o = CampOrganiser("brownies193.txt", numTents, capacityTents)
    o.happTrial(numTrials, priority)

def showFriends():
    print (o)

if __name__ == "__main__":
    sorter("brownies193.txt", capacityTents = 4)
    showFriends()






