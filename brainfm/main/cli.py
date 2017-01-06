#!/usr/bin/env python

import brainfm
import click
import jmespath
import json
import pathlib
import shlex
import subprocess
import sys
import terminaltables
import webbrowser

CONFIG_PATH = pathlib.Path("~/.brainfm/config").expanduser()
CACHE_PATH = pathlib.Path("~/.brainfm/cache").expanduser()
CACHE_PATH.mkdir(parents=True, exist_ok=True)
STATIONS_PATTERN = jmespath.compile("[*].[station_id, name, canonical_name]")

# TODO graceful failure when config is missing/invalid
with CONFIG_PATH.open() as config_file:
    config = json.load(config_file)

client = brainfm.Connection(config["email"], config["password"])

# TODO expire cached values
if (CACHE_PATH / "svu").exists():
    with (CACHE_PATH / "svu").open() as svu_file:
        client._svu = svu_file.read()
else:
    with (CACHE_PATH / "svu").open(mode="w") as svu_file:
        svu_file.write(client.svu)

cached = {
    "stations": None
}

if (CACHE_PATH / "stations").exists():
    with (CACHE_PATH / "stations").open() as stations_file:
        cached["stations"] = json.load(stations_file)


def render(d, is_error=False):
    print(json.dumps(d, indent=4, sort_keys=True))
    if is_error:
        sys.exit(1)


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
def svu():
    """Display the current siteVisitorUUID"""
    print(client.svu)


@cli.command()
def ls():
    """List available stations"""
    if not cached["stations"]:
        cached["stations"] = client.get_stations()
        with (CACHE_PATH / "stations").open(mode="w") as fp:
            json.dump(cached["stations"], fp, indent=4, sort_keys=True)
    headers = ["id", "name", "canonical"]
    data = sorted(STATIONS_PATTERN.search(cached["stations"]))
    table = terminaltables.AsciiTable(
        table_data=[headers] + data,
        title="Available Stations")
    print(table.table)


@cli.command()
@click.argument("station_id")
def gs(station_id):
    """Get a single station"""
    station = client.get_station(station_id=station_id)
    render(station)


@cli.command()
@click.argument("station_id")
def gt(station_id):
    """Get a station token"""
    token = client.get_token(station_id=station_id)
    render(token)


@cli.command()
@click.argument("station_id")
def url(station_id):
    """Get a station URL"""
    token = client.get_token(station_id=station_id)
    if isinstance(token, brainfm.Error):
        render(token, is_error=True)
    print("https://stream.brain.fm/?tkn=" + token["session_token"])


@cli.command()
@click.argument("station_id")
@click.option("--player", help="Command used to play the stream.  Defaults to browser.")
def play(station_id, player=None):
    """Play a station stream"""
    token = client.get_token(station_id=station_id)
    if isinstance(token, brainfm.Error):
        render(token, is_error=True)
    stream_url = "https://stream.brain.fm/?tkn=" + token["session_token"]
    if player:
        subprocess.run(shlex.split(player) + [stream_url])
    else:
        webbrowser.open_new_tab(stream_url)

main = cli
