import os.path
import subprocess
import tqdm
import multiprocessing
import argparse

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--inputTable", required=True, help="Path to table giving paths to the VCF files in column 1 "
                                                          "and paths to the corresponding BAM files in column 2")
ap.add_argument("-u", "--uniqueStarts", type=int, default=3, help="Minimum number of unique starting positions for mutation - those with less will be removed (Default: 3)")
ap.add_argument("--readLen", type=int, default = 150, help="Length of Illumina reads (Default: 150)")
ap.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (Default: 10)")
ap.add_argument("-minC", "--minCoverage", type=int, default=15, help="Minimum coverage (Default: 15)")
ap.add_argument("-maxC", "--maxCoverage", type=int, default=47, help="Maximum coverage (Default: 47)")
ap.add_argument("-minMQ", "--minMappingQuality", type=int, default=90, help="Minumum mapping quality (Default: 90)")
ap.add_argument("-minGQ", "--minGenotypeQuality", type=int, default=90, help="Minumum genotype quality (Default: 90)")
args = vars(ap.parse_args())

# just for counting
readIndex = 0

# user-specified
threadNum = args["threads"]
print("thread:", threadNum)

vcfBam = args["inputTable"]

readLen = args["readLen"]
minCount = args["uniqueStarts"]
minQualRMS = args["minMappingQuality"]
minQualGenotype = args["minGenotypeQuality"]
minCov = args["minCoverage"]
maxCov = args["maxCoverage"]
sorSNP = 3
sorInDel = 10

varSet = set()
varDict = dict()
newVarSet = set()

# todo: write in log if pos < 75 and somehow catch if position +75 > ref file
#  make minCov and maxCov depending on averageCoverage
#  and change behavior midterm - currently the input is already pre-filtered
#  in terms of MQRankSum and so on
#  !! I do create the tables in here later on, so I can adjust the names


with open(vcfBam, "r") as link:
    tableBamDict = dict()
    for line in link:
        A = line.split("\t")
        tab = A[0] + ".tab"
        bam = A[1].strip()
        tableBamDict.update({tab: bam})
        filename = tab.split("/")[-1]
        dirPath = tab.replace(filename, "")

print("Step 1:\tCreate tables from VCF files if stills necessary\n")

pbar = tqdm.tqdm(total=len(tableBamDict.keys()))

for tabFile in tableBamDict.keys():

    pbar.set_description(desc=tabFile.split("/")[-1])

    # if table is not yet existing, create it
    if not os.path.isfile(tabFile):
        proc = subprocess.run(
            ["gatk", "VariantsToTable", "-V", tabFile.replace(".tab", ""),  "-O", tabFile, "-F", "CHROM", "-F", "POS", "-F", "ID", "-F", "QUAL", "-F",
             "SOR", "-F", "REF", "-F", "ALT", "-GF", "GT", "-GF", "AD", "-F", "DP", "-GF", "GQ", "-GF", "PL", "-F", "AMD"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    pbar.update()

pbar.update()
print("\nStep 2:\tParsing all tables files and extracting the unique variants.\n")

tablesPaths = tableBamDict.keys()
pbar1 = tqdm.tqdm(total=len(tablesPaths))

for path in tablesPaths:
    with open(path, "r") as table:

        pbar1.set_description(desc=path.split("/")[-1])

        prefix = path.split("/")[-1].split(".")[0]
        table.readline()

        for line in table:
            A = line.split("\t")

            chrom = A[0]
            pos = A[1]

            if int(pos) < readLen:
                continue

            qual = A[3]
            sor = A[4]
            ref = A[5]
            alt = A[6]

            if len(ref) == len(alt) == 1:
                sorLimit = sorSNP
            else:
                sorLimit = sorInDel

            cov = A[7]
            count = A[10].split(",")[0]
            gq = A[11]

            # variant is added to the set, then to the dict
            # if the variant was already in the dict, it was added at leat one prior time
            # --> discard this variant again from set, so that it will not be in the set any longer
            varSet.add((chrom, pos, ref, alt))
            if (chrom, pos, ref, alt) in varDict:
                varSet.discard((chrom, pos, ref, alt))

            varDict.update({(chrom, pos, ref, alt): (cov, qual, sor, count, gq, path)})
        pbar1.update()

print("\n"+str(len(varSet)) + " unique variants found.\n")
print("Step 3:\tFiltering those variants and creating BAM files.\n")


varList = list(varSet)

def func(varList):

    (chrom, pos, ref, alt) = varList

    (cov, qual, sor, count, gq, path) = varDict[(chrom, pos, ref, alt)]
    prefix = path.split("/")[-1].split(".")[0]

    bamfile = tableBamDict[path]

    if len(ref) == len(alt) == 1:
        sorLimit = sorSNP
    else:
        sorLimit = sorInDel

    if minCov <= float(cov) and float(cov) <= maxCov and float(qual) >= minQualRMS and float(sor) <= sorLimit and float(count) >= minCount and float(gq) >= minQualGenotype:
        region = chrom + ":" + str(int(pos) - readLen) + "-" + str(int(pos) + readLen)
        newName = dirPath + "extractedBams/" + prefix + "." + region + ".bam"
        subprocess.call(["samtools", "view", "-b", "-o", newName, bamfile, region])


subprocess.call(["mkdir", "-p", dirPath + "extractedBams"])

with multiprocessing.Pool(threadNum) as p:
    r = list(tqdm.tqdm(p.imap(func, varList), total=len(varList)))

