import configparser
import tempfile
from contextlib import contextmanager
from pathlib import Path

import click

from send_to_kindle.converter import html_to_mobi
from send_to_kindle.downloader import download_images, get_article
from send_to_kindle.sender.email_sender import EmailSender


def get_config_path(config_file):
    if config_file is None:
        config_file = Path(Path.home(), "send_to_kindle.ini").resolve()
    else:
        config_file = Path(config_file)
    if not config_file.exists():
        raise ValueError("The configuration file does not exist")
    return config_file


def get_config(config_file):
    config_file = get_config_path(config_file)
    parser = configparser.ConfigParser()
    parser.read(str(config_file))
    return parser


@contextmanager
def write_temp_html(html, folder=None, delete=True):
    try:
        temp_html = tempfile.NamedTemporaryFile(
            suffix=".html", mode="w", dir=folder, delete=delete
        )
        temp_html.write(html)
        temp_html.flush()
        yield Path(temp_html.name)
    finally:
        temp_html.close()


# pylint: disable=too-many-locals,too-many-arguments
@click.command()
@click.argument("url")
@click.option("--config", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option(
    "--output", "-o", type=click.Path(exists=True, file_okay=False), default=None
)
@click.option("--keep", "-k", type=click.BOOL, default=False)
def download(url, config, output, keep):
    configuration = get_config(config)
    from_email = configuration.get("mail_account", "from")
    password = configuration.get("mail_account", "password")
    to_email = configuration.get("mail_account", "to")
    host = configuration.get("mail_server", "host")
    port = configuration.getint("mail_server", "port")
    try:
        use_tls = configuration.getboolean("mail_server", "use_tls")
    except configparser.NoOptionError:
        use_tls = True
    kindlegen_path = Path(configuration.get("kindlegen", "path"))

    article = get_article(url)

    # pylint: disable=bad-continuation
    with write_temp_html(
        article.to_html().prettify(), folder=output, delete=not keep
    ) as html:
        download_images(html.parent, article.image_map)
        mobi_file = html_to_mobi(kindlegen_path, html, article.title)

    sender = EmailSender(from_email, password, host, port, use_tls)
    sender.send_mail(article.title, to_email, mobi_file)


if __name__ == "__main__":
    download()  # pylint: disable=no-value-for-parameter
