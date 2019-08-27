import os

VERSION = None
NAME = 'geofinder'

here = os.path.abspath(os.path.dirname(__file__))

about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join('/Users/mikeherbert/GeoFinder/geofinder', '__version__.py')) as f:
        exec(f.read(), about)
    tkn = about['__version__'].split('.')
    next_build = int(tkn[-1]) + 1
    next_ver = f'{tkn[0]}.{tkn[1]}.{next_build}'
    print(next_ver)