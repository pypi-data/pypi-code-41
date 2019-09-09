def spelling_correction(sent):
    import numpy as np 
    import pandas as pd
    from subprocess import check_output
    import re
    from collections import Counter
    import wget
    import gzip
    import gensim
    import os

    #Downloading word2vec
    print("Downloading  Word2vec...")
    url = "https://s3.amazonaws.com/dl4j-distribution/GoogleNews-vectors-negative300.bin.gz"
    wget.download(url)

    #Unzip word2vec
    print("\n")
    print("Unziping Word2vec")
    input = gzip.GzipFile("GoogleNews-vectors-negative300.bin.gz", 'rb')
    s = input.read()
    input.close()

    print("\n")
    output = open("GoogleNews-vectors-negative300.bin", 'wb')
    output.write(s)
    output.close()

    print("Word2vec Downloaded and Unzipped Successfully")
    print("Loading Word2vec...")

    model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True)

    words = model.index2word
    w_rank = {}
    for i,word in enumerate(words):
        w_rank[word] = i
    WORDS = w_rank

    print("Loading Word2vec Done.")
    print("Loading SGnet")

    def words(text): return re.findall(r'\w+', text.lower())

    def P(word): 
        "Probability of `word`."
        # use inverse of rank as proxy
        # returns 0 if the word isn't in the dictionary
        return - WORDS.get(word, 0)

    def correction(word): 
        "Most probable spelling correction for word."
        return max(candidates(word), key=P)

    def candidates(word): 
        "Generate possible spelling corrections for word."
        return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

    def known(words): 
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in WORDS)

    def edits1(word):
        "All edits that are one edit away from `word`."
        letters    = 'abcdefghijklmnopqrstuvwxyz'
        splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
        deletes    = [L + R[1:]               for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
        replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
        inserts    = [L + c + R               for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(word): 
        "All edits that are two edits away from `word`."
        return (e2 for e1 in edits1(word) for e2 in edits1(e1))

    def correct_sentence(sent):
        core_sent = sent.split()
        correct_sent = []
        for i in range(len(core_sent)):
            corr = correction(core_sent[i])
            correct_sent.append(corr)
        return correct_sent

    return correct_sentence(sent)        