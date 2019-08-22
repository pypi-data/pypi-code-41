from blogger.converters.basic_converter import BasicConverter
from blogger.converters.gtts_converter import GTTSConverter


def resolve(key):
    if key == "basic":
        return BasicConverter()

    if key == "gtts":
        return GTTSConverter()

    raise ValueError("There is no valid converter named {}.".format(key))


def supported_converters():
    """
    Get the converters that are supported by this CLI.

    The converters are returned as a tuple of tuples in the following
    format:

        ```
        (
            (
                "converter_key",
                "description of this converter"
            ),

            ...
        )
        ```

    :return tuple: Returns the supported converts.
    """

    return (
        ("basic", "A simple text to speech converter. (default)"),
        ("gtts", "The Google cloud-based text to speech converter API."),
    )
