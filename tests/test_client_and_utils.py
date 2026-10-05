import pytest

import socialinfrascorepy as si
from socialinfrascorepy._utils import _as_dataframe, _clamp_limit


def test_client_strips_url_and_requires_strings():
    c = si.client("https://demo.supabase.co///", "anon-key")
    assert c.supabase_url == "https://demo.supabase.co"

    with pytest.raises(si.SIScorecardError):
        si.client("", "anon-key")
    with pytest.raises(si.SIScorecardError):
        si.client("https://demo.supabase.co", "")


def test_clamp_limit_behavior():
    assert _clamp_limit(5, max_limit=10) == 5
    assert _clamp_limit(0, max_limit=10) == 1
    assert _clamp_limit(999, max_limit=10) == 10


def test_as_dataframe_shapes():
    assert _as_dataframe(None).empty
    assert _as_dataframe([]).empty

    df_dict = _as_dataframe({"a": 1})
    assert list(df_dict.columns) == ["a"]
    assert len(df_dict) == 1

    df_list = _as_dataframe([{"a": 1}, {"a": 2}])
    assert list(df_list["a"]) == [1, 2]


PUBLIC_URL = "https://annuvayiqynyksnzkpoy.supabase.co"
PUBLIC_KEY = "sb_publishable_SS0DtvFh990Zcj-6q7t4nw_VRdCF_Vb"


def test_client_defaults_to_public_project(monkeypatch):
    monkeypatch.delenv("SI_SUPABASE_URL", raising=False)
    monkeypatch.delenv("SI_SUPABASE_ANON_KEY", raising=False)
    c = si.client()
    assert c.supabase_url == PUBLIC_URL
    assert c.anon_key == PUBLIC_KEY
    assert c.access_token is None


def test_client_env_vars_override_defaults(monkeypatch):
    monkeypatch.setenv("SI_SUPABASE_URL", "https://self-hosted.example.com/")
    monkeypatch.setenv("SI_SUPABASE_ANON_KEY", "env-key")
    c = si.client()
    assert c.supabase_url == "https://self-hosted.example.com"
    assert c.anon_key == "env-key"


def test_client_empty_env_vars_fall_back_to_defaults(monkeypatch):
    monkeypatch.setenv("SI_SUPABASE_URL", "")
    monkeypatch.setenv("SI_SUPABASE_ANON_KEY", "")
    c = si.client()
    assert c.supabase_url == PUBLIC_URL
    assert c.anon_key == PUBLIC_KEY


def test_client_explicit_args_beat_env_and_positional_works(monkeypatch):
    monkeypatch.setenv("SI_SUPABASE_URL", "https://env.example.com")
    monkeypatch.setenv("SI_SUPABASE_ANON_KEY", "env-key")
    c = si.client("https://arg.example.com", "arg-key")
    assert (c.supabase_url, c.anon_key) == ("https://arg.example.com", "arg-key")
    c = si.client(anon_key="only-key")
    assert (c.supabase_url, c.anon_key) == ("https://env.example.com", "only-key")
