#coding: utf8
from __future__ import absolute_import
import sys
from xserver.utils.cli_color import print_with_color
from xserver.utils.console_utils import get_args_from_console, get_first_arg_from_console
from xserver.docker_image.utils import update_docker_image

# import image templates
from xserver.docker_image.templates.build_images import build_common_image, build_mongodb, build_demo,\
    build_pyweb, build_pyubuntu, build_farbox_bucket, build_supervisor, build_ipfs


# xserver_build mongodb
# xserver_build mongodb --version=3.6.5
# xserver_build demo
# xserver_build demo --version=0.0.2 --old_version=0.0.1 --update  "cmd1" "cmd2"
# xserver_build pyweb --version=2018 --update "RUN pip install setuptools==40.0.0"
# .etc


template_map ={
    'pyubuntu': build_pyubuntu,
    'pyweb': build_pyweb,
    'demo': build_demo,
    'farbox_bucket': build_farbox_bucket,
    'xserver_demo_app': build_demo,
    'mongodb': build_mongodb,
    'supervisor': build_supervisor,
    'ipfs': build_ipfs,
}


def main():
    raw_args = sys.argv[2:]
    kwargs, args = get_args_from_console(raw_args, long_opts=['username=', 'old_version=', 'version=', 'update'])
    image_name = get_first_arg_from_console()

    # 没有指定 username， 就会从系统中尝试提取其它 image 以获得 username

    if 'update' in kwargs and kwargs.get('version'):
        # update image
        # xserver_build demo --version=0.0.2 --old_version=0.0.1 --update  "cmd1" "cmd2"
        # xserver_build pyweb --version=2018 --update "RUN pip install setuptools==40.0.0"
        # 可以在某个 version 的基础上， 运行 cmds， 然后构建新的 version；如果没有指定 old_version, 则认为两者一致
        old_version = kwargs.get('old_version') or kwargs.get('version')
        new_version = kwargs.get('version')
        update_docker_image(
            image_name = image_name,
            old_version = old_version,
            new_version = new_version,
            cmds = args
        )

    elif image_name in template_map:
        build_func = template_map[image_name]
        build_func(*args, **kwargs)
    else:
        build_common_image(image_name, **kwargs) # 通用的
        #print_with_color('fail to match %s'%image_name, color='red')


if __name__ == '__main__':
    main()