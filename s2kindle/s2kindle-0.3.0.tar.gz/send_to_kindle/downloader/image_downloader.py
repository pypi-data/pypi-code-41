import shutil
from pathlib import Path

import requests
from PIL import Image


def download_images(folder, image_map):
    for image_id, img_url in image_map.items():
        image_path = Path(folder, image_id)
        # pylint: disable=bad-continuation
        with open(image_path, "wb") as output_file, requests.get(
            img_url, stream=True
        ) as response:
            shutil.copyfileobj(response.raw, output_file)
        image = Image.open(str(image_path.resolve()))
        rgb_im = image.convert("RGB")
        rgb_im.save(str(image_path.resolve()))
