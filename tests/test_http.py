import pytest
import requests

import socialinfrascorepy as si
from socialinfrascorepy import _http
from socialinfrascorepy._themes import _get_themes

URL = "https://demo.supabase.co"


def anon():
    return si.client(URL, "anon-key")


def authed():
    return si.client(URL, "anon-key", access_token="user-token")


def test_anonymous_call_sends_apikey_and_anon_bearer(http):
    http.reply(200, [{"theme": 1, "type": "Park"}])
    out = _http.perform(anon(), "/rest/v1/rpc/fn_get_themes", json={})

    assert out == [{"theme": 1, "type": "Park"}]
    call = http.last
    assert call["method"] == "POST"
    assert call["url"] == f"{URL}/rest/v1/rpc/fn_get_themes"
    assert call["headers"]["apikey"] == "anon-key"
    assert call["headers"]["Authorization"] == "Bearer anon-key"
    assert call["json"] == {}


def test_authenticated_call_sends_user_bearer(http):
    http.reply(200, [])
    _http.perform(authed(), "/rest/v1/requests", method="get", params={"limit": 1}, auth=True)

    call = http.last
    assert call["method"] == "GET"
    assert call["headers"]["apikey"] == "anon-key"
    assert call["headers"]["Authorization"] == "Bearer user-token"
    assert call["params"] == {"limit": 1}


def test_auth_required_raises_before_any_network(http):
    with pytest.raises(si.SIScorecardError, match="sign_in"):
        _http.perform(anon(), "/rest/v1/requests", method="GET", auth=True)
    assert http.calls == []


def test_non_auth_call_ignores_token_and_uses_anon_bearer(http):
    http.reply(200, {})
    _http.perform(authed(), "/auth/v1/signup", json={"email": "a"})
    assert http.last["headers"]["Authorization"] == "Bearer anon-key"


def test_path_joining_tolerates_missing_leading_slash(http):
    http.reply(200, [])
    _http.perform(anon(), "rest/v1/x")
    assert http.last["url"] == f"{URL}/rest/v1/x"


def test_postgrest_error_message_is_surfaced(http):
    http.reply(401, {"message": "JWT expired", "code": "PGRST301"})
    with pytest.raises(si.SIScorecardError, match="JWT expired") as exc:
        _http.perform(authed(), "/rest/v1/requests", method="GET", auth=True)
    assert exc.value.status_code == 401


def test_gotrue_error_messages_are_surfaced(http):
    http.reply(400, {"error": "invalid_grant", "error_description": "Invalid login credentials"})
    with pytest.raises(si.SIScorecardError, match="Invalid login credentials"):
        _http.perform(anon(), "/auth/v1/token", params={"grant_type": "password"})

    http.reply(422, {"msg": "Password should be at least 6 characters"})
    with pytest.raises(si.SIScorecardError, match="at least 6"):
        _http.perform(anon(), "/auth/v1/signup")


def test_non_json_error_falls_back_to_body_text(http):
    http.reply(502, text="Bad gateway")
    with pytest.raises(si.SIScorecardError, match="Bad gateway"):
        _http.perform(anon(), "/rest/v1/x")


def test_empty_body_returns_empty_list(http):
    http.reply(200, text="")
    assert _http.perform(anon(), "/rest/v1/x") == []


def test_transport_failure_becomes_si_error(http):
    http.error = requests.ConnectionError("no route")
    with pytest.raises(si.SIScorecardError, match="no route"):
        _http.perform(anon(), "/rest/v1/x")


def test_every_module_routes_through_perform(http):
    """No module other than _http may import requests."""
    import pathlib

    src = pathlib.Path(_http.__file__).parent
    offenders = [
        p.name
        for p in src.glob("*.py")
        if p.name != "_http.py" and "import requests" in p.read_text()
    ]
    assert offenders == []


def test_pyodide_patch_is_noop_outside_browser():
    assert _http._patch_for_pyodide() is False


def test_pyodide_patch_calls_pyodide_http_when_available(monkeypatch):
    import sys
    import types

    calls = []
    fake = types.SimpleNamespace(patch_all=lambda: calls.append("patched"))
    monkeypatch.setattr(sys, "platform", "emscripten")
    monkeypatch.setitem(sys.modules, "pyodide_http", fake)
    monkeypatch.setattr(_http, "_PYODIDE_PATCHED", False)

    assert _http._patch_for_pyodide() is True
    assert calls == ["patched"]


def test_pyodide_patch_survives_missing_pyodide_http(monkeypatch):
    import sys

    monkeypatch.setattr(sys, "platform", "emscripten")
    monkeypatch.setitem(sys.modules, "pyodide_http", None)  # forces ImportError
    monkeypatch.setattr(_http, "_PYODIDE_PATCHED", False)
    assert _http._patch_for_pyodide() is False


def test_internal_get_themes_posts_to_rpc(http):
    http.reply(200, [{"theme": i, "type": f"t{i}"} for i in range(5)])
    df = _get_themes(anon())
    assert len(df) == 5
    assert http.last["url"].endswith("/rest/v1/rpc/fn_get_themes")
