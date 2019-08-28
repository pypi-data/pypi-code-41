import csv

def TextWriter(outputpath_vcf, data):
    file = open(outputpath_vcf, 'w')
    for dt in data:
        file.writelines(dt)

    # with open(outputpath_vcf, mode='w') as result:
    #     work = csv.writer(result, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    #     work.writerow(data)

def csvWriter(outputpath_csv, snip_dic,experimentName,sampleId):
    with open(outputpath_csv, mode='w', newline='') as csv_file:
        fieldnames = ['experimentName', 'sampleId', 'snpName', 'observed1', 'observed2', 'observed3', 'observed4']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for snip, snip_observe  in snip_dic.items():
            observe1= ''
            observe2= ''
            observe3= ''
            observe4= ''
            count=0
            for observe in sorted(snip_observe.keys()):
                snp = snip_observe[observe]
                if(snp.isValid != 0):
                    if(count==0):
                        observe1=observe
                    elif(count==1):
                        observe2=observe
                    elif(count==2):
                        observe3=observe
                    elif(count==3):
                        observe4=observe

                    count=count+1

            writer.writerow(
                {'experimentName': experimentName, 'sampleId': sampleId, 'snpName': snip, 'observed1': observe1,
                 'observed2': observe2,'observed3': observe3,'observed4': observe4})


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
        # data.append(vcf.alt[:len(vcf.alt) - 1])
        data.append(vcf.alt)
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