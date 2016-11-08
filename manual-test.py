from pathlib import Path
from brainfm import Connection

config_location = Path("~/.brainfm/config")
with config_location.expanduser().open() as f:
    config = {}
    for line in f.readlines():
        key, value = line.split("=")
        config[key.strip()] = value.strip()


connection = Connection()
connection.login(config["email"], config["password"])
connection.load_operations()
print(connection.get_stations())
