import os
import click

from hawking.encoder.vgg import VGGImageEncoder
from hawking.encoder.resnet50 import ResNet50ImageEncoder


@click.command()
@click.argument('image_dir')
@click.option('--arch', '-a', help="Underlying Neural Nets architecture: vgg16, resnet50", default="resnet50")
def encode_images(image_dir, arch):
    files = os.listdir(image_dir)
    if arch == 'vgg16':
        enc = VGGImageEncoder()
    elif arch == 'resnet50':
        enc = ResNet50ImageEncoder()
    for f in files:
        path = os.path.join(image_dir, f)
        v = enc.encode(path)
        print(v.shape)
        print(v)
        input()


if __name__ == '__main__':
    encode_images()
