import warnings

import pytest

import socialinfrascorepy as si

URL = "https://demo.supabase.co"


def test_sign_in_uses_expected_endpoint(http):
    http.reply(200, {
        "access_token": "access",
        "refresh_token": "refresh",
        "expires_in": 3600,
        "token_type": "bearer",
    })

    cli = si.client(URL, "anon")
    result = si.sign_in(cli, "user@example.com", "pw")

    assert http.last["url"] == f"{URL}/auth/v1/token"
    assert http.last["params"] == {"grant_type": "password"}
    assert http.last["json"]["email"] == "user@example.com"
    assert result["client"].access_token == "access"


def test_sign_in_bad_password_raises_server_message(http):
    http.reply(400, {"error_description": "Invalid login credentials"})
    with pytest.raises(si.SIScorecardError, match="Invalid login"):
        si.sign_in(si.client(URL, "anon"), "u@example.com", "bad")


def test_get_request_status_uses_expected_query(http):
    http.reply(200, [{"id": "req-1", "status": "success"}])

    authed = si.client(URL, "anon", access_token="token")
    df = si.get_request_status(authed, "req-1")

    assert http.last["method"] == "GET"
    assert http.last["url"].endswith("/rest/v1/requests")
    assert http.last["params"]["id"] == "eq.req-1"
    assert http.last["headers"]["Authorization"] == "Bearer token"
    assert df.iloc[0]["status"] == "success"


GEOM = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}


def test_submit_request_serializes_theme_ids(http):
    http.reply(200, {"request": {"id": "req-2"}})

    authed = si.client(URL, "anon", access_token="token")
    result = si.submit_request(authed, geometry=GEOM, theme_ids=[1, 3, 4])

    assert http.last["url"].endswith("/rest/v1/rpc/fn_submit_request")
    assert http.last["json"]["p_theme_ids"] == "1,3,4"
    assert result["request"]["id"] == "req-2"


def test_submit_request_does_not_send_retired_params(http):
    http.reply(200, {"request": {"id": "req-3"}})
    authed = si.client(URL, "anon", access_token="token")

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        si.submit_request(authed, geometry=GEOM, sites_grid_sqkm=2, n_keywords=9)

    payload = http.last["json"]
    assert "p_sites_grid_sqkm" not in payload
    assert "p_n_keywords" not in payload
    msgs = " ".join(str(w.message) for w in caught)
    assert "sites_grid_sqkm" in msgs and "n_keywords" in msgs and "ignored" in msgs


def test_submit_request_rejects_unknown_kwargs(http):
    authed = si.client(URL, "anon", access_token="token")
    with pytest.raises(TypeError, match="bogus"):
        si.submit_request(authed, geometry=GEOM, bogus=1)
    assert http.calls == []


def test_submit_request_requires_sign_in(http):
    with pytest.raises(si.SIScorecardError, match="sign_in"):
        si.submit_request(si.client(URL, "anon"), geometry=GEOM)
    assert http.calls == []


def test_deprecated_theme_aliases_warn_and_still_work(http):
    http.reply(200, [{"theme": 1, "type": "Park"}])
    cli = si.client(URL, "anon")
    with pytest.warns(DeprecationWarning, match="get_themes"):
        df = si.get_themes(cli)
    assert len(df) == 1

    http.reply(200, [{"theme": 1, "type": "Park", "term": "park"}])
    with pytest.warns(DeprecationWarning, match="get_theme_keywords"):
        si.get_theme_keywords(cli, theme_ids=[1])
    assert http.last["json"] == {"p_theme_ids": "1"}


def test_get_sites_posts_location_id(http):
    http.reply(200, [{"source": "overture"}])
    authed = si.client(URL, "anon", access_token="token")
    df = si.get_sites(authed, "42", limit=10)
    assert http.last["json"] == {"p_location_id": "42", "p_limit": 10}
    assert df.iloc[0]["source"] == "overture"
