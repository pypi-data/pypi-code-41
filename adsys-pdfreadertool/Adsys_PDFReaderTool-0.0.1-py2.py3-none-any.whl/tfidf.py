#!/usr/bin/env python3
from pprint import pprint
from collections import defaultdict
import PyPDF2
from os import listdir
from os.path import isfile, join
import pprint as pp
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import extract




filename = "/Users/dontesmall/Desktop/pdf_test_folder"






CORPUS =  extract.extractTexttoarray((filename))

documents = []

for indx in CORPUS:
     documents.append(", ".join(map(str, indx)))
# Format of the corpus is that each newline has a new 'document'
# CORPUS = """
# In information retrieval, tf–idf or TFIDF, short for term frequency–inverse document frequency, is a numerical statistic that is intended to reflect how important a word is to a document in a collection or corpus.[1] It is often used as a weighting factor in searches of information retrieval, text mining, and user modeling. The tf–idf value increases proportionally to the number of times a word appears in the document and is offset by the number of documents in the corpus that contain the word, which helps to adjust for the fact that some words appear more frequently in general. Tf–idf is one of the most popular term-weighting schemes today; 83% of text-based recommender systems in digital libraries use tf–idf.
# LeBron Raymone James Sr. (/ləˈbrɒn/; born December 30, 1984), often referred to mononymously as LeBron, is an American professional basketball player for the Los Angeles Lakers of the National Basketball Association (NBA). He is often considered the best basketball player in the world and regarded by some as the greatest player of all time.[1][2][3][4] His accomplishments include four NBA Most Valuable Player Awards, three NBA Finals MVP Awards, and two Olympic gold medals. James has appeared in fifteen NBA All-Star Games and been named NBA All-Star MVP three times. He won the 2008 NBA scoring title, is the all-time NBA playoffs scoring leader, and is fourth in all-time career points scored. He has been voted onto the All-NBA First Team twelve times and the All-Defensive First Team five times.
# Marie Skłodowska Curie (/ˈkjʊəri/;[3] French: [kyʁi]; Polish: [kʲiˈri]; born Maria Salomea Skłodowska;[a] 7 November 1867 – 4 July 1934) was a Polish and naturalized-French physicist and chemist who conducted pioneering research on radioactivity. She was the first woman to win a Nobel Prize, the first person and only woman to win twice, and the only person to win a Nobel Prize in two different sciences. She was part of the Curie family legacy of five Nobel Prizes. She was also the first woman to become a professor at the University of Paris, and in 1995 became the first woman to be entombed on her own merits in the Panthéon in Paris.
# """.strip().lower()

DOC_ID_TO_TF = {} # doc-id -> {tf: term_freq_map where term_freq_map is word -> percentage of words in doc that is this one,
CORPUS_CONTINER =  str(documents).strip('[]')                 #           tfidf: ...}

DOCS = CORPUS_CONTINER.split("\n") # Documents where the index is the doc id
WORDS = CORPUS_CONTINER.split()
DF = defaultdict(lambda: 0)
for word in WORDS:
    DF[word] += 1

for doc_id, doc in enumerate(DOCS):

    #print("HERE IS THE DOCS :" + str(DOCS))
    #Num of times of the word showed up in doc
    TF = defaultdict(lambda: 0)
    TFIDF = {}
    doc_words = doc.split()
    word_count = len(doc_words)
    # percentage of words in doc that is this one = count of this word in this doc / total number of words in this doc

    for word in doc_words:
        # Here is the total num of count
        TF[word] +=1

    for word in TF.keys():
        TF[word] /= word_count
        TFIDF[word] = TF[word] / DF[word]

# loop over tfidt to sort it as a map
    pairs = [(word, tfidf) for word, tfidf in TFIDF.items()]
    # Why by [1] ?
    pairs.sort(key =   lambda p: p[1])
    top_10 = pairs[-15:]
    print("TOP 10 TFIDF")
    pprint(top_10)
    print("BOTTOM 10 TFIDF")
    pprint(pairs[0:15])

    DOC_ID_TO_TF[doc_id] = {'tf': TF, 'tfidf': TFIDF}
    # pprint(DOC_ID_TO_TF)
