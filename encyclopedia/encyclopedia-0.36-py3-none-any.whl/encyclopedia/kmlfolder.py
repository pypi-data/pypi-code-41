# standard
import unittest
from tempfile import NamedTemporaryFile
# internal
from encyclopedia import Unindexed, KML, Arboretum

class KML_Folder(Unindexed):

    def __init__(self, filename=None):
        Unindexed.__init__(self)
        self.kml = KML() # the final KML output
        base = 'Document'
        self.tree = Arboretum() # the attribute tree
        self.tree += base
        self.folders = {} # mapping from the folder name to KML element
        self.styles = {}
        self.folders[base] = base
        self.tree[base, 'altmode'] = 'absolute'
        self.tree[base, 'extrude'] = False
        self.tree[base, 'tesselate'] = False
        self.filename = filename

    def stylize(self, values):
        self.styles[values['id']] = self.kml.stylize(KML.Style(values))

    def draw(self, node, data):
        self.kml.draw(data,
            folder=self.folders[node],
            style=self.styles[self.tree[node, 'styleUrl']],
            scale=self.tree[node, 'scale'],
            shape=self.tree[node, 'dae'],
            tesselate=self.tree[node, 'tesselate'],
            geometry=self.tree[node, 'geometry'],
            extrude=self.tree[node, 'extrude'],
            altitude=self.tree[node, 'altmode'])

    @staticmethod
    def foldered(value):
        '''
        assure that KML_Folder only creates Folder(s)
        '''
        FOLDER_HEADER = 'Folder'
        if value.split('/')[-1] != FOLDER_HEADER:
            return value + '/' + FOLDER_HEADER
        else:
            return value

    def __setitem__(self, key, value):
        self.tree[key] = value
        if not isinstance(key, tuple):
            self.kml[self.folders[key]] = folder = KML_Folder.foldered(value)
            self.kml[folder, 'name'] = folder.split('/')[-2]
            self.folders[value] = folder
        return self

    def __getitem__(self, key):
        return self.kml[self.folders[key]]

    def __delitem__(self, key):
        del self.folders[key]
        del self.tree[key]
        del self.kml[key]

    def __iter__(self):
        yield from self.tree

    def __len__(self):
        return len(self.tree)

    def unique(self, thing):
        '''
        create a unique folder name for the KML_Folder
        '''
        return self.kml.unique(KML_Folder.foldered(thing))

    def write(self, file):
        self.kml.write(file)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.kml.write(self.filename)

class Test_KML_Folder(unittest.TestCase):

    def test_basic(self):
        with NamedTemporaryFile() as f:
            with KML_Folder(f.name) as kt:
                kt.stylize(
                {
                'id':'s1',
                'fill.on':True,
                'line.green':1,
                'line.blue':0,
                'line.red':1,
                'line.opacity':1,
                'line.width':2
                })
                kt.stylize(
                {
                'id':'s2',
                'line.green':0,
                'line.blue':0,
                'line.red':1,
                'line.opacity':1,
                'line.width':3
                })

                kt['Document', 'geometry'] = 'LineString'

                for node in ['G1', 'G2']:
                    kt['Document'] = node

                kt['G2', 'styleUrl'] = 's2'
                kt['G1', 'styleUrl'] = 's1'

                for node in ['S1', 'S2', 'S3']:
                    for other in ['G1', 'G2']:
                        kt[other] = other + '/' + node

                for node in ['T1', 'T2', 'T3']:
                    kt['G1/S1'] = 'S1/' + node

                data = [
                    {'uid':1, 'id':17, 'lat':1, 'lon':2, 'alt':0},
                    {'uid':2, 'id':12, 'lat':17, 'lon':21, 'alt':-1},
                    {'uid':3, 'id':13, 'lat':21, 'lon':22, 'alt':-2}
                ]
                kt.draw('S1/T2', data)
                # check some things
                assert len(kt) == len(list(kt))

if __name__ ==  '__main__':
    unittest.main()
