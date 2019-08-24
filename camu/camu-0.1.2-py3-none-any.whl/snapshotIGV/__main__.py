#!/usr/bin/env python
import subprocess
import time
import tqdm
import math
import argparse

# Known issue: might have problems if IGV is not properly started yet - increase time.sleep

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--directory", required=True, help="Path to directory with BAM files")
ap.add_argument("-r", "--reference", required=True, help="Path to reference genome")
ap.add_argument("-t", "--table", required=True, help="Path to result score table after detectFIO.py")
ap.add_argument("-o", "--outputDirectory", required=True, help="Path to directory for IGV Snapshots")
args = vars(ap.parse_args())

bamFolder=args["directory"]
refFile=args["reference"]
filterTable=args["table"]
snapshotDir = args["outputDirectory"]

fileList = list()
with open(filterTable, "r") as nameFile:
    # skip header
    nameFile.readline()
    for line in nameFile:
        name = line.split("\t")[0]
        fileList.append(bamFolder + name)

with open(snapshotDir + "IGVBatchFile.txt", "w") as batchFile:
    batchFile.write('echo "new"\n')
    batchFile.write('sleep 2\n')
    batchFile.write('echo ' + '"' + 'genome ' + refFile + '"' + '\n')
    batchFile.write('sleep 2\n')
    batchFile.write('echo ' + '"' + 'snapshotDirectory ' + snapshotDir[:-1] + '"' + "\n")
    batchFile.write('sleep 2\n')
    batchFile.write('echo "maxPanelHeight 500"\n')
    batchFile.write('sleep 2\n')
    for file in fileList:
        batchFile.write('echo ' + '"' + 'load ' + file + '"' + '\n')
        position = file.split(".")[1] + "." + file.split(".")[2]
        batchFile.write('sleep 2\n')
        batchFile.write('echo ' + '"' + "goto " + position + '"' + "\n")
        batchFile.write('sleep 2\n')
        batchFile.write('echo "sort position"\n')
        batchFile.write('sleep 2\n')
        batchFile.write('echo "expand"\n')
        batchFile.write('sleep 2\n')
        batchFile.write('echo "snapshot"\n')
        batchFile.write('sleep 2\n')
        batchFile.write('echo "new"\n')
        batchFile.write('sleep 2\n')
    batchFile.write('echo "exit"')


proc = subprocess.Popen(["igv", ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def execute(cmd):
    popen = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

# IGV needs time to open up before the batch script can be started, so here I wait for 5 seconds
time.sleep(10)
cmd = "sh " + snapshotDir + "IGVBatchFile.txt" + "|nc 127.0.0.1 60151"
#ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
#output = ps.communicate()[0]
#print(output)

i = 0
pbar = tqdm.tqdm(total=len(fileList))
index_old = 0
for msg in execute(cmd):
    if "OK" in msg:
        try:
            index = math.floor((max(i, 8) - 8)/6)
            pbar.set_description(desc=fileList[index].split("/")[-1])
            i += 1
            if index > index_old:
                pbar.update()
            index_old = index
        except IndexError:
            print(msg)
pbar.update()


