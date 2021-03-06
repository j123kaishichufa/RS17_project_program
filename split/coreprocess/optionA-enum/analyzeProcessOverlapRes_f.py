import sys
import csv

CLASSNAME2IDDict = dict()
CLASSID2NAMEDict = dict() #[classID] = className
CLASSID2CLUSTERDict = dict() #[classID] = list[clusterID]
CLUSTERID2CLASSDict = dict() #[clusterID] = list[classID]

CLUSTERID2TSDict = dict() #[clusterID] = [testcaseID1, id2, ..]
TSID2NAMEDict = dict()   #[testcaseID] = testcaseName


TRACEList = list()  #[traceID] = list()=[ edgeID1, edgeID2 ...]
METHODList = list()  #[methodID] = METHOD()
EDGEList = list()   #[edgeID] = EDGE()
EDGEDict = dict()  #dict[methodID1][methodID2] = edgeID

class MethodNode:
    def __init__(self, ID, justname, longname, shortname, className, parameter, returnType):
        self.ID = ID
        self.justname = justname
        self.longname = longname #has paralist
        self.shortname = shortname #has paralist
        self.className = className
        self.parameter = parameter
        self.returnType = returnType

class MethodEdge:
    def __init__(self, startID, endID):
        self.startID = startID
        self.endID = endID

# methodname_full.(prafulltype, parafulltype)
def getLongName(methodName, para):
    if para == '':
        post = '()'
    else:
        post = '(' + para + ')'
    return methodName + post

#paraList = ['A.B.C', 'D.E.F'], return ['B.C','E.F']
def getShortParaList(paraList):
    oneList = list()
    for para in paraList:
        arr = para.split('.')
        if len(arr) > 2:
            shortname = arr[len(arr) - 2] + '.' + arr[len(arr) - 1]
        else:
            shortname = para
        oneList.append(shortname)
    return oneList


# methodname_short(prashorrtype, parashottype)
def getShortName(methodName, para):
    arr = methodName.split('.')
    if len(arr) >= 2:
        shortname = arr[len(arr) - 2] + '.' + arr[len(arr) - 1]
    else:
        shortname = methodName

    if para == '':
        post = '()'
    else:
        paraList = para.split(',')
        shortParaList = getShortParaList(paraList)
        post = '('  + ','.join(shortParaList) + ')'
    return shortname + post


#return TRACEList
# methodNodeList,    methodEdgeList. egdeDict
def readWorkflowFile(filename):
    global TRACEList
    global METHODList
    global EDGEList
    global EDGEDict

    methodIndex = 0
    edgeIndex = 0
    tmpMethodDict = dict() #dict(methodname) = ID
    tmpClassDict = dict()  #dict(className) = ID

    with open(filename, "r", newline="") as fp:
        reader = csv.reader(fp)
        for each in reader:
            #print each
            [traceID, order, structtype, startMethodName, endMethodName, m1_para, m2_para, class1, class2, m1_return, m2_return, weight] = each
            if traceID == 'traceID':
                continue
            startLongName = getLongName(startMethodName, m1_para)
            endLongName = getLongName(endMethodName, m2_para)
            startShortName = getShortName(startMethodName, m1_para)
            endShortName = getShortName(endMethodName, m2_para)
            if startLongName not in tmpMethodDict:
                tmpMethodDict[startLongName] = methodIndex
                oneMethod = MethodNode(methodIndex, startMethodName, startLongName, startShortName, class1, m1_para, m1_return)
                METHODList.append(oneMethod)
                methodIndex += 1
            if endLongName not in tmpMethodDict:
                tmpMethodDict[endLongName] = methodIndex
                oneMethod = MethodNode(methodIndex, endMethodName, endLongName, endShortName, class2, m2_para, m2_return)
                METHODList.append(oneMethod)
                methodIndex += 1

            startID = tmpMethodDict[startLongName]
            endID = tmpMethodDict[endLongName]
            if startID not in EDGEDict:
                EDGEDict[startID] = dict()
            if endID not in EDGEDict[startID]:
                EDGEDict[startID][endID] = edgeIndex
                oneEdge = MethodEdge(startID, endID)
                EDGEList.append(oneEdge)
                edgeIndex += 1

            edgeID = EDGEDict[startID][endID]
            currentLen = len(TRACEList)
            if int(traceID) == currentLen:
                TRACEList.append(list())
            TRACEList[int(traceID)].append(edgeID)


