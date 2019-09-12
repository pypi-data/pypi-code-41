def git():
    import os
    command='cd ~ && \
    wget https://gist.githubusercontent.com/whohe/9bf4574b1d2d00a613e2/raw/8bfcdf01d14f4088ca15248a76212988255763a1/.gitconfig && \
    cp .gitconfig /home/who/. && chown who:who .gitconfig'
    os.system(command)

