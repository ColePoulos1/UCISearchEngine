try:
   import cPickle as pickle
except:
   import pickle
from collections import Counter
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from math import log
import numpy as np
from collections import Counter
import time, os, re
from indexer import extractTuple, alphabetI
inalph=re.compile('^[a-z0-9]+$')

def doQuery(query, urlDict, seekList, count):
    starttime = time.time()
    stopWords = set(stopwords.words('english'))
    query_words = [PorterStemmer().stem(w) for w in word_tokenize(query.lower()) if inalph.match(w) and w not in stopWords]
    if len(query_words) == 0:
        print("Invalid Query (No findable non-trivial words)")
        return
    qc = Counter(query_words)

    postRanking = {}
    first = True
    highestID = 0
    qlist = []
    for qword,qdf in qc.items():
        curInd = open('indeces/ind'+qword[0], 'r')
        if len(qword) > 1 and seekList[alphabetI(qword[0])][alphabetI(qword[1])] == -1:
            print("NO RESULTS FOUND")
            return
        if len(qword) > 1:
            curInd.seek(seekList[alphabetI(qword[0])][alphabetI(qword[1])]) #use skiplist on second letter in query
        for line in curInd:
            lTup = extractTuple(line)
            if qword == lTup[0]:
                qlist.append((1 + log(qdf,10)) * log(count / float(len(lTup[1])),10)) #query tf-idf
                for post in lTup[1]:
                    if first:
                        postRanking.update({post[0] : [post[1]]})
                        if highestID < post[0]:
                            highestID = post[0]
                    elif post[0] > highestID:
                        break
                    elif post[0] in postRanking.keys():
                        postRanking[post[0]].append(post[1])
                break
        else:
            print("NO RESULTS FOUND")
            return
        first = False
        curInd.close()
    #print(postRanking.values())
    #print(qlist)
    #round(np.inner(qlist, v) / (np.linalg.norm(qlist) * np.linalg.norm(v)), 3)
    #1 - spatial.distance.cosine(qlist, v)
    #cosine similarity not working, had to revert to sum method
    postRanking = [(k,sum(v)) for k,v in postRanking.items() if len(v)==len(qlist)]
    postRanking.sort(key=lambda x: -x[1])
    print("About " + str(len(postRanking)) + " results (" + str(round((time.time() - starttime)*1000)) + " milliseconds)")
    for u,r in postRanking[:20]:
        print(urlDict[u])
    return