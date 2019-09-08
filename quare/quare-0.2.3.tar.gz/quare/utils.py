import click
import dateparser


def print_quip_message(msg, thread=None):
    thread = f"| ({thread}) " if thread else ""
    msg_header = f"[{msg.created} {thread}| @{msg.author_name}]"
    click.echo(f"""{click.style(msg_header, bold=True)} {msg.text}""")


def get_usec(value):
    if value is None:
        return
    dt = dateparser.parse(value, settings={"RETURN_AS_TIMEZONE_AWARE": True})
    if dt is None:
        raise click.BadParameter("Could not parse datetime")
    usecs = int(dt.timestamp() * 1e6)
    return usecs
