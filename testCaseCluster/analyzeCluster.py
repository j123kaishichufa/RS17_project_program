import sys
import csv

SMOOTH_THR = 10

def readCSV(fileName):
    resList = list()
    with open(fileName, "rb") as fp:
        reader = csv.reader(fp)
        for each in reader:
            resList.append(each)
    return resList

def writeCSV(listList, fileName):
    with open(fileName, "wb") as fp:
        writer = csv.writer(fp)
        writer.writerows(listList)
    print fileName
#classList=[ [id1, name1], [id2, name2], [id3, name3], ...]
def processClass(classList):
    classID2NameDict = dict()
    for each in classList:
        [classID, className] = each
        classID2NameDict[int(classID)] = className
    return classID2NameDict

#fvList = M= [ [ts1, ,,,,], [], [], ...]
def processFeatureVec(fvList):
    fvM = list()
    for eachList in fvList:
        del eachList[0] #testcaseName
        tmpList = list()
        for each in eachList:
            tmpList.append(int(each))
        fvM.append(tmpList)
    return fvM

#clusterList = [ [clusterID, testcaseID, testcaseName][][] ,  ...]
def processCluster(clusterList):
    resList = list()
    for eachList in clusterList:
        [clusterID, tsID, tsName] = eachList
        clusterID = int(clusterID)
        tsID = int(tsID)
        if len(resList) == clusterID:
            resList.append(list())
        resList[clusterID].append(tsID)
    '''
    print "\nfirst process cluster..."
    for each in resList:
        print each
    '''
    return resList

#print set by classname instead of classID
def printSet(oneSet, classID2NameDict):
    resList = list()
    for classID in list(oneSet):
        resList.append(classID2NameDict[classID])
    return resList

#compute the classcount for each cluster
def mergeCluster(clusterList, fvList, classCount):
    resList = list()
    for clusterID in range(0, len(clusterList)):
        tsIDList = clusterList[clusterID]
        tmpList = [0] * classCount
        for eachTsID in tsIDList:
            #two list is sumed togeter for each element
            tmpList = map(lambda x, y : x + y, tmpList, fvList[eachTsID])
        resList.append(tmpList)
    '''
    print "\nafter merge..."
    for each in resList:
        print each
    '''
    return resList

#smooth cluster, if a class total number < SMOOTH_THR, then make it 0.
def del_smoothCluster(clusterList):
    clusterCount = len(clusterList)
    classCount = len(clusterList[0])
    for j in range(0, classCount):
        tmp = 0
        for i in range(0, clusterCount):
            tmp += clusterList[i][j]
        if tmp < SMOOTH_THR:
            for i in range(0, clusterCount):
                clusterList[i][j] = 0

    return clusterList

#smooth cluster, if a cell value < SMOOTH_THR, then make it 0.
def smoothCluster(clusterList):
    n = len(clusterList)
    m = len(clusterList[0])
    for i in range(0, n):
        for j in range(0, m):
            if clusterList[i][j] < SMOOTH_THR:
                clusterList[i][j] = 0
    return clusterList


#change the list into set, that is delete the '0' column
def trans2Set(clusterList):
    clusterClassIDList = list()
    for eachList in clusterList:
        tmpList = list()
        for classID in range(0, len(eachList)):
            if eachList[classID] != 0:
                tmpList.append(classID)
        clusterClassIDList.append(tmpList)
    '''
    print "\nafter transformation"
    for each in clusterClassIDList:
        print each
    '''
    return clusterClassIDList

#set operation: get each cluster's differSet
#list = [classid1, classid2,..] ,  [classid3, classid2, .. ][]
def genBuSet(clusterClassIDList, classID2NameDict):
    print "compute each cluster's only ..."
    buSetList = list()   #eachelement is a set
    for clusterID in range(0, len(clusterClassIDList)):
        otherBingSet = set()
        for otherClusterID in range(0, len(clusterClassIDList)):
            if otherClusterID != clusterID:
                otherBingSet = otherBingSet |  set(clusterClassIDList[otherClusterID])
        differSet = set(clusterClassIDList[clusterID]) - otherBingSet
        buSetList.append(differSet)
        print "cluster: ", clusterID, "allLen:", len(clusterClassIDList[clusterID]), ", diffLen:", len(differSet), "  differSet: ", printSet(differSet, classID2NameDict)
        #print len(clusterClassIDList[clusterID]), ' ... ',clusterClassIDList[clusterID]

#C2 + C3 + C4 + CN
def getCombination(N):
    clusterIDList =  range(0, N)
    resList = list()
    for m in range(2, N + 1):
        from itertools import combinations
        # comoute m zuhe
        tmp = list(combinations(clusterIDList, m))
        resList.extend(tmp)
    return resList

#set operation: get all combination's jiaoSet
def genJiaoSet(clusterClassIDList, classID2NameDict):
    clusterCount = len(clusterClassIDList)
    allCombinations = getCombination(clusterCount)
    print "\nall combinations:\n", allCombinations
    for eachCombination in allCombinations:
        #eachCombination = (clusterID1, clusterID2, ...)
        #compute each combination's jiaoji
        tmpSet = set( clusterClassIDList[eachCombination[0]] )
        for eachClusterID in eachCombination:
            tmpSet = tmpSet & set( clusterClassIDList[eachClusterID] )
        print "cluster: ", eachCombination, " jiaoSet: ", printSet(tmpSet, classID2NameDict)
#process the clustering result
#python pro.py   clusterFileName.csv  featureVectorFileName.csv  classFileName.csv  OutmergeClusterFile.csv
if __name__ == '__main__':
    clusterFileName = sys.argv[1]
    featureVectorFileName = sys.argv[2]
    classFileName = sys.argv[3]
    outClusterFileName = sys.argv[4]

    classList = readCSV(classFileName)
    classID2NameDict = processClass(classList)
    fvList = readCSV(featureVectorFileName)
    fvList = processFeatureVec(fvList)
    clusterList = readCSV(clusterFileName)
    clusterList = processCluster(clusterList)

    #process the original cluster
    clusterList = mergeCluster(clusterList, fvList, len(classID2NameDict))
    writeCSV(clusterList, outClusterFileName)
    clusterClassIDList = trans2Set(clusterList)
    genBuSet(clusterClassIDList, classID2NameDict)
    genJiaoSet(clusterClassIDList, classID2NameDict)

    #process the new cluster
    print "\n\n\n"
    newClusterList = smoothCluster(clusterList)
    writeCSV(newClusterList, outClusterFileName + "new.csv")
    clusterClassIDList = trans2Set(newClusterList)
    genBuSet(clusterClassIDList, classID2NameDict)
    genJiaoSet(clusterClassIDList, classID2NameDict)