from .ghost import GhostProvider
from .manual import ManualProvider
from .medium import MediumProvider


def resolve(key):
    if key == "ghost":
        return GhostProvider()

    if key == "manual":
        return ManualProvider()

    if key == "medium":
        return MediumProvider()

    raise ValueError("There is no valid provider named {}.".format(key))


def supported_providers():
    """
    Get the content providers that are supported by this CLI.

    The providers are returned as a tuple of tuples in the following
    format:

        ```
        (
            (
                "provider_key",
                "description of this provider"
            ),

            ...
        )
        ```

    :return tuple: Returns the supported providers.
    """

    return (
        ("manual", "Uses user provided input to determine how to parse content (default)"),
        ("ghost", "Handles parsing content for Ghost hosted blogs (https://ghost.io)"),
        ("medium", "Handles parsing content written on Medium (https://medium.com)"),
    )
