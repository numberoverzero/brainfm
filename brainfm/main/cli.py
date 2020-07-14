#!/usr/bin/env python
import shlex
import subprocess
import webbrowser

import click
import jmespath
import terminaltables

import brainfm

ENVKEY_SID = "BRAINFM_SID"
ENVKEY_API_ENDPOINT = "BRAINFM_API_ENDPOINT"
ENVKEY_STREAM_ENDPOINT = "BRAINFM_STREAM_ENDPOINT"
STATIONS_PATTERN = jmespath.compile("[*].[id, name, string_id, length]")


def validate_client(client: brainfm.Connection):
    if not client.sid:
        raise click.UsageError(
            "missing option --sid or environment variable {}\n".format(ENVKEY_SID) +
            "Did you run `brain init` and export the variable?"
        )


@click.group()
@click.version_option()
@click.option("--sid", envvar=ENVKEY_SID)
@click.option("--api-endpoint", envvar=ENVKEY_API_ENDPOINT)
@click.option("--stream-endpoint", envvar=ENVKEY_STREAM_ENDPOINT)
@click.pass_context
def cli(ctx, sid, api_endpoint, stream_endpoint):
    ctx.obj = brainfm.Connection(
        sid=sid,
        api_endpoint=api_endpoint,
        stream_endpoint=stream_endpoint)


@cli.command()
@click.option("--email", prompt=True)
@click.option("--password", prompt=True, confirmation_prompt=True, hide_input=True)
@click.option("--simple", is_flag=True, default=False)
@click.pass_obj
def init(client: brainfm.Connection, email, password, simple):
    """Create a session id.  Use --simple to omit instructions"""
    client.login(email, password)
    if simple:
        print(client.sid)
    else:
        args = ENVKEY_SID, client.sid, ENVKEY_STREAM_ENDPOINT, client.stream_endpoint
        print("\nAdd the following to your .profile, .bashrc, or equivalent:\n")
        print("    export {}=\"{}\"\n    export {}=\"{}\"\n".format(*args))


@cli.command()
@click.pass_obj
def details(client: brainfm.Connection):
    """Describe the connection params"""
    validate_client(client)
    print("sid {}\napi {}\nstream {}\n".format(
        client.sid,
        client.api_endpoint,
        client.stream_endpoint
    ))


@cli.command()
@click.pass_obj
@click.option("-a", is_flag=True, default=False)
def ls(client: brainfm.Connection, a):
    """List stations"""
    validate_client(client)
    stations = client.list_stations()
    headers = ["id", "name", "string_id", "length"]
    data = sorted(STATIONS_PATTERN.search(stations))
    if a:
        ls_title = "All Stations"
    else:
        ls_title = "Playable Stations"
        data = [station for station in data if station[3]]
    for i, station in enumerate(data[:]):
        duration = int(station[3])
        if duration == 0:
            data[i][3] = "None"
        elif duration == 60:
            data[i][3] = "1 hr"
        elif duration > 60:
            data[i][3] = str(int(duration / 60)) + " hrs"
        else:
            data[i][3] = str(duration) + " mins"
    table = terminaltables.AsciiTable(table_data=[headers] + data, title=ls_title)
    print(table.table)


@cli.command()
@click.argument("station_id")
@click.pass_obj
def gt(client: brainfm.Connection, station_id):
    """Create a station token"""
    validate_client(client)
    token = client.get_token(station_id)
    print(token)


@cli.command()
@click.argument("station_id")
@click.pass_obj
def url(client: brainfm.Connection, station_id):
    """Create a station url"""
    validate_client(client)
    token = client.get_token(station_id)
    print(client.make_stream_url(token))


@cli.command()
@click.argument("station_id")
@click.option("--player", help="Command used to play the stream.  Defaults to browser.")
@click.pass_obj
def play(client: brainfm.Connection, station_id, player=None):
    """Play a station"""
    validate_client(client)
    token = client.get_token(station_id)
    stream_url = client.make_stream_url(token)
    if player:
        subprocess.run(shlex.split(player) + [stream_url])
    else:
        webbrowser.open_new_tab(stream_url)


main = cli
