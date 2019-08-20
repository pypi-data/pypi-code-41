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
