import bamnostic as bs
import argparse
import os.path
import json
import csv

from WholeGenomeAnalysis.SNP.model.AutoTypingResult import AutoTypingResult
from WholeGenomeAnalysis.SNP.model.Sample import Sample
from WholeGenomeAnalysis.SNP.model.Amplicon import Amplicon
from WholeGenomeAnalysis.SNP.model.SequenceObject import SequenceObject
from WholeGenomeAnalysis.SNP.model.Snp import Snp
from WholeGenomeAnalysis.SNP.process import CallSnip as callsnip
from WholeGenomeAnalysis.SNP.process import QualityCalculation as qualityCalculation
from WholeGenomeAnalysis.SNP.reader import reader as reader
from WholeGenomeAnalysis.SNP.writer import writer as write
# from WholeGenomeAnalysis.SNP.model.Vcf import Vcf
from WholeGenomeAnalysis.SNP.process import runConvert
from pathlib import Path

parser = argparse.ArgumentParser(description='Input for Snip program')

parser.add_argument("-s", "--snpJsonpath", help='input snp json file path', required=True, dest="snpJsonpath")
parser.add_argument("-j", "--jsonpath", help='input json file path (output json from the sample processor program', required=True, dest="jsonPath")
parser.add_argument("-b", "--bampath", help='input bam file path', required=True, dest="bamPath")
parser.add_argument("-o", "--outfolder", help='output folder location', required=True, dest="outfolder")
parser.add_argument("-v", "--vcf", help='vcf head information path', required=True, dest="vcfpath")

complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}

args = parser.parse_args()

if (os.path.exists(args.snpJsonpath)):
    print("File exist : " + args.snpJsonpath)
else:
    print("Missing json file : " + args.snpJsonpath)
    exit()

if (os.path.exists(args.bamPath)):
    print("File exist : " + args.bamPath)
else:
    print("Missing bam file : " + args.bamPath)
    exit()

if (os.path.exists(args.jsonPath)):
    print("File exist : " + args.jsonPath)
else:
    print("Missing bam json : " + args.jsonPath)
    exit()

if (os.path.exists(args.outfolder)):
    print("Folder exist : " + args.outfolder)
else:
    print("Created path : " + args.outfolder)
    os.mkdir(args.outfolder)

if (os.path.exists(args.vcfpath)):
    print("File exist : " + args.vcfpath)
else:
    print("Missing vcf header file : " + args.vcfpath)
    exit()


snpJsonpath = args.snpJsonpath
bamPath = args.bamPath
jsonpath = args.jsonPath

snpData = reader.JsonReader(snpJsonpath)
qualityData = reader.JsonReader(jsonpath)
bam = bs.AlignmentFile(bamPath, 'rb')

# copiedbam = copy.copy(bam)

# for snp in data['SNP']:
#     print('name : ' + snp['name'])

snpVersion = snpData['SNPVERSION']
targetSnpVersion = snpData['VERSION']
experimentID = qualityData['ExperimentID']
experimentName = qualityData['ExperimentName']
plateName = qualityData['PlateName']
sampleId = qualityData['SampleID']


# Create output path

#outputpath = args.outfolder+'/'+sampleId+'.csv'
#outputpath_vcf = args.outfolder+'/'+sampleId+'.vcf'

outputpath = Path(args.outfolder+'/'+sampleId+".csv")
outputpath_vcf = Path(args.outfolder+'/'+sampleId+".vcf")

print("output csv path : " + str(outputpath))
print("output vcf path : " + str(outputpath_vcf))

autoResult = AutoTypingResult(snpVersion, targetSnpVersion)
smpl = Sample(experimentID, experimentName, plateName, sampleId)

snip_dic = {}
snip_totalReads = {}

#with open(outputpath, mode='w', newline='') as csv_file:
#    fieldnames = ['experimentName', 'sampleId', 'seqName', 'rawReads', 'snpName', 'chrom', 'chromStart', 'chromEnd',
#                  'refNCBI', 'refUCSC', 'targeted', 'observed', 'minBaseOcurrances', 'minBasePercentages',
#                  'minBaseQualityPercentage']
#    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#    writer.writeheader()

