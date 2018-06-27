#!/usr/bin/env python
import shlex
import subprocess
import webbrowser

import click
import jmespath
import terminaltables

import brainfm


STATIONS_PATTERN = jmespath.compile("[*].[id, name, string_id]")


def validate_client(client):
    if not client.sid:
        raise click.UsageError(
            "missing environment variable {}\n".format(brainfm.SID_ENVIRON_KEY) +
            "Did you run `brain init` and export the variable?"
        )


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):
    ctx.obj = brainfm.Connection()


@cli.command()
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, confirmation_prompt=True, hide_input=True)
@click.option("--simple", is_flag=True, default=False)
@click.pass_obj
def init(client, email, password, simple):
    """Create a session id

    By default prints out usage instructions.  For programmatic
    use, pass --simple to only print the bare sid.
    """
    client.login(email, password)
    sid = client.sid
    if simple:
        print(sid)
    else:
        print("\nAdd the following to your .profile, .bashrc, or equivalent:\n")
        print("    export {}=\"{}\"\n".format(brainfm.SID_ENVIRON_KEY, sid))


@cli.command()
@click.pass_obj
def sid(client):
    """Print out the session id"""
    validate_client(client)
    print(client.sid)


@cli.command()
@click.pass_obj
def ls(client):
    """List stations"""
    validate_client(client)
    stations = client.list_stations()
    headers = ["id", "name", "string_id"]
    data = sorted(STATIONS_PATTERN.search(stations))
    table = terminaltables.AsciiTable(
        table_data=[headers] + data,
        title="Available Stations")
    print(table.table)


@cli.command()
@click.argument("station_id")
@click.pass_obj
def gt(client, station_id):
    """Create a station token"""
    validate_client(client)
    token = client.get_token(station_id)
    print(token)


@cli.command()
@click.argument("station_id")
@click.pass_obj
def url(client, station_id):
    """Create a station url"""
    validate_client(client)
    token = client.get_token(station_id)
    print(brainfm.build_stream_url(token))


@cli.command()
@click.argument("station_id")
@click.option("--player", help="Command used to play the stream.  Defaults to browser.")
@click.pass_obj
def play(client, station_id, player=None):
    """Play a station"""
    validate_client(client)
    token = client.get_token(station_id)
    stream_url = brainfm.build_stream_url(token)
    if player:
        subprocess.run(shlex.split(player) + [stream_url])
    else:
        webbrowser.open_new_tab(stream_url)


main = cli
