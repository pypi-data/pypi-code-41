# from WholeGenomeAnalysis.SNP.reader import reader
# import os
# import bamnostic as bs

from GenomeAnalysis.WholeGenomeAnalysis.SNP.model.AutoTypingResult import AutoTypingResult
from GenomeAnalysis.WholeGenomeAnalysis.SNP.model.Sample import Sample
from GenomeAnalysis.WholeGenomeAnalysis.SNP.model.Amplicon import Amplicon
from GenomeAnalysis.WholeGenomeAnalysis.SNP.model.Snp import Snp

# for j in range(1, 3):
#     venue1 = Amplicon()
#     venue1.set("rname" + str(j))
#
#     print('j' + str(j))
#
#     for i in range(j):
#         w1 = Snp(i, "seqName", 100, "SNP_0", "chrom", 1000, 1002, "refNCBI", "refUCSC", "observed", "AT", 100, 100, 95,"ACGTACGT")
#         w1.seqName = "SNP_" + str(i)
#         venue1.add(w1)
#         print('i' + str(i))
#
#     print(vars(venue1))
#     for sp in venue1.get():
#         print(vars(sp))


w1 = Snp(1, "seqName", 100, "SNP_0", "chrom", 1000, 1002, "refNCBI", "refUCSC", "observed", "AT", 100, 100, 95, "ACGTACGT")
w2 = Snp(1, "seqName", 100, "SNP_0", "chrom", 1000, 1002, "refNCBI", "refUCSC", "observed", "AT", 100, 100, 95, "ACGTACGT")
w3 = Snp(1, "seqName", 100, "SNP_0", "chrom", 1000, 1002, "refNCBI", "refUCSC", "observed", "AT", 100, 100, 95, "ACGTACGT")

w1.seqName = "SNP_1"
w2.seqName = "SNP_2"
w3.seqName = "SNP_3"

v1 = Amplicon("rname1")
# v1.set("rname1")

v1.add(w1)
v1.add(w2)

v2 = Amplicon("rname2")
# v2.set("rname2")

v2.add(w3)


x1 = Sample("experimentID", "experimentName", "plateName", "S1--S1")
x1.add(v1)

x2 = Sample("experimentID", "experimentName", "plateName", "S2--S2")
x2.add(v2)

y = AutoTypingResult("snpVersion", "targetSnpVersion")
y.add(x1)
y.add(x2)

print(vars(y))
for sample in y.get():
    print(vars(sample))

    for amplicon in sample.get():
        print(vars(amplicon))

        for snp in amplicon.get():
            print(vars(snp))


# print(vars(v1))
# for sp in v1.get():
#     print(vars(sp))
#
# print('------------- 1')
#
# print(vars(v2))
# for sp in v2.get():
#     print(vars(sp))
#
# print('------------- 2')

# filepath=r'C:\Users\seho\PycharmProjects\GenomeAnalysis\Documentation\SNP151.json'
# bampath=r'C:\Users\seho\PycharmProjects\GenomeAnalysis\Example\284169513\S284169513.bam'
# data=reader.snpJsonReader(filepath)
#
# for snp in data['SNP']:
#     print('name : ' + snp['name'])
#
# bam=bs.AlignmentFile(bampath, 'rb')
#
# #for sequence in bam:
# #    if(hasattr(sequence, 'reference_name')):
# #        print(sequence.reference_name)
#
# BlotName='NMP'
# SampleName='284169513'
# for sequence in bam:
#     if (hasattr(sequence, 'reference_name')):
#         start=sequence.pos
#         end=sequence.pos+len(sequence.seq)
#         for snp in data['SNP']:
#             if(snp['chrom'] == sequence.reference_name):
#                 chromStart=snp['chromStart']
#                 chromEnd=snp['chromEnd']
#                 if(start < chromStart < end and start < chromEnd < end):
#                     AmpliconName=sequence.query_name.split('#')[2]
#                     rawReads = sequence.query_name.split('#')[4]
#                     targetPositionStart=chromStart-start
#                     targetPositionEnd=chromEnd-start
#
#                     rawbases=sequence.seq[targetPositionStart:targetPositionEnd]
#                     print(BlotName+','+SampleName+','+AmpliconName+','+rawReads+','+snp['name']+','+snp['chrom']+','+str(chromStart)+','+str(chromEnd)+','+snp['refNCBI']+','+snp['refUCSC']+','+snp['observed']+','+rawbases)




