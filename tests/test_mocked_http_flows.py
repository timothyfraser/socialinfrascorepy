from dataclasses import dataclass

import socialinfrascorepy as si


@dataclass
class FakeResponse:
    status_code: int
    payload: object

    @property
    def text(self):
        if self.payload is None:
            return ""
        return "ok"

    def json(self):
        return self.payload


def test_sign_in_uses_expected_endpoint(monkeypatch):
    called = {}

    def fake_post(url, headers=None, json=None):
        called["url"] = url
        called["json"] = json
        return FakeResponse(200, {
            "access_token": "access",
            "refresh_token": "refresh",
            "expires_in": 3600,
            "token_type": "bearer",
        })

    monkeypatch.setattr("socialinfrascorepy._auth._requests.post", fake_post)

    cli = si.client("https://demo.supabase.co", "anon")
    result = si.sign_in(cli, "user@example.com", "pw")

    assert called["url"].endswith("/auth/v1/token?grant_type=password")
    assert called["json"]["email"] == "user@example.com"
    assert result["client"].access_token == "access"


def test_get_request_status_uses_expected_query(monkeypatch):
    captured = {}

    def fake_get(url, headers=None, params=None):
        captured["url"] = url
        captured["params"] = params
        return FakeResponse(200, [{"id": "req-1", "status": "success"}])

    monkeypatch.setattr("socialinfrascorepy._requests._requests.get", fake_get)

    authed = si.client("https://demo.supabase.co", "anon", access_token="token")
    df = si.get_request_status(authed, "req-1")

    assert captured["url"].endswith("/rest/v1/requests")
    assert captured["params"]["id"] == "eq.req-1"
    assert df.iloc[0]["status"] == "success"


def test_submit_request_serializes_theme_ids(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, json=None):
        captured["url"] = url
        captured["json"] = json
        return FakeResponse(200, {"request": {"id": "req-2"}})

    monkeypatch.setattr("socialinfrascorepy._requests._requests.post", fake_post)

    authed = si.client("https://demo.supabase.co", "anon", access_token="token")
    geom = {"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]}

    result = si.submit_request(
        authed,
        geometry=geom,
        theme_ids=[1, 3, 4],
        sites_grid_sqkm=2,
    )

    assert captured["url"].endswith("/rest/v1/rpc/fn_submit_request")
    assert captured["json"]["p_theme_ids"] == "1,3,4"
    assert result["request"]["id"] == "req-2"
