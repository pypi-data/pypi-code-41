import json
import datetime

def JsonReader(filePath):
    with open(filePath) as json_file:
        return json.load(json_file)

def VCFReader(filePath, sampleid):
    header = []

    with open(filePath, 'r') as v:
        for line in v:

            if "fileDate" in line:
                date = datetime.datetime.today()
                line = line.replace('\n', '') + date.strftime('%Y%m%d') + '\n'

            elif "CHROM" in line:
                line = line + '\t' + sampleid + '\n'

            header.append(line)

    return header