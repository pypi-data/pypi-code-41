import csv

def TextWriter(outputpath_vcf, data):
    file = open(outputpath_vcf, 'w')
    for dt in data:
        file.writelines(dt)

    # with open(outputpath_vcf, mode='w') as result:
    #     work = csv.writer(result, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    #     work.writerow(data)

def VCFWriter(outputpath_vcf, vcfs):

    file = open(outputpath_vcf, 'a')

    for vcf in vcfs:
        format = ""
        format_value = ""
        data = []

        data.append(vcf.chrom)
        data.append(vcf.pos)
        data.append(vcf.id)
        data.append(vcf.ref)
        data.append(vcf.alt[:len(vcf.alt)-1])
        data.append(vcf.qual)
        data.append(vcf.filter)

        for name in vcf.info.dic:
            data.append(name + "=" + str(vcf.info.dic[name]))

        for name in vcf.format.dic:
            format = format + name + ":"

        data.append(format[:len(format)-1])

        for name in vcf.format.dic:
            format_value = format_value + str(vcf.format.dic[name]) + ":"

        data.append(format_value[:len(format_value)-1])

        line = '\t#'.join(str(x) for x in data)
        lst = line.split('#')
        file.writelines(lst)
        file.writelines('\n')