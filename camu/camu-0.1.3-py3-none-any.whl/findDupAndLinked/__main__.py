#!/usr/bin/env python
import numpy as np
import pysam
import glob
import multiprocessing
import sys
import time
import tqdm
from collections import Counter
import subprocess
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True, help="Path to directory with BAM files")
ap.add_argument("-o", "--output", default = None, help="Path for output table")
ap.add_argument("-c", "--control", required=True, help="Path to control BAM file")
ap.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (Default: 10)")
ap.add_argument("-u", "--uniqueStarts", type=int, default=3, help="Minimum number of unique starting positions for mutation - those with less will be removed (Default: 3)")
ap.add_argument("-v", "--variantRate", type=float, default=0.1, help="Variants occurring above this rate are treated as true variants in the control (Default=0.1)")
args = vars(ap.parse_args())


# just for counting
readIndex = 0

# user-specified
threadNum = args["threads"]
minReads = args["uniqueStarts"]
maxInDelLength = 2
variantThreshold = args["variantRate"]

control = args["control"]

base=args["directory"]
fileList = glob.glob(base+"*.bam")

if not args["output"]:
    output = base+"ScoreTable.tsv"
else:
	output = args["output"]
class read:

    startPos = -1   # steht drin
    CIGAR = ""

    def __init__(self, startPos, CIGAR, sequence, revComp):
        self.startPos = startPos  # -1 when using the samfile because it fits this way
        self.CIGAR = CIGAR
        self.deletions = set()    # aus CIGAR
        self.misMatches = set()   # aus RefSeq
        self.insertions = set()   # aus CIGAR
        self.hardclip = set()      # aus CIGAR
        self.softclip = set()     # aus CIGAR
        self.endPos = -1         # start + Matches und Deletions in CIGAR ! generell für insertions +1
        self.sequence = sequence
        self.refSeq = ""
        self.labels = []
        self.revComp = revComp  # bool if read is refComp

    def readOutCIGAR(self):
        # make string splittable

        cigar = self.CIGAR.replace("M", "M ")
        cigar = cigar.replace("D", "D ")
        cigar = cigar.replace("I", "I ")
        cigar = cigar.replace("H", "H ")
        cigar = cigar.replace("S", "S ")
        cigar = cigar.replace("N", "N ")
        cigar = cigar.replace("P", "P ")

        cigarList = cigar.split(" ")
        seqCounter = 0
        refCounter = self.startPos
        skipNext = False


        for entry in cigarList[:-1]:

            if entry[-1] == "M":
                for i in range(int(entry[:-1])):
                    self.refSeq += self.sequence[seqCounter]
                    seqCounter += 1
                    refCounter += 1

            elif entry[-1] == "D" or entry[-1] == "N":
                for i in range(int(entry[:-1])):
                    self.deletions.add(refCounter-1)
                    self.refSeq += "-"
                    refCounter += 1

            # Insertions are called for current AND next position
            elif entry[-1] == "I":
                for i in range(int(entry[:-1])):
                    self.insertions.add(refCounter-1)
                    seqCounter +=1

            elif entry[-1] == "S":
                for i in range(int(entry[:-1])):
                    self.softclip.add(refCounter)
                    seqCounter += 1

            elif entry[-1] == "H":
                for i in range(int(entry[:-1])):
                    self.hardclip.add(refCounter)

            elif entry[-1] == "P":
                print("Padding detected")
                seqCounter += 1

        self.endPos = refCounter

    def compareWithReference(self, refCoverage, refStart, NMs, controlDict):
        # printing to make sure
        #print(self.startPos - refStart)
        #print(self.CIGAR)
        #print(self.refSeq)
        #print(reference[self.startPos:self.endPos])

        # get candidate position
        midPos = refStart + len(refCoverage) // 2 - 1
        candMutPos = midPos - self.startPos

        for pos in range(max(0, self.startPos - refStart), min(len(refCoverage), self.endPos - refStart)):
            refCoverage[pos] += 1

        for i in range(len(self.refSeq)):
            try:
                if self.refSeq[i] not in controlDict[i + self.startPos+1] and controlDict[i + self.startPos+1] != "X":
                    #print(i+1)
                    #print(self.startPos)
                    #print(self.refSeq[i])
                    #print(controlDict[i+self.startPos+1])
                #if self.refSeq[i] != reference[i + self.startPos]:
                    if i-1 + self.startPos in self.deletions:
                        #print("deletion found")
                        continue
                    elif i + self.startPos in self.softclip:
                        #print("softclip found")
                        continue
                    elif i + self.startPos in self.hardclip:
                        #print("hardclip found")
                        continue
                    else:
                        self.misMatches.add(i + self.startPos)
                        # append Mismatch base + start position
                        if i == candMutPos:
                            if self.revComp:
                                NMs.append((self.refSeq[i], self.startPos + len(self.sequence)))
                            else:
                                NMs.append((self.refSeq[i], self.startPos))

            # not included in mpileup because control was not enough covered / bad quality
            # --> mismatch shouldn't be called here
            except KeyError:
                continue


        # remove InDels if present in control
        delTemp = set()
        for delPos in self.deletions:
            try:
                if "D" not in controlDict[delPos+1]:
                    delTemp.add(delPos)
            except KeyError:
                continue
        self.deletions = delTemp

        insTemp = set()
        for insPos in self.insertions:
            try:
                if "I" not in controlDict[insPos+1]:
                    insTemp.add(insPos)
            except KeyError:
                continue
        self.insertions = insTemp


        # make sure that softclipped positions do not account as mismatches
        # - normally should not happen due to if elif else above
        for position in self.softclip:
            if position > refStart and position < refStart + len(refCoverage):
                refCoverage[position - refStart] -= 1

        for position in self.deletions:
            if position > refStart and position < refStart + len(refCoverage):
                refCoverage[position - refStart] -= 1

        for position in self.hardclip:
            if position > refStart and position < refStart + len(refCoverage):
                refCoverage[position - refStart] -= 1

        global readIndex
        readIndex += 1

        # assign label
        if midPos in self.misMatches:
            self.labels.append("Mismatch")
        if midPos in self.insertions:
            self.labels.append("Insertion")
        if midPos in self.deletions:
            self.labels.append("Deletion")

        #print(readIndex, "\t",  refStart)

        #print("Mismatches:\t", self.misMatches)
        #print("Deletions:\t", self.deletions)
        #print("Insertions:\t", self.insertions)

