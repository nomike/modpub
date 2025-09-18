from unittest import mock
from modpub.plugins.thingiverse.api import ThingiverseAPI

def test_headers():
    api = ThingiverseAPI(access_token="abc")
    h = api._headers()
    assert h["Authorization"].startswith("Bearer ")

def test_get_thing_builds_url():
    api = ThingiverseAPI(access_token="abc")
    with mock.patch.object(api.session, "get") as m:
        m.return_value.status_code = 200
        m.return_value.json.return_value = {"id": 1}
        api.get_thing("1")
        args, kwargs = m.call_args
        assert args[0].endswith("/things/1")
