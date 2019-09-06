# THIS FILE IS GENERATED FROM PADDLEPADDLE SETUP.PY
#
full_version    = '1.5.2'
major           = '1'
minor           = '5'
patch           = '2'
rc              = '0'
istaged         = False
commit          = 'a5696153a013552bfaa612ca407eba318e18ba54'
with_mkl        = 'ON'

def show():
    if istaged:
        print('full_version:', full_version)
        print('major:', major)
        print('minor:', minor)
        print('patch:', patch)
        print('rc:', rc)
    else:
        print('commit:', commit)

def mkl():
    return with_mkl
