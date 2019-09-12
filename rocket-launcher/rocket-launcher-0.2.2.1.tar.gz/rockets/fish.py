def fish():
    import os
    command='mkdir -p ~/.config/fish && \
    echo "export LC_ALL=es_CO.UTF-8" >> ~/.config/fish/config.fish && \
    echo "export EDITOR=vim" >> ~/.config/fish/config.fish && \
    cp ~/.config && /home/who/.config -r && chown who:who .gitconfig -R'
    os.system(command)