class File:

    allReads = []
    scaffold = ""
    noOfReads = -1
    refStart = -1
    refEnd = -1
    refLength = -1
    refCoverage = []
    nonMatchMatrix = [[]]
    uniqueStartPosForSNP = set()
    uniqueStartPosForIns = set()
    uniqueStartPosForDel = set()
    indMaxCorrDictSNP = dict()
    indMaxCorrDictIns = dict()
    indMaxCorrDictDel = dict()
    NMs = list()



def buildResultTableHeader(currFile):
    resultTable = ["Filename\t" + "MutationType\t" + "SNPType\t" + "MaxCorrForSNP\t" + "NoUniqueStartPosForSNP\t" + "score"]
    return resultTable


def readCurrBamFile(inputfile, currFile):

    currFile.allReads = []
    currFile.scaffold = ""


    with pysam.AlignmentFile(inputfile, "rb") as samfile:

        # no .readline() for AlignmentFile, so I'm doing it the ugly way...
        for line in samfile:
            currFile.scaffold = samfile.get_reference_name(line.reference_id)
            break

        for line in samfile:
            A = str(line).split("\t")
            #print(A)
            # check bitwise flag to know if read is reverse complement
            revComp = False
            if int(A[1]) & 16:
                revComp = True

            startPos = int(A[3])
            CIGAR = A[5]
            sequence = A[9]

            currFile.allReads.append(read(startPos, CIGAR, sequence, revComp))
    return


