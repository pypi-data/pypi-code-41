import click
from .base import BaseCommand

VOICES = (
    # United States Accents
    ("US-A", "United States english accent option A", "en-US-Wavenet-A"),
    ("US-B", "United States english accent option B", "en-US-Wavenet-B"),
    ("US-C", "United States english accent option C", "en-US-Wavenet-C"),
    ("US-D", "United States english accent option D", "en-US-Wavenet-D"),
    ("US-E", "United States english accent option E", "en-US-Wavenet-E"),
    ("US-F", "United States english accent option F", "en-US-Wavenet-F"),
    # Australian Accents
    ("AU-A", "Australian english accent option A", "en-AU-Wavenet-A"),
    ("AU-B", "Australian english accent option B", "en-AU-Wavenet-B"),
    ("AU-C", "Australian english accent option C", "en-AU-Wavenet-C"),
    ("AU-D", "Australian english accent option D", "en-AU-Wavenet-D"),
    # Great Britain Accents
    ("GB-A", "British english accent option A", "en-GB-Wavenet-A"),
    ("GB-B", "British english accent option B", "en-GB-Wavenet-B"),
    ("GB-C", "British english accent option C", "en-GB-Wavenet-C"),
    ("GB-D", "British english accent option D", "en-GB-Wavenet-D"),
    # Indian Accents
    ("IN-A", "Indian english accent option A", "en-IN-Wavenet-A"),
    ("IN-B", "Indian english accent option B", "en-IN-Wavenet-B"),
    ("IN-C", "Indian english accent option C", "en-IN-Wavenet-C"),
)


class VoicesCommand(BaseCommand):
    def run(self):
        """
        Entry point for `blogger voices`.
        """
        if self.options.get("list", False):
            return self.print_list()
        return self.print_help()

    def print_list(self):
        """
        Iterates and prints the list of supported voices.

        These voices are only relevant when using the google cloud API for text
        to speech.
        """
        for voice in VOICES:
            click.echo("{key} {description}".format(key=click.style(voice[0], fg="green"), description=voice[1]))
