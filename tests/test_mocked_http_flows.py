from dataclasses import dataclass

import pandas as pd

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


FAIR_USE_COLUMNS = [
    "tier",
    "display_name",
    "per_day",
    "day_requests",
    "remaining_today",
    "per_hour",
    "hour_requests",
    "remaining_this_hour",
    "km2_per_day",
    "day_km2",
    "km2_per_hour",
    "hour_km2",
    "concurrent",
    "running",
    "waiting_limit",
    "waiting",
    "hour_resets_at",
    "day_resets_at",
]


def _fair_use_payload(**limit_overrides):
    limits = {
        "concurrent": 3,
        "per_hour": 30,
        "per_day": 200,
        "km2_per_hour": 15000,
        "km2_per_day": 50000,
        "waiting": 20,
    }
    limits.update(limit_overrides)
    return {
        "tier": "free",
        "display_name": "Test User",
        "limits": limits,
        "usage": {
            "running": 1,
            "waiting": 0,
            "hour_requests": 4,
            "hour_km2": 12.5,
            "day_requests": 17,
            "day_km2": 140.25,
        },
        "resets": {
            "hour_at": "2026-10-11T15:00:00+00:00",
            "day_at": "2026-10-12T14:12:00+00:00",
        },
    }


def test_get_remaining_queries_calls_fair_use_status(monkeypatch):
    captured = {}

    def fake_post(url, headers=None, json=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return FakeResponse(200, _fair_use_payload())

    monkeypatch.setattr("socialinfrascorepy._account._requests.post", fake_post)

    authed = si.client("https://demo.supabase.co", "anon", access_token="token")
    df = si.get_remaining_queries(authed)

    assert captured["url"].endswith("/rest/v1/rpc/fn_fair_use_status")
    assert captured["json"] == {}
    assert captured["headers"]["Authorization"] == "Bearer token"

    assert list(df.columns) == FAIR_USE_COLUMNS
    assert len(df) == 1
    row = df.iloc[0]
    assert row["tier"] == "free"
    assert row["display_name"] == "Test User"
    assert row["per_day"] == 200
    assert row["day_requests"] == 17
    assert row["remaining_today"] == 183
    assert row["per_hour"] == 30
    assert row["hour_requests"] == 4
    assert row["remaining_this_hour"] == 26
    assert row["km2_per_day"] == 50000
    assert row["day_km2"] == 140.25
    assert row["km2_per_hour"] == 15000
    assert row["hour_km2"] == 12.5
    assert row["concurrent"] == 3
    assert row["running"] == 1
    assert row["waiting_limit"] == 20
    assert row["waiting"] == 0
    assert row["hour_resets_at"] == pd.Timestamp("2026-10-11T15:00:00Z")
    assert row["day_resets_at"] == pd.Timestamp("2026-10-12T14:12:00Z")


def test_get_remaining_queries_unlimited_is_missing(monkeypatch):
    payload = _fair_use_payload(
        per_day=-1,
        per_hour=-1,
        km2_per_day=-1,
        km2_per_hour=-1,
        concurrent=-1,
        waiting=-1,
    )
    payload["tier"] = "developer"
    payload["resets"] = {"hour_at": None, "day_at": None}

    def fake_post(url, headers=None, json=None):
        return FakeResponse(200, payload)

    monkeypatch.setattr("socialinfrascorepy._account._requests.post", fake_post)

    authed = si.client("https://demo.supabase.co", "anon", access_token="token")
    df = si.get_remaining_queries(authed)

    row = df.iloc[0]
    assert row["tier"] == "developer"
    for col in (
        "per_day",
        "remaining_today",
        "per_hour",
        "remaining_this_hour",
        "km2_per_day",
        "km2_per_hour",
        "concurrent",
        "waiting_limit",
    ):
        assert pd.isna(row[col]), col
    # Usage is still reported when limits are unlimited.
    assert row["day_requests"] == 17
    assert row["hour_requests"] == 4
    assert pd.isna(row["hour_resets_at"])
    assert pd.isna(row["day_resets_at"])


def test_get_remaining_queries_never_negative(monkeypatch):
    payload = _fair_use_payload(per_hour=3)

    def fake_post(url, headers=None, json=None):
        return FakeResponse(200, payload)

    monkeypatch.setattr("socialinfrascorepy._account._requests.post", fake_post)

    authed = si.client("https://demo.supabase.co", "anon", access_token="token")
    df = si.get_remaining_queries(authed)

    assert df.iloc[0]["remaining_this_hour"] == 0
