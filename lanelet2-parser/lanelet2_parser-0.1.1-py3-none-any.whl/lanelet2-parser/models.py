
class Point():
    '''
    Point
    '''
    id = None
    lat = None
    lon = None
    x = None
    y = None
    z = None
    attributes = []

    def __init__(self, id, lat, lon, attributes)
        self.id = id
        self.lat = lat
        self.lon = lon
        self.attributes = attributes


class Linestring():
    '''
    Linestrings
    '''
    id = None
    points = []
    attributes = []

    def __init__(self, id, points, attributes):
        self.id = id
        self.points = points
        self.attributes = attributes


class Lanelet():
    '''
    Lanelet model
    '''
    id = None
    left_bound = None
    right_bound = None
    center_line = None
    attributes = []
    regulatory_element = []

    def __init__(self, id, left_bound, right_bound, center_line, attributes, regulatory_element):
        self.id = id
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.center_line = center_line
        self.attributes = attributes
        self.regulatory_element = regulatory_element


class RegulatoryElement():
    '''
    RegulatoryElement
    '''
    attributes = []
    parameters = []

    def __init__(self, attributes, parameters):
        self.attributes = attributes
        self.parameters = parameters