def isInterEdge(startID, endID):
    global CLASSNAME2IDDict
    global CLASSID2CLUSTERDict
    global METHODList


    className1 = METHODList[startID].className
    className2 = METHODList[endID].className
    #print 'methodName1=',METHODList[startID].justname, 'methodName2=',METHODList[endID].justname
    #print 'className1=',className1, 'className2=',className2
    classID1 = -1
    classID2 = -1
    clusterIDList1 = list()
    clusterIDList2 = list()
    if className1 in CLASSNAME2IDDict:
        classID1 = CLASSNAME2IDDict[className1]
    if className2 in CLASSNAME2IDDict:
        classID2 = CLASSNAME2IDDict[className2]
    if classID1 != -1:
        clusterIDList1 = CLASSID2CLUSTERDict[classID1]
    if classID2 != -1:
        clusterIDList2 = CLASSID2CLUSTERDict[classID2]
    '''
    if classID1 != -1:
        print 'classID1=', classID1
    if classID2 != -1:
        print 'classID2=', classID2
    '''
    if classID1 == -1:
        return False
    if classID2 == -1:
        return False
    if classID1 != -1 and classID2 != -1:
        set1 = set(clusterIDList1)
        set2 = set(clusterIDList2)
        if len(set1 & set2) != 0:
            return False
    return True



#operate TRACEList[traceID]=[edgeID1, edgeID2]
#generate res[traceID][interedgeID] = count
# not process fv=0 cluster, beacuse it is not in CLUSTERID2CLASSDict
def filterOutInterEdge():
    global TRACEList
    global EDGEList

    resDict = dict()  #dict[traceID][interEdgeID] = count
    for traceID in range(0, len(TRACEList)):
        #print 'traceID=', traceID
        for edgeID in TRACEList[traceID]:
            #print 'edgeID=', edgeID
            startMethodID = EDGEList[edgeID].startID
            endMethodID = EDGEList[edgeID].endID
            isCross = isInterEdge(startMethodID, endMethodID)
            if isCross == True:
                #print 'True'
                if traceID not in resDict:
                    resDict[traceID] = dict()
                if edgeID not in resDict[traceID]:
                    resDict[traceID][edgeID] = 1
                else:
                    resDict[traceID][edgeID] += 1
    return resDict

#generate res[traceID][interedgeID] = count
def workflowMetric(interDict):
    global TSID2NAMEDict
    interComWfCount = 0 # workflow number which need inter-omponent communication
    withinComWfCount = 0 #  ..............which not need inter-omponent communication
    interCallCount = 0   #sum up interCallCount in allworkflow
    interCallCount_avg = 0 #interCallCount per allworkflow
    interCallCount_f = 0
    interCallCount_avg_f = 0

    interComWfCount = len(interDict)
    withinComWfCount = len(TSID2NAMEDict) - interComWfCount
    tmpList = list()
    for traceID in interDict:
        keyList = interDict[traceID].keys()  #interEdgeIDList
        tmpList.append(len(keyList))
    interCallCount =sum(tmpList)
    if len(tmpList) != 0:
        interCallCount_avg = interCallCount / float(len(tmpList))
    else:
        interCallCount_avg = 0.0

    tmpList = list()
    for traceID in interDict:
        valueList = interDict[traceID].values()  #interEdgeCountList
        tmpList.append(sum(valueList))
    interCallCount_f =sum(tmpList)
    if len(tmpList) != 0:
        interCallCount_avg_f = interCallCount_f / float(len(tmpList))
    else:
        interCallCount_avg_f = 0.0
    #print interComWfCount, withinComWfCount, interCallCount, interCallCount_avg, interCallCount_f, interCallCount_avg_f
    return interComWfCount, withinComWfCount, interCallCount, interCallCount_avg, interCallCount_f, interCallCount_avg_f


