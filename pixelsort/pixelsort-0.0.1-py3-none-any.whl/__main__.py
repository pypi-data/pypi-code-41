import logging
from PIL import Image
from pixelsort.pixelsort import pixelsort
from pixelsort.util import id_generator

def _main(args):
    output_path = args.pop("output_image_path")
    logging.debug("Opening image...")
    args["image"] = Image.open(args.pop("image_input_path"))
    mask_path = args.pop("mask_path")
    if mask_path:
        logging.debug("Opening mask...")
        args["mask_image"] = Image.open(mask_path)
    interval_file_path = args.pop("interval_file_path")
    if interval_file_path:
        logging.debug("Opening interval image...")
        args["interval_image"] = Image.open(interval_file_path)
    output_img = pixelsort(**args)
    logging.debug("Saving image...")
    if not output_path:
        output_path = id_generator() + ".png"
        logging.warning(f"No output path provided, defaulting to {output_path}")
    output_img.save(output_path)


if __name__ == "__main__":
    from pixelsort.argparams import parse_args
    _main(parse_args())