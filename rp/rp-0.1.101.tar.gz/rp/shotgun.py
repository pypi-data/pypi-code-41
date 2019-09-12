#A dependency shotgun
packages=[
'js2py',
'pyflann',#TODO: This needs to be fixed. It's broken for python3. It needs to be fixed using 2to3, and then inlined into this rp package. This is needed for flann_dict
'HTMLParser',
'Pyperclip',
'colorama',
'drawille',
'exofrills',
'gtts_token',
'lazyasd',
'matplotlib',
'more_itertools',
'pandas',
'pyaudio',
'pygame',
'pymatbridge',
'requests',
'rtmidi',
'scipy',
'serial',
'setproctitle',
'sklearn',
'sounddevice',
'suplemon',
'send2trash',
'urwid',
'win_unicode_console',
'youtube_dl',
'opencv-python',
'scikit-learn',
'pillow',
'playsound',
'numpngw',
'psutil',
'xonsh',
'pyqtgraph',
'pyqt5',
'vispy',
'pytube',
'sk-video']
def shotgun():
    for package in packages:
        bar='――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――'
        print(bar)
        print("ATTEMPTING TO INSTALL PACKAGE:".center(len(bar)))
        print(package.center(len(bar)))
        print(bar)
        from subprocess import run
        from os import name
        if name=='nt':# We're on windows
            run('pip3 install '+package,shell=True)# Might be prompted for a password
        else:
            run('sudo pip3 install '+package,shell=True)# Might be prompted for a password
try:
    shotgun()
except:
    print("Shotgun errored and is now cancelled. Try it again with shotgun.shotgun()")
    pass