#!/usr/bin/env python

import brainfm
import click
import jmespath
import json
import pathlib
import requests
import sys
import terminaltables
import webbrowser

CONFIG_PATH = pathlib.Path("~/.brainfm/config").expanduser()
CACHE_PATH = pathlib.Path("~/.brainfm/cache").expanduser()
CACHE_PATH.mkdir(parents=True, exist_ok=True)
STATIONS_PATTERN = jmespath.compile("[*].[station_id, name, canonical_name]")

# TODO graceful failure when config is missing/invalid
with CONFIG_PATH.open() as fp:
    config = json.load(fp)

client = brainfm.Connection(config["email"], config["password"])

# TODO expire cached values
if (CACHE_PATH / "svu").exists():
    with (CACHE_PATH / "svu").open() as fp:
        client._svu = fp.read()
else:
    with (CACHE_PATH / "svu").open(mode="w") as fp:
        fp.write(client.svu)

cached = {
    "stations": None
}

if (CACHE_PATH / "stations").exists():
    with (CACHE_PATH / "stations").open() as fp:
        cached["stations"] = json.load(fp)


@click.group()
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
@click.option("--station-id", "-id", help="Station ID", required=True)
def gs(station_id):
    """Get a single station"""
    try:
        output = client.get_station(station_id=station_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            output = {
                "code": "UnknownStationID",
                "error": "Unknown station {!r}".format(station_id)}
        else:
            raise e
    print(json.dumps(output, indent=4, sort_keys=True))


@cli.command()
@click.option("--station-id", "-id", help="Station ID", required=True)
def gt(station_id):
    try:
        output = client.get_token(station_id=station_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            output = {
                "code": "UnknownStationID",
                "error": "Unknown station {!r}".format(station_id)}
        else:
            raise e
    print(json.dumps(output, indent=4, sort_keys=True))


@cli.command()
@click.argument("station_id")
def play(station_id):
    try:
        token = client.get_token(station_id=station_id)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(json.dumps(
                {
                    "code": "UnknownStationID",
                    "error": "Unknown station {!r}".format(station_id)},
                indent=4, sort_keys=True))
            sys.exit(1)
        else:
            raise e
    webbrowser.open_new_tab(
        "https://stream.brain.fm/?tkn=" + token["session_token"])

main = cli
