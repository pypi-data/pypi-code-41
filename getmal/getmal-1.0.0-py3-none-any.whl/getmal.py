import os
import json

from pathlib import Path
from argparse import ArgumentParser

from bs4 import BeautifulSoup
from urllib.request import urlopen

if __name__ == '__main__':
    # parser = ArgumentParser(description='Process some integers.')

    # himynameis
    # parser.add_argument('username', metavar='USER', type=str, help='username')

    # 7: All Anime
    # 1: Currently Watching
    # 2: Completed
    # 3: On Hold
    # 4: Dropped
    # 6: Plan to Watch
    # parser.add_argument('status', metavar='STATUS', type=int, help='status')

    # args = parser.parse_args()

    #url = 'https://myanimelist.net/animelist/{}?status={}'.format(args.username, args.status)
    url = 'https://myanimelist.net/animelist/valsaven?status=3'
    print(url)

    soup = BeautifulSoup(urlopen(url), 'lxml')
    data = soup.select('.list-table')[0]['data-items']

    encoded = json.loads(data)

    beautify = json.dumps(encoded, sort_keys=True, indent=4)

    print(beautify)

    filename = 'lol.json'

    # os.chdir(os.path.dirname(__file__))

    data_folder = Path(os.getcwd())
    print(data_folder)

    file_to_open = data_folder / filename

    # f = open(file_to_open)

    # print(f.read())

    with open(file_to_open, 'a') as out:
        out.write(beautify)

# .list-table-data > .data.number

# .list-table-data > .data.image > .link > .image(src)

# .list-table-data > .data.title > .link

# .list-table-data > .data.score > .link

# .list-table-data > .data.type

# # current episode
# .list-table-data > .data.progress > span[0] > .link

# #total episode

# .list-table-data > .data.progress > span[1]
# data progress
