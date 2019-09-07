import requests
import sys

def downloader(url,localdir):
    r = requests.get(url, allow_redirects=True, stream=True)
    total_length = r.headers.get('content-length')
    output = open(localdir, 'wb')
    if total_length is None: # no content length header
        output.write(r.content)
    else:
        dl = 0
        total_length = int(total_length)
        for data in r.iter_content(total_length/100):
            dl += len(data)
            output.write(data)
            done = int(50 * dl / total_length)
            sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
            sys.stdout.flush()

