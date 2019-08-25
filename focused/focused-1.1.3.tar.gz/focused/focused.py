import html

import click
import requests

from tqdm import tqdm

from .blocks import clean, title


@click.command()
@click.argument(
    "articles",
    nargs=-1
)
@click.option(
    "--no-scripts", "-ns",
    default=True,
    help="Remove scripts in the web page."
)
@click.option(
    "--output", "-o",
    type=click.Choice(["cli", "python", "file"]),
    default="cli"
)
def focus(articles, no_scripts, output):
    # Set headers
    headers = {"user-agent": "focused"}

    if not isinstance(articles, tuple):
        articles = (articles,)

    for article in tqdm(articles):
        # Get website
        response = requests.get(
            article,
            headers=headers
        )
        if response.status_code != 200:
            raise Exception(f"[{response.status_code}]")

        # Remove comments and scripts
        head, body = clean(response.text, no_scripts)

        # Compose web page and unescape html entites
        page = html.unescape(
            f"<!DOCTYPE html>\n<html>\n{head}\n{body}\n</html>"
        )

        if output == "cli":
            click.echo(page)
        elif output == "file":
            with open(f"{title(head)}.html", "w") as file:
                file.write(page)
        else:
            return page


if __name__ == "__main__":
    focus()
