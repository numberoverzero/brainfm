import json
import re
import requests


__version__ = "3.0.0"

__all__ = [
    "BROWSER",
    "Connection",
]

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

STREAM_ENDPOINT_V0 = "https://stream.brain.fm"
STREAM_ENDPOINT_V1 = "https://stream2.brain.fm"

APP_HTML_URL = "https://www1.brain.fm/app"
RE_FEATURES = re.compile(r"window\.__FEATURES__ = (?P<features>{[^}]*?});")


class Connection:
    """You must set Connection.sid or call Connection.login(email, pw)

    If brain.fm starts filtering on user-agent,
    set :attr:`Connection.user_agent` to :data:`brainfm.BROWSER`.
    """

    def __init__(
            self, sid=None, user_agent=DEFAULT_USER_AGENT,
            api_endpoint=None, stream_endpoint=None):
        self.session = requests.Session()
        self.user_agent = user_agent
        self.sid = sid

        self.api_endpoint = api_endpoint or DEFAULT_API_ENDPOINT
        # lazy compute stream_endpoint when it's needed
        self._stream_endpoint = stream_endpoint

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

    @property
    def stream_endpoint(self) -> str:
        if not self._stream_endpoint:
            self._apply_fallback_features()
        return self._stream_endpoint

    @stream_endpoint.setter
    def stream_endpoint(self, value: str) -> None:
        self._stream_endpoint = value

    @stream_endpoint.deleter
    def stream_endpoint(self) -> None:
        self._stream_endpoint = None

    def login(self, email: str, password: str) -> dict:
        del self.sid
        payload = {"email": email, "password": password, "type": "LOGIN"}
        # populates session.cookies["connect.sid"]
        r = self.session.post(self._make_api_path("/login"), json=payload)
        r.raise_for_status()
        j = r.json()
        self._apply_features(j["features"])
        return j

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

    def make_stream_url(self, token: str) -> str:
        endpoint = self.stream_endpoint
        if not endpoint.endswith("/?tkn="):
            endpoint += "/?tkn="
        return endpoint + token

    def _make_api_path(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.api_endpoint + path

    def _apply_features(self, features: dict) -> None:
        # don't override _stream_endpoint if a value is already set;
        #   the user may want to ignore the feature flags or is using a
        #   different service that has the same interface as brain.fm
        if not self._stream_endpoint:
            if features.get("new-stream", False):
                self._stream_endpoint = STREAM_ENDPOINT_V1
            else:
                self._stream_endpoint = STREAM_ENDPOINT_V0

    def _apply_fallback_features(self) -> None:
        """
        Use when the context from Connection.login isn't available but you still need access to feature flags.

        Requests the base app html and applies a very, very dumb regex to find window.__FEATURES__
        Don't be surprised when this breaks due to nearly any changes on their side.
        """
        try:
            r = self.session.get(APP_HTML_URL)
            r.raise_for_status()
            match = RE_FEATURES.search(r.text)
            if not match:
                raise ValueError("no match")
            raw = match.groupdict()["features"]
            features = json.loads(raw)
        except Exception as e:
            raise RuntimeError((
                "failed to parse features using fallback method.\n"
                "please file an issue at https://github.com/numberoverzero/brainfm/issues"
            )) from e
        else:
            self._apply_features(features)
