#coding: utf8
from __future__ import absolute_import
import os
import json
import base64

docker_image_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
docker_image_original_dir = os.path.join(docker_image_dir, 'original_files')



def dump_docker_image_files(image_name):
    image_files_filepath = os.path.join(docker_image_dir, 'files', '%s.py'%image_name)
    scripts_folder = os.path.join(docker_image_dir, 'original_files', image_name)
    if not os.path.isdir(scripts_folder):
        return # ignore
    sub_filenames = os.listdir(scripts_folder)
    files_data = {}
    for sub_filename in sub_filenames:
        if sub_filename.startswith('.'):
            continue
        #if sub_filename in ['Dockerfile']:
        #    continue
        sub_filepath = os.path.join(scripts_folder, sub_filename)
        if not os.path.isfile(sub_filepath):
            continue
        with open(sub_filepath, 'rb') as f:
            file_content = f.read()
        files_data[sub_filename] = base64.b64encode(file_content)
    files_data_s = json.dumps(files_data)
    image_files_content = 'import json,base64\nfiles_data="""%s"""\nfiles_data=json.loads(files_data)\nfiles_data={k:base64.b64decode(v) for k,v in files_data.items()}' % files_data_s
    with open(image_files_filepath, 'wb') as f:
        f.write(image_files_content)



def dump_all():
    print('dump all for %s' % docker_image_original_dir)
    sub_filenames = os.listdir(docker_image_original_dir)
    for sub_filename in sub_filenames:
        sub_filepath = os.path.join(docker_image_original_dir, sub_filename)
        if not os.path.isdir(sub_filepath):
            continue
        image_name = sub_filename
        dump_docker_image_files(image_name)


if __name__ == '__main__':
    dump_all()





