import os
import click

from blogger.converters import resolve as resolve_converter
from blogger.providers import resolve as resolve_provider
from blogger.utils import string

from .base import BaseCommand


class AudioCommand(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.converter_key = self.options.get("converter") or "basic"
        self.converter = resolve_converter(self.converter_key)

        self.provider_key = self.options.get("provider") or "manual"
        self.provider = resolve_provider(self.provider_key)

        self.output = self.options.get("output") or "./blogger.mp3"

    def run(self):
        self.text = self.get_original_text()
        if not self.validate():
            return

        # Determine what the preview value is going to be. If the --full-preview
        # flag is passed, then we will show the entire text to them before
        # processing. Otherwise, it will be a truncated snippet of the
        # beginning of the text.
        preview = self.text
        if not self.options.get("full_preview"):
            preview = self.text_preview(length=600, indent=4, chunk=50)

        click.echo(click.style("Converting audio using the {} converter:".format(self.converter_key), fg="blue"))
        click.echo("  {title}\n{text}".format(title=click.style("Text Preview:", fg="blue"), text=preview))

        click.echo(click.style("Processing...", fg="blue"))
        self.converter.out(
            self.text,
            path=self.output,
            token=self.options.get("token"),
            voice=self.options.get("voice"),
            pitch=self.options.get("pitch"),
            rate=self.options.get("rate"),
        )
        click.echo(click.style("Successfully outputted to {}".format(self.output), fg="green"))

    def validate(self):
        """
        Validate the input data.

        :return bool: Returns True if validate data, False otherwise.
        """
        if os.path.isfile(self.output):
            if not self.options.get("yes", False) and not click.confirm(
                click.style(
                    "The output file already exists ({}). Are you sure you want to overwrite?".format(self.output),
                    fg="yellow",
                ),
                default=False,
            ):
                click.echo(click.style("Exiting.", fg="yellow"))
                return False

        return True

    def text_preview(self, length, indent=0, chunk=None):
        """
        Gets a short preview of the text passed into the command.
        """
        text = self.text

        if len(text) > length:
            text = text[0:length] + "..."

        if chunk and indent:
            chunks = string.chunk(text, chunk_size=chunk)
            text = "".join(["{indent}{text}\n".format(indent=" " * indent, text=chunk) for chunk in chunks])

        return text

    def get_original_text(self):
        """
        Handle getting the text passed into the command. There's three possible
        scenarios for how text can be passed into the CLI:

          1. via STDIN
          2. via command line argument (--text)
          2. via file path (--file)
          3. via URL (--url)

        :return str: Returns the text that needs to be converted to speech.
        """

        if self.options.get("file"):
            path = self.options.get("file")

            try:
                with open(path) as input_file:
                    return string.html_to_text(input_file.read())
            except:
                raise ValueError("The input file {} does not exist or is not readable.".format(path))

        if self.options.get("text"):
            return string.html_to_text(self.options.get("text"))

        if self.options.get("inline_text"):
            return string.html_to_text(self.options.get("inline_text"))

        if self.options.get("url"):
            return self.provider.read(
                url=self.options.get("url"),
                title_selector=self.options.get("url_title_selector"),
                content_selector=self.options.get("url_content_selector"),
            )

        raise ValueError(
            "There is no text to process. Please see `--help` for more details "
            "on how to pass text into the audio command."
        )
