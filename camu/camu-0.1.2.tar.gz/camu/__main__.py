#!/usr/bin/env python
import subprocess
import argparse

def main():
	ap = argparse.ArgumentParser()
#	ap.add_argument("-d", "--directory", required=True, help="Path to directory with BAM files")
#	ap.add_argument("-s", "--samples", required=True, help="Path to directory containing all samples' BAM files")
	ap.add_argument("-i", "--inputTable", required=True, help="Path to table giving paths to the VCF files in column 1 and paths to the corresponding BAM files in column 2")
	ap.add_argument("-c", "--control", required=True, help="Path to control BAM file")
	ap.add_argument("-r", "--reference", required=True, help="Path to reference genome")
	ap.add_argument("--readLen", type=int, default = 150, help="Length of Illumina reads (Default: 150)")
	ap.add_argument("-minC", "--minCoverage", type=int, default=15, help="Minimum coverage (Default: 15)")
	ap.add_argument("-maxC", "--maxCoverage", type=int, default=47, help="Maximum coverage (Default: 47)")
	ap.add_argument("-minMQ", "--minMappingQuality", type=int, default=90, help="Minumum mapping quality (Default: 90)")
	ap.add_argument("-minGQ", "--minGenotypeQuality", type=int, default=90, help="Minumum genotype quality (Default: 90)")
	ap.add_argument("-j", "--threads", type=int, default=10, help="Number of threads (Default: 10)")
	ap.add_argument("-m", "--minScore", type=float, default=0.1, help="Minimum score for CM to be included (Default: 0.1) ")
	ap.add_argument("-u", "--uniqueStarts", type=int, default=3, help="Minimum number of unique starting positions for mutation - those with less will be removed (Default: 3)")
	ap.add_argument("-v", "--variantRate", type=float, default=0.1, help="Variants occurring above this rate are treated as true variants in the control (Default=0.1)")
	args = vars(ap.parse_args())

	with open (args["inputTable"], "r") as inputFile:
		A = inputFile.readline().strip().split("\t")
		vcfFileName = A[0].split("/")[-1]
		bamFileName = A[1].split("/")[-1]
		args["directory"] = A[0].replace(vcfFileName, "") + "extractedBams/"
		args["samples"] = A[1].replace(bamFileName, "")
    
	print(args["directory"])
	print(args["samples"])
	table = args["directory"] + "ScoreTable.tsv"
	tableFIO = table.replace(".tsv", "_afterFIO.tsv")
	outputIGV = args["directory"] +"IGV"
	IGVSnap = outputIGV + "/snapshots/"
	IGVSessions = outputIGV + "/sessions/"

	# create directories for IGV output
	subprocess.call(["mkdir", "-p", outputIGV])
	subprocess.call(["mkdir", "-p", outputIGV + "/snapshots"])
	subprocess.call(["mkdir", "-p", outputIGV + "/sessions"])

	# call scripts
	subprocess.call(['python3', '-m', 'preprocessing', '-i', args["inputTable"], '-t', str(args["threads"]) , '--readLen', str(args["readLen"]), '-u', str(args["uniqueStarts"]), '-minC', str(args["minCoverage"]), '-maxC', str(args["maxCoverage"]), '-minGQ', str(args["minGenotypeQuality"]), '-minMQ', str(args["minMappingQuality"]), '-minC', str(args["minCoverage"])])
	subprocess.call(['python3', '-m', 'findDupAndLinked', '-d', args["directory"], '-c', args["control"] , '-t', str(args["threads"]), '-u', str(args["uniqueStarts"]), '-v', str(args["variantRate"])])
	subprocess.call(['python3', '-m','detectFIO', '-d', args["directory"], '-s', args["samples"], '-t', table, '-m', str(args["minScore"]), '-u', str(args["uniqueStarts"])])
	subprocess.call(['python3', '-m','IGVSessions', '-d', args["directory"], '-c', args["control"],  '-s', args["samples"], '-t', tableFIO, '-r', args["reference"], '-o', IGVSessions])
	subprocess.call(['python3', '-m','snapshotIGV', '-d', args["directory"], '-t', tableFIO, '-r', args["reference"], '-o', IGVSnap])

main()