for sequence in bam:
    if (hasattr(sequence, 'reference_name')):
        #if sequence.query_name.startswith('SNP'):
        arrObject = []

        start = sequence.pos
        end = sequence.pos + len(sequence.seq)
        if(sequence.flag == 16):
            strand = '-'
        else:
            strand = '+'

        sObject = SequenceObject(start,end,sequence.cigar,sequence.seq,sequence.reference_name)
        arrObject.append(sObject)

        xa=''
        if "XA" in sequence.tags:
            xa = sequence.tags.get("XA")[1]

        if(";" in xa):
            pair_list = xa.split(";")
            for pair in pair_list:
                if(pair != ''):
                    comma_list = pair.split(",")
                    newReferenceName=comma_list[0]
                    newstrand=comma_list[1][0:1]
                    newstart=int(comma_list[1][1:])
                    newend=int(comma_list[1][1:]) + len(sequence.seq)
                    newcigar=bs.utils.parse_cigar(comma_list[2])

                    if(strand == newstrand):
                        newSequence = sequence.seq
                    else:
                        newSequence = "".join(complement.get(base,base) for base in reversed(sequence.seq))

                    arrObject.append(SequenceObject(newstart,newend,newcigar,newSequence,newReferenceName))

        # print("1. reference_name: " + sequence.reference_name + " | 1. sequence.query_name: " + sequence.query_name)
        # print("1. sequence.read_name: " + sequence.read_name)
        # dt = {}
        print("Name : " + sequence.query_name)
        AmpliconName = sequence.query_name.split('#')[2]
        amp = Amplicon(AmpliconName)

        for matchObject in arrObject:
            matchStart, matchEnd, matchCigar, matchSeq, matchChr = matchObject.get()

            for snip in snpData['SNP']:
                if (snip['chrom'] == matchChr):

                    # print("2. reference_name: " + sequence.reference_name)v
                    # print("2. sequence.query_name: " + sequence.query_name)

                    chromStart = snip['chromStart']
                    chromEnd = snip['chromEnd']

                    if (matchStart < chromStart < matchEnd and matchStart < chromEnd < matchEnd):
                        # print("1. reference_name: " + sequence.reference_name + " | 1. sequence.query_name: " + sequence.query_name)

                        # AmpliconName = sequence.query_name.split('#')[2]
                        insertionCount = callsnip.CigarInsertionCount(matchCigar)
                        if (insertionCount > 10):
                            continue

                        rawReads = sequence.query_name.split('#')[4]
                        targetPositionStart = chromStart - matchStart
                        targetPositionEnd = chromEnd - matchStart
                        print("targetPositionStart : " + str(targetPositionStart) + " | targetPositionEnd: " + str(targetPositionEnd))
                        calStart, calend, baseMark= callsnip.CigarCalculation(targetPositionStart, targetPositionEnd, matchCigar)
                        print("start : " + str(calStart) + " | end: " + str(calend))
                        rawbases = matchSeq[calStart:calend]

                        if (baseMark == 'D'):
                            rawbases = '-'

                        if (calStart == calend and rawbases == ''):
                            rawbases = '-'

                        minBaseOcurrances, minBasePercentages, minBaseQualityPercentage = qualityCalculation.getQuality(qualityData, rawbases, calStart, calend, sequence.query_name)
                        #rawbases = sequence.seq[targetPositionStart:targetPositionEnd]

                        #snps = Snp(1, sequence.query_name, rawReads, snip['name'], snip['chrom'], chromStart, chromEnd,
                        #           snip['refNCBI'], snip['refUCSC'], snip['observed'], rawbases, minBaseOcurrances, minBasePercentages, minBaseQualityPercentage, sequence)

                        # dt.update(vars(snps))
                        # dt = json.dumps(dt)

                        #amp.add(snps)

                        snps = Snp(1, sequence.query_name, rawReads, snip['name'], snip['chrom'], str(chromStart), str(chromEnd),
                                   snip['refNCBI'], snip['refUCSC'], snip['observed'], rawbases, str(minBaseOcurrances), str(minBasePercentages), str(minBaseQualityPercentage), sequence)

                        if(snip['name'] in snip_dic):
                            dicSnipDetail = snip_dic[snip['name']]
                            if(rawbases in dicSnipDetail):
                                getSnip = dicSnipDetail[rawbases]

                                getSnip.rawReads = int(getSnip.rawReads)+int(snps.rawReads)
                                getSnip.minBaseOcurrances = int(getSnip.minBaseOcurrances) + int(snps.minBaseOcurrances)

                                if (getSnip.minBasePercentages > snps.minBasePercentages):
                                    getSnip.minBasePercentages = snps.minBasePercentages
                                if(getSnip.minBasePercentages > snps.minBasePercentages):
                                    getSnip.minBasePercentages = snps.minBasePercentages
                                if (getSnip.minBaseQualityPercentage > snps.minBaseQualityPercentage):
                                    getSnip.minBaseQualityPercentage = snps.minBaseQualityPercentage

                                #lstSnip.append(snps)
                                dicSnipDetail[rawbases] = getSnip
                            else:
                                #lstSnip = []
                                #lstSnip.append(snps)
                                dicSnipDetail[rawbases] = snps
                        else:
                            #lstSnip = []
                            dicSnipDetail = {}
                            #lstSnip.append(snps)
                            dicSnipDetail[rawbases]=snps
                            snip_dic[snip['name']] = dicSnipDetail

                        if( snip['name'] in snip_totalReads ):
                            snip_totalReads[snip['name']] = int(snip_totalReads[snip['name']])+int(rawReads)
                        else:
                            snip_totalReads[snip['name']] = int(rawReads)


                        #writer.writerow({'experimentName': experimentName, 'sampleId': sampleId, 'seqName': sequence.query_name, 'rawReads': rawReads, 'snpName': snip['name'], 'chrom': snip['chrom'], 'chromStart': str(chromStart), 'chromEnd': str(chromEnd), 'refNCBI': snip['refNCBI'], 'refUCSC': snip['refUCSC'], 'targeted': snip['observed'], 'observed': rawbases, 'minBaseOcurrances': str(minBaseOcurrances), 'minBasePercentages': str(minBasePercentages), 'minBaseQualityPercentage': str(minBaseQualityPercentage)})

                        print(experimentName + ',' + sampleId + ',' + sequence.query_name + ',' + rawReads + ',' + snip[
                            'name'] + ',' + snip['chrom'] + ',' + str(chromStart) + ',' + str(chromEnd) + ',' + snip[
                                  'refNCBI'] + ',' + snip['refUCSC'] + ',' + snip['observed'] + ',' + rawbases  + ',' + str(minBaseOcurrances) + ',' + str(minBasePercentages) + ',' + str(minBaseQualityPercentage))
                        isTargeted = True

            # AmpliconName = sequence.query_name.split('#')[2]
            # amp = Amplicon(AmpliconName)

            # if AmpliconName in AmpliconList:
            #     amp = AmpliconList[AmpliconName] # Get Amplicon object by AmpliconName
            #     amp.add(dt)

            #if isTargeted == True:
            #    smpl.add(amp)
            #else:
            #    print("None Target List: " + sequence.query_name)

final_snp_list = callsnip.filterSnipObject(snip_dic, snip_totalReads,0.05)
write.csvWriter(outputpath, final_snp_list, experimentName,sampleId)


converter = runConvert.Converter()
vcfs = converter.convert(final_snp_list, sampleId)
header = reader.VCFReader(args.vcfpath, sampleId)

write.TextWriter(outputpath_vcf, header)
write.VCFWriter(outputpath_vcf, vcfs)





# autoResult.add(smpl)
#
# autoResult.autoTyping_dic = {}
# autoResult.autoTyping_dic["snpVersion"] = autoResult.snpVersion
# autoResult.autoTyping_dic["targetSnpVersion"] = autoResult.targetSnpVersion
# autoResult.autoTyping_dic["sample"] = autoResult.sample_list
#
# Convert_Json = {
#     "autoTypingResult": autoResult.autoTyping_dic
# }
#
# jsonFormat = json.dumps(Convert_Json, indent=4)
# print(jsonFormat)

