#!/usr/bin/env python

import json
import pathlib
import shlex
import subprocess
import webbrowser

import click
import jmespath
import terminaltables

import brainfm


CONFIG_PATH = pathlib.Path("~/.brainfm/config").expanduser()
CACHE_PATH = pathlib.Path("~/.brainfm/cache").expanduser()
CACHE_PATH.mkdir(parents=True, exist_ok=True)
STATIONS_PATTERN = jmespath.compile("[*].[id, name, string_id]")


def build_client():

    # TODO expire cached values
    try:
        sid = (CACHE_PATH / "sid").read_text().strip()
    except Exception:
        sid = None
        with CONFIG_PATH.open() as config_file:
            config = json.loads(config_file.read().strip())

    client = brainfm.Connection(sid=sid)
    if sid is None:
        client.login(config["email"], config["password"])
        (CACHE_PATH / "sid").write_text(client.sid.strip())
    return client


client = build_client()


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
def sid():
    """Display the current siteVisitorUUID"""
    print(client.sid)


@cli.command()
def ls():
    """List available stations"""
    stations = client.get_stations()
    headers = ["id", "name", "string_id"]
    data = sorted(STATIONS_PATTERN.search(stations))
    table = terminaltables.AsciiTable(
        table_data=[headers] + data,
        title="Available Stations")
    print(table.table)


@cli.command()
@click.argument("station_id")
def gt(station_id):
    """Get a station token"""
    token = client.get_token(station_id)
    print(token)


@cli.command()
@click.argument("station_id")
def url(station_id):
    """Get a station URL"""
    token = client.get_token(station_id)
    print(brainfm.build_stream_url(token))


@cli.command()
@click.argument("station_id")
@click.option("--player", help="Command used to play the stream.  Defaults to browser.")
def play(station_id, player=None):
    """Play a station stream"""
    token = client.get_token(station_id)
    stream_url = brainfm.build_stream_url(token)
    if player:
        subprocess.run(shlex.split(player) + [stream_url])
    else:
        webbrowser.open_new_tab(stream_url)


main = cli
