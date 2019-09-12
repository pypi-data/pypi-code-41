def editor():
    import os
    command='echo "cd ~ \ngit clone https://github.com/whohe/.vim\n\
    ln -s .vim/vimrc .vimrc \ncd ~/.vim \n\
    git submodule update --init --recursive \n\
    cd /home/who \ngit clone https://github.com/whohe/.vim\n\
    ln -s .vim/vimrc .vimrc \n cd /home/who/.vim \n\
    git submodule update --init --recursive " >> /tmp/deploy_editor.sh && \
    sh /tmp/deploy_editor.sh && \
    sudo -H -u who sh /tmp/deploy_editor.sh \
    rm /tmp/deploy_editor.sh' 
    os.system(command)