def getClustersofClass(classID):
    global CLUSTERID2CLASSDict
    resList = list()
    for clusterID in CLUSTERID2CLASSDict:
        classIDList = CLUSTERID2CLASSDict[clusterID]
        if classID in classIDList:
            resList.append(clusterID)
    return resList

def isInitMethod(methodID):
    global METHODList
    methodName = METHODList[methodID].justname
    if '.<init>' in methodName:
        return True
    else:
        return False


# -1 => yourself.
# other-> -1 is your provided private API
# other-> your is your provided PrivateAPI
#generate res[clusterID][apiID] = 1 in case the api is repetitive
def extractAPI(interDict):
    global CLASSNAME2IDDict
    global METHODList
    global EDGEList

    clusterAPIDict = dict()  #dict[cluserID] = [uniqueCalleeMethodID1, 2, ...]
    for traceID in interDict:
        #print 'traceID=', traceID,
        for interEdgeID in interDict[traceID]:
            #print 'interEdgeID=', interEdgeID,
            oneEdge = EDGEList[interEdgeID]
            className2 = METHODList[oneEdge.endID].className
            #print 'className2=',className2,
            if className2 in CLASSNAME2IDDict:
                classID2 = CLASSNAME2IDDict[className2]
                #print 'classID=',classID2,
                itsClusterIDList = getClustersofClass(classID2)

                for eachClusterID in itsClusterIDList:
                    if eachClusterID not in clusterAPIDict:
                        clusterAPIDict[eachClusterID] = dict()
                    if isInitMethod(oneEdge.endID) == False and (oneEdge.endID not in clusterAPIDict[eachClusterID]):
                        clusterAPIDict[eachClusterID][oneEdge.endID] = 1

    return clusterAPIDict

# clusterAPIDict[clusterID][apiID] = 1
def APIMetric(clusterAPIDict):
    #print clusterAPIDict
    APICount = 0
    APICount_avg = 0 #api count /clusterNum
    for clusterID in clusterAPIDict:
        APIList = clusterAPIDict[clusterID].keys()
        APICount += len(APIList)
    if len(clusterAPIDict) != 0:
        APICount_avg = APICount / float(len(clusterAPIDict))
    else:
        APICount_avg = 0
    return APICount, APICount_avg


def readOverlapResFile(fileName):
    classID2NameDict = dict()
    className2IDDict = dict()
    classID2ClusterDict = dict()
    clusterID2ClassDict = dict()
    with open(fileName, 'r', newline="") as fp:
        reader = csv.reader(fp)
        for each in reader:
            [classID, className, clusterID] = each
            if classID == 'classID':
                continue
            classID = int(classID)
            clusterID = int(clusterID)
            if classID not in classID2NameDict:
                classID2NameDict[classID] = className
                className2IDDict[className] = classID

            if classID not in classID2ClusterDict:
                classID2ClusterDict[classID] = list()
            classID2ClusterDict[classID].append(clusterID)

            if clusterID not in clusterID2ClassDict:
                clusterID2ClassDict[clusterID] = list()
            clusterID2ClassDict[clusterID].append(classID)
    #print 'classID2NameDict:' ,classID2NameDict
    #print 'classID2ClusterDict:', classID2ClusterDict
    #print 'clusterID2ClassDict:', clusterID2ClassDict
    return classID2NameDict, className2IDDict, classID2ClusterDict, clusterID2ClassDict


def readTestCaseClusterFile(fileName):
    clusterID2TsDict = dict()
    tsID2NameDict = dict()
    with open(fileName, 'r', newline="") as fp:
        reader = csv.reader(fp)
        for each in reader:
            [clusterID, testcaseID, testcaseName] = each
            clusterID = int(clusterID)
            testcaseID = int(testcaseID)
            if clusterID not in clusterID2TsDict:
                clusterID2TsDict[clusterID] = list()
            clusterID2TsDict[clusterID].append(testcaseID)

            if testcaseID not in tsID2NameDict:
                tsID2NameDict[testcaseID] = testcaseName
    return clusterID2TsDict, tsID2NameDict


