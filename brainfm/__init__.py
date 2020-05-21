import os

import requests


__version__ = "1.0.0"

__all__ = [
    "BROWSER",
    "DEFAULT_USER_AGENT",
    "DEFAULT_API_ENDPOINT",
    "DEFAULT_STREAM_ENDPOINT",
    "Connection",
]

SID_ENVIRON_KEY = "BRAINFM_SID"

# not the most reliable, but I don't think it matters too much anyway
# src: https://techblog.willshouse.com/2012/01/03/most-common-user-agents/
# percent 8.9%
# Last Updated: Thu, 21 May 2020 21:32:00 +0000
BROWSER = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/81.0.4044.138 Safari/537.36")
DEFAULT_USER_AGENT = "github.com/numberoverzero/brainfm v" + __version__
DEFAULT_API_ENDPOINT = "https://www1.brain.fm"
DEFAULT_STREAM_ENDPOINT = "https://stream.brain.fm/?tkn="


class Connection:
    """Use an SID from ``brainfm.SID_ENVIRON_KEY`` or Connection.login(email, pw)

    If brain.fm starts filtering on user-agent,
    set :attr:`Connection.user_agent` to :data:`brainfm.BROWSER`.
    """

    def __init__(
            self, sid=None, user_agent=DEFAULT_USER_AGENT,
            api_endpoint=DEFAULT_API_ENDPOINT,
            stream_endpoint=DEFAULT_STREAM_ENDPOINT):
        self.session = requests.Session()
        self.api_endpoint = api_endpoint
        self.stream_endpoint = stream_endpoint
        self.user_agent = user_agent
        # try to load sid from env vars
        if sid is None:
            sid = os.environ.get(SID_ENVIRON_KEY, None)
        self.sid = sid

    @property
    def user_agent(self) -> str:
        return self.session.headers["User-Agent"]

    @user_agent.setter
    def user_agent(self, value: str) -> None:
        self.session.headers["User-Agent"] = value

    @property
    def sid(self) -> str:
        return self.session.cookies.get("connect.sid", None)

    @sid.setter
    def sid(self, value: str) -> None:
        self.session.cookies["connect.sid"] = value

    @sid.deleter
    def sid(self) -> None:
        del self.session.cookies["connect.sid"]

    def login(self, email: str, password: str) -> dict:
        del self.sid
        payload = {"email": email, "password": password, "type": "LOGIN"}
        # populates session.cookies["connect.sid"]
        r = self.session.post(self._make_api_path("/login"), json=payload)
        r.raise_for_status()
        return r.json()

    def list_stations(self) -> list:
        r = self.session.get(self._make_api_path("/stations"))
        r.raise_for_status()
        return r.json()["stations"]

    def get_token(self, station_id: int) -> str:
        """Return a token for the given station that can be used to make a stream url"""
        r = self.session.post(self._make_api_path("/tokens"), json={"stationId": station_id})
        r.raise_for_status()
        songs = r.json()["songs"]
        return songs[0]["token"]

    def _make_api_path(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.api_endpoint + path

    def make_stream_url(self, token: str) -> str:
        return self.stream_endpoint + token
