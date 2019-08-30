import argparse
import os.path
from WholeGenomeAnalysis import reader
from WholeGenomeAnalysis import QualityCalculation as qualityCalculation

parser = argparse.ArgumentParser(description='Input for Snip program')

parser.add_argument("-j", "--jsonpath", help='input json file path (output json from the sample processor program', required=True, dest="jsonPath")

args = parser.parse_args()

if (os.path.exists(args.jsonPath)):
    print("File exist : " + args.jsonPath)
else:
    print("Missing bam json : " + args.jsonPath)
    exit()

jsonpath = args.jsonPath

qualityData = reader.JsonReader(jsonpath)
# copiedbam = copy.copy(bam)

# for snp in data['SNP']:
#     print('name : ' + snp['name'])

snpVersion = 151
targetSnpVersion = 1

rawbase='AG'
start=236
end=238

arrBases = list(rawbase)
#print(arrBases)
minBaseOcurrances ,minBasePercentages, minBaseQualityPercentage = qualityCalculation.getQuality(qualityData,rawbase,start,end)

print (minBaseOcurrances ,minBasePercentages, minBaseQualityPercentage )

#for amplicon in qualityData['Amplicon']:
#    for allele in amplicon['Allele']:
#        if (allele['SequenceName'] == "SNP#41#AMPL788534#1#596"):
#            for i in range(start, end):
#                print(i)
#                for k,v in allele['BaseOcurrances'].items():
#                    if(k==rawbase):
#                        x = v.split(",")
#                        print(x[i])
#                        break
#                for k,v in allele['BasePercentages'].items():
#                    if(k==rawbase):
#                        x = v.split(",")
#                        print(x[i])
#                        break
#                for k,v in allele['BaseQualityPercentage'].items():
#                    if(k==rawbase):
#                        x = v.split(",")
#                        print(x[i])
#                        break
            #print(allele['BaseOcurrances'])
            #print(allele['BaseQuality'])
            #print(allele['BasePercentages'])
            #print(allele['BaseQualityPercentage'])
            #print(allele['AverageQuality'])