
class TestingCodeFile:
    '''
        Hold the file with the method being tested.
    '''

    def __init__(self, path, lines, def_start, body_start, end):
        '''
            path = Path to the file.
            lines = List of strings representing lines of code in the file.
            def_start = Start of function definition.
            body_start = Start of function body (line of first command).
            end = Line before the next statement. OR End of the file.
        '''
        self.path = path
        self.lines = lines
        self.def_start = def_start
        self.body_start = body_start
        self.end = end

    def filename(self, extension=True):
        ps = self.path.split('/')
        if extension:
            return ps[-1]
        fname = ps[-1]
        return fname[:fname.rfind('.')]

    def working_directory(self):
        ps = self.path.split('/')
        wd = ps[:-1]
        return '/'.join(wd)
