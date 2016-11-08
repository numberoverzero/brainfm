import requests

__version__ = "0.1.0"


class Connection:
    def __init__(self):
        self.session = requests.session()
        # siteVisitorUUID
        self.svu = None
        self.operations = {}

    def login(self, email, password):
        r = self.session.post(
            "https://www.brain.fm/login",
            json={"email": email, "pass": password})
        r.raise_for_status()
        self.svu = r.json()["siteVisitorUUID"]

    def load_operations(self):
        r = self.session.post(
            "https://www.brain.fm/post/rtecmg",
            json={"svu": self.svu})
        r.raise_for_status()
        self.operations = r.json()

    def get_stations(self):
        return self._rtecm("getExploreStations")

    def _rtecm(self, operation, **kwargs):
        # TODO cst will probably change in the future, but
        # for now the javascript does a random walk to inject
        # the operation characters into the svu.
        # Because the svu is random:
        #
        #     var f = d + Math.floor(Math.random() * (a.length / 5));
        #
        # cst could technically collide on every character being identical
        # until the last character.  This collapses the complex ``inter``
        # function down to a simple append; the consuming application almost
        # certainly rebuilds the operation argument by stripping it from the
        # uuid (and ignores average offset of the operation characters)

        payload = {
            "svu": self.svu,
            "cst": self.svu + self.operations[operation],
            **kwargs,
        }

        r = self.session.post(
            "https://www.brain.fm/post/rtecm",
            json=payload)
        r.raise_for_status()
        return r.json()
