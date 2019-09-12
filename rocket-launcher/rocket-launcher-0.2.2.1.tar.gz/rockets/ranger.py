def ranger():
    import os
    command='export TERM=linux && \
    export TERMINFO=/bin/sh && \
    ranger --copy-config=all && \
    sudo -H -u who ranger --copy-config=all'
    os.system(command)

