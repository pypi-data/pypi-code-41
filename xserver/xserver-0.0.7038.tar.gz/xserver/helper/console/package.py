#coding: utf8
from __future__ import absolute_import
from xserver.utils.cli_color import print_with_color
from xserver.utils.console_utils import get_args_from_console, get_first_arg_from_console
from xserver.helper.package_utils import dump_deploy_dir, deploy_project_dir
import os
import sys


# xserver_package dump  <folder path>
# xserver_package deploy <package_name or filepath> <name>(/home/run/xxxx at last)

# xserver_package deploy farbox_bucket.server farbox_bucket 1024mb

# xserver_package replace <filepath> old_string new_string

def main():
    raw_args = sys.argv[2:]
    kwargs, args = get_args_from_console(raw_args)
    action = get_first_arg_from_console()
    if action == 'dump' and args:
        folder_to_dump = args[0]
        if not os.path.isdir(folder_to_dump):
            print_with_color('%s is not a folder'%folder_to_dump, color='red')
            return
        else:
            dump_deploy_dir(folder_to_dump)
    elif action == 'deploy' and len(args)>=1:
        # xserver_package deploy farbox_bucket farbox_bucket memcache=3000mb
        # xserver_package deploy <package> <project> memcache=3000mb
        # # xserver_package deploy <deploy_dir> <project> memcache=3000mb
        if len(args) == 1:
            args.insert(0, args[0],)
        package_name = args[0]
        project_name = args[1]
        more_args = args[2:]

        # 可接受参数 memcache cpu mem, 是为资源的硬性限制
        kwargs_for_deploy = {}
        for arg in more_args:
            if '=' not in arg:
                continue
            else:
                k, v = arg.split('=', 1)
                k = k.strip()
                v = v.strip()
                kwargs_for_deploy[k] = v
        deploy_project_dir(package_name, project_name, **kwargs_for_deploy)
    elif action == 'replace' and len(args) >=3:
        # 一般是在 deploy 某个 project 后， 需要局部替换里面的配置文件，当然要确保 old_string 具有相对的唯一性
        filepath = args[0]
        old_string = args[1]
        new_string = args[2]
        if not os.path.isfile(filepath):
            print('can not find %s' % filepath)
            return
        with open(filepath, 'rb') as f:
            raw_content =f.read()
        new_content = raw_content.replace(old_string, new_string)
        with open(filepath, 'wb') as f:
            f.write(new_content)
    else:
        print_with_color('error, should be like: dump <folder> or deploy <package> <project_name>')


if __name__ == '__main__':
    main()