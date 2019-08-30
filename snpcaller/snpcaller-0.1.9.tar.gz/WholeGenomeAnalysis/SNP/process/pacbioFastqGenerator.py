import argparse
import os.path
import json
import csv
from pathlib import Path
from WholeGenomeAnalysis.SNP.model.PacBioObject import PacBioObject

def remove_non_ascii(text):
    return ''.join(i for i in text if ord(i)<128)

parser = argparse.ArgumentParser(description='Input for Snip program')

parser.add_argument("-i", "--inputcsv", help='input csv file with tab delimited', required=True, dest="inputcsv")
parser.add_argument("-o", "--output", help='output location', required=True, dest="output")

args = parser.parse_args()

with open(args.inputcsv, newline='') as csv_file:
    sequence_reader = csv.reader(csv_file, delimiter='\t')
    for line in sequence_reader:
        ExperimentName = remove_non_ascii(line[0])
        SampleName = line[1]
        BarcodeID = line[2]
        SequenceName = line[3]
        Sequence = line[4]
        ExperimentID = line[6]
        jName = line[7]
        experiment_foder = Path(args.output+'/'+ExperimentName+'/')
        data_folder = Path(args.output+'/'+ExperimentName+'/'+SampleName+'/')
        File_Path = Path(args.output + '/'+ExperimentName+'/' + SampleName + '/' + SampleName + '.fasta')
        jSon_Path = Path(args.output + '/'+ExperimentName+'/' + SampleName + '/' + SampleName + '.json')
        #file_to_open = data_folder / SampleName+'.fastq'

        #if "PGx" not in SampleName:
        #    continue

        if not os.path.exists(experiment_foder):
            os.mkdir(experiment_foder)

        if not os.path.exists(data_folder):
            os.mkdir(data_folder)

        #if not os.path.exists(jSon_Path):
        #    os.mkdir(data_folder)
        pbo = PacBioObject(jName, ExperimentName, SampleName, BarcodeID, ExperimentID)

        outF = open(File_Path, "a")
        outF.write('>'+SequenceName+"\n")
        outF.write(Sequence+"\n")
        outF.close()
        import json

        #with open(jSon_Path, 'w', encoding='utf-8-sig') as f:
        #    json.dump(pbo.__dict__, f, ensure_ascii=False)


        with open(jSon_Path, 'w', encoding='utf-8') as f:
            json.dump(pbo.__dict__, f, ensure_ascii=False, indent=4)

        #outF = open("myOutFile.txt", "w")

