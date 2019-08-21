from fuzzysearch import find_near_matches
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from concurrent.futures import ThreadPoolExecutor, wait

def compare(input, texts,length=5, threshold=1):
    '''Uses fizzysearch´s Levenshtein search to find matches in n length'''
    matches = []
    query = []
    for n in range((len(input) - length + 1)):
        query.append(input[n:n+length])
    for q in query:
        for index, t in enumerate(texts, start=0):
            for x in find_near_matches(q,t,max_l_dist=threshold):
                matches.append((x,index,q))
    return matches

class NaturalLP():
    '''Used for NLP
    Inits with a language, picks stop words for comparison
    '''
    def __init__(self, lang = "english"):
        '''Inits to specific language'''
        self.stem = SnowballStemmer(lang)
        self.stopwords = set(stopwords.words(lang))

    def preprocess(self, input):
        '''Stop word removal and preprocessing'''
        output = []
        dic = []
        for index, x in enumerate(input):
            if x not in self.stopwords:
                output.append(self.stem.stem(x))
                dic.append(index)
        return output, dic 

    def bulkpreprocess(self, input, threads):
        '''Bulk multithreaded preprocess function'''
        output = []
        pre = self.preprocess
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for x in input:
                futures.append(executor.submit(pre, x))
            wait(futures)
            for x in futures:
                output.append(x.result())
        return output

    def addstopword(self, stopwords):
        '''Add a word or list to stopwords'''
        if isinstance(stopwords, str):
            self.stopwords.add(stopwords)
        elif isinstance(stopwords, list):
            self.stopwords.update(set(stopwords))
        else:
            pass

def shingle(input, k):
    '''Shingles the input in k length ngrams'''
    if k < 2:
        return input
    output = []
    for index in range(0, len(input)-k+1):
        output.append(input[index:index+k])
    return output

def shin_matches(shin1, shin2):
    '''Returns a list of tuples of the matches'''
    output = []
    for i, x in enumerate(shin1):
        for j, y in enumerate(shin2):
            if x == y:
                output.append((i, j))
    return output

def cluster_old(matches, gap, miin):
    '''Clusters matches based un Chebyshev distance, with gap as maximum distance and min as minimum cluster size'''
    #Initial Clustering
    temp = [[matches[0]]]
    for x in matches[1:]:
        for y in temp:
            t = False
            for z in y:
                if max(abs(x[0] - z[0]), abs(x[1] - z[1])) < gap:
                    t = True
                    break
            if t:
                y.append(x)
            else:
                temp.append([x])
    #Cluster duplicate check
    merges = []
    for i, x in enumerate(temp):
        for y in x:
            for j, z in enumerate(temp[i+1:], i+1):
                if (i,j) not in merges and y in z:
                    merges.append((i,j))
    #Cluster meging
    output = []
    exclude = []
    for i, x in enumerate(merges):
        output.append( temp[x[0]].extend([x for x in temp[x[1]] if x not in temp[x[0]]]) )
        exclude.extend([x[0], x[1]])
    output.extend([x for x in temp if x not in exclude])
    return [x for x in output if len(x) >= miin]

def cluster(matches, gap, miin):
    '''Much improved version of clustering (cluster_old)'''
    clusters = []
    for x in matches:
        merge = False
        for i, y in enumerate(clusters):
            for z in y:
                if max(abs(x[0]-z[0]), abs(x[1] - z[1])) <= gap:
                    if not merge:
                        y.append(x)
                        merge = i
                    else:
                        clusters[merge].extend([k for k in y if k not in clusters[merge]])
                        y = []
                    break
        if not merge:
            clusters.append([x])
    return [x for x in clusters if len(x) >= miin]

def get_dist(matches):
    '''Gets distance to the closest match of every point'''
    output = []
    for x in matches:
        dic = []
        for y in x:
            min_dist = 256
            for z in x:
                if y != z and max(abs(y[0]-z[0]), abs(y[1] - z[1])) < min_dist:
                    min_dist = max(abs(y[0]-z[0]), abs(y[1] - z[1]))
            dic.append(min_dist)
        output.append(dic)
    return output

