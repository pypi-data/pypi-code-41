from .path import Chibi_path
import tempfile, shutil


class Chibi_temp_path( Chibi_path ):
    def __new__( cls, *args, **kw ):
        args_2 = []
        args_2.append( tempfile.mkdtemp() )
        return str.__new__( cls, *args_2, **kw )

    def __del__( self ):
        self.delete()

    def __add__( self, other ):
        return Chibi_path( str( self ) ) + other
