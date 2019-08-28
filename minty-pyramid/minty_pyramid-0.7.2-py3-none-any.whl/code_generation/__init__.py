import click

from . import generate, openapi


@click.command()
@click.option(
    "--filename",
    help="OpenAPI filename (JSON file)",
    default="apidocs/openapi30.json",
)
def generate_routes(filename):
    """Create `routes.py` and `test_routes.py` based on OpenAPI file.

    :param filename: json OpenAPI filename
    :type filename: str
    :param package_name: package name
    :type package_name: str
    """
    file = openapi.load_json_file(filename)
    try:
        file["info"]["x-url-base"]
        package_name = file["info"]["x-package-name"]
    except KeyError:
        print(
            "Add 'x-package-name' and 'x-base-url' to the info block of 'openapi30.json' file "
        )
        return
    routes = openapi.parse_routes(oa_file=file, package_name=package_name)
    generate.routes(routes, package_name)
    generate.test_routes(routes, package_name)
    generate.apidocs(package_name=package_name)


@click.command()
@click.option("--package-name", help="Name of package to create views for.")
@click.option(
    "--filename", help="OpenAPI filename (JSON file)", default="api-spec.json"
)
def generate_views(filename: str, package_name: str):
    """Generate `views.py` with handlers based on OpenAPI file.

    :param filename: json OpenAPI filename
    :type filename: str
    :param package_name: package name
    :type package_name: str
    """
    file = openapi.load_json_file(filename)
    routes = openapi.parse_routes(oa_file=file, package_name=package_name)
    generate.views(routes, package_name)
