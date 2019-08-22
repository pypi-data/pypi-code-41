import numpy as np
import sys
import os
import glob
import wave
import multiprocessing
from functools import partial
from scipy.fftpack import fft
from scipy.io import wavfile
from scipy import signal
from tqdm import tqdm
import librosa
import librosa.util
import random 
from scipy.stats import skew, kurtosis
import warnings
import resampy

SAMPLE_RATE = 16000
TIME_LAP = 0.2

def _save (data, wavfile, target_path):
    savedir = os.path.join (target_path, os.path.basename (os.path.dirname (os.path.dirname (wavfile))))
    if not os.path.isdir (savedir):
        os.mkdir (savedir)
    target_file = os.path.join(savedir, "%s.npy" % os.path.basename (wavfile))
    np.save(target_file, data)

def norm_volmue (y):
    return y / np.max (np.abs (y))
_normalize = norm_volmue

def whitening (y):
    mean = np.mean (y)    
    std = np.std (y)  
    return (y - mean) / std
    
def log (x, name = ""):
    return np.log (np.abs (x) + 1e-3) / 6.7
  
def add_padding (x, padding):
    if not padding:
        return x
    return np.concatenate ([x, np.zeros (padding)])

def to_db (S):
  S = np.abs (S) + 1e-10 
  return 10 * np.log10(S) - 10 * np.log10(np.max (S))

def gain (input, output, target_dBFS = -20.0):
    from pydub import AudioSegment
    
    sound = AudioSegment.from_file (input)
    change_in_dBFS = target_dBFS - sound.dBFS
    normalized_sound = sound.apply_gain (change_in_dBFS)
    normalized_sound.export(output, output.split (".")[-1].lower ())
    return normalized_sound.dBFS
        
def _compress (data, name, padding = 0, valid_max = 2.0, valid_min = -2.0):
    # padding 3 means 2 convolution, 1 polling    
    data = data.real
    if name == "poly_features":
        data = data / 10.
    elif name == "rmse":
        data = data / 4.
    elif name == "spectral_contrast":
        data = data / 50.
    elif name == "mel":
        data = data / -80.
    elif name in ("stft", "spectral_centroid", "spectral_bandwidth", "spectral_rolloff"):        
        data = log (data, name)
                          
    features = np.array ([
        add_padding (np.mean (data, axis = 1), padding),
        add_padding (np.max (data, axis = 1), padding),
        add_padding (np.min (data, axis = 1), padding),
        add_padding (np.median (data, axis = 1), padding),
        add_padding (np.var (data, axis = 1), padding),
        add_padding (skew (data, axis = 1) / 15., padding),
        add_padding (np.log (abs (kurtosis (data, axis = 1)) + 1e-3) / 6.7, padding)
    ])
    if np.min (features) < valid_min or np.max (features) > valid_max:
        #print (name, int (np.max (features)), int (np.max (features)))
        raise AssertionError
    return features

