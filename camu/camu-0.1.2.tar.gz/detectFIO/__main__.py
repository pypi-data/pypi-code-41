#!/usr/bin/env python
import numpy as np
import glob
import os
import multiprocessing
import sys
import time
import tqdm
import subprocess
import re
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True, help="Path to directory with BAM files")
ap.add_argument("-s", "--samples", required=True, help="Path to directory containing all samples' BAM files")
ap.add_argument("-t", "--table", required=True, help="Path to result score table from findDupAndLinked.py")
ap.add_argument("-o", "--output", default = None, help="Path for output table")
ap.add_argument("-m", "--minScore", type=float, default=0.1, help="Minimum score for CM to be included (Default: 0.1) ")
ap.add_argument("-u", "--uniqueStarts", type=int, default=3, help="Minimum number of unique starting positions for mutation variant - those with less will be removed (Default: 3)")
args = vars(ap.parse_args())


#dirPath = "/media/nicolas/Intenso/SamplesBam/"
dirPath=args["directory"]
#ResTablePath = "/home/nicolas/Documents/bamFiles/R1F-Bam/R1F.ScoreTable.tsv"
ResTablePath=args["table"]
#samples = glob.glob(dirPath + "*.bam")
samples=glob.glob(args["samples"] + "*.bam")

if not args["output"]:
    outpath=ResTablePath.replace(".tsv", "_afterFIO.tsv")
else:
    outpath=args["output"]

# will give the first found other sample for every CM
CM_sampleFindDict = dict((key, []) for key in samples)

minReads = args["uniqueStarts"]
threshold = args["minScore"]
CM_list = list()
remainingCM = dict()

# create indexes for all bam-files if not existing
for file in samples:
    if not os.path.isfile(file + ".bai"):
        print("Building index for " + file)
        proc = subprocess.run(["samtools",  "index", file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

with open (ResTablePath, "r") as table:
    # skip header
    table.readline()

    # add CM above threshold to list
    for line in table:
        A = line.split("\t")
        score = float(A[5])

        # go to next if score is below threshold
        if score <= threshold:
            continue
        else:
            name = A[0]
            if A[1] == "Insertion":
                CM_list.append((name, "I"))
                continue
            elif A[1] == "Deletion":
                CM_list.append((name, "D"))
                continue
            elif A[1] == "Mismatch":
                SNP_freq = []
                # get base and frequency
                B = A[2].split(",")
                B[-1].strip("\n")
                for i in range(len(B)//2):
                    SNP_freq.append((B[i*2].replace("'", ""), float(B[i*2+1])))

                # add SNP if minReads reached
                startPosNum = int(A[4])
                for entry in SNP_freq:
                    if entry[1] * startPosNum >= minReads:
                        CM_list.append((name, "M" + entry[0].replace(" ", "")))

print(len(CM_list))

pbar = tqdm.tqdm(total=len(CM_list))

# todo: take softclipped into account(-A)?

#CM_list = CM_list[:1]
#CM_list = [('R1F5.Crip3.0_scaffold21:101073-101373.bam', 'I')]
for CM in CM_list:

    pbar.set_description(desc=CM[0])
    pbar.update()

    #print(CM)
    name = CM[0]#.split("/")[-1]
    scaff = name.split(":")[0]
    scaff = scaff.split(".", 1)[1]
    posTemp = name.split(":")[1]
    posMin = int(posTemp.split("-")[0])
    posMax = int(posTemp.split("-")[1].replace(".bam", ""))
    pos = (posMax + posMin)//2

    for sample in samples:
        # check if Insertion in any read:
        proc = subprocess.run(["samtools",  "mpileup", "-A", sample, "-r", scaff+":"+str(pos)+"-"+str(pos)],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #print(str(proc.stdout))
        # sometimes the position is not included in the sample, then stdout equals "b''"
        if len(str(proc.stdout)) > 3:
            variants = (str(proc.stdout)[1:].replace("'", "").split("\\t"))[4]
        else:
            variants = ""

        # variable to check no single sample contained variant
        broke = False

        # skip own sample's file
        if CM[0].split(".")[0] == sample.split("/")[-1].split(".")[0]:
            continue
        # for the rest, look if insertion, deletion, SNP is included
        else:
            if CM[1] == "I":
                if "+" in variants:
                    currCMs = CM_sampleFindDict[sample]
                    currCMs.append(CM[0])
                    CM_sampleFindDict.update({sample:currCMs})
                    broke = True
                    break

            elif CM[1] == "D":
                if "-" in variants:
                    currCMs = CM_sampleFindDict[sample]
                    currCMs.append(CM[0])
                    CM_sampleFindDict.update({sample: currCMs})
                    broke = True
                    break
            # remaining are MT, MC, MA or MG
            else:
                if CM[1][1].lower() in variants.lower():
                    currCMs = CM_sampleFindDict[sample]
                    currCMs.append(CM[0])
                    CM_sampleFindDict.update({sample: currCMs})
                    broke = True
                    break
    # passed all samples
    if not broke:
        #print(CM[0], " passed")
        remainingCM.update({CM[0]:CM[1]})

#print(CM_sampleFindDict)
#print(len(remainingCM))
#for entry in sorted(remainingCM):
#    print(entry)

# rematch those that passed
with open (ResTablePath, "r") as table:
    # put header to output
    output = table.readline()

    for line in table:
        A = line.split("\t")
        score = float(A[5])
        name = A[0]

        # check if bam is still kept
        if name in remainingCM:
            # check mismatch-type
            if A[1] == "Insertion" and remainingCM[name] == "I":
                output += line
            elif A[1] == "Deletion" and remainingCM[name] == "D":
                output += line
            elif A[1] == "Mismatch" and remainingCM[name][0] == "M":
                output += line

with open(outpath, "w") as outfile:
    outfile.write(output)
