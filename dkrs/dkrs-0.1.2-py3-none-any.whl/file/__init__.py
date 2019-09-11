# Copyright (C) 2019 Erhu Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import errno
import json
import os
import shutil
import stat
import zipfile


class File:
    def __init__(self):
        pass

    @staticmethod
    def unzip(zip_file_path, target_dir):
        """
        解压 zip 文件到指定目录
        """
        zipfile.ZipFile(zip_file_path).extractall(target_dir)

    @staticmethod
    def zip_dir(dir_path, zip_file_path):
        # 下面这个方法会自动加上 zip 后缀
        # shutil.make_archive(zip_file_path, 'zip', dir_path)
        for root, dirs, files in os.walk(dir_path):
            zf = zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED)
            for f in files:
                zf.write(os.path.join(root, f), arcname=f)
            zf.close()

    @staticmethod
    def remove_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)

    @staticmethod
    def remove_dir(directory):
        if os.path.exists(directory):
            for root, dirs, files in os.walk(directory, topdown=False):
                for name in files:
                    filename = os.path.join(root, name)
                    os.chmod(filename, stat.S_IWUSR)
                    os.remove(filename)
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(directory)

    @staticmethod
    def mkdir_p(path):
        """
        递归创建目录
        """
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as exc:  # Python >2.5
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else:
                    raise
        else:
            print(f'目录 {path} 已存在，不重新创建')

    @staticmethod
    def dump_json(json_file, data):
        with open(json_file, 'w') as fp:
            json.dump(data, fp, indent=2, sort_keys=True, ensure_ascii=False)

    @staticmethod
    def rename(file1, file2):
        """
        重命名文件
        """
        # windows 系统必须先删除文件，再重命名
        if os.path.exists(file2):
            os.remove(file2)
        os.rename(file1, file2)

    @staticmethod
    def remove_macosx(target_dir):
        """
        删除目录下的 __MACOSX 目录
        """
        dir_to_remove = []
        # 遍历目录，记录哪些目录包含 __MACOSX
        for root, dirs, files in os.walk(target_dir):
            for f in files:
                path = os.path.join(root, f)
                try:
                    index = path.index('__MACOSX')
                except ValueError:
                    index = -1
                if index != -1:
                    dir_to_remove.append(path[:(index + len('__MACOSX'))])

        # 删除 __MACOSX 目录
        for d in list(set(dir_to_remove)):
            print(f'删除目录:{d}')
            shutil.rmtree(d)

    @staticmethod
    def _handle_file_by_line(file_path, func):
        """
        调用函数 func 按行处理文件
        """
        with open(file_path, 'r') as f:
            altered_line = [func(line.rstrip()) for line in f]
        with open(file_path, 'w') as f:
            f.write('\n'.join(altered_line))
        return True

    @staticmethod
    def replace_lines_when_contains(file_path, origin, target):
        """
        如果 origin 在某行中，将此行替换为 target
        :param file_path: 文件路径
        :param origin: 查找的内容
        :param target: 要替换成的内容
        """
        File._handle_file_by_line(file_path, lambda line: target if origin in line else line)

    @staticmethod
    def load_settings(file_path):
        """
        加载 setting.gradle 文件
        """
        comment_char1 = "//"
        comment_char2 = "/*"
        comment_char3 = "*/"
        sep = 'include '

        props = []
        with open(file_path, "rt") as f:
            for line in f:
                # 替换掉引号
                line = line.replace("'", '')
                line = line.replace('"', '')
                line = line.strip()
                # 以 include 开始，并且排除注释行(暂不处理多行注释)
                if line and line.startswith(sep) \
                        and not line.startswith(comment_char1) \
                        and comment_char2 not in line \
                        and comment_char3 not in line:
                    props.append(line.split(sep)[-1].strip())
        return props

    @staticmethod
    def read_string(file_path):
        """
        以字符串的形式返回文件内容
        :param file_path: 文件路径
        :return:
        """
        if not os.path.exists(file_path):
            return ''

        with open(file_path, 'rt', encoding='utf-8') as f:
            return f.read().strip()

    @staticmethod
    def read_lines(file_path):
        """
        以字符串数组的形式返回文件内容
        :param file_path: 文件路径
        :return:
        """
        if not os.path.exists(file_path):
            return ''

        with open(file_path, 'rt') as f:
            return f.readlines()

    @staticmethod
    def zip_dir(_dir, _zip_file):
        """
        压缩目录
        :param _dir: 文件所在目录
        :param _zip_file: zip 文件路径
        """
        os.chdir(_dir)
        for root, dirs, files in os.walk(_dir):
            z = zipfile.ZipFile(_zip_file, 'w', zipfile.ZIP_DEFLATED)
            for log in files:
                z.write(log)
            z.close()

    @staticmethod
    def rename(file1, file2):
        """
        重命名文件
        """
        # windows 系统必须先删除文件，再重命名
        if os.path.exists(file2):
            os.remove(file2)
        os.rename(file1, file2)

    @staticmethod
    def save_string(file_path, msg):
        """
        写字符串到文件
        """
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, 'wt') as f:
            return f.write(msg)

    @staticmethod
    def load_properties(file_path, sep='=', comment_char='#'):
        """
        加载 .properties 文件
        """
        if not os.path.exists(file_path):
            return None

        props = {}
        with open(file_path, "rt", encoding='utf8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith(comment_char):
                    key_value = line.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"')
                    props[key] = value
        return props

    @staticmethod
    def replace_file_content(file_path, content1, content2):
        """
        将 file_path 文件中的 content1 替换为 content2
        """
        File._handle_file_by_line(file_path, lambda line: line.replace(content1, content2))
