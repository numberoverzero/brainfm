# import http.client
from pathlib import Path
from brainfm import Connection
# http.client.HTTPConnection.debuglevel = 1

config_location = Path("~/.brainfm/config")
with config_location.expanduser().open() as f:
    config = {}
    for line in f.readlines():
        key, value = line.split("=")
        config[key.strip()] = value.strip()


connection = Connection(**config)
print(connection.get_token(station_id=55))
