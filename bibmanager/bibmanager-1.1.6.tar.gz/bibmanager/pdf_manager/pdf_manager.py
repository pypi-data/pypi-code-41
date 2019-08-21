import requests


def fetch(bibtex, filename):
    """
    Take info from here:
    https://github.com/adsabs/adsabs-dev-api/blob/9bcd908841beaf79f7c72acbf3e381aa7753ac76/Search_API.ipynb

    and Here:
    https://stackoverflow.com/questions/34503412
    """
    #token = cm.get('ads_token')
    token = 'ibi1LqVmOp5Ku9gxL2HRYGnVnhdTa7DbTT5s5jjY'

    filename = 'tmp_paper.pdf'

    # Examples:
    bibtex = '2017AJ....153....3C'  # Journal available
    bibtex = '2019ApJ...872..111C'  # Not available
    bibtex = '2006S&C....16..239T'  # ampersand
    bibtex = '2019JHyd..573....1A'  # No arxiv
    bibtex = '2010arXiv1012.3754A'  # no journal

    PDF = 'PUB_PDF'
    query = ('https://ui.adsabs.harvard.edu/link_gateway/'
            f'{urllib.parse.quote(bibtex)}/{PDF}')
    try:
        r = requests.get(query, headers={'Authorization': f'Bearer {token}'})
    except requests.exceptions.ConnectionError:
        print('Failed to establish a connection.')
        return
    # r.status_code r.reason
    # 200  'OK'
    # 400  'BAD REQUEST'   journal/eprint does not exists
    # 403  'Forbidden'
    if r.ok:
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"Fetched journal PDF into: '{filename}'.")
        return
    elif r.status_code == 403:
        print('Forbidden access to journal PDF.')

    PDF = 'EPRINT_PDF'
    query = ('https://ui.adsabs.harvard.edu/link_gateway/'
            f'{urllib.parse.quote(bibtex)}/{PDF}')
    r = requests.get(query, headers={'Authorization': f'Bearer {token}'})

    if r.ok:
        with open(filename, 'wb') as f:
            f.write(r.content)
        print(f"Fetched eprint PDF into: '{filename}'.")
        return
    else:
        print('Could not fetch journal nor eprint PDF.')
