import os
from setuptools import find_packages, setup
from setuptools.command.egg_info import egg_info
import tarfile
# this will break with python3...
from urllib import urlretrieve

class DownloadModelFiles(egg_info):
    def run(self):
        root_dir = os.path.abspath(os.path.dirname(__file__))
        models_dir = os.path.join(root_dir, 'thumbor_extras/detectors/model_files')
        if not os.path.exists(models_dir):
            os.mkdir(models_dir)

        # dnn_face_detector
        face_detector_param_filename = os.path.join(models_dir, 'opencv_face_detector_uint8.pb')
        if not os.path.exists(face_detector_param_filename):
            print('downloading dnn_face_detector model parameters file')
            urlretrieve(
                'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180220_uint8/opencv_face_detector_uint8.pb',
                face_detector_param_filename
            )

        face_detector_config_filename = os.path.join(models_dir, 'opencv_face_detector.pbtxt')
        if not os.path.exists(face_detector_config_filename):
            print('downloading dnn_face_detector model config file')
            urlretrieve(
                'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/opencv_face_detector.pbtxt',
                face_detector_config_filename
            )

        # dnn_object_detector
        model_name = 'ssd_mobilenet_v2_coco_2018_03_29'
        object_detector_param_filename = os.path.join(models_dir, 'frozen_inference_graph.pb')
        if not os.path.exists(object_detector_param_filename):
            print('downloading and extracting dnn_object_detector model params file')
            tar_filename = model_name + '.tar.gz'
            tar_filepath = os.path.join(root_dir, tar_filename)
            urlretrieve(
                'http://download.tensorflow.org/models/object_detection/' + tar_filename,
                tar_filepath
            )
            tar = tarfile.open(tar_filepath)
            extract_filename = os.path.join(model_name, 'frozen_inference_graph.pb')
            tar.extract(
                extract_filename,
                path=root_dir
            )
            tar.close()
            os.remove(tar_filepath)
            os.rename(
                os.path.join(root_dir, extract_filename),
                object_detector_param_filename
            )
            os.rmdir(os.path.join(root_dir, model_name))
        config_filename = model_name + '.pbtxt'
        object_detector_config_filename = os.path.join(models_dir, config_filename)
        if not os.path.exists(object_detector_config_filename):
            print('downloading dnn_object_detector model config file')
            urlretrieve(
                'https://raw.githubusercontent.com/opencv/opencv_extra/master/testdata/dnn/' + config_filename,
                object_detector_config_filename
            )

        # continue with the normal process
        egg_info.run(self)

with open('readme.md') as f:
    long_description = f.read()

setup(
    name='thumbor_extras',
    version='1.0.1',
    author='Austin Blanton',
    author_email='imaus10@gmail.com',
    description='Some useful extensions to thumbor - extra filters and detectors.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/imaus10/thumbor_extras',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2 :: Only', # pending thumbor's upgrade to python3
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    install_requires=[
        'opencv-python',
        'thumbor'
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'mock',
        'pytest'
    ],
    cmdclass={
        'egg_info' : DownloadModelFiles,
    },
    include_package_data=True
 )
