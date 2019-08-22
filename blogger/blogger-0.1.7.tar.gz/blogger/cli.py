import sys
import click
from blogger import commands


@click.group()
def main():
    """
    Blogger CLI
    """


@main.command()
# Input options
@click.option("--text", help="The text to convert to speech.")
@click.option("--file", help="The file path to the file containing text to convert to speech.")
@click.option("--url", help="Parse an article from a URL.")
@click.option(
    "-p",
    "--provider",
    help="When parsing from a URL, the provider defines the content provider (Ex. Medium, Ghost, etc.)",
)
# Manual provider only options
@click.option(
    "--url-title-selector",
    help="For the manual provider, this specifies the tag and class or id in the DOM that contains the title.",
)
@click.option(
    "--url-content-selector",
    help="For the manual provider, this specifies the tag and class or id in the DOM that contains the content.",
)
# GTTS only options
@click.option("-t", "--token", help="Google API token used for the gtts provider.")
@click.option("-vi", "--voice", help="The voice option.")
@click.option("-vp", "--pitch", help="The pitch of the voice on a scale of -20.0 to 20.0.")
@click.option("-vr", "--rate", help="The rate of speech on a scale of 0.0 to 4.0.")
# General options
@click.option("-c", "--converter", help="The type of text to speech converter to use. Defaults to basic.")
@click.option("-o", "--output", help="The output path for the audio file. If not specified, output will go to STDOUT.")
@click.option("--full-preview/--short-preview", default=False, help="Preview the entire article before converting.")
@click.option("-v", "--verbose/--no-verbose", default=False, help="Provides more debugging information.")
@click.option("-y", "--yes/--no", default=False, help="Assumes yes to prompts.")
# Arguments
@click.argument("inline_text", required=False)
@click.pass_context
def audio(ctx, *args, **kwargs):
    """
    Generates an audio file from text, files, or urls.

    All input is assumed to be in either plain text or HTML format. Any other
    formats could have potential issues during processing.
    """
    with commands.handler():
        return commands.AudioCommand(ctx, *args, **kwargs).run()


@main.command()
@click.option("-l", "--list/--no-list", default=False, help="List all of the available converters.")
@click.pass_context
def converters(ctx, *args, **kwargs):
    """
    Details for text to speech converters.
    """
    with commands.handler():
        return commands.ConvertersCommand(ctx, *args, **kwargs).run()


@main.command()
@click.option("-l", "--list/--no-list", default=False, help="List all of the available content providers.")
@click.pass_context
def providers(ctx, *args, **kwargs):
    """
    Details for content providers.
    """
    with commands.handler():
        return commands.ProvidersCommand(ctx, *args, **kwargs).run()


@main.command()
@click.option("-l", "--list/--no-list", default=False, help="List all of the available voices when using gtts.")
@click.pass_context
def voices(ctx, *args, **kwargs):
    """
    Details for voice options.
    """
    with commands.handler():
        return commands.VoicesCommand(ctx, *args, **kwargs).run()


if __name__ == "__main__":
    sys.exit(main())
