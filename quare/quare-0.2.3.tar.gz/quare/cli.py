# -*- coding: utf-8 -*-

"""Console script for quare."""

import json
import html

import click

import quare.utils as utils

from .quare import get_user_info, get_user_token, set_user_token
from .quip import QuipClient, QuipError
from .quip_classes import QuipMessage, QuipThread
from .quip_websocket import stream_updates
from .ui_messages import AUTH_ERROR_MESSAGE


@click.group("main", help="")
@click.version_option()
def main():
    """Main quare CLI entry point.

    This runs as the first step in processing any CLI command.
    """


@click.command()
@click.option("-a", "--alias", default="Default", show_default=True)
@click.option("--json", "json_", is_flag=True)
def whoami(alias, json_):
    """Print information about the logged in users."""
    try:
        alias, token = get_user_token(alias)
        user, user_table = get_user_info(token, alias=alias)
        if json_:
            click.echo(json.dumps(user))
        else:
            click.echo(user_table)
    except QuipError as ex:
        if ex.code == 401 and "Invalid access_token" in str(ex):
            raise click.ClickException(AUTH_ERROR_MESSAGE)
        raise  # reraise


@click.command()
@click.option("-a", "--alias", default="Default")
@click.option("-t", "--token", prompt=True)
def auth(alias, token):
    """Store an API authentication token."""
    set_user_token(alias, token.strip())
    click.secho("Token stored!", fg="bright_green")


main.add_command(whoami)
main.add_command(auth)


@main.group("doc")
def document():
    """Commands for interacting with documents."""


@document.command(name="append")
@click.option(
    "-a", "--alias", default="Default", help="Quip `auth' alias", show_default=True
)
@click.option("-c", "--content", help="Markdown to append to document.")
@click.option(
    "-f",
    "--file",
    "fd",
    type=click.File(),
    help="Markdown to append to document. Will ignore --content if provided.",
)
@click.option("-i", "--id", "doc_id", required=True)
@click.option("--json", "json_", is_flag=True)
def doc_append(alias, content, fd, doc_id, json_):
    """Append content to an existing Quip document."""
    _, token = get_user_token(alias)
    content = fd.read() if fd else content
    if not content:
        raise click.UsageError('You must pass either "--content" or "--file".')
    client = QuipClient(token)
    client.edit_document(doc_id, f"\n{content}\n", format="markdown")


@main.group("msg")
def message():
    """Commands for interacting with chats/comment threads."""


@message.command(name="get")
@click.option("-r", "--room", required=True)
@click.option("-s", "--since", type=str, default="1999")
@click.option("-a", "--alias", default="Default", show_default=True)
@click.option("--json", "json_", is_flag=True)
@click.option(
    "-l", "--last", default=200, show_default=True, type=int, help="Last n messages"
)
@click.option(
    "--decending/--ascending",
    "is_desc",
    default=False,
    help="Created date/time sort order",
)
def msg_get(room, last, since, alias, json_, is_desc):
    """Retrieve messages from Quip."""
    token, thread = get_thread(alias, room)
    start_usec = utils.get_usec(since)
    messages = thread.get_messages(token, last_n=last, start_usec=start_usec)
    if not is_desc:
        messages.reverse()
    print_msgs(messages, json_)


@message.command(name="stream")
@click.option("-a", "--alias", default="Default", show_default=True)
def msg_stream(alias):
    """Stream messages via Quip's websocket. Close using CTRL-C"""
    _, token = get_user_token(alias)
    stream_updates(token)


@message.command(name="send")
@click.option("-a", "--alias", default="Default", show_default=True)
@click.option(
    "-c", "--content", help="The body of the message to send. Use '-' for stdin"
)
@click.option("-r", "--room", required=True)
@click.option(
    "--frame",
    type=click.Choice(["bubble", "card", "line"]),
    help="Adjust the display of the message",
)
@click.option("--silent", is_flag=True)
@click.option(
    "-m", "--monospace", help="Format the message as monospace code.", is_flag=True
)
@click.option("--file", "file_", type=click.File("r"))
def msg_send(alias, content, room, frame, silent, monospace, file_):
    """Send messages to a quip chat/document."""
    token, thread = get_thread(alias, room)
    content = click.get_text_stream("stdin").read() if content == "-" else content
    content = file_.read() if file_ else content
    parts = format_msg_content(content, monospace=monospace)
    msg = thread.send_message(
        token, content=content, frame=frame, silent=silent, parts=parts
    )
    if msg:
        messages = thread.get_messages(token, last_n=5)
        messages.reverse()
        print_msgs(messages)


def format_msg_content(content, monospace=False):
    if monospace:
        content = (
            "<pre class='prettyprint'>"
            + html.escape(content, quote=True).replace("\n", "<br>").replace(" ", " ")
            + "</pre>"
        )
        return json.dumps([["monospace", content]])
    else:
        return None


def get_thread(alias, room):
    """Send messages to a quip chat/document."""
    _, token = get_user_token(alias)
    thread = QuipThread.get_thread(token, room)
    return token, thread


def print_msgs(messages, json_=False):
    """Print and format messages."""
    if json_:
        click.echo(json.dumps(messages))
        return
    else:
        for message in messages:
            utils.print_quip_message(QuipMessage.from_dict(message))
