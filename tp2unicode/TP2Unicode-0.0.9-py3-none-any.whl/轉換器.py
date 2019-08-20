import csv


def 轉換(text):
    with open('unicode.csv') as csvfile:
        對應表 = csv.DictReader(csvfile)
        for row in 對應表:
            text = text.replace(chr(int(row['原始編碼'], 16)), row['對應編碼'])
    return text
