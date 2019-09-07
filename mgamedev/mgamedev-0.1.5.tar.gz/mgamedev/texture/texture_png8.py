import os
import shutil 
import json
import logging

class TextureFmt(object):

    _texturelist = []

    @classmethod
    def _handlepng8(cls, fileobj):
        cmd_str = "pngquant --force --output {outfile} {basefile}"
        print("Formst texture %s to png8.." % fileobj.split(os.sep)[-1])
        os.system(cmd_str.format(outfile=fileobj , basefile=fileobj))

    @classmethod
    def _fmtpng8(cls):
        for fileobj in cls._texturelist:
            cls._handlepng8(fileobj

    @classmethod
    def _fmtpvr(cls):
        for fileobj in cls._texturelist:
            cls._handlepvr(fileobj)

    @classmethod
    def _get_texture(cls, path):
        for filename in os.listdir(path):
            fileobj = os.path.join(path, filename)
            if os.path.isfile(fileobj):
                if filename.endswith(".png"):
                    cls._texturelist.append(fileobj)
            else:
                cls._get_texture(fileobj)

    @classmethod
    def excute(cls, tarpath):
        cls._get_texture(tarpath)
        strlist = json.dumps(cls._texturelist, sort_keys = True, indent = 4)
        # cls._fmtpng8()
        cls._fmppvr()

if __name__ == "__main__":
    TextureFmt.excute(os.getcwd())