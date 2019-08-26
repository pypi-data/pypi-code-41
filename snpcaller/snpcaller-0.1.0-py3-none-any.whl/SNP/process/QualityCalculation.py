def getQuality(qualityData, rawbase, start, end, sequenceName):
    ###### Get Quality Input
    print("sequenceName : " + sequenceName)
    print("rawbase : " + str(rawbase))
    print("start : " + str(start))
    print("end : " + str(end))


    minBaseOcurrances = 99999999999
    minBasePercentages = 100.0
    minBaseQualityPercentage = 100.0

    arrBases = list(rawbase)
    i = start
    for amplicon in qualityData['Amplicon']:
        for allele in amplicon['Allele']:
            if (allele['SequenceName'] == sequenceName):
                #for i in range(start, end):
                for base in arrBases:
                    if(base == '-'):
                        base = "Deletion"

                    for k, v in allele['BaseOcurrances'].items():
                        if (k == base):
                            x = v.split(",")
                            print(x[i])
                            if (minBaseOcurrances > int(x[i]) ):
                                minBaseOcurrances = int(x[i])
                            break
                    for k, v in allele['BasePercentages'].items():
                        if (k == base):
                            x = v.split(",")
                            print(x[i])
                            if (minBasePercentages > float(x[i])):
                                minBasePercentages = float(x[i])
                            break
                    for k, v in allele['BaseQualityPercentage'].items():
                        if (k == base):
                            x = v.split(",")
                            print(x[i])
                            if (minBaseQualityPercentage > float(x[i])):
                                minBaseQualityPercentage = float(x[i])
                            break

                    i=i+1

    return minBaseOcurrances,minBasePercentages,minBaseQualityPercentage
