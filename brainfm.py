import jmespath
import operator
import requests

__version__ = "0.1.1"

# http://www.useragentstring.com/index.php?id=19841
BROWSER = ("Mozilla/5.0 (Windows NT 6.1) "
           "AppleWebKit/537.36 (KHTML, like Gecko) "
           "Chrome/41.0.2228.0 Safari/537.36")
DEFAULT_USER_AGENT = "github.com/numberoverzero/brainfm v" + __version__

operation_map = {
    # setSessionCompleted  # dumps a ton of info from station_data and session_data dicts
    # setTrialSessionCompletedFunc  # unknown; not seen
    # createFeedbackQueue  # called after seeking in a long session, before setSessionCompleted
    "set_rating": {
        "name": "setRating",
        "method": "post",
        "parameters": [
            {
                "name": "session_id",
                "required": True,
                "type": int
            },
            {
                "name": "rating",
                "required": True,
                "type": int
            },
            {
                "name": "token",
                "alias": "stream_token",
                "required": True,
                "type": str
            },
            {
                "name": "station_id",
                "required": True,
                "type": int
            },
            {
                "name": "reason",
                "required": True,
                "type": str
            }
        ],
        "response": None
    },
    # setTestCompleted  # unknown; not seen
    # setFeedback
    "get_stations": {
        "name": "getExploreStations",
        "method": "post",
        "parameters": [],
        "response": jmespath.compile(
            "*[*].{station_id:id, name:name, canonical_name:string_id}[]")
    },
    # getMainStations  # not implemented for now, use get_stations
    # getMainStations_NoPlans  # not implemented for now, use get_stations
    # getStationsByID  # unknown; not seen
    "get_station": {
        "name": "getStation",
        "method": "post",
        "parameters": [
            {
                "name": "id",
                "alias": "station_id",
                "required": True,
                "type": int
            }
        ],
        "response": jmespath.compile(
            "{station_id: id, name: name, canonical_name: string_id}")
    },
    "get_token": {
        "name": "getTokenJSON",
        "method": "post",
        "parameters": [
            {
                "name": "sid",
                "alias": "station_id",
                "required": True,
                "type": int
            },
            {
                # TODO WHAT IS THIS
                "name": "m",
                "required": False,
                "default": False,
                "type": bool
            },
            {
                "name": "pt",
                "alias": "previous_session_token",
                "required": False,
                "type": str
            }
        ],
        "response": jmespath.compile(
            "{session_id: id, group: group, name: name, "
            "station_id: station_id, session_token: token}")
    },
    # testToken  # unknown; not seen
    # getFeedbackQueueJSON  # unknown; not seen
    # setDisclaimerAccepted  # unknown; not seen
}


def param_name(p):
    return p.get("alias", p["name"])


def build_operation(name):
    spec = operation_map[name]
    parameters = spec["parameters"]

    def operation(self, **kwargs):
        # 0. Validate parameters
        expected = set(param_name(p) for p in parameters)
        required = set(param_name(p) for p in parameters if p["required"])
        actual = set(kwargs.keys())
        # Too many parameters
        if actual - expected:
            raise TypeError(
                "Unexpected parameters {}".format(actual - expected))
        # Too few parameters
        if required - actual:
            raise TypeError(
                "Missing required parameters {}".format(required - actual))

        # 1. Transform alias -> name
        wire_kwargs = {}
        for param in parameters:
            if param_name(param) in kwargs:
                wire_kwargs[param["name"]] = kwargs[param_name(param)]
            elif "default" in param:
                default = param["default"]
                if callable(default):
                    default = default()
                wire_kwargs[param["name"]] = default

                    # 2. Send request through connection
        resp = self._rtecm(spec, wire_kwargs)

        # 3. Unpack response if the operation has one
        if spec["response"]:
            return spec["response"].search(resp)

    doc = "Calls {}.".format(spec["name"])
    if parameters:
        doc += "\n"
        tpl = "\n:param {type} {name}: {required}"
        for param in sorted(parameters, key=operator.itemgetter("name")):
            doc += tpl.format(
                type=param["type"].__name__,
                name=param_name(param),
                required="Required" if param["required"] else "(Optional)"
            )
    operation.__doc__ = doc
    return operation


class Connection:
    """Low-level operation mapping and parameter validation.

    If brain.fm starts filtering on user-agent,
    set :attr:`Connection.user_agent` to :data:`brainfm.BROWSER`.
    """

    def __init__(self, email, password):
        self._credentials = {
            "email": email,
            "pass": password
        }
        self._svu = None
        self._operation_keys = None
        self.user_agent = DEFAULT_USER_AGENT

    @property
    def svu(self):
        if self._svu is None:
            # login
            r = requests.post(
                "https://www.brain.fm/login",
                json=self._credentials,
                headers={"User-Agent": self.user_agent})
            r.raise_for_status()
            self._svu = r.json()["siteVisitorUUID"]
        return self._svu

    @property
    def operation_keys(self):
        if self._operation_keys is None:
            # get operation keys
            r = requests.post(
                "https://www.brain.fm/post/rtecmg",
                json={"svu": self.svu},
                headers={"User-Agent": self.user_agent})
            r.raise_for_status()
            self._operation_keys = r.json()
        return self._operation_keys

    def _rtecm(self, spec, wire_kwargs):
        # TODO ===============================================================
        # cst will probably change in the future, but
        # for now the javascript does a random walk to inject
        # the operation characters into the svu.
        # Because the svu is random and the offset uses Math.random:
        #
        #     var f = d + Math.floor(Math.random() * (a.length / 5));
        #
        # cst could technically collide on every character being identical
        # until the last character.  This collapses the complex ``inter``
        # function down to a simple append; the consuming application almost
        # certainly rebuilds the operation argument by stripping it from the
        # uuid (and ignores average offset of the operation characters).
        #
        # To find the function in the future, it's currently called a.inter
        # and uses String.prototype.insertStringAt
        # TODO ===============================================================
        payload = {
            "svu": self.svu,
            "cst": self.svu + self.operation_keys[spec["name"]],
            **wire_kwargs,
        }

        r = requests.post(
            "https://www.brain.fm/post/rtecm",
            data=payload,
            headers={"User-Agent": self.user_agent})
        r.raise_for_status()
        return r.json()

for name in operation_map:
    func = build_operation(name)
    setattr(Connection, name, func)
