try:
   import cPickle as pickle
except:
   import pickle
from bs4 import BeautifulSoup
from collections import Counter
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from math import log
import lxml
import os, shutil, re
alph = '0123456789abcdefghijklmnopqrstuvwxyz'
inalph=re.compile('^[a-z0-9]+$')

def doIndex(curjson, partDict, count): #tokenize, stem, and store postings in partial dictionary for curjson
    stopWords = set(stopwords.words('english'))
    soup = BeautifulSoup(curjson['content'], "lxml" , from_encoding=curjson['encoding'])
    textTokens = [PorterStemmer().stem(w.lower()) for w in word_tokenize(soup.get_text()) if inalph.match(w) and w not in stopWords]
    tupCount = Counter(textTokens)

    if soup.title:
        for titletok in [PorterStemmer().stem(w.lower()) for w in word_tokenize(soup.title.text) if inalph.match(w) and w not in stopWords]:
            tupCount[titletok] += 5
    for impsent in soup.find_all(["h1", "h2", "h3", "b", "strong"]):
        for imptok in [PorterStemmer().stem(w.lower()) for w in word_tokenize(impsent.text) if inalph.match(w) and w not in stopWords]:
            tupCount[imptok] += 3

    for k,v in tupCount.items():
        if len(k) > 1:
            if k in partDict:
                partDict[k].append((count, v))
            else:
                partDict[k] = [(count, v)]
    return curjson['url']


def dumpDict(partDict, dumpCount): #dump temporary dictionary so we don't use too much memory
    sortPart = sorted(partDict.items()) #make sure terms are sorted
    pasti = 0
    for i in range(len(sortPart)):
        if i+1 == len(sortPart) or sortPart[i][0][0] != sortPart[i+1][0][0]:
            print("DUMPING INTO INDEX ", sortPart[i][0][0])
            curInd = open('indeces/ind' + sortPart[i][0][0], 'w') #make corresponding blank final index
            curInd.close()
            curInd = open('indecesdump/ind' + sortPart[i][0][0] + str(dumpCount), 'w')
            for k in sortPart[pasti:i+1]:  #partition dict into new small temp files
                curInd.write(str(k))
                curInd.write("\n")
            curInd.close()

            pasti = i+1
    partDict.clear()
    return


def makeIdf(count, urlDict, dumpCount, seekList):
    for f in os.listdir('indeces'): #need to combine all the dumped indeces
        print("MAKING IDF FOR INDEX ", f)
        tcomb = open('indecesdump/comb', 'w') #refresh combine file
        tcomb.close()
        for d in range(dumpCount):
            combineFiles('indecesdump/comb','indecesdump/' + f + str(d)) #combine all temp files of one letter

        pasti = '\0'
        finInd = open('indeces/'+f, 'w') #do final tf-idf computation with final posting list lengths
        curInd = open('indecesdump/comb', 'r')
        templist = [-1] * 36
        for line in curInd:
            cTup = extractTuple(line)
            cList = []
            for post in cTup[1]:
                tf = 1+log(post[1],10)
                idf = log(float(count) / len(cTup[1]), 10)
                cList.append((post[0], tf * idf))
            finInd.write(str((cTup[0],cList)))
            finInd.write('\n')

            if pasti < cTup[0][1]:
                templist[alphabetI(cTup[0][1])] = finInd.tell() #index the index with seeklist
                pasti = cTup[0][1]

        seekList[alphabetI(f[3])] = templist
        finInd.close()
        curInd.close()

    while os.path.isdir('indecesdump'): #remove dumped partial indeces
        shutil.rmtree('indecesdump', ignore_errors=True)
    os.makedirs('indecesdump')

    urlMap = open('urlmap.pk', 'wb') #dump url map into file at end
    pickle.dump(urlDict, urlMap, -1)
    urlMap.close()
    seekF = open('seeklist.pk', 'wb')  # dump url map into file at end
    pickle.dump(seekList, seekF, -1)
    seekF.close()
    return


def combineFiles(file1,file2): #combines two indeces without much memory footprint, file1 will have combined data.
    curDump = None
    nextDump = None
    try:
        curDump = open(file1, 'r')
        nextDump = open(file2, 'r')
    except:
        return
    outDump = open('indecesdump/temp', 'w')
    curLine = curDump.readline()
    nextLine = nextDump.readline()

    while nextLine != '' and curLine != '':
        nextTup = extractTuple(nextLine)
        curTup = extractTuple(curLine)
        if nextTup[0] < curTup[0]: #progress nextfile
            outDump.write(str(nextTup))
            outDump.write('\n')
            nextLine = nextDump.readline()
        elif nextTup[0] > curTup[0]: #progress curfile
            outDump.write(str(curTup))
            outDump.write('\n')
            curLine = curDump.readline()
        else: #progress both files and COMBINE lists
            combList = curTup[1] + nextTup[1]
            outDump.write(str((curTup[0],combList)))
            outDump.write('\n')
            curLine = curDump.readline()
            nextLine = nextDump.readline()

    while nextLine != '': #finish nextfile if not done
        nextTup = extractTuple(nextLine)
        outDump.write(str(nextTup))
        outDump.write('\n')
        nextLine = nextDump.readline()
    while curLine != '':  # finish curfile if not done
        curTup = extractTuple(curLine)
        outDump.write(str(curTup))
        outDump.write('\n')
        curLine = curDump.readline()

    curDump.close()
    nextDump.close()
    outDump.close()
    shutil.copyfile('indecesdump/temp',file1)
    return


def extractTuple(st): #turns a string into a usable tuple (term,posting list)
    dt = (st[2:].split("',")[0], st[st.index("[") + 2:st.index("]") - 1].split("), ("))
    newdt = []
    for x in dt[1]:
        newdt.append((int(x.split(", ")[0]), float(x.split(", ")[1])))
    return (dt[0], newdt)

def alphabetI(st): #returns position of this string in alphabet (to simplify index of index)
    return alph.index(st)