def buildTable(bamfileName, currFile):

    # get refStart and refEnd
    refRange = bamfileName.split("_")[-1]
    refRange = refRange.split(".")[0]
    refRange = refRange.split(":")[1]
    currFile.refStart = int(refRange.split("-")[0])
    currFile.refEnd = int(refRange.split("-")[1])
    currFile.refLength = currFile.refEnd - currFile.refStart
    midPos = currFile.refLength//2 - 1

    # make sure that the CIGAR = None elements are not included
    currFile.allReads = [x for x in currFile.allReads if x.CIGAR != "None"]

    # List giving the coverage per position - used to correctly compute MM-ratio later on
    currFile.refCoverage = [0 for _ in range(currFile.refLength)]

    leftmostPos = float("inf")
    rightmostPos = 0

    for read in currFile.allReads:
        if read.startPos < leftmostPos:
            leftmostPos = read.startPos
        if read.startPos + len(read.sequence) > rightmostPos:
            rightmostPos = read.startPos + len(read.sequence)

    ##########################################

    name = bamfileName  # .split("/")[-1]
    scaff = name.split(":")[0]
    scaff = scaff.split(".", 1)[1]

    proc = subprocess.run(
        ["samtools", "mpileup", "-A", control, "-r", scaff + ":" + str(leftmostPos-1) + "-" + str(rightmostPos+1)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    mpileup = str(proc.stdout).split("\\n")[:-1]
    controlDict = dict()

    for entry in mpileup:
        pos = int(entry.split("\\t")[1])
        count = int(entry.split("\\t")[3])
        bases = entry.split("\\t")[4].upper()

        limit = int(np.floor(count * 0.1))
        consensus = "X"
        if bases.count("A") > limit:
            consensus += "A"
        if bases.count("C") > limit:
            consensus += "C"
        if bases.count("G") > limit:
            consensus += "G"
        if bases.count("T") > limit:
            consensus += "T"
        if bases.count("+") > limit:
            consensus += "I"
        if bases.count("-") > limit:
            consensus += "D"

        controlDict.update({pos: consensus})

    #print(controlDict)

    ##########################################

    # reset non-match list
    currFile.NMs = list()
    for read in currFile.allReads:
        read.readOutCIGAR()
        read.compareWithReference(currFile.refCoverage, currFile.refStart, currFile.NMs, controlDict)

    # build read-nonMatch-Matrix and startPositions-list

    currFile.nonMatchMatrix = [[0 for _ in range(currFile.refLength)] for _ in range(len(currFile.allReads))]

    # these vectors contain 1 at position i if i-th read contained misMatch/Ins/Del at midPos
    misMatchVector = []
    insertionVector = []
    deletionVector = []

    for i in range(len(currFile.allReads)):
        misMatchVector.append(0)
        insertionVector.append(0)
        deletionVector.append(0)
        for position in currFile.allReads[i].misMatches:
            if position >= currFile.refStart and position < currFile.refEnd:
                currFile.nonMatchMatrix[i][position - currFile.refStart] = 1
                if position == currFile.refStart + midPos:
                    misMatchVector[i] = 1
        for position in currFile.allReads[i].insertions:
            if position >= currFile.refStart and position < currFile.refEnd:
                currFile.nonMatchMatrix[i][position - currFile.refStart] = 1
                if position == currFile.refStart + midPos:
                    insertionVector[i] = 1
        for position in currFile.allReads[i].deletions:
            if position >= currFile.refStart and position < currFile.refEnd:
                currFile.nonMatchMatrix[i][position - currFile.refStart] = 1
                if position == currFile.refStart + midPos:
                    deletionVector[i] = 1

    # count unique startPos for all midSNP-containing reads
    currFile.uniqueStartPosForSNP = set()
    currFile.uniqueStartPosForIns = set()
    currFile.uniqueStartPosForDel = set()

    for read in currFile.allReads:
        if "Mismatch" in read.labels:
            if read.revComp:
                currFile.uniqueStartPosForSNP.add(read.startPos + len(read.sequence))
            else:
                currFile.uniqueStartPosForSNP.add(read.startPos)
        if "Insertion" in read.labels:
            if read.revComp:
                currFile.uniqueStartPosForIns.add(read.startPos + len(read.sequence))
            else:
                currFile.uniqueStartPosForIns.add(read.startPos)
        if "Deletion" in read.labels:
            if read.revComp:
                currFile.uniqueStartPosForDel.add(read.startPos + len(read.sequence))
            else:
                currFile.uniqueStartPosForDel.add(read.startPos)

    # make list of those mutationTypes that should be further processed
    # (having at least minReads unique startPositions)
    validMutTypes = []

    if len(currFile.uniqueStartPosForSNP) >= minReads:
        validMutTypes.append("Mismatch")

    if len(currFile.uniqueStartPosForIns) >= minReads:
        validMutTypes.append("Insertion")

    if len(currFile.uniqueStartPosForDel) >= minReads:
        validMutTypes.append("Deletion")

    # if validMutTypes is empty no kind of mutation got minReads-times uniqueStartPosition
    # --> return empty list so that following steps are skipped
    if not validMutTypes:
        return validMutTypes

    # extract positions with misMatches or indDels
    ind = []
    for i in range(len(currFile.nonMatchMatrix[0])):
        for j in range(len(currFile.nonMatchMatrix)):
            if 1 == currFile.nonMatchMatrix[j][i]:
                ind.append(i)
                break

    # make copies of ind and manipulate if necessary
    indSNP = ind.copy()
    indIns = ind.copy()
    indDel = ind.copy()

    # if 1 not in Vector, than for no read the midPos was mismatched/inserted/deleted
    if 1 not in misMatchVector:
        indSNP.remove(midPos)
    if 1 not in insertionVector:
        indIns.remove(midPos)
    if 1 not in deletionVector:
        indDel.remove(midPos)

    # because InDel can be longer than one position,
    # the neighboring positions are not included for correlation
    inDelStart = midPos - maxInDelLength // 2
    inDelEnd = midPos + maxInDelLength // 2

    for position in range(inDelStart, inDelEnd+1):
        if position != midPos:
            if position in indIns:
                indIns.remove(position)
            if position in indDel:
                indDel.remove(position)

    newMatrixSNP = []
    newMatrixIns = []
    newMatrixDel = []


    nonTrans = np.transpose(currFile.nonMatchMatrix)
    nonTransSNP = nonTrans.copy()
    nonTransSNP[midPos] = misMatchVector
    nonTransIns = nonTrans.copy()
    nonTransIns[midPos] = insertionVector
    nonTransDel = nonTrans.copy()
    nonTransDel[midPos] = deletionVector

    for index in indSNP:
        newMatrixSNP.append(nonTransSNP[index])
    for index in indIns:
        newMatrixIns.append(nonTransIns[index])
    for index in indDel:
        newMatrixDel.append(nonTransDel[index])

    # if there are no mismatches except for the midSNP, a correlation of 0 can be assigned
    if len(newMatrixSNP) <= 1:
        currFile.indMaxCorrDictSNP = {currFile.refLength//2-1: 0}
    else:
        corrMatrixSNP = np.corrcoef(newMatrixSNP)
        currFile.indMaxCorrDictSNP = dict()

        for i in range(len(corrMatrixSNP)):
            corrMatrixSNP[i][i] = 0
            currFile.indMaxCorrDictSNP.update({indSNP[i]: np.max(corrMatrixSNP[i])})

    if len(newMatrixIns) <= 1:
        currFile.indMaxCorrDictIns = {currFile.refLength//2-1: 0}
    else:
        corrMatrixIns = np.corrcoef(newMatrixIns)
        currFile.indMaxCorrDictIns = dict()

        for i in range(len(corrMatrixIns)):
            corrMatrixIns[i][i] = 0
            currFile.indMaxCorrDictIns.update({indIns[i]: np.max(corrMatrixIns[i])})
    if len(newMatrixDel) <= 1:
        currFile.indMaxCorrDictDel = {currFile.refLength//2-1: 0}
    else:
        corrMatrixDel = np.corrcoef(newMatrixDel)
        currFile.indMaxCorrDictDel = dict()

        for i in range(len(corrMatrixDel)):
            corrMatrixDel[i][i] = 0
            currFile.indMaxCorrDictDel.update({indDel[i]: np.max(corrMatrixDel[i])})

    return validMutTypes


def appendResultTable(bamfileName, resultTable,
                      refLength, currFile, label="None"):

    if label == "Mismatch":
        indMaxCorrDict = currFile.indMaxCorrDictSNP
        uniqueStartPos = currFile.uniqueStartPosForSNP
    if label == "Insertion":
        indMaxCorrDict = currFile.indMaxCorrDictIns
        uniqueStartPos = currFile.uniqueStartPosForIns
    if label == "Deletion":
        indMaxCorrDict = currFile.indMaxCorrDictDel
        uniqueStartPos = currFile.uniqueStartPosForDel

    resultTable.append(bamfileName.split("/")[-1] + "\t" + label)


    # get base ratios
    if label == "Mismatch":
        NM_set = set(currFile.NMs)
        nm_len = len(NM_set)
        NM_list = list(NM_set)
        baseCount = list()
        for base, start in NM_list:
            baseCount.append(base)
        baseCounter = Counter(baseCount)
        baseFreqTemp = [["G", baseCounter["G"]/nm_len],
                    ["A", baseCounter["A"]/nm_len],
                    ["T", baseCounter["T"]/nm_len],
                    ["C", baseCounter["C"]/nm_len]]
        baseFreq = list()
        for sublist in baseFreqTemp:
            if sublist[1] > 0.0:
                baseFreq.extend(sublist)
        baseFreq = str(baseFreq).replace("\n", "").replace("[", "").replace("]", "")
    else:
        baseFreq = " "
    resultTable[-1]+=("\t" + baseFreq)

    #Corr
    if refLength//2-1 in indMaxCorrDict.keys():
        resultTable[-1] += "\t" + str(indMaxCorrDict[refLength//2-1])
    else:
        resultTable[-1] += "\t0"

    resultTable[-1] += ("\t" + str(len(uniqueStartPos)))

    score = np.log10(len(uniqueStartPos)) * (1 - indMaxCorrDict[refLength//2-1])
    resultTable[-1] += ("\t" + str(score))
    return resultTable


def func(fileList):#, results, index):

    firstIteration = True


    # iterate trough all .bam-Files in given directory
    for bamfileName in fileList:

        pbar.set_description(desc= bamfileName.split("/")[-1])
        pbar.update()

        # create new File-object for the current file
        currFile = File()

        # extract the information given in the filename
        try:
            posRange = bamfileName.split(".")
            posRange = posRange[2].split("_")
            posRange = posRange[1].split("-")
            endPos = int(posRange[1])
            posRange = posRange[0].split(":")
            startPos = int(posRange[1])
        except IndexError:
            with open (base + "errors.log", "a") as log:
                log.write(bamfileName + ":\tFilename not valid\n")
            continue

        # read the file
        try:
            readCurrBamFile(bamfileName, currFile)
        except OSError:
            with open (base + "errors.log", "a") as log:
                log.write(bamfileName + ":\tError when reading file\n")
            continue

        # use function buildTable to extract coverage per position, mismatch per position
        try:
            validMutTypes = buildTable(bamfileName, currFile)
        except ValueError:
            with open(base + "errors.log", "a") as log:
                log.write(bamfileName, ":\tInvalid CIGAR string detected\n")
            continue

        if firstIteration:
            resultTable = buildResultTableHeader(currFile)
            firstIteration = False

        if not validMutTypes:
            with open(base + "removed.log", "a") as log:
                log.write(bamfileName.split("/")[-1] + "\n")

        for label in validMutTypes:
            resultTable = appendResultTable(bamfileName, resultTable, currFile.refLength, currFile, label)


        #for entry in resultTable:
        #    print(entry)
    #results[index] = resultTable
    return resultTable

# clear log
with open(base + "removed.log", "w") as log:
    log.write(time.asctime(time.localtime(time.time())) + "\n")
    log.write("Directory name:\t" + base + "\n")
    log.write("Excluded - number of unique start positions < " + str(minReads) + ":\n")

with open(base + "errors.log", "w") as log:
    log.write(time.asctime(time.localtime(time.time())) + "\n")
    log.write("Directory name:\t" + base + "\n")
    log.write("Errors:\n")


# Make it parallel
#fileList = fileList[:20]

pbar = tqdm.tqdm(total=len(fileList))

n = len(fileList)//threadNum
p = multiprocessing.Pool(threadNum)
res = p.map(func, [fileList])
p.close()

resultTable = res
#print(log)

with open(output, "w") as outfile:
    for row in resultTable[0]:
        outfile.write(str(row) + "\n")


