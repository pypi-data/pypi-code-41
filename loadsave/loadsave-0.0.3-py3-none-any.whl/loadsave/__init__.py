import csv
import pickle
import json
import wave
import struct
import array
import itertools as it

name = "loadsave"



class handle_csv:
    def __init__(self):
        pass
    def load(self, fname, args):
        result = []
        with open(fname, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                result.append(dict(row))
        return result
    def save(self, data, fname, args):
        with open(fname, 'w', newline='') as f:

            fieldnames = data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    def help(self):
        print('CSV reader/writer\n\tload(fname): returns list of dicts\n\tsave(data, fname): data must be a list of dicts')

class handle_pkl:
    def load(self, fname, args):
        with open(fname, 'rb') as f:
            return pickle.load(f)
    def save(self, data, fname, args):
        with open(fname, 'wb') as f:
            pickle.dump(data, f)
    def help(self):
        print('PKL reader/writer\n\tSaves and loads python data structures')

class handle_json:
    def load(self, fname, args):
        with open(fname) as f:
            text = f.read()
            return json.loads(text)
    def save(self, data, fname, args):
        text = json.dumps(data)
        with open(fname, 'w') as f:
            f.write(text)
    def help(self):
        print("JSON\n\tload(fname): Loads a JSON file into a python dictionary\n\tsave(data,fname): Saves input data as a JSON\n\t\tValid input data structures: dict, list, tuple, string, int, float, bool, None")

class handle_wav:
    def load(self, fname, args):
        # When the with block completes, the Wave_read.close() -docs.python.org/3/library/wave
        with wave.open(fname, 'rb') as file:
            params = file.getparams()
            nchannels, sampwidth, framerate, nframes, comptype, compname = params

            bytes = file.readframes(nframes) # Read all frames from audio
            fmt = "<"+str(nchannels*nframes)+"h"
            y = list(struct.unpack_from(fmt,bytes))

            if nchannels>1:
                result = []
                for i in range(nchannels):
                    result.append(y[i::nchannels])
                return result, framerate
            else:
                return y, framerate
    def save(self, data, fname, args):
        if not (len(data)==2):
            raise Exception("\n\ndata must be a tuple or list of the form (waveform, samplerate)\n")

        with wave.open(fname, 'wb') as file:

            y, framerate = data
            if type(y[0])==list:
                nchannels = len(y)
                nframes = len(y[0])
            else:
                nchannels = 1
                nframes = len(y)
            sampwidth = 2
            comptype = "NONE"
            compname = 'not compressed'
            params = nchannels, sampwidth, framerate, nframes, comptype, compname
            file.setparams(params)
            if nchannels == 1:
                bytes = array.array('h', y).tobytes()
                file.writeframes(bytes)
            else:
                stream = list(it.chain(*list(zip(*y)))) # Weaves all channels into one list
                bytes = array.array('h', stream).tobytes()
                file.writeframes(bytes)
    def help(self):
        print("WAV")
        print("\tload(fname): Returns y, framerate")
        print("\t\ty: Audio data. If fname is a mono track file, y is a list of ints. Otherwise, y is a list of lists, where each list cooresponds to a separate track, e.g. for a stereo file y = [l,r] for left and right output")
        print("\t\tframerate: sample rate in Hz")
        print("\tsave(data,fname): data must be a tuple or list in the same format which is returned from load(fname), i.e. data = [y,framerate]")
        print("\tUsage:")
        print("\t\ty,sr = load('example.wav')")
        print("\t\ty = y[0] #Extract the left output from a stereo track")
        print("\t\tsave((y,sr),'mono.wav')")

filetypes = {
    'csv':handle_csv(),
    'pkl':handle_pkl(),
    'json':handle_json(),
    'wav':handle_wav()
}




def load(fname, args = {}):
    ext = fname.split('.')[-1].lower()
    return filetypes[ext].load(fname, args)

def save(data, fname, args = {}):
    ext = fname.split('.')[-1].lower()
    return filetypes[ext].save(data, fname, args)

def help(ext):
    filetypes[ext].help()
