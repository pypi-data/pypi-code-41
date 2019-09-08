
import PyPDF2
from io import BytesIO
from os import listdir
import pprint as pp
import sys,os,nltk,subprocess
from os.path import isfile, join
from nltk.corpus import stopwords
from PyPDF2 import PdfFileReader, utils
from collections import defaultdict
import config




FILENAME = config.pathName

# Understanding imports
# object access vs class access
# super
# descriptors

def textFromFile(filename):

    pdfFileObj = open(filename,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj,strict= False)

    text = [page.extractText().replace('\n', '') for page in pdfReader.pages]

    clean_data =removestopwords(text)
    return clean_data


def removestopwords(text):

    stop_words = set(stopwords.words('english'))
    #need to use regex for pattern matching temporay
    new_stopwords = ['page','1|','also','|','[, ]','v5','1.','2.','5.5','6','v6','4',' ©','[,]']
    stop_words.update(new_stopwords)

    word_tokens = nltk.word_tokenize(str(text).strip('[]').lower())

    filter_sentence = ' '.join([ word for word in word_tokens if not word in stop_words])


    result= []
    result.append(filter_sentence)
    print("")

    return result

def opendir(filename_= None):
    result = defaultdict(lambda: 0)
    counter = 0
    if filename_ is not None:
        for filename in os.listdir(filename_):
            if filename.endswith('.pdf'):
                result[counter]= filename
                counter+=1

    return result

def extractTexttoarray(dirname):
    # print("Before")
    # dirname2 = PdfReader.load()
    # print("After")
    onlyfiles = [f for f in listdir(dirname) if isfile(join(dirname, f)) ]

    filteredfile_list = filter(lambda f: f.endswith(('.pdf','.PDF')), onlyfiles)
    result = [textFromFile(join(dirname, f)) for f in filteredfile_list]

    return result



if __name__ == '__main__':
    print(sys.stdout.encoding)
    #pp.pprint(opendir(FILENAME))

    #pp.pprint(extractTexttoarray(FILENAME))
