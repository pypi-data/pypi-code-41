
import PyPDF2
from os import listdir
from os.path import isfile, join
import pprint as pp
import extract
import kivy
import config


DEFAULT_DIR = config.pathName

normalizedTermFrequency = {}
dictOFIDFNoDuplicates = {}
def run_tfidf(dirname):
    #Here is where load needs to be called, disable other buttons if filename_ None

    def create_dirifles(fName = None):
        if fName is None:
            return "Select File/Folder to Generate PDF Keywords"
        docu = extract.extractTexttoarray(fName)
        docs = []

        for indx in docu:
            docs.append(", ".join(map(str, indx)))

        return docs

    #---Calculate term frequency --
    documents = create_dirifles(DEFAULT_DIR)
    #First: tokenize words
    dictOfWords = {}

    for index, sentence in enumerate(documents):
        tokenizedWords = sentence.split(' ')
        dictOfWords[index] = [(word,tokenizedWords.count(word)) for word in tokenizedWords]

    #print(dictOfWords)

    #second: remove duplicates
    termFrequency = {}

    for i in range(0, len(documents)):
        listOfNoDuplicates = []
        for wordFreq in dictOfWords[i]:
            if wordFreq not in listOfNoDuplicates:
                listOfNoDuplicates.append(wordFreq)
            termFrequency[i] = listOfNoDuplicates
    #print(termFrequency)

    #Third: normalized term frequency
    #normalizedTermFrequency = {}
    for i in range(0, len(documents)):
        sentence = dictOfWords[i]
        lenOfSentence = len(sentence)
        listOfNormalized = []
        for wordFreq in termFrequency[i]:
            normalizedFreq = wordFreq[1]/lenOfSentence
            listOfNormalized.append((wordFreq[0],normalizedFreq))
        normalizedTermFrequency[i] = listOfNormalized

    #print(normalizedTermFrequency)


    #---Calculate IDF

    #First: put all sentences together and tokenze words
    allDocuments = ''
    for sentence in documents:
        allDocuments += sentence + ' '
    allDocumentsTokenized = allDocuments.split(' ')

    #print(allDocumentsTokenized)

    allDocumentsNoDuplicates = []

    for word in allDocumentsTokenized:
        if word not in allDocumentsNoDuplicates:
            allDocumentsNoDuplicates.append(word)


    #print(allDocumentsNoDuplicates)

    #Calculate the number of documents where the term t appears
    dictOfNumberOfDocumentsWithTermInside = {}

    for index, vocab in enumerate(allDocumentsNoDuplicates):
        count = 0
        for sentence in documents:
            if vocab in sentence:
                count += 1
        dictOfNumberOfDocumentsWithTermInside[index] = (vocab, count)

    #print(dictOfNumberOfDocumentsWithTermInside)


    #calculate IDF
    #dictOFIDFNoDuplicates = {}

    import math
    for i in range(0, len(normalizedTermFrequency)):

        listOfIDFCalcs = []
        for word in normalizedTermFrequency[i]:
            for x in range(0, len(dictOfNumberOfDocumentsWithTermInside)):
                if word[0] == dictOfNumberOfDocumentsWithTermInside[x][0]:
                    listOfIDFCalcs.append((word[0],math.log(len(documents)/dictOfNumberOfDocumentsWithTermInside[x][1])))
        dictOFIDFNoDuplicates[i] = listOfIDFCalcs

    # for word,b in dictOFIDFNoDuplicates.items():
    #     print(word, ":",b)


def PDF_keywords():
    run_tfidf(DEFAULT_DIR)

    dictOFTF_IDF = {}
    bad_chars = [';', ':', '!', "*", "'", ")", ".", "-", "...", "(",',','``']
    for i in range(0,len(normalizedTermFrequency)):
        listOFTF_IDF = []
        TFIDF_Sort = {}
        TFsentence = normalizedTermFrequency[i]
        IDFsentence = dictOFIDFNoDuplicates[i]
        for doc_Keyidx in range(0, len(TFsentence)):

            if TFsentence[doc_Keyidx ][0] not in bad_chars and not TFsentence[doc_Keyidx][0].isdigit():
                #listOFTF_IDF.append((TFsentence[x][0],TFsentence[x][1]*IDFsentence[x][1]))

                tf_Generated_Keywords = TFsentence[doc_Keyidx ][0]
                tf_keywordscores = TFsentence[doc_Keyidx][1]*IDFsentence[doc_Keyidx][1]
                #Need to format output text of tf_keywords,tf_keywordscores

                listOFTF_IDF.append((("%s" % (tf_Generated_Keywords)),tf_keywordscores))

                TFIDF_Sort[tf_Generated_Keywords] = tf_keywordscores

        dictOFTF_IDF[i] = listOFTF_IDF

        #sort Functionality
        # pairs = [(word, tfidf) for word, tfidf in TFIDF_Sort.items()]
        # # Why by [1] ?
        # pairs.sort(key =   lambda p: p[1])
        # top_10 = pairs[-20:]
        # print("TOP 10 TFIDF")
        # pp.pprint(top_10)
        # print("BOTTOM 10 TFIDF")
        # pp.pprint(pairs[0:20])
    return dictOFTF_IDF



if __name__ == '__main__':
    run_tfidf(DEFAULT_DIR)
