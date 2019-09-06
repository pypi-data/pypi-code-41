class LibraryItem:
    """Single library item record"""
    
    def __init__(self, name=None, cls=None, label=None, 
                 properties=None, columnbreaks=None):
        if properties is None:
            properties = []
        if columnbreaks is None:
            columnbreaks = []
        self.name = name
        self.label = label
        self.properties = properties
        self.columnbreaks = columnbreaks
