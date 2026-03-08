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