def _gen_colored_noise (spectral_shape, samples_to_generate):
    # https://www.kaggle.com/holzner/generating-different-colors-of-noise
    def normalize(samples):
        std = samples.std()
        if std > 0:
            return samples / std
        else:
            return samples
    
    flat_spectrum = np.random.normal(size = samples_to_generate // 2 + 1) + \
            1j * np.random.normal(size = samples_to_generate // 2 + 1)
    return normalize(np.fft.irfft (flat_spectrum * spectral_shape).real)

def gen_noise (color, samples_to_generate):
    assert samples_to_generate % 2 == 0
    if color == 'white':
        return np.random.normal(size = samples_to_generate)    
    spectrum_len = samples_to_generate // 2 + 1
    if color == 'pink':
        return _gen_colored_noise(1. / (np.sqrt(np.arange(spectrum_len) + 1.)), samples_to_generate)        
    elif color == 'blue':
        return _gen_colored_noise(np.sqrt(np.arange(spectrum_len)), samples_to_generate)    
    elif color == 'brown' or color == 'red':
        return _gen_colored_noise(1. / (np.arange(spectrum_len) + 1), samples_to_generate)
    elif color == 'violet' or color == 'purple':
        return _gen_colored_noise(np.arange(spectrum_len), samples_to_generate)    
    
def augment (y, sr, time_stretch = False, pitch_shift = False, random_laps = False, add_noise = False):    
    if add_noise:
        if y.shape [0] % 2 == 1:
            y = y [:-1] # make even
    
        color = random.choice ([
            'white',   # flat spectrum
            'pink',    # -3dB (factor 0.5)  per octave / -10 dB (factor 0.1) per decade
            'blue',    # +3dB (factor 2)    per octave / +10 dB (factor 10) per decade
            'brown',   # -6dB (factor 0.25) per octave / -20 dB (factor 0.01) per decade
            'violet'
        ])
        noise = gen_noise (color, y.shape [0]) / 4
        gain = np.random.uniform(0.01, 0.12)
        #print (color, gain)
        y = y * (1.0 - gain) + ((gain * noise).astype ("float32"))
    
    if time_stretch:
        rate = 1.0
        if random.randrange (2):
            rate += max (0.02, random.random () / 5.)
        else:
            rate -= max (0.02, random.random () / 5.)     
        y = librosa.effects.time_stretch (y, rate)
        #print ("time_stretch", rate)
    
    if pitch_shift:
        n_step = random.choice (range (-3, 4))
        y = librosa.effects.pitch_shift (y, sr, n_step + random.random (), bins_per_octave = 24)
        #print ("pitch_shift", n_step)
    
    if random_laps and librosa.get_duration(y, sr = sr) > 1.6:
       time_lap = random.random () / 3
       removable = int (sr * time_lap)
       y = y [removable:len (y) - removable]
       y = np.roll (y, random.randrange (len (y)))
    
    return y   

def augment_with_norm (y, sr = SAMPLE_RATE, *args, **karg):
    y = augment (y, sr, *args, **karg)
    y = norm_volmue (y)
    return whitening (y)

def loadraw (wavfile, sample_rate = SAMPLE_RATE, time_lap = 0.2, due_limit = (0.5, 10), res_type = "kaiser_best"):
    if res_type == "hann_window":
        y, sr_orig = librosa.load (wavfile, None, True)
        y = resampy.resample(y, sr_orig, sample_rate, filter = 'sinc_window', window = signal.hann)
        sr = sample_rate
    else:
        y, sr = librosa.load (wavfile, sample_rate, True, res_type = res_type)
    
    a_duration = librosa.get_duration(y, sr = sr)
    removable = int (sample_rate * time_lap)
    y = y [removable:len (y) - removable]
    # Trim the beginning and ending silence
    try:
        y, index = librosa.effects.trim (y)
    except ValueError:        
        return None, sr   
    duration = librosa.get_duration(y, sr = sr)
    #print ("    + duration: {:2.1f} sec => {:2.1f} sec".format (a_duration, duration))
    if duration < due_limit [0] or duration > due_limit [1]:
        warnings.warn ("audio file length is invalid, ignored")
        return None, sr
    if len (y) % 2 == 1:
        y = y [:-1]
    return y, sr
    
def load (wavfile, sample_rate = SAMPLE_RATE, time_lap = 0.2, due_limit = (1, 5), res_type = "kaiser_best", *args, **karg):
    y, sr = loadraw (wavfile, sample_rate, time_lap, due_limit, res_type)
    if y is None:
        return y, sr    
    return featurize (y, sr)    
 
DEFAULT_RECIPE = [
    "mel", "mfcc", "chroma_cqt", "chroma_cens", "zero_crossing_rate", "tonnetz", "rmse", 
    "spectral_contrast", "poly_features", "chroma_stft", 
    "spectral_centroid", "spectral_bandwidth", "spectral_rolloff"
]
   
def generate (y, sample_rate = SAMPLE_RATE, recipe = DEFAULT_RECIPE, n_mfcc = 40, n_mel = 40, padding = 0):
    feature_stack = []
    numfeat = []
    
    # stft ----------------------------------------------------
    stft = librosa.stft (y, n_fft=1024, win_length=512, hop_length=256)
    if "mel" in recipe:
        # mel specrogram ------------------------------------------
        D = np.abs (stft) ** 2
        S = librosa.feature.melspectrogram(S = D, n_mels = n_mel)
        vec = librosa.power_to_db (S, ref = np.max)
        feature_stack.extend (_compress (vec, "mel", padding))
        numfeat.append (vec.shape [0])        
        
    if "stft" in recipe:
        feature_stack.extend (_compress (vec, "stft", padding))
        numfeat.append (vec.shape [0])
        
    if "mfcc" in recipe:
        vec = librosa.feature.mfcc(S = stft, sr = sample_rate, n_mfcc = n_mfcc, n_fft=512, hop_length = 256)
        feature_stack.extend (_compress (vec, "mfcc", padding))
        numfeat.append (vec.shape [0])
        
    if "chroma_cqt" in recipe:        
        vec = librosa.feature.chroma_cqt (y=y, sr = sample_rate, n_chroma = 12, hop_length = 256)
        feature_stack.extend (_compress (vec, "chroma_cqt", padding))
        numfeat.append (vec.shape [0])
        
    if "chroma_cens" in recipe:
        vec = librosa.feature.chroma_cens (y=y, sr = sample_rate, n_chroma = 12, hop_length = 256)
        feature_stack.extend (_compress (vec, "chroma_cens", padding))    
        numfeat.append (vec.shape [0])
        
    if "zero_crossing_rate" in recipe:
        vec = librosa.feature.zero_crossing_rate (y = y)
        feature_stack.extend (_compress (vec, "zero_crossing_rate", padding))
        numfeat.append (vec.shape [0])
        
    if "tonnetz" in recipe:
        vec = librosa.feature.tonnetz (y=y, sr = sample_rate)
        feature_stack.extend (_compress (vec, "tonnetz", padding))
        numfeat.append (vec.shape [0])
        
    if "rmse" in recipe:
        vec = librosa.feature.rmse (S = stft, hop_length = 256)
        feature_stack.extend (_compress (vec, "rmse", padding))
        numfeat.append (vec.shape [0])
        
    for ff in [each for each in recipe if each in ("spectral_contrast", "poly_features", "chroma_stft", "spectral_centroid", "spectral_bandwidth", "spectral_rolloff")]:
        vec = getattr (librosa.feature, ff) (y = y, sr = sample_rate, hop_length = 256)
        feature_stack.extend (_compress (vec, ff, padding))        
        numfeat.append (vec.shape [0])    
    features = np.hstack (tuple (feature_stack))
    assert features.shape == ((sum (numfeat) + len (numfeat) * padding) * 7,)
    return features

AUDIO_ERRS = 0
def make (wavfile, sample_rate = SAMPLE_RATE, time_lap = 0.2, due_limit = (1, 5), recipe = DEFAULT_RECIPE, padding = 0, time_stretch = False, pitch_shift = False, random_laps = False, add_noise = False):
    global AUDIO_ERRS
    
    y, sr = load (wavfile, sample_rate, time_lap, due_limit, time_stretch, pitch_shift, random_laps, add_noise)
    if y is None:
        return
    try:
        return generate (y, sr, recipe, padding = padding)
    except AssertionError:
        AUDIO_ERRS += 1
        print ("audio file may be irregular, ignored ({})".format (AUDIO_ERRS))
        return None    

def save (wavfile, target_path, sample_rate = SAMPLE_RATE, time_lap = 0.2, due_limit = (1, 5), recipe = DEFAULT_RECIPE, padding = 0, **karg):
    features = make (wavfile, sample_rate, time_lap, due_limit, recipe, padding)
    if features is None:
        return False
    _save (features, wavfile, target_path)
    return True

def puff (wavfile, target_path, sample_rate = SAMPLE_RATE, time_lap = 0.2, due_limit = (1, 5), recipe = DEFAULT_RECIPE, padding = 0, n_gen = 3):
    if not os.path.isfile (os.path.join (target_path, wavfile + ".npy")):    
        if not save (wavfile, target_path, sample_rate, time_lap, due_limit, recipe, padding):
            return 0
         
    n = 1
    for i in range (n_gen * 2):
        fn = "{}.{}".format (wavfile, n)
        if os.path.isfile (os.path.join (target_path, fn + ".npy")):
            n += 1
            continue
        params = (random.randrange (2), random.randrange (2), random.randrange (2), random.randrange (2))
        if sum (params) == 0:
            continue
        features = make (wavfile, sample_rate, time_lap, due_limit, recipe, padding, time_stretch = params [0], pitch_shift = params [1], random_laps = params [2], add_noise = params [3], padding = padding)
        if features is None:
            continue        
        _save (features, fn, target_path)
        n += 1
        if n == n_gen:
            break
    
    return n    


if __name__ == '__main__':    
    y, sr = load  (os.path.join (os.path.dirname (__file__), "test.wav"))
    print (y.shape)   
    print (librosa.get_duration(y)) 
    stft = librosa.stft (y [:sr], n_fft=2048, win_length=1200, hop_length=256)
    print (stft.shape)
    ft = generate (y, sr)
    print (ft.shape)
    
    
