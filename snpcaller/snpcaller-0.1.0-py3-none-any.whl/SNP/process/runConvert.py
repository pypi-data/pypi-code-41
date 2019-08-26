#import vcf
import copy
import time
from WholeGenomeAnalysis.SNP.model.Vcf import Vcf
# from WholeGenomeAnalysis.SNP.model.Info import INFO
# from WholeGenomeAnalysis.SNP.model.Format import FORMAT

# class INFO:
#     # DP = {}
#     # SVTYPE = {}
#     # FUNC = {}
#     dic = {}
#     # The class "constructor" - It's actually an initializer
#     # def __init__(self, DP, SVTYPE, FUNC):
#     #     self.DP = DP
#     #     self.SVTYPE = SVTYPE
#     #     self.FUNC = FUNC
#     def make_INFO(self, dp):
#         self.dic["DP"] = dp
#         # info = INFO(DP)
#         return INFO
#
#     def make_INFO_CNV(self):
#         self.dic["SVTYPE"] = "CNV"
#         # info = INFO(SVTYPE)
#         return INFO
#
# class FORMAT:
#     # GT = {}
#     # CN = {}
#     # DP = {}
#     dic = {}
#     # The class "constructor" - It's actually an initializer
#     # def __init__(self, GT, CN, DP):
#     #     self.GT = GT
#     #     self.CN = CN
#     #     self.DP = DP
#     def make_FORMAT_CNV(self, gt, cn):
#         self.dic["GT"] = gt
#         self.dic["CN"] = cn
#         # format = FORMAT(GT, CN)
#         return FORMAT
#
#     def make_FORMAT(self, gt, dp):
#         self.dic["GT"] = gt
#         self.dic["DP"] = dp
#         # format = FORMAT(GT, DP)
#         return FORMAT

# def make_INFO(self, dp):
#     DP = {"DP": dp}
#     info = INFO(DP)
#     return info
#
# def make_INFO_CNV(self):
#     SVTYPE = {"SVTYPE": 'CNV'}
#     info = INFO(SVTYPE)
#     return info

# def make_FORMAT_CNV(self, gt, cn):
#     GT = {"GT": gt}
#     CN = {"CN": cn}
#     format = FORMAT(GT, CN)
#     return format
#
# def make_FORMAT(self, gt, dp):
#     GT = {"GT": gt}
#     DP = {"DP": dp}
#     format = FORMAT(GT, DP)
#     return format

class Converter:
    vcfs = []

    def __init__(self):
        self.vcfAddress = "C:/Destination/vcf_sample.vcf"
        # self.vcfs = []
        self.sampleid = ''

    def init_vcf(self):
        vcf_reader = vcf.Reader(open(self.vcfAddress, 'r'))

        for record in vcf_reader:
            print(record)

    def set_gt(self, gt, numberofsnp):
        _gt = ''
        if numberofsnp == 1:
            if gt == 0:
                _gt = '0/0'
            elif gt == 1:
                _gt = '1/1'

        else:
            if gt == 0:
                _gt = 'ERROR'
            elif gt == 1:
                _gt = '0/1'
            elif gt == 2:
                _gt = '1/2'

        return _gt

    def convert(self, Snps, sampleId):
        self.sampleid = sampleId
        chrom = ''
        pos = ''
        id = ''
        ref = ''
        alt = ''
        qual = ''
        filter = ''
        gt = 0
        numberofsnp = 0
        reads = 0
        snpname = ''

        for name in sorted(Snps):

            for base, snp in Snps[name].items():

                if len(snpname) == 0:
                    snpname = name

                if snpname != name:
                    # global format
                    # global info

                    class INFO:
                        dic = {}

                        def make_INFO(self, dp):
                            self.dic["DP"] = dp
                            # info = INFO(DP)
                            return INFO

                        def make_INFO_CNV(self):
                            self.dic["SVTYPE"] = "CNV"
                            # info = INFO(SVTYPE)
                            return INFO

                    class FORMAT:
                        dic = {}

                        def make_FORMAT_CNV(self, gt, cn):
                            self.dic["GT"] = gt
                            self.dic["CN"] = cn
                            # format = FORMAT(GT, CN)
                            return FORMAT

                        def make_FORMAT(self, gt, dp):
                            self.dic["GT"] = gt
                            self.dic["DP"] = dp
                            # format = FORMAT(GT, DP)
                            return FORMAT

                    genotype = self.set_gt(gt, numberofsnp)
                    format = FORMAT()
                    info = INFO()

                    if alt == '<CNV>':
                        format = format.make_FORMAT_CNV()
                        info = info.make_INFO_CNV()
                    else:
                        format = format.make_FORMAT(genotype, reads)
                        info = info.make_INFO(reads)

                    alt = alt.replace(alt+",", "")

                    print(">>>>>")
                    print(gt, numberofsnp)
                    print(chrom, pos, id, ref, alt, qual, filter, info.dic, format.dic, self.sampleid)

                    # _info = copy.deepcopy(info)
                    # _format = copy.deepcopy(format)
                    # vcf = Vcf(chrom, pos, id, ref, alt, qual, filter, _info, _format, self.sampleid)
                    # _vcf = copy.deepcopy(vcf)
                    # self.vcfs.append(_vcf)

                    # for vcf in self.vcfs:
                    #     print(vcf)
                    #     print(vcf.info)
                    #     print(vcf.info.dic)

                    self.vcfs.append(Vcf(chrom, pos, id, ref, alt, qual, filter, info, format, self.sampleid))

                    # initialize
                    alt = ''
                    gt = 0
                    numberofsnp = 0
                    reads = 0
                    snpname = name

                numberofsnp = numberofsnp + 1
                chrom = snp.chrom
                pos = snp.chromStart
                id = snp.snpName
                ref = snp.refNCBI

                if snp.rawBases == '<CNV>':
                    alt = '<CNV>'
                else:
                    alt = alt + snp.rawBases + ','

                qual = '.'
                filter = 'PASS'
                reads = reads + int(snp.rawReads)

                if snp.refNCBI != snp.rawBases:
                    gt = gt + 1

        return self.vcfs

# def run():
#     start = time.time()
#     # Initiate
#     vcf = Converter()
#     # Set HEADER on VCF
#     # vcf.init_vcf()
#
#     end = time.time()
#     print('Comeplete! Total time is ')
#     print(end - start)
#
# if __name__ == '__main__':
#     run()
