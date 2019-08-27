import click
import json

from .util import createGirderClient


@click.command(
    name="collection_query",
    short_help="Query collections using Mongo.",
    help="Query collections using the specified Mongo query.",
)
@click.option(
    "-q", "--query", required=False, help="The query to search with."
)
@click.option(
    "-d",
    "--data",
    required=False,
    help="A file containing the query to search with.",
)
@click.option(
    "-u",
    "--username",
    required=False,
    help="The user's username on the Girder instance.",
)
@click.option(
    "-p",
    "--password",
    required=False,
    help="The user's password on the Girder instance.",
)
@click.option(
    "--api-key",
    required=False,
    help="The api key for the Girder instance being used.",
)
@click.option(
    "--api-url",
    required=True,
    help="The api url of the Girder instance being used.",
)
def main(query, data, username, password, api_key, api_url):
    if query and data:
        raise click.ClickException("Both modes (Query and Data) specified.")
    elif query:
        loadedQuery = query
    elif data:
        loadedQuery = open(data, "r").read()
    else:
        raise click.ClickException("Query or Data must be specified.")

    gc = createGirderClient(
        api_url, api_key=api_key, username=username, password=password
    )

    response = gc.sendRestRequest(
        method="GET",
        path="collection/geobrowser/search",
        parameters={"query": loadedQuery},
    )

    click.echo(json.dumps(response, indent=4))


if __name__ == "__main__":
    main()
