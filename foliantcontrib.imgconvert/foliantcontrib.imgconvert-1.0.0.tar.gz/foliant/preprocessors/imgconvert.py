'''
Preprocessor for Foliant documentation authoring tool.
Converts images from different formats to PNG.
'''

import re

from pathlib import Path
from hashlib import md5
from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'convert_path': 'convert',
        'cache_dir': Path('.imgconvertcache'),
        'image_width': 0,
        'formats': {}
    }

    _img_ref_pattern = re.compile(
        r'(\!\[.*\]\(.+\))'
    )

    _fmt_specified_img_ref_pattern = re.compile(
        r'(^\!\[(?P<caption>.*)\]\((?P<path>((?!\:\/\/).)*[^\/\s]+\.(?P<format>[^\/\s]+))\)$)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._cache_path = (self.project_path / self.options['cache_dir']).resolve()
        self._current_dir_path = self.working_dir.resolve()

        self.logger = self.logger.getChild('imgconvert')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def _process_imgconvert(self, caption: str, img_path: str, format: str) -> str:
        source_img_path = (self._current_dir_path / img_path).resolve()

        self.logger.debug(f'Full path to the source image: {source_img_path}')

        img_hash = md5(f'{self.options["image_width"]}'.encode())

        img_hash.update(format.encode())

        with open(source_img_path, 'rb') as source_img_file:
            source_img_file_body = source_img_file.read()
            img_hash.update(f'{source_img_file_body}'.encode())

        converted_img_path = (self._cache_path / f'{img_hash.hexdigest()}.png').resolve()

        self.logger.debug(f'Converted image path: {converted_img_path}')

        converted_img_ref = f'![{caption}]({converted_img_path})'

        if converted_img_path.exists():
            self.logger.debug(f'Converted image already exists')

            return converted_img_ref

        converted_img_path.parent.mkdir(parents=True, exist_ok=True)

        resize_options = ''

        if self.options['image_width'] > 0:
            resize_options = f'-resize {self.options["image_width"]}'

        try:
            command = (
                f'{self.options["convert_path"]} ' +
                f'"{source_img_path}" ' +
                f'{resize_options} ' +
                f'"{converted_img_path}"'
            )

            self.logger.debug(f'Running the command: {command}')

            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

            self.logger.debug(f'Converted image saved, width: {self.options["image_width"]} (0 means auto)')

        except CalledProcessError as exception:
            self.logger.error(str(exception))

            raise RuntimeError(
                f'Processing of image {img_path} failed: {exception.output.decode()}'
            )

        return converted_img_ref

    def process_imgconvert(self, content: str) -> str:
        processed_content = ''

        content_parts = self._img_ref_pattern.split(content)

        for content_part in content_parts:
            img_ref = self._img_ref_pattern.fullmatch(content_part)

            if img_ref:
                self.logger.debug(f'Image reference found: {img_ref.group(0)}')

                fmt_specified_img_ref = self._fmt_specified_img_ref_pattern.fullmatch(content_part)

                if fmt_specified_img_ref:
                    img_ref_caption = fmt_specified_img_ref.group('caption')
                    img_ref_path = fmt_specified_img_ref.group('path')
                    img_ref_format = fmt_specified_img_ref.group('format').lower()

                    self.logger.debug(
                        f'Caption: {img_ref_caption}, ' +
                        f'user-specified path: {img_ref_path}, ' +
                        f'format: {img_ref_format}'
                    )

                    if img_ref_format != 'png' or self.options['image_width'] > 0:

                        allowed_targets = self.options['formats'].get(img_ref_format, {}).get('targets', [])

                        self.logger.debug(f'Allowed targets: {allowed_targets} (empty set means all)')

                        if not allowed_targets or self.context['target'] in allowed_targets:
                            self.logger.debug('The image should be converted')

                            content_part = self._process_imgconvert(img_ref_caption, img_ref_path, img_ref_format)

                    else:
                        self.logger.debug('Skipping PNG image with no width to resize')

                else:
                    self.logger.debug('Format not specified, or remote image referenced. Skipping')

            processed_content += content_part

        return processed_content

    def apply(self):
        self.logger.info('Applying preprocessor')

        for markdown_file_path in self.working_dir.rglob('*.md'):
            self.logger.debug(f'Processing the file: {markdown_file_path}')

            self._current_dir_path = markdown_file_path.parent.resolve()

            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            processed_content = self.process_imgconvert(content)

            if processed_content:
                with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                    markdown_file.write(processed_content)

        self.logger.info('Preprocessor applied')
