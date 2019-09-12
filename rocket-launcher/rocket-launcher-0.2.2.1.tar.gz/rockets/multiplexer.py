def multiplexer():
    import os
    command='echo "cd ~ \nmkdir -p .byobu \n\
    git clone https://github.com/whohe/.tmux ~/.tmux --branch master-fish \n\
    ln -s .tmux/tmux.conf .tmux.conf \ncd .tmux \n\
    git submodule update --init --recursive \ncd ~/.byobu \n\
    ln -s ../.tmux.conf . " > /tmp/deploy_multiplexer.sh \n\
    sh /tmp/deploy_multiplexer.sh && \
    sudo -H -u who sh /tmp/deploy_multiplexer.sh \
    rm /tmp/deploy_multiplexer.sh'
    os.system(command)

