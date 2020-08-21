from indexer import doIndex,dumpDict,makeIdf
from querizer import doQuery
import os, json, shutil
import warnings
try:
   import cPickle as pickle
except:
   import pickle
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def initializeIndex():
    count=0
    dumpCount = 0
    partDict= {}
    urlDict = {}
    seekList = [[-1] * 36] * 36
    urlMap = open('urlmap.pk', 'wb')
    pickle.dump({}, urlMap, -1)
    urlMap.close()
    seekt = open('seeklist.pk', 'wb')
    pickle.dump([], seekt, -1)
    seekt.close()

    while os.path.isdir('indeces') or os.path.isdir('indecesdump'):
        shutil.rmtree('indeces', ignore_errors=True)
        shutil.rmtree('indecesdump', ignore_errors=True)
    os.makedirs('indeces')
    os.makedirs('indecesdump')

    for d in os.listdir('DEV'):
        for f in os.listdir(os.path.join('DEV',d)):
            print("RUNNING, TOTAL: " + str(count))
            with open(os.path.join('DEV',d,f), 'r') as curjson:  # open in readonly mode
                urlDict[count] = doIndex(json.load(curjson), partDict, count)
            count+=1
            if count % 1000 == 999:
                dumpDict(partDict, dumpCount)
                dumpCount+=1
                print("TOTAL: " + str(count))
    if count % 1000 != 999:
        dumpDict(partDict, dumpCount)
        dumpCount+=1
    makeIdf(count, urlDict, dumpCount, seekList)
    countSave = open('count.pk', 'wb')
    pickle.dump(count, countSave, -1)
    countSave.close()
    print("FINISHED, TOTAL: "+str(count))


if __name__=='__main__':
    urlM = open('urlmap.pk', 'rb')
    urlD = pickle.load(urlM)
    urlM.close()
    seekM = open('seeklist.pk', 'rb')
    seekL = pickle.load(seekM)
    seekM.close()
    countM = open('count.pk', 'rb')
    countI = pickle.load(countM)
    countM.close()
    while(True):
        query = input("Search: ")
        if query == "DEV:INDEX":
            initializeIndex()
            break
        elif query == "DEV:QUIT":
            break
        else:
            doQuery(query, urlD, seekL, countI)
