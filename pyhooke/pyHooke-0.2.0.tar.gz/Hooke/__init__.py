from Hooke import search, extract, order, compare
from .compare import NaturalLP
import time
from concurrent.futures import ThreadPoolExecutor, wait

def tim(times = None):
    '''Times Action'''
    if times:
        times.append(time.time())
    else:
        times = []
        times.append(time.time())
        return times

def read_file(file):
    '''Read and tokenize file using textract
    Takes a file as input, and outputs raw and normalized texts
    If it fails to read, it just runs "read_text"
    '''
    read = search.read(file)
    norread = extract.normalize(read)
    return read, norread

def read_text(text):
    '''Reads and tokenizes text
    Takes a text as input, and outputs raw and normalized texts 
    '''
    read = text.split()
    norread = extract.normalize(read)
    return read, norread

def divide(read):
    '''Divides text, output list of searches'''
    queries = search.div(read)
    return queries

def search_texts(queries):
    '''Searches using google'''
    sources = search.search(queries)
    return sources

def download_texts(sources, threads = 10, max_time = 30, timeout = 10, pdfsupport = False):
    '''Download texts from search using multithreading
    Returns normalized set of texts. The indices match their source
    '''
    nortexts = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for url in sources:
            futures.append(executor.submit(extract.doall, url, timeout, pdfsupport))
        wait(futures, timeout=max_time)
        for x in futures:
            nortexts.append(x.result())
    return nortexts

def levenshtein_compare(norread, nortexts, length = 30, threshhold = 7):
    '''Compares the texts with the input
    Returns unordered set of matches
    '''
    norcom = compare.compare(norread, nortexts, threshold=threshhold,length=length)
    return norcom

def order_results(norcom, sources):
    '''Orders Array of matches
    Returns ordered
    '''
    matchs = norcom
    sources = sources
    m2 = order.source_sort(order.match_elements(matchs) , len(sources))
    m3 = order.check_merges(m2)
    m4 = order.separate_matches(m3)
    matches = order.join_matches(m4)
    return matches

def print_matches(matches, sources = None, used = None):
    '''Prints
    Returns a list of indices of used sources
    '''
    if isinstance(matches[0][0], order.Match):
        print("\nMatches:")
        for x in matches:
            if len(x) > 0:
                print(f"{len(x)} matches from {x[0].source}")
        return
    if not used:
        used = []
    print("\nMatches:")
    used = order.print_matches(matches, sources, used)
    return used

def Textual(input, verbose = True, length = 20, threshhold = 5, threads = 15, max_time = 30, timeout = 10, pdfsupport = True):
    '''Does a textual search of the input'''
    read, norread = read_file(input)
    queries = divide(read)
    sources = search_texts(queries)
    nortexts = download_texts(sources, threads = threads, max_time = max_time, timeout = timeout, pdfsupport = pdfsupport)
    norcom = levenshtein_compare(norread, nortexts,length = length, threshhold = threshhold)
    matches = order_results(norcom, sources)
    if verbose:
        print_matches(matches, sources)
    return matches

def print_time(times):
    '''Prints Time'''
    print("\nTime taken:")
    for x in range(0, len(times) - 1):
        print(times[x+1]- times[x])
    print("Total:", times[-1] - times[0])

def shingle(input,k):
    '''Shingle the input in k length ngrams'''
    output = compare.shingle(input, k)
    return output

def pre_search(norread, stopwords=None):
    '''Makes a google search of the text without stop words'''
    if not stopwords:
        stopwords = Nlp().stopwords
    norread = [x for x in norread if x not in stopwords]
    output = ""
    for x in norread:
        output = output + " " + x
    output = divide(output)
    return search_texts(output)

def full_shin_comparison(input1, input2, dic1, dic2, shingle_size, gap, miin):
    input1 = compare.shingle(input1, shingle_size)
    input2 = compare.shingle(input2, shingle_size)
    matches = compare.shin_matches(input1, input2)
    matches = compare.cluster(matches, gap, miin)
    dist = compare.get_dist(matches)
    matches = order.de_preprocess(matches, dic1, dic2, dist)
    dist = order.bilinear(dist)
    output = order.shingle_final(matches, dist)
    return output

def Shingled(input, lang="english", miin=3, gap=2, shingle_size=1, threads = 10, pdfsupport = True, max_time=100, verbose = True):
    '''Does a complete search of the input using nlp'''
    nnlp = NaturalLP(lang)
    read, norread = read_file(input)
    sources = search_texts(divide(read))
    sources.append([x for x in pre_search(norread, nnlp.stopwords) if x not in sources])
    nortexts = download_texts(sources, threads = threads, pdfsupport = pdfsupport)
    nnlp.addstopword("hello")
    preread = nnlp.preprocess(norread)
    pretexts = nnlp.bulkpreprocess(nortexts, threads = threads)
    output = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for text in pretexts:
            futures.append(executor.submit(full_shin_comparison, preread[0], text[0], preread[1], text[1], shingle_size, gap, miin))
        wait(futures, timeout=max_time)
        for x in futures:
            output.append(x.result())
    for i, x in enumerate(output):
        for y in x:
            y.source = sources[i]
    if verbose:
        print_matches(output)
    return output
    

if __name__ == "__main__":
    times = tim()
    #Textual("In information theory, linguistics and computer science, the Levenshtein distance is a string metric for measuring the difference between two sequences. Informally, the Levenshtein distance between two words is the minimum number of single-character edits (insertions, deletions or substitutions) required to change one word into the other")
    Shingled("In information theory, linguistics and computer science, the Levenshtein distance is a string metric for measuring the difference between two sequences. Informally, the Levenshtein distance between two words is the minimum number of single-character edits (insertions, deletions or substitutions) required to change one word into the other","english",3,3,2)
    print_time(times)