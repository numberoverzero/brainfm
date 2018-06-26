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

from .lazy import deferred


CONFIG_PATH = pathlib.Path("~/.brainfm/config").expanduser()
STATIONS_PATTERN = jmespath.compile("[*].[id, name, string_id]")


# deferred so that brain --help doesn't
# build a client just to dump usage info
@deferred
def build_client():
    with CONFIG_PATH.open() as config_file:
        config = json.loads(config_file.read().strip())
    client = brainfm.Connection()
    client.login(config["email"], config["password"])
    return client


client = build_client()


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
def sid():
    """Create a session id"""
    print(client.sid)


@cli.command()
def ls():
    """List stations"""
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
    """Create a station token"""
    token = client.get_token(station_id)
    print(token)


@cli.command()
@click.argument("station_id")
def url(station_id):
    """Create a station url"""
    token = client.get_token(station_id)
    print(brainfm.build_stream_url(token))


@cli.command()
@click.argument("station_id")
@click.option("--player", help="Command used to play the stream.  Defaults to browser.")
def play(station_id, player=None):
    """Play a station"""
    token = client.get_token(station_id)
    stream_url = brainfm.build_stream_url(token)
    if player:
        subprocess.run(shlex.split(player) + [stream_url])
    else:
        webbrowser.open_new_tab(stream_url)


main = cli