#return clusterNum, noZeroFvClusterNum,  repeatClassNum,  repeatCount/repeatClassNum
def basicMetric():
    global CLASSID2CLUSTERDict
    global CLUSTERID2CLASSDict
    totalClusterNum = max(CLUSTERID2CLASSDict.keys()) + 1
    noZeroClusterNum = len(CLUSTERID2CLASSDict)

    repeatClassDict = dict()  #classID, repeatCount
    for classID in CLASSID2CLUSTERDict:
        clusterIDList = CLASSID2CLUSTERDict[classID]
        if len(clusterIDList) > 1:
            repeatClassDict[classID] = len(clusterIDList)
    if len(repeatClassDict) == 0:
        repeatAvg = 0
    else:
        repeatAvg = round(sum(repeatClassDict.values()) / float(len(repeatClassDict)), 5)
    repeatNum = len(repeatClassDict)

    return totalClusterNum, noZeroClusterNum, repeatNum, repeatAvg


#python pro.py
#coreprocess/processOverlap/jforum219Testcase1_clusters_0.03csv
#coreprocess/testcaseClusteirng/jforum219Testcase1_jm_AVG_20.csv
#workflow/jforum219_workflow_reduced.csv
'''
if __name__ == '__main__':
    overlapResFileName = sys.argv[1]  #[classID, className, clusterID ]
    testcaseClusterFileName = sys.argv[2] #[clusterID, testcaseID, testcaseName]
    workflowFileName = sys.argv[3]
    #apiFileName = sys.argv[4]
'''
def analyzeProcessOverlapRes(overlapResFileName,  testcaseClusterFileName, workflowFileName):
    global CLASSNAME2IDDict
    global CLASSID2NAMEDict
    global CLASSID2CLUSTERDict
    global CLUSTERID2CLASSDict
    global CLUSTERID2TSDict
    global TSID2NAMEDict
    global TRACEList
    global METHODList
    global EDGEList
    global EDGEDict

    CLASSNAME2IDDict = dict()
    CLASSID2NAMEDict = dict()
    CLASSID2CLUSTERDict = dict()
    CLUSTERID2CLASSDict = dict()
    CLUSTERID2TSDict = dict()
    TSID2NAMEDict = dict()
    TRACEList = list()
    METHODList = list()
    EDGEList = list()
    EDGEDict = dict()

    [CLASSID2NAMEDict, CLASSNAME2IDDict, CLASSID2CLUSTERDict, CLUSTERID2CLASSDict] = readOverlapResFile(overlapResFileName)
    [CLUSTERID2TSDict, TSID2NAMEDict] = readTestCaseClusterFile(testcaseClusterFileName)
    #print CLUSTERID2TSDict
    #print TSID2NAMEDict

    #return TRACEList
    # methodNodeList,    methodEdgeList. egdeDict
    readWorkflowFile(workflowFileName)
    #print 'TRACEList', TRACEList
    #print 'METHODList', METHODList
    #print 'EDGEDict', EDGEDict
    [totalClusterNum, noZeroClusterNum, repeatClassNum, repeatClassAvg] = basicMetric()

    #operate TRACEList[traceID]=[edgeID1, edgeID2]
    #generate res[traceID][interedgeID] = count
    interTsEdgeDict = filterOutInterEdge()
    #print 'interTsEdgeDict=',interTsEdgeDict
    [interComWfCount, withinComWfCount, interCallCount, interCallCount_avg, interCallCount_f, interCallCount_avg_f] = workflowMetric(interTsEdgeDict)
    clusterAPIDict = extractAPI(interTsEdgeDict)
    (APICount, APICount_avg) = APIMetric(clusterAPIDict)


    resList = list()
    resList.extend([totalClusterNum, noZeroClusterNum, repeatClassNum, repeatClassAvg])
    resList.extend([interComWfCount, withinComWfCount, interCallCount, interCallCount_avg, interCallCount_f, interCallCount_avg_f])
    resList.extend([APICount, APICount_avg])

    resStrList = [str(each) for each in resList]
    strstr = ','.join(resStrList)
    #print 'analyze overlapResult metric:', strstr
    return resList